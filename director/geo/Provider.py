
class GeoProvider:
    def __init__(self, config):
        self.provider = config["provider"]

    def get_location(self, networks):
        raise NotImplemented
