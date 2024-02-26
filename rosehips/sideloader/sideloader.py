import glob
import os
import json
import sys
import subprocess

from flask import Blueprint, request, current_app, render_template, jsonify
from werkzeug.utils import secure_filename

from pbshm.authentication import authenticate_request

#Create sideloader blueprint
bp = Blueprint(
    "sideloader",
    __name__,
    static_folder = "static",
    template_folder = "templates"
)

@bp.route("/", methods=("GET", "POST"))
@authenticate_request("sideloader-list")
def list_modules():
    # Upload
    error = ""
    if request.method == "POST":
        if "configuration" not in request.files:
            error = "No file found"
        else:
            # Ensure JSON file type
            file = request.files["configuration"]
            if file.filename.strip() == "":
                error = "No file selected"
            elif file.filename.rsplit('.', 1)[1].lower() != "json":
                error = "The file must be a JSON file"
            else:
                # Ensure valid JSON
                config_str = file.read()
                config = {}
                try:
                    config = json.loads(config_str)
                except ValueError as err:
                    error = "Invalid JSON file"
                if config:
                    # Ensure required keys
                    keys = ["package", "namespace", "path", "url_prefix", "blueprint"]
                    for key in keys:
                        if key not in config:
                            error = f"{key} key is missing in JSON"
                            break
                        elif not isinstance(config[key], bool) and len(config[key]) == 0:
                            error = f"{key} key must have a value"
                            break
                    if len(error) == 0:
                        # Ensure package values
                        package = None
                        if "name" not in config["package"]:
                            package = config["package"]
                        else:
                            if "source" not in config["package"]:
                                error = "source key in package is missing in JSON"
                            elif len(config["package"]["source"]) == 0:
                                error = "source key in package must have a value"
                            else:
                                package = config["package"]["name"]
                        if package is not None:
                            # Ensure package configuration
                            if len(package) == 0:
                                error = "the name of the package cannot be empty"
                            elif package.find("git+") == 0:
                                error = "when using a git+ package url, the name must be declared in the JSON file which matches the name given within the project build file" 
                            elif os.path.isfile(os.path.join(current_app.instance_path, f"{secure_filename(package)}-disabled.module")):
                                error = f"there is already a pending module file for {package}"
                            elif os.path.isfile(os.path.join(current_app.instance_path, f"{secure_filename(package)}.module")):
                                error = f"there is already an installed module file for {package}"
                            else:
                                # Save module config
                                with open(os.path.join(current_app.instance_path, f"{secure_filename(package)}-disabled.module"), "w", encoding="utf-8") as write_file:
                                    json.dump(config, write_file, indent=4)
    # Existing Modules
    modules = []
    for config_file in glob.glob(os.path.join(current_app.instance_path, "*.module")):
        with open(os.path.join(current_app.instance_path, config_file), "r") as module:
            module_config = json.load(module)
            module_config["enabled"] = False if config_file.rfind("-disabled.module") == len(config_file) - len("-disabled.module") else True
            modules.append(module_config)
    return render_template("sideload-modules.html", modules=modules, error=error)

@bp.route("/install-module/<module_name>", methods=["POST"])
@authenticate_request("sideloader-install")
def install_module(module_name: str):
    if os.path.isfile(os.path.join(current_app.instance_path, f"{module_name}.module")):
        raise Exception(f"The module {module_name} is already installed on this instance of the framework")
    if not os.path.isfile(os.path.join(current_app.instance_path, f"{module_name}-disabled.module")):
        raise Exception(f"The module {module_name} does not exist in this instance of the framework")
    with open(os.path.join(current_app.instance_path, f"{module_name}-disabled.module"), "r") as module_file:
        module_config = json.load(module_file)
        if "source" in module_config["package"]:
            print(f"Installing module {module_name} via pip package {module_config['package']['name']}({module_config['package']['source']}@{module_config['package']['version'] if 'version' in module_config['package'] else 'latest'})")
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{module_config['package']['source']}=={module_config['package']['version']}" if 'version' in module_config['package'] else module_config['package']['source']])
        else:
            print(f"Installing module {module_name} via pip package {module_config['package']}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_config["package"]])
        print(f"Marking module {module_name} as enabled")
        os.rename(os.path.join(current_app.instance_path, f"{module_name}-disabled.module"), os.path.join(current_app.instance_path, f"{module_name}.module"))
    return jsonify({"status":"installed"})

@bp.route("/uninstall-module/<module_name>", methods=["POST"])
@authenticate_request("sideloader-uninstall")
def uninstall_module(module_name: str):
    if os.path.isfile(os.path.join(current_app.instance_path, f"{module_name}-disabled.module")):
        raise Exception(f"The module {module_name} is already uninstalled on this instance of the framework")
    if not os.path.isfile(os.path.join(current_app.instance_path, f"{module_name}.module")):
        raise Exception(f"The module {module_name} is not installed on this instance of the framework")
    with open(os.path.join(current_app.instance_path, f"{module_name}.module"), "r") as module_file:
        module_config = json.load(module_file)
        package = module_config["package"]["name"] if "name" in module_config["package"] else module_config["package"]
        print(f"Uninstalling module {module_name} via pip package {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        print(f"Marking module {module_name} as disabled")
        os.rename(os.path.join(current_app.instance_path, f"{module_name}.module"), os.path.join(current_app.instance_path, f"{module_name}-disabled.module"))
    return jsonify({"status":"uninstalled"})
    