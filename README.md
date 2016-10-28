# League Cooldowns

A small (console) utility
for the game League of Legends
to display cooldowns 
of all champion currently in a specific game.
It can also periodically check 
for new games for a specific summoner.

## Installation

(installation process pending improvements)

1. Download git repo or zip archive
2. Create a virtualenv (optional)
3. Install requirements
4. Run using `python -m league_cooldowns`

```
$ git clone https://github.com/FichteFoll/league-cooldowns
$ cd league-cooldowns
$ virtualenv venv
$ source venv/bin/activate
(on Windows) > .\venv\Scripts\activate.bat
$ pip install -r requirements.txt
```

A Riot Games API key is required 
and can be obtained from the [Riot Games API Dashboard][].
You can either write that key to a file named `key`
or pass it as an argument every time you run the command.

[Riot Games API Dashboard]: https://developer.riotgames.com/

## Usage

```
usage: __main__.py [-h] [--no-check-updates] [-n] [-m] [--key KEY]
                   [--verbosity VERBOSITY] [-v] [-q]
                   [region] summoner_name

Look up a summoner name's current game and display cooldowns of all champions
in that game.

positional arguments:
  region                May be omitted and defaults to 'euw'. Use 'help' as
                        region to show the available regions (still requires
                        summoner_name argument).
  summoner_name         Summoner name to look up. Spaces are stripped by
                        Riot's API.

optional arguments:
  -h, --help            show this help message and exit
  --no-check-updates    Disables checking for data updates
  -n, --show-summoner-names
                        Show summoner names in tables
  -m, --monitor         Keep looking for active games
  --key KEY             Riot API key (otherwise sourced from 'key' file)
  --verbosity VERBOSITY
                        Directly control verbosity of output (0 to 4);
                        default: 3
  -v                    Increase verbosity level
  -q                    Decrease verbosity level
```

### Example

```
$ python -m league_cooldowns skvardags
Loading current game info...
Loading champion spell data...

Game Mode: Classic, Map: Summoners Rift (Ranked)
┌Blue Team (Their Team)──┬────────────────┬──────────────────┬─────────────┐
│ Champion │ Q           │ W              │ E                │ R           │
├──────────┼─────────────┼────────────────┼──────────────────┼─────────────┤
│ Lee Sin  │ 11/10/9/8/7 │ 14             │ 10               │ 90/75/60    │
│ LeBlanc  │ 6           │ 18/16/14/12/10 │ 14/12.5/11/9.5/8 │ 40/32/24    │
│ Talon    │ 8/7/6/5/4   │ 10             │ 18/16/14/12/10   │ 100/80/60   │
│ Morgana  │ 11          │ 10             │ 23/21/19/17/15   │ 120/110/100 │
│ Vayne    │ 6/5/4/3/2   │ 6              │ 20/18/16/14/12   │ 100/85/70   │
└──────────┴─────────────┴────────────────┴──────────────────┴─────────────┘
┌Red Team (Your Team)──────────┬────────────────────┬────────────────────┬─────────────┐
│ Champion │ Q                 │ W                  │ E                  │ R           │
├──────────┼───────────────────┼────────────────────┼────────────────────┼─────────────┤
│ Ekko     │ 9/8.5/8/7.5/7     │ 22/20/18/16/14     │ 11/10/9/8/7        │ 110/90/70   │
│ Orianna  │ 6/5.25/4.5/3.75/3 │ 9                  │ 9                  │ 110/95/80   │
│ Ezreal   │ 6.5/6/5.5/5/4.5   │ 9                  │ 19/17.5/16/14.5/13 │ 120         │
│ Nidalee  │ 6                 │ 13/12/11/10/9      │ 12                 │ 3           │
│ Thresh   │ 20/18/16/14/12    │ 22/20.5/19/17.5/16 │ 9                  │ 140/120/100 │
└──────────┴───────────────────┴────────────────────┴────────────────────┴─────────────┘
```
