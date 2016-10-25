import requests

api_key = None

HOST = "https://{endpoint}.api.pvp.net"


def set_key(key):
    global api_key
    api_key = key


def _build_url(url_base: str, region: str, **kwargs):
    if url_base.startswith("/"):
        url_base = HOST + url_base
    kwargs.setdefault('endpoint', region)
    kwargs.setdefault('region', region)
    kwargs.setdefault('platform', Platform[region])

    return url_base.format(**kwargs)


def _get_data(url, params=None):
    if not params:
        params = {}
    params.setdefault('api_key', api_key)

    r = requests.get(url, params=params)
    return r.json()


def _staticdata(variant, params=None, region="euw"):
    url = _build_url("/api/lol/static-data/{region}/v1.2/{variant}",
                     region=region, variant=variant)

    return _get_data(url, params)


def get_champions(params=None):
    return _staticdata("champion", params)


def get_versions():
    return _staticdata("versions")
