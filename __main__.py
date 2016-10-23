#!/usr/bin/env python3.5

import argparse
import json
import logging
import pathlib
import sys

import riot_api

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
    l.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitor cooldowns of champions in your current game"
    )
    parser.add_argument("region")
    parser.add_argument("summoner_name")
    parser.add_argument("--no-check-updates", dest="check_updates", action='store_false',
                        help="Disables checking for data updates")
    parser.add_argument("--monitor", action='store_true',
                        help="Keep looking for active games")
    parser.add_argument("--key", help="Riot API key")
    return parser.parse_args()


def main():
    params = parse_args()

    init_logging()

    if params.key:
        riot_api.set_key(params.key)
    else:
        riot_api.set_key(key_file_path.read_text().trim())

    # load current game info
    #
    # load champion data
    data = ChampionSpellData(params.check_updates)
    # extract cooldown information
    # 'cooldownBurn'

if __name__ == '__main__':
    main()
