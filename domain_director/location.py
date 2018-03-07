import requests

from domain_director import is_bssid


class MLSRemoteException(Exception):
    pass


class InvalidBSSIDException(Exception):
    pass


def get_location(wifi_networks, api_key="test"):
    post_body = {
        "wifiAccessPoints": []
    }

    for network in wifi_networks:
        if not is_bssid(network["macAddress"]):
            raise InvalidBSSIDException
        post_body["wifiAccessPoints"].append({"macAddress": network["macAddress"],
                                              "signalStrength": int(network["signalStrength"])
                                              if "signalStrength" in network else 0})

    r = requests.post("https://location.services.mozilla.com/v1/geolocate?key={}".format(api_key), json=post_body)
    if r.status_code is not 200:
        raise MLSRemoteException("Status Code {status}: {response}".format(status=r.status_code, response=r.text))

    response = r.json()
    return response["location"]["lat"], response["location"]["lng"], response["accuracy"]
