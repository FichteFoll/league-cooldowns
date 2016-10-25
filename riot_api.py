import requests
import typing as t

# Commonly used types (for type hints)
Params = t.Dict[str, str]
JSON = t.Dict[str, t.Any]


api_key = None  # type: str

HOST = "https://{endpoint}.api.pvp.net"


def set_key(key: str):
    global api_key
    api_key = key


def _build_url(url_base: str, region: str, **kwargs: t.Any):
    if url_base.startswith("/"):
        url_base = HOST + url_base
    kwargs.setdefault('endpoint', region)
    kwargs.setdefault('region', region)
    kwargs.setdefault('platform', Platform[region])

    return url_base.format(**kwargs)


def _get_data(url: str, params: Params = None) -> JSON:
    if not params:
        params = {}
    params.setdefault('api_key', api_key)

    r = requests.get(url, params=params)
    return r.json()


def _staticdata(variant: str, params: Params = None, region="euw") -> JSON:
    url = _build_url("/api/lol/static-data/{region}/v1.2/{variant}",
                     region=region, variant=variant)

    return _get_data(url, params)


def get_champions(params: Params = None) -> JSON:
    return _staticdata("champion", params)


def get_versions() -> JSON:
    return _staticdata("versions")
