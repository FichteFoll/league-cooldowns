import enum
import logging
import re
import requests
import typing as t

HOST = "https://{endpoint}.api.pvp.net"

# Commonly used types (for type hints)
Params = t.Dict[str, str]
JSON = t.Dict[str, t.Any]


l = logging.getLogger(__name__)

api_key = None  # type: str


###################################################################################################


class Platform(str, enum.Enum):
    br = "BR1"
    eune = "EUN1"
    euw = "EUW1"
    jp = "JP1"
    kr = "KR"
    lan = "LA1"
    las = "LA2"
    na = "NA1"
    oce = "OC1"
    pbe = "PBE1"
    ru = "RU"
    tr = "TR1"


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

    l.debug("Requesting '%s' with params: %s", url, params)
    r = requests.get(url, params=params)
    return r.json()


def _staticdata(variant: str, params: Params = None, region="euw") -> JSON:
    url = _build_url("/api/lol/static-data/{region}/v1.2/{variant}",
                     region=region, endpoint='global', variant=variant)

    return _get_data(url, params)


def _standardize_summoner_name(summoner_name: str) -> str:
    # The standardized summoner name
    # is the summoner name in all lower case
    # and with spaces removed.
    return re.sub(r"\s", "", summoner_name.lower())


###################################################################################################


def set_key(key: str):
    global api_key
    api_key = key


def format_status(data: JSON) -> str:
    return "Status code: {status_code}, message: {message}".format(**data['status'])


def get_champions(params: Params = None) -> JSON:
    return _staticdata("champion", params)


def get_versions() -> JSON:
    return _staticdata("versions")


def get_summoner_id(region: str, summoner_name: str) -> t.Optional[int]:
    """Determine ID of a summoner by name.

    Returns None if summoner name is not found.
    """
    standardized_name = _standardize_summoner_name(summoner_name)
    url = _build_url("/api/lol/{region}/v1.4/summoner/by-name/{summoner_name}",
                     region=region, summoner_name=standardized_name)

    result = _get_data(url)

    if standardized_name not in result:
        return None
    else:
        return result[standardized_name]['id']


def get_current_game_info(region: str, summoner_id: int) -> t.Optional[JSON]:
    url = _build_url("/observer-mode/rest/consumer/getSpectatorGameInfo/{platform}/{summoner_id}",
                     region=region, summoner_id=summoner_id)

    # 404 if not in-game
    result = _get_data(url)
    if 'status' in result:
        if result['status']['status_code'] == 404:
            # not in-game
            return None
        else:
            l.warn("Non-standard result! %s", format_status(result))
            return None
    else:
        return result
