from domain_director.geo.MozillaProvider import MozillaProvider


class GeoProvider:
    def __init__(self, config):
        self.provider = config["provider"]

    def get_location(self, networks):
        raise NotImplemented

    @staticmethod
    def get_provider(config):
        if config["provider"] == "mozilla":
            return MozillaProvider(config)
