import enum


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


class Map(int, enum.Enum):
    summoners_rift_summer = 1
    summoners_rift_autumn = 2
    the_proving_grounds = 3
    twisted_treeline_original = 4
    the_crystal_scar = 8
    twisted_treeline = 10
    summoners_rift = 11
    howling_abyss = 12
    butchers_bridge = 14

    @property
    def formatted(self) -> str:
        name_parts = [s.capitalize() for s in self.name.split("_")]
        if name_parts[-1] in ('Summer', 'Autumn', 'Original'):
            name_parts[-1] = "({})".format(name_parts[-1])
        return " ".join(name_parts)


class GameMode(str, enum.Enum):
    ARAM = "ARAM"
    ASCENSION = "ASCENSION"
    CLASSIC = "CLASSIC"
    SHOWDOWN = "FIRSTBLOOD"
    PORO_KING = "KINGPORO"
    DOMINION = "ODIN"
    ONE_FOR_ALL = "ONEFORALL"
    TUTORIAL = "TUTORIAL"
    NEXUS_SIEGE = "SIEGE"

    @property
    def formatted(self) -> str:
        if self == self.ARAM:
            return self.ARAM.value
        name_parts = [s.capitalize() for s in self.name.split("_")]
        return " ".join(name_parts)


class GameType(str, enum.Enum):
    CUSTOM = "CUSTOM_GAME"
    TUTORIAL = "TUTORIAL_GAME"
    MATCHED = "MATCHED_GAME"


class Queue(str, enum.Enum):
    CUSTOM = "CUSTOM"
    NORMAL_BLIND_FIVES = "NORMAL_5x5_BLIND"
    BOT_FIVES = "BOT_5x5"
    BOT_INTRO_FIVES = "BOT_5x5_INTRO"
    BOT_BEGINNER_FIVES = "BOT_5x5_BEGINNER"
    BOT_INTERMEDIATE_FIVES = "BOT_5x5_INTERMEDIATE"
    NORMAL_BLIND_THREES = "NORMAL_3x3"
    NORMAL_DRAFT_FIVES = "NORMAL_5x5_DRAFT"
    DOMINION_BLIND = "ODIN_5x5_BLIND"
    DOMINION_DRAFT = "ODIN_5x5_DRAFT"
    BOT_DOMINION = "BOT_ODIN_5x5"
    RANKED_SOLO = "RANKED_SOLO_5x5"
    RANKED_PREMADE_THREES = "RANKED_PREMADE_3x3"
    RANKED_PREMADE_FIVES = "RANKED_PREMADE_5x5"
    RANKED_THREES = "RANKED_TEAM_3x3"
    RANKED_FIVES = "RANKED_TEAM_5x5"
    BOT_THREES = "BOT_TT_3x3"
    TEAM_BUILDER = "GROUP_FINDER_5x5"
    ARAM = "ARAM_5x5"
    ONE_FOR_ALL = "ONEFORALL_5x5"
    SHOWDOWN_SOLO = "FIRSTBLOOD_1x1"
    SHOWDOWN_DUO = "FIRSTBLOOD_2x2"
    HEXAKILL_SUMMONERS_RIFT = "SR_6x6"
    URF = "URF_5x5"
    BOT_URF = "BOT_URF_5x5"
    DOOM_BOTS_1 = "NIGHTMARE_BOT_5x5_RANK1"
    DOOM_BOTS_2 = "NIGHTMARE_BOT_5x5_RANK2"
    DOOM_BOTS_5 = "NIGHTMARE_BOT_5x5_RANK5"
    ASCENSION = "ASCENSION_5x5"
    HEXAKILL_TWISTED_TREELINE = "HEXAKILL"
    BUTCHERS_BRIDGE = "BILGEWATER_ARAM_5x5"
    PORO_KING = "KING_PORO_5x5"
    NEMESIS_DRAFT = "COUNTER_PICK"
    BLACK_MARKET = "BILGEWATER_5x5"
    NEXUS_SIEGE = "SIEGE"
    DYNAMIC_QUEUE = "TEAM_BUILDER_DRAFT_UNRANKED_5x5"
    RANKED_DYNAMIC_QUEUE = "TEAM_BUILDER_DRAFT_RANKED_5x5"

    @classmethod
    def for_id(cls, id_):
        try:
            return cls.by_id[id_]
        except:
            return None

Queue.by_id = {
    0: Queue.CUSTOM,
    65: Queue.ARAM,
    2: Queue.NORMAL_BLIND_FIVES,
    4: Queue.RANKED_SOLO,
    6: Queue.RANKED_PREMADE_FIVES,
    7: Queue.BOT_FIVES,
    8: Queue.NORMAL_BLIND_THREES,
    9: Queue.RANKED_PREMADE_THREES,
    75: Queue.HEXAKILL_SUMMONERS_RIFT,
    76: Queue.URF,
    14: Queue.NORMAL_DRAFT_FIVES,
    16: Queue.DOMINION_BLIND,
    17: Queue.DOMINION_DRAFT,
    83: Queue.BOT_URF,
    25: Queue.BOT_DOMINION,
    91: Queue.DOOM_BOTS_1,
    92: Queue.DOOM_BOTS_2,
    93: Queue.DOOM_BOTS_5,
    31: Queue.BOT_INTRO_FIVES,
    32: Queue.BOT_BEGINNER_FIVES,
    33: Queue.BOT_INTERMEDIATE_FIVES,
    98: Queue.HEXAKILL_TWISTED_TREELINE,
    100: Queue.BUTCHERS_BRIDGE,
    70: Queue.ONE_FOR_ALL,
    41: Queue.RANKED_THREES,
    42: Queue.RANKED_FIVES,
    300: Queue.PORO_KING,
    96: Queue.ASCENSION,
    72: Queue.SHOWDOWN_SOLO,
    52: Queue.BOT_THREES,
    310: Queue.NEMESIS_DRAFT,
    73: Queue.SHOWDOWN_DUO,
    313: Queue.BLACK_MARKET,
    315: Queue.NEXUS_SIEGE,
    61: Queue.TEAM_BUILDER,
    400: Queue.DYNAMIC_QUEUE,
    410: Queue.RANKED_DYNAMIC_QUEUE
}

RANKED_QUEUES = {Queue.RANKED_SOLO, Queue.RANKED_THREES,
                 Queue.RANKED_FIVES, Queue.RANKED_DYNAMIC_QUEUE}
