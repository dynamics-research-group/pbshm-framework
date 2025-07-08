import importlib
import pathlib

from jinja2 import Environment, FileSystemLoader

generatedmatrix = importlib.import_module("generate-matrix")

def load_build_matrix():
    """Load build matrix"""
    return generatedmatrix.main()

def generate_containerfile(template, context):
    """Generate Containerfile content based on build variant."""
    return template.render(context)

def main():
    """Apply templates to build matrix"""
    
    # get current build list
    matrix = load_build_matrix()

    # Setup Jinja2 environment and load template
    env = Environment(
        loader=FileSystemLoader('.'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template("Containerfile.j2")

    # itterate through builds
    for build in matrix["include"]:

        # ensure folder structure        
        container_path = pathlib.Path(build["containerfiles"][0:build["containerfiles"].rindex("/")])
        container_path.mkdir(parents=True, exist_ok=True)

        # generate build context
        build_context = build["build_info"]
        build_context["path"] = build["containerfiles"][0:build["containerfiles"].rindex("/")]
        
        # generate container file
        container_content = generate_containerfile(template, build_context)

        # write container file
        print(f"Writing {build["containerfiles"]}")
        with open(build["containerfiles"], "w") as file:
            file.write(container_content)
    
    # complete
    print(f"Generated {len(matrix["include"])} Containerfiles")

if __name__ == "__main__":
    main()