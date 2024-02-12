# PBSHM Framework
The PBSHM Framework is a preconfigured version of the [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core) and module ecosystem. The goal of the PBSHM Core, was to build a base application which facilitated the curation of PBSHM Modules which intern consume [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema) data. The purpose of the PBSHM Framework is to provide a single packaged product of the [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema), [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core), and any relevant PBSHM Modules: to showcase the available technology in an easy to use manner and enable anyone, regardless of their coding knowledge, to interact with the aforementioned technology.

For more information on the PBSHM Core, please see the [GitHub repository](https://github.com/dynamics-research-group/pbshm-flask-core). Each module included within the PBSHM Framework is linked [below](#included-modules), with details of the module authors and any further information on how to use the module. For more information on how to create a module for PBSHM Core, please see the [module template](https://github.com/dynamics-research-group/pbshm-module-template) repository.

The minimum version of Python required to run the PBSHM Core is version 3.9.18.

## Included modules
Below is a list of modules included within the framework and links to the corresponding repositories and guides.
| Module | Description | Author | Repo | Documentation |
| --- | --- | --- | --- | --- |
| `pbshm-channel-toolbox` | A collection of tools to help processing channel data | [dsbrennan](https://github.com/dsbrennan) | [dsbrennan/channel-tools](https://github.com/dsbrennan/channel-tools) | [README](https://github.com/dsbrennan/channel-tools/blob/main/README.md) |
| `pbshm-ie-toolbox` | A collection of tools to help processing IE models | [dsbrennan](https://github.com/dsbrennan) | [dsbrennan/ie-tools](https://github.com/dsbrennan/ie-tools) | [README](https://github.com/dsbrennan/ie-tools/blob/main/README.md) |
| `pbshm-network-mcs` | An implementation of the Jaccard Index and Maximum Common Subgraph to generate network similarity scores for a a given set of IE models | [jgosliga](https://github.com/jgosliga) | [dynamics-research-group/ag-mcs](https://github.com/dynamics-research-group/ag-mcs) | [README](https://github.com/dynamics-research-group/ag-mcs/blob/main/README.md) |

## Installation
Install the package via pip:
```
pip install pbshm-framework
```

## Setup
Set the Flask application path and environment.

For Linux/Mac:
```
export FLASK_APP=pbshm
export FLASK_DEBUG=1
```

For Windows:
```
set FLASK_APP=pbshm
set FLASK_DEBUG=1
```

Configure settings and initialise the database with a new root user:
```
flask init config
flask init db new-root-user
```
The above steps will prompt you for all the required fields to set up the system.

## Running
The application is run via the standard Flask command:
```
flask run
```


## Bug reporting
If you encounter any issues/bugs with the system or the instructions above, please raise an issue through the [issues system](https://github.com/dynamics-research-group/pbshm-framework/issues) on GitHub.