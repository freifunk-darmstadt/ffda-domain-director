from mozls import query_mls, WifiNetwork, MLSException

from domain_director.geo import Location
from domain_director.geo.Provider import GeoProvider


class MozillaProvider(GeoProvider):
    def __init__(self, config):
        GeoProvider.__init__(self, config)

        self.api_key = config["mozilla"]["api_key"]

    def get_location(self, networks):
        try:
            mls_response = query_mls(
                wifi_networks=[WifiNetwork(mac_address=network["bssid"], signalStrength=int(network["signal"]))
                               for network in networks],
                apikey=self.api_key)
            return Location(self.provider, mls_response.lat, mls_response.lon, mls_response.accuracy)
        except MLSException:
            # handle MLS data as optional (it is anyway)
            return None
