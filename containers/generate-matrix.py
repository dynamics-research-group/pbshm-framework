import json
import os
import sys


def main():
    """Generate build stratergy matrix
    The function loads the version json and generates an includes
    json file to stdout that can be brought into a github action via a context.

    Raises:
        FileNotFoundError: Unable to find versions.json in the current working directory
    """

    # read version file
    if not os.path.exists("versions.json"):
        raise FileNotFoundError("Versions JSON file not found")
    payload = None
    with open("versions.json", "r") as file:
        payload = json.load(file)

    # process payload
    includes = []
    additional_index_keys = {"database_version": "db", "wsgi_package": "", "reverse_proxy": ""}
    for version in payload["versions"]:

        # generate shared tags
        v, pv, pi = (
            version["framework_version"],
            version["shared"]["python_version"],
            version["shared"]["python_image"],
        )
        shared_tags, shared_dev_suffix, shared_standalone_suffix = [f"{v}-py{pv}-{pi}"], None, None
        if "dev" in version["shared"]:
            shared_dev_suffix = f"-db{version["shared"]["dev"]["database_version"]}"
            shared_tags.append(f"{v}-dev-py{pv}-{pi}{shared_dev_suffix}")
        if "standalone" in version["shared"]:
            db, wsgi, proxy = (
                version["shared"]["standalone"]["database_version"],
                version["shared"]["standalone"]["wsgi_package"],
                version["shared"]["standalone"]["reverse_proxy"],
            )
            shared_standalone_suffix = f"-db{db}-{wsgi}-{proxy}"
            shared_tags.append(f"{v}-standalone-py{pv}-{pi}{shared_standalone_suffix}")

        # enumerate variants
        for variant in version["variants"]:
            for python in variant["python_version"]:
                for image in variant["python_image"]:

                    # generate minor, release and additional tags
                    minor_tag, release_tag, additional_tags = None, None, []
                    if variant["type"] == "base":
                        minor_tag = version["name"]
                        release_tag = version["framework_version"]
                    else:
                        minor_tag = f"{version["name"]}-{variant["type"]}"
                        release_tag = f"{version["framework_version"]}-{variant["type"]}"
                        for key in additional_index_keys.keys():
                            if key in variant:
                                additional_tags.append(
                                    f"{additional_index_keys[key]}{variant[key]}"
                                )

                    # generate individual tags and partial shared tags
                    tag_suffix = f"-{'-'.join(additional_tags)}" if len(additional_tags) > 0 else ""
                    tags = [f"{release_tag}-py{python}-{image}{tag_suffix}"]
                    shared_suffix = ""
                    if variant["type"] == "dev":
                        shared_suffix = shared_dev_suffix
                    elif variant["type"] == "standalone":
                        shared_suffix = shared_standalone_suffix
                    if python != pv and image == pi and shared_suffix == tag_suffix:
                        tags.extend([f"{release_tag}-py{python}", f"{minor_tag}-py{python}"])
                    elif python == pv and image != pi and shared_suffix == tag_suffix:
                        tags.extend([f"{release_tag}-{image}", f"{minor_tag}-{image}"])

                    # generate full shared tags
                    if tags[0] in shared_tags:
                        tags.extend(
                            [
                                f"{release_tag}-py{python}",
                                f"{release_tag}-{image}",
                                f"{release_tag}",
                                f"{minor_tag}-py{python}-{image}",
                                f"{minor_tag}-py{python}",
                                f"{minor_tag}-{image}",
                                f"{minor_tag}",
                            ]
                        )

                    # create build
                    suffix_end_path = (
                        shared_suffix[3:] if shared_suffix[0:3] == "-db" else shared_suffix[1:]
                    ).replace("-", "/")
                    if len(suffix_end_path) > 0:
                        suffix_end_path += "/"
                    build = {
                        "image": "pbshm-framework",
                        "tags": " ".join(tags),
                        "context": "./",
                        "containerfiles": f"./{version["name"]}/{variant["type"]}/{python}/{image}/{suffix_end_path}Containerfile",
                        "build_info": {
                            "version": version["name"],
                            "type": variant["type"],
                            "python_version": python,
                            "python_image": image,
                        },
                    }

                    # copy additional keys into build info
                    for key in additional_index_keys.keys():
                        if key in variant:
                            build["build_info"][key] = variant[key]

                    # append build
                    includes.append(build)

    # output includes json
    sys.stdout.write(json.dumps({"include": includes}))


if __name__ == "__main__":
    main()
