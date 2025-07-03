#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def load_versions(versions_file="versions.json"):
    """Load version configuration from JSON file."""
    try:
        with open(versions_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {versions_file} not found. Please run 'versions.sh' first.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {versions_file}: {e}")
        sys.exit(1)

def generate_containerfile(template, context):
    """Generate Containerfile content based on image variant."""
    content = template.render(context)
    return re.sub(r'[\r\n][\r\n]{2,}', '\n\n', content)

def main():
    """Main function to process templates."""
    # Load versions configuration
    versions_data = load_versions()

    # Setup Jinja2 environment and load template
    env = Environment(
        loader=FileSystemLoader('.'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template("Containerfile.j2")

    # Determine which versions to process
    if len(sys.argv) > 1:
        requested_versions = sys.argv[1:]
    else:
        requested_versions = list(versions_data.keys())

    # Process each requested version
    for version in requested_versions:
        if version not in versions_data:
            print(f"Warning: Version '{version}' not found in versions.json")
            continue

        print(f"Applying templates for version: {version}")

        # Process each image configuration for this version
        for image_tag, config in versions_data[version].items():
            framework_version = config["framework_version"]
            image_variant = config["framework_image_variant"]
            python_version = config["python_version"]
            debian_version = config["debian_version"]

            print(f"Processing: {image_tag} = {framework_version} with {image_variant} image, Python {python_version} on {debian_version}")

            # Create output directory
            output_dir = Path(framework_version) / image_variant / f"python{python_version}" / debian_version
            print(f"Creating directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Prepare template context
            context = config | {
                "needs_mongodb" : image_variant in [ "dev", "standalone"],
                "needs_supervisor": image_variant in ["dev", "standalone"],
                "needs_caddy": image_variant == "standalone",
            }

            # Generate and write Containerfile
            print(f"Creating Containerfile in {output_dir}...")
            containerfile_content = generate_containerfile(template, context)

            containerfile_path = output_dir / "Containerfile"
            with open(containerfile_path, 'w') as f:
                f.write(containerfile_content)

            print("Generated Containerfile")

if __name__ == "__main__":
    main()
