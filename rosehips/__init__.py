import os
import json

from flask import Flask
from werkzeug.exceptions import Unauthorized

from pbshm import (
    authentication,
    initialisation,
    mechanic,
    timekeeper,
    autostat,
    cleanse,
    ietools,
    graphcomparison,
    ievisualiser,
)
from pbshm.cleanse import commands as cleanse_commands
from rosehips import layout, sideloader


def create_app(test_config=None):
    # Create Flask App
    app = Flask(__name__, instance_relative_config=True)

    # Load Configuration
    app.config.from_mapping(
        PAGE_SUFFIX=" - PBSHM Framework",
        LOGIN_MESSAGE="Welcome to the ROSEHIPS Consortium PBSHM Framework, please enter your authentication credentials below.",
        FOOTER_MESSAGE="PBSHM Framework © ROSEHIPS Consortium 2024",
        NAVIGATION={
            "modules": {"Home": "layout.home"},
            "network": {"MCS Comparison": "graphcomparison.list"},
            "design": {"IE Builder": "ie-visualiser.list_models"},
            "toolbox": {
                "Channel Statistics": "autostat.population_list",
                "Cleanse Data": "cleanse.route_list",
                "IE Debug": "ie-tools.list_models",
            },
            "system": {"Sideload Module": "sideloader.list_modules"},
        },
    )
    (
        app.config.from_file("config.json", load=json.load, silent=True)
        if test_config is None
        else app.config.from_mapping(test_config)
    )

    # Ensure Instance Folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Add Core Blueprints
    app.register_blueprint(initialisation.bp)  ## Initialisation
    app.register_blueprint(mechanic.bp)  ## Mechanic
    app.register_blueprint(timekeeper.bp, url_prefix="/timekeeper")  ## Timekeeper
    app.register_blueprint(authentication.bp, url_prefix="/authentication")  ## Authentication

    # Add Framework Blueprints
    app.register_blueprint(layout.bp, url_prefix="/layout")  ## Layout

    # Add Included Route Blueprints
    app.register_blueprint(autostat.bp, url_prefix="/toolbox/autostat")
    app.register_blueprint(cleanse.bp, url_prefix="/toolbox/cleanse")
    app.register_blueprint(ietools.bp, url_prefix="/toolbox/ie")
    app.register_blueprint(graphcomparison.bp, url_prefix="/network/mcs")
    app.register_blueprint(ievisualiser.bp, url_prefix="/design/ie")

    # Add Included Command Blueprints
    app.register_blueprint(cleanse_commands.bp)

    # Add Sideloader Blueprints
    with app.app_context():
        sideloader.register_sideloaded_modules()
    app.register_blueprint(sideloader.bp, url_prefix="/sideloader")  ## Sideloader

    # Set Root Page
    app.add_url_rule("/", endpoint="layout.home")

    # Register Error Handlers
    app.register_error_handler(Unauthorized, authentication.handle_unauthorised_request)

    # Return App
    return app
