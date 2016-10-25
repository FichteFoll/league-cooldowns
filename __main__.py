#!/usr/bin/env python3.5

import argparse
import json
import logging
import pathlib
import sys

import riot_api

DEFAULT_REGION = "euw"

__file_p__ = pathlib.Path(__file__)

l = logging.getLogger(__name__)

key_file_path = __file_p__.with_name("key")


class ChampionSpellData:

    file_name = "champion_spells.json"
    file_path = __file_p__.with_name(file_name)

    def __init__(self, check_updates=True):
        self.json = None
        self._load()
        if check_updates:
            self.sync()

    def _load(self):
        if self.file_path.exists():
            self.json = json.load(self.file_path.read_text())

    def _download(self):
        l.info("Downloading champion data...")
        self.json = riot_api.get_champions({'champData': 'spells'})

        with self.file_path.open("w") as f:
            json.dump(self.json, f)

    def sync(self):
        if not self.json:
            self._download()
            return

        l.info("Checking for updated data...")
        versions = riot_api.get_versions()
        latest_version = versions[0]
        current_version = self.json['version']

        l.info("Current version: %s, latest version: %s", current_version, latest_version)
        if latest_version.split(".") > current_version.split("."):
            self._download()


def init_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("{message}", style="{")
    handler.setFormatter(formatter)
    l.addHandler(handler)
    l.setLevel(logging.DEBUG)
    # l.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitor cooldowns of champions in your current game"
    )
    parser.add_argument("region", default=DEFAULT_REGION)
    parser.add_argument("summoner_name")
    parser.add_argument("--no-check-updates", dest="check_updates", action='store_false',
                        help="Disables checking for data updates")
    parser.add_argument("--monitor", action='store_true',
                        help="Keep looking for active games")
    parser.add_argument("--key", help="Riot API key (otherwise sourced from 'key' file)")
    return parser.parse_args()


def main():
    params = parse_args()

    init_logging()

    if params.key:
        riot_api.set_key(params.key)
    else:
        riot_api.set_key(key_file_path.read_text().strip())

    try:
        riot_api.Platform[params.region]
    except KeyError:
        l.error("Region not found")
        return 1

    l.info("Loading current game info...")
    summoner_id = riot_api.get_summoner_id(params.region, params.summoner_name)
    l.debug("Summoner id: %d", summoner_id)
    if summoner_id is None:
        l.error("Summoner name not found")
        return 2

    current_game_info = riot_api.get_current_game_info(params.region, summoner_id)
    if current_game_info is None:
        l.warn("Summoner not currently in game")
        return 0

    import pprint
    pprint.pprint(current_game_info)

    # TODO extract participating champions (and summnames)

    # load champion data
    data = ChampionSpellData(params.check_updates)
    # TODO extract cooldown information
    # 'cooldownBurn'

    return 0


if __name__ == '__main__':
    sys.exit(main())
