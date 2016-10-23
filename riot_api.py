import requests

api_key = None

HOST = "https://global.api.pvp.net"


def set_key(key):
    global api_key
    api_key = key


def _get_data(url, params=None):
    if not params:
        params = {}
    params.setdefault('api_key', api_key)
    r = requests.get(url, params=params)
    return r.json()


def _staticdata(variant, params=None, region="euw"):
    url = ("{host}/api/lol/static-data/{region}/v1.2/{variant}"
           .format(host=HOST, region=region, variant=variant))
    return _get_data(url, params)


def get_champions(params=None):
    return _staticdata("champion", params)


def get_versions():
    return _staticdata("versions")
