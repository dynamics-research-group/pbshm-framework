# PBSHM Framework
The PBSHM Framework is a preconfigured version of the [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core) and module ecosystem. The goal of the PBSHM Core, was to build a base application which facilitated the curation of PBSHM Modules which intern consume [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema) data. The purpose of the PBSHM Framework is to provide a single packaged product of the [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema), [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core), and any relevant PBSHM Modules: to showcase the available technology in an easy to use manner and enable anyone, regardless of their coding knowledge, to interact with the aforementioned technology.

For more information on the PBSHM Core, please see the [GitHub repository](https://github.com/dynamics-research-group/pbshm-flask-core). Each module included within the PBSHM Framework is linked [below](#included-modules), with details of the module authors and any further information on how to use the module. For more information on how to create a module for PBSHM Core, please see the [module template](https://github.com/dynamics-research-group/pbshm-module-template) repository.

The minimum version of Python required to run the PBSHM Framework is version 3.9.18. [Click here](#installation) for details on how to install the PBSHM Framework on your local machine.

## Included modules
Below is a list of modules included within the framework and links to the corresponding repositories and guides.
| Module | Description | Author | Repo | Documentation |
| --- | --- | --- | --- | --- |
| `pbshm-channel-toolbox` | A collection of tools to help processing channel data | [dsbrennan](https://github.com/dsbrennan) | [dsbrennan/channel-tools](https://github.com/dsbrennan/channel-tools) | [README](https://github.com/dsbrennan/channel-tools/blob/main/README.md) |
| `pbshm-ie-toolbox` | A collection of tools to help processing IE models | [dsbrennan](https://github.com/dsbrennan) | [dsbrennan/ie-tools](https://github.com/dsbrennan/ie-tools) | [README](https://github.com/dsbrennan/ie-tools/blob/main/README.md) |
| `pbshm-network-mcs` | An implementation of the Jaccard Index and Maximum Common Subgraph to generate network similarity scores for a a given set of IE models | [jgosliga](https://github.com/jgosliga) | [dynamics-research-group/ag-mcs](https://github.com/dynamics-research-group/ag-mcs) | [README](https://github.com/dynamics-research-group/ag-mcs/blob/main/README.md) |
| `pbshm-ie-visualiser` | A 3D model builder for creating, editing, and viewing IE models | [josiemcculloch](https://github.com/josiemcculloch) | [dynamics-research-group/pbshm-ie-model-builder](https://github.com/dynamics-research-group/pbshm-ie-model-builder) | [README](https://github.com/dynamics-research-group/pbshm-ie-model-builder/blob/main/README.md) |

## Installation
The simplist way to install the PBSHM Framework is via the `pbshm-framework` python package available through the standard `pip` commands. It is recomended to install the `pbshm-framework` package into a dedicated [python virtual environment](https://docs.python.org/3/tutorial/venv.html).

Use the following command to install the latest version of the `pbshm-framework` in your python environment:
```
pip install pbshm-framework
```
Once you have installed the PBSHM Framework on your local machine, you must [configure your installation](#configure-framework) to communicate with the PBSHM Database and then you can [start the framework](#starting-the-framework).

## Upgrade
If you installed the PBSHM Framework via the `pbshm-framework` python package (as described in the [installation](#installation) instructions): you can upgrade your installation to the latest available version through the following command in your python environment:
```
pip install --upgrade pbshm-framework
```

## Configure Flask
PBSHM Framework is built upon [Flask](https://github.com/pallets/flask) and as such, Flask must be configured to understand which application to load and whether debug information should be included. This information is passed onto Flask via the `FLASK_APP` and `FLASK_DEBUG` environment variables. The commands below will set these environment variables dependent upon your operating system:

Linux/Mac:
```
export FLASK_APP=rosehips
export FLASK_DEBUG=1
```

Windows (CMD):
```
set FLASK_APP=rosehips
set FLASK_DEBUG=1
```

Windows (Powershell):
```
$env:FLASK_APP="rosehips"
$env:FLASK_DEBUG=1
```

## Configure Framework
There are two steps to configuring the PBSHM Framework: entering the details of the database configuration ([configure settings](#configure-settings)), and initialising the database ([initialise database](#initialise-database)). 

If this is your first time installing any of the PBSHM Ecosystem, you will need to complete both steps. However, if you already have a working copy of [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core) (or any associated PBSHM Module) on your local machine, you will most likely have already initialised the database with the [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema) and created a system login. Therefore, you only need to complete the database configuration step ([configure settings](#configure-settings)). 

Once these aformentioned steps have been completed, you can now [start the framework](#starting-the-framework). Please note that these configuration steps only need to be completed once. When you want to start the framework after installation, you need only use the command highlighted in the [starting the framework](#starting-the-framework) section.

### Configure Settings
To configure the system settings (database credentials, user collection, default collection, etc), simply use the following command and the system will prompt you to enter the required details (please ensure you have [configured flask](#configure-flask) before completing this step):
```
flask init config
```

### Initialise Database
To initialise the database with the latest version of the [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema) and create a login for the system, simply use the following command and the system will prompt you for any required login details and install the latest version of the PBSHM Schema into the selected database (please ensure you have [configured the system settings](#configure-settings) before completing this step):
```
flask init db new-root-user
```

## Starting the Framework
To start the framework using the inbuilt Flask development server, use the following command (please ensure you have [configured flask](#configure-flask) before running this command):
```
flask run
```

## Bug reporting
If you encounter any issues/bugs with the system or the instructions above, please raise an issue through the [issues system](https://github.com/dynamics-research-group/pbshm-framework/issues) on GitHub.