from .client import Client


def _default_api_factory(api_client_package, api_name, config):
    configuration = api_client_package.Configuration()
    for key in config:
        if key == "api_key":
            configuration.api_key["developer_hapikey"] = config["api_key"]
        elif key == "retry":
            configuration.retries = config["retry"]
        else:
            setattr(configuration, key, config[key])

    api_client = api_client_package.ApiClient(configuration=configuration)

    return getattr(api_client_package, api_name)(api_client=api_client)


class HubSpot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            api_factory=_default_api_factory,
        )
