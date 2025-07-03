#!/usr/bin/env python3

import json
from pathlib import Path

def generate_versions():
    """Generate versions.json configuration file."""

    # TODO: some of these can probably be generated programmatically, 
    # e.g. by pulling metadata from the PyPI JSON API, but for now we will hardcode them

    framework_versions = ["0.7.1"]
    framework_image_variants = ["base", "dev", "standalone"]
    python_versions = ["3.12", "3.13"]
    debian_versions = ["bookworm", "trixie"]
    wsgi_package = "gunicorn"  # TODO: eventually this can be a list of wsgi packages
    database_version =  "8.0"

    # Generate JSON with PBSHM framework version as top-level key
    config = {}

    for framework_version in framework_versions:
        print(f"Processing PBSHM framework version: {framework_version}")

        # Initialize the framework version key with an empty object
        config[framework_version] = {}

        for framework_image_variant in framework_image_variants:
            for python_version in python_versions:
                for debian_version in debian_versions:
                    # Create a configuration key for this combination
                    image_tag = f"{framework_version}-{framework_image_variant}-py{python_version}-{debian_version}"
                    print(f"  Adding configuration: {image_tag}")

                    config[framework_version][image_tag] = {
                        "framework_version": framework_version,
                        "framework_image_variant": framework_image_variant,
                        "python_version": python_version,
                        "debian_version": debian_version,
                        "wsgi_package": wsgi_package,
                        "database_version": database_version
                    }

    # Write to versions.json
    with open("versions.json", 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Generated versions.json with {len(config)} framework versions")

if __name__ == "__main__":
    generate_versions()
