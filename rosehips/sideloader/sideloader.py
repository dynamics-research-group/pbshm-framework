import glob
import importlib
import importlib.util
import os
import json
import site
import sys
import subprocess
import typing

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

def register_sideloaded_modules() -> None:
    #Calculate site packages
    site_package_paths = site.getsitepackages()
    default_package_path = os.path.join(site_package_paths[1 if len(site_package_paths) > 1 and sys.platform == "win32" else 0])
    #Load modules
    for search_file in glob.glob(os.path.join(current_app.instance_path, "*[!-disabled].module")):
        with open(os.path.join(current_app.instance_path, search_file), "r") as module_file:
            #Ensure path
            module_config = json.load(module_file)
            module_path = module_config["path"]
            if len(module_path) < 2:
                continue
            #Determine path location
            selected_module_path, default_search_path = None, os.path.join(default_package_path, *module_path[:-1])
            if os.path.isdir(default_search_path): selected_module_path = default_search_path
            else:
                for potential_path in site_package_paths:
                    current_search_path = os.path.join(potential_path, *module_path[:-1])
                    if current_search_path == default_search_path:
                        continue
                    elif os.path.isdir(current_search_path):
                        selected_module_path = current_search_path
                        break
            if selected_module_path is None:
                print(f"Unable to locate path for namespace {module_config['namespace']}")
                continue
            #Load module
            print(f"Registering {module_config['namespace']} from {os.path.join(selected_module_path, module_config['path'][-1])}")
            module_spec = importlib.util.spec_from_file_location(module_config["namespace"], os.path.join(selected_module_path, module_config["path"][-1]))
            module = importlib.util.module_from_spec(module_spec)
            sys.modules[module_config["namespace"]] = module
            module_spec.loader.exec_module(module)
            #Register blueprint
            if module_config["blueprint"]:
                bp.register_blueprint(module.bp, url_prefix=module_config["url_prefix"])
            #Navigation
            for navigation_section in module_config["navigation"]:
                if navigation_section not in current_app.config["NAVIGATION"]:
                    current_app.config["NAVIGATION"][navigation_section] = {display_value:f"sideloader.{endpoint_value}" for (display_value, endpoint_value) in module_config["navigation"][navigation_section].items()}
                else:
                    for display_value in module_config["navigation"][navigation_section]:
                        if display_value not in current_app.config["NAVIGATION"][navigation_section]:
                            current_app.config["NAVIGATION"][navigation_section][display_value] = f"sideloader.{module_config['navigation'][navigation_section][display_value]}"

@bp.context_processor
def utility_processor():
    def url_for(
        endpoint: str,
        *,
        _anchor: str = None,
        _method: str = None,
        _scheme: str = None,
        _external: bool = None,
        **values: typing.Any
    ) -> str:
        endpoint_suffix_index = endpoint.find('.')
        if endpoint_suffix_index > 0:
            endpoint_suffix = endpoint[:endpoint_suffix_index]
            for child_blueprints, _ in bp._blueprints:
                if child_blueprints.name == endpoint_suffix:
                    endpoint = f"{bp.name}.{endpoint}"
                    break
        return current_app.url_for(endpoint, _anchor=_anchor, _method=_method, _scheme=_scheme, _external=_external, **values)
    return dict(url_for=url_for)

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
