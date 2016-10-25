#!/usr/bin/env python3.5

import argparse
import collections
import json
import logging
import pathlib
import pprint
import sys
import typing as t

import colorama
import terminaltables

from . import riot_api


DEFAULT_REGION = "euw"

__file_p__ = pathlib.Path(__file__)

l = logging.getLogger(__name__)

key_file_path = pathlib.Path("key")


###################################################################################################

def _pdebug(data: t.Any, title: str = ""):
    """Use the pprint module for debugging output."""
    if l.isEnabledFor(logging.DEBUG):
        l.debug("=" * 79)
        if title:
            l.debug("  " + title)
            l.debug("+" * 79)
        l.debug(pprint.pformat(data))
        l.debug("=" * 79)


class ChampionSpellData:

    file_name = "champion_spells.json"
    file_path = __file_p__.parent / "cache" / file_name

    def __init__(self, check_updates: bool = True):
        self.json = None
        self._load()
        if check_updates:
            self.sync()

    def _load(self):
        if self.file_path.exists():
            with self.file_path.open() as f:
                self.json = json.load(f)

    def _download(self):
        l.info("Downloading champion data...")
        new_json = riot_api.get_champions({'champData': 'spells'})
        if 'status' in new_json:
            l.error("Unable to download champion data. %s", riot_api.format_status(new_json))

        self.file_path.parent.mkdir(exist_ok=True)
        with self.file_path.open("w") as f:
            json.dump(new_json, f)
        self.json = new_json

    def sync(self):
        if not self.json:
            self._download()
            return

        l.info("Checking for updated data...")
        versions = riot_api.get_versions()
        latest_version = versions[0]
        current_version = self.json['version']

        l.debug("Current version: %s, latest version: %s", current_version, latest_version)
        if latest_version.split(".") > current_version.split("."):
            self._download()

    def for_champion_id(self, id_: int) -> riot_api.JSON:
        for ch_data in self.json['data'].values():
            if id_ == ch_data['id']:
                return ch_data
        return None


SpellData = collections.namedtuple("SpellData", "cooldown cooldown_burn")

CooldownInfo = collections.namedtuple("CooldownInfo",
                                      "summoner_id summoner_name champion_id champion_name "
                                      "spell_data")

TeamList = t.List[t.List[CooldownInfo]]


def collect_cooldown_info(participants, data) -> TeamList:
    team_map = collections.defaultdict(list)

    for part in participants:
        ch_data = data.for_champion_id(part['championId'])
        spell_data = [SpellData(spell['cooldown'], spell['cooldownBurn'])
                      for spell in ch_data['spells']]
        cd_info = CooldownInfo(part['summonerId'],
                               part['summonerName'],
                               part['championId'],
                               ch_data['name'],
                               spell_data)
        team_map[part['teamId']].append(cd_info)

    assert len(team_map) == 2
    return [team_map[k] for k in sorted(team_map)]


def render_cooldowns(teams: TeamList, summoner_id: int):
    _pdebug(teams, "Teams")

    titles = ["Blue Team", "Red Team"]
    colors = [colorama.Fore.CYAN, colorama.Fore.RED]
    titles_appendix = {True: "Your Team", False: "Their Team"}

    header = ["Champion", "Q", "W", "E", "R"]
    for i, team in enumerate(teams):
        table_data = [header]
        is_your_team = False
        for cd_info in team:
            cooldowns = [sd.cooldown_burn for sd in cd_info.spell_data]
            row = [cd_info.champion_name, *cooldowns]
            if cd_info.summoner_id == summoner_id:
                is_your_team = True
                row = [colorama.Fore.YELLOW + cell + colorama.Style.RESET_ALL + colors[i]
                       for cell in row]
            table_data.append(row)

        title = "{} ({})".format(titles[i], titles_appendix[is_your_team])
        table = terminaltables.SingleTable(table_data, title)
        print("{}{}{}".format(colors[i], table.table, colorama.Style.RESET_ALL))  # colorize

###################################################################################################


def init_logging(level: int):
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("{message}", style="{")
    handler.setFormatter(formatter)
    l.addHandler(handler)
    l.setLevel(level)
    # l.setLevel(logging.INFO)


def parse_args():
    default_verbosity = 3

    parser = argparse.ArgumentParser(
        description="Monitor cooldowns of champions in your current game"
    )

    parser.add_argument("region", default=DEFAULT_REGION)
    parser.add_argument("summoner_name")
    parser.add_argument("--no-check-updates", dest="check_updates", action='store_false',
                        help="Disables checking for data updates")
    # parser.add_argument("--monitor", action='store_true',
    #                     help="Keep looking for active games")
    parser.add_argument("--key", help="Riot API key (otherwise sourced from 'key' file)")

    # verbosity control
    parser.add_argument('--verbosity', type=int,
                        help="Directly control verbosity of output (0 to 4); default: {}"
                             .format(default_verbosity))
    parser.add_argument("-v", action='append_const', const=1, dest="v", default=[],
                        help="Increase verbosity level")
    parser.add_argument("-q", action='append_const', const=-1, dest="v",
                        help="Decrease verbosity level")

    params = parser.parse_args()

    # translate verbosity to logging level
    logging_level = params.verbosity
    if logging_level is None:
        logging_level = default_verbosity + sum(params.v)
    logging_level = max(0, min(logging_level, 4))
    logging_level = (5 - logging_level) * 10

    return params, logging_level


def main():
    colorama.init()
    params, logging_level = parse_args()

    init_logging(logging_level)

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

    _pdebug(current_game_info, "Current Game Info")

    data = ChampionSpellData(params.check_updates)
    teams = collect_cooldown_info(current_game_info['participants'], data)
    render_cooldowns(teams, summoner_id)

    return 0
