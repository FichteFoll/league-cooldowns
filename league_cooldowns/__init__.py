import argparse
import collections
import datetime
import json
import logging
import pathlib
import pprint
import sys
import time
import typing as t

import colorama
import terminaltables

from . import riot_api


DEFAULT_REGION = "euw"

__file_p__ = pathlib.Path(__file__)

l = logging.getLogger(__name__)

KEY_FILE_PATH = pathlib.Path("key")


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


_now = datetime.datetime.now


class ChampionSpellData:

    file_name = "champion_spells.json"
    file_path = __file_p__.parent / "cache" / file_name

    def __init__(self, check_updates: bool = True):
        self.json = None
        l.info("Loading champion spell data...")
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

        l.debug("Checking for updated data...")
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


def show_game_info(current_game_info: riot_api.JSON):
    game_type = riot_api.const.GameType(current_game_info['gameType'])
    game_mode = riot_api.const.GameMode(current_game_info['gameMode'])
    game_map = riot_api.const.Map(current_game_info['mapId'])
    game_queue = riot_api.const.Queue.for_id(current_game_info['gameQueueConfigId'])

    type_appendix = ""
    if game_type == riot_api.const.GameType.CUSTOM:
        type_appendix = " (Custom)"
    elif game_type == riot_api.const.GameType.TUTORIAL:
        type_appendix = " (Tutorial)"
    elif game_queue in riot_api.const.RANKED_QUEUES:
        type_appendix = " (Ranked)"

    print("Game Mode: {}, Map: {}{}"
          .format(game_mode.formatted, game_map.formatted, type_appendix))


SpellData = collections.namedtuple("SpellData", "cooldown cooldown_burn")

CooldownInfo = collections.namedtuple("CooldownInfo",
                                      "summoner_id summoner_name champion_id champion_name "
                                      "spell_data")

TeamList = t.List[t.List[CooldownInfo]]


def collect_cooldown_info(participants: riot_api.JSON, data: ChampionSpellData) -> TeamList:
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

    # A few defensive checks
    assert len(team_map) in (1, 2)
    assert 100 in team_map
    return [team_map[k] for k in sorted(team_map)]


def show_cooldowns(teams: TeamList, summoner_id: int, show_summoner_names: bool):
    _pdebug(teams, "Teams")

    titles = ["Blue Team", "Red Team"]
    colors = [colorama.Fore.CYAN, colorama.Fore.RED]
    titles_appendix = {True: "Your Team", False: "Their Team"}

    header = ["Champion", "Q", "W", "E", "R"]
    if show_summoner_names:
        header[1:1] = ["Summoner"]
    for i, team in enumerate(teams):
        table_data = [header]
        is_your_team = False
        for cd_info in team:
            row = [cd_info.champion_name]
            if show_summoner_names:
                row.append(cd_info.summoner_name)
            row.extend(sd.cooldown_burn for sd in cd_info.spell_data)

            # Highlight summoner_id column
            if cd_info.summoner_id == summoner_id:
                is_your_team = True
                row = [colorama.Fore.YELLOW + cell + colorama.Style.RESET_ALL + colors[i]
                       for cell in row]

            table_data.append(row)

        title = "{} ({})".format(titles[i], titles_appendix[is_your_team])
        table = terminaltables.SingleTable(table_data, title)
        print("{}{}{}".format(colors[i], table.table, colorama.Style.RESET_ALL))  # colorize


def do_once(params, summoner_id):
    l.info("Loading current game info...")
    current_game_info = riot_api.get_current_game_info(params.region, summoner_id)
    if current_game_info is None:
        l.warning("Summoner not currently in game")
        return 0

    data = ChampionSpellData(params.check_updates)

    _pdebug(current_game_info, "Current Game Info")
    print()
    show_game_info(current_game_info)

    teams = collect_cooldown_info(current_game_info['participants'], data)
    show_cooldowns(teams, summoner_id, params.show_summoner_names)

    return 0


def monitor(params, summoner_id):
    data = ChampionSpellData(params.check_updates)

    print("Monitor mode enabled. Press Ctrl-C to quit.")

    current_game_info = None
    while True:
        if not current_game_info:
            print("Loading current game info... ({:%x %X})".format(_now()))
            current_game_info = riot_api.get_current_game_info(params.region, summoner_id)
        if not current_game_info:
            print("Summoner not currently in game")
            time.sleep(30)
            if not l.isEnabledFor(logging.DEBUG):
                print(colorama.Cursor.UP(2), end='')
            continue

        _pdebug(current_game_info, "Current Game Info")
        print()
        show_game_info(current_game_info)

        teams = collect_cooldown_info(current_game_info['participants'], data)
        show_cooldowns(teams, summoner_id, params.show_summoner_names)

        while True:
            time.sleep(60)
            new_current_game_info = riot_api.get_current_game_info(params.region, summoner_id)

            if not new_current_game_info:
                print("Game ended ({:%x %X})".format(_now()))
                current_game_info = None
                break

            elif new_current_game_info['gameId'] != current_game_info['gameId']:
                print("New game detected! ({:%x %X})".format(_now()))
                current_game_info = new_current_game_info
                break


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
        description="""
            Look up a summoner name's current game
            and display cooldowns of all champions
            in that game.
        """
    )

    parser.add_argument("region", nargs='?', default=DEFAULT_REGION,
                        help="May be omitted and defaults to '{}'. "
                             "Use 'help' as region to show the available regions "
                             "(still requires summoner_name argument)."
                             .format(DEFAULT_REGION))
    parser.add_argument("summoner_name",
                        help="Summoner name to look up. "
                             "Spaces are stripped by Riot's API.")

    parser.add_argument("--no-check-updates", dest="check_updates", action='store_false',
                        default=True, help="Disables checking for data updates")
    parser.add_argument("-n", "--show-summoner-names", action='store_true', default=False,
                        help="Show summoner names in tables")
    parser.add_argument("-m", "--monitor", action='store_true', default=False,
                        help="Keep looking for active games")
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
        riot_api.set_key(KEY_FILE_PATH.read_text().strip())

    try:
        riot_api.const.Platform[params.region]
    except KeyError:
        l.error("Region not found")
        print("The following regions are available:")
        for region in riot_api.const.Platform:
            print(region.name)
        return 1

    summoner_id = riot_api.get_summoner_id(params.region, params.summoner_name)
    l.debug("Summoner id: %d", summoner_id)
    if summoner_id is None:
        l.error("Summoner name not found")
        return 2

    if not params.monitor:
        return do_once(params, summoner_id)
    else:
        return monitor(params, summoner_id)
