import rosehips


def create_app(test_config=None):
    # create base framework app
    app = rosehips.create_app(test_config)

    # return app
    return app
