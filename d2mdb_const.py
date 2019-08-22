import api_key

# settings constants
API_KEY = api_key.API_KEY

# other constants - do not touch
HISTORY_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/"
DETAILS_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/"
HEROES_URL = "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1"
API_RATE_LIMIT = 2 # (in seconds)
API_NUM_RETRIES = 20

# DB schema stuff
SQL_MATCH_SCHEMA = (
	"CREATE TABLE matches ("
		"id INT UNSIGNED,"
		"hero INT UNSIGNED,"
		"kills INT UNSIGNED,"
		"deaths INT UNSIGNED,"
		"assists INT UNSIGNED,"
		"gold INT UNSIGNED,"
		"last_hits INT UNSIGNED,"
		"denies INT UNSIGNED,"
		"gpm INT UNSIGNED,"
		"xpm INT UNSIGNED,"
		"hero_damage INT UNSIGNED,"
		"tower_damage INT UNSIGNED,"
		"hero_healing INT UNSIGNED,"
		"level INT UNSIGNED,"
		"team BOOLEAN,"
		"our_kills INT UNSIGNED,"
		"our_deaths INT UNSIGNED,"
		"our_assists INT UNSIGNED,"
		"our_gold INT UNSIGNED,"
		"our_last_hits INT UNSIGNED,"
		"our_denies INT UNSIGNED,"
		"our_xpm INT UNSIGNED,"
		"our_gpm INT UNSIGNED,"
		"our_hero_damage INT UNSIGNED,"
		"our_tower_damage INT UNSIGNED,"
		"our_hero_healing INT UNSIGNED,"
		"our_level INT UNSIGNED,"
		"their_kills INT UNSIGNED,"
		"their_deaths INT UNSIGNED,"
		"their_assists INT UNSIGNED,"
		"their_gold INT UNSIGNED,"
		"their_last_hits INT UNSIGNED,"
		"their_denies INT UNSIGNED,"
		"their_xpm INT UNSIGNED,"
		"their_gpm INT UNSIGNED,"
		"their_hero_damage INT UNSIGNED,"
		"their_tower_damage INT UNSIGNED,"
		"their_hero_healing INT UNSIGNED,"
		"their_level INT UNSIGNED,"
		"won BOOLEAN,"
		"duration INT UNSIGNED,"
		"start_time TIMESTAMP,"
		"game_mode INT UNSIGNED,"
		"ranked BOOLEAN,"
		"lobby_type INT UNSIGNED,"
		"first_blood_time INT UNSIGNED,"
		"leaver_status BOOLEAN,"
		"have_mega_creeps BOOLEAN,"
		"against_mega_creeps BOOLEAN,"
		"PRIMARY KEY(id)"
	")"
)

SQL_VERSION_SCHEMA = (
	"CREATE TABLE version ("
		"version INT UNSIGNED"
	")"
)

DB_SCHEMA_VERSION = 3

SQL_HERO_SCHEMA = (
	"CREATE TABLE heroes ("
		"id INT UNSIGNED,"
		"name TEXT,"
		"internal_name TEXT,"
		"PRIMARY KEY(id)"
	")"
)

HEROES_DB_FILE = 'heroes.db'

# (API attribute to table field)
PLAYER_ATTRS = {
	"kills": "kills",
	"deaths": "deaths",
	"assists": "assists",
	"gold": "gold",
	"last_hits": "last_hits",
	"denies": "denies",
	"gold_per_min": "gpm",
	"xp_per_min": "xpm",
	"hero_damage": "hero_damage",
	"tower_damage": "tower_damage",
	"hero_healing": "hero_healing",
	"level": "level",
}

# "proper" labels for each field in the match
DB_FIELD_NAMES = {
	"id": "Match ID",
	"hero": "Hero",
	"kills": "Kills",
	"deaths": "Deaths",
	"assists": "Assists",
	"gold": "Gold",
	"last_hits": "Last Hits",
	"denies": "Denies",
	"gpm": "GPM",
	"xpm": "XPM",
	"hero_damage": "Hero Damage",
	"tower_damage": "Tower Damage",
	"hero_healing": "Hero Healing",
	"level": "Level",
	"team": "Team",
	"our_kills": "Our Kills",
	"our_deaths": "Our Deaths",
	"our_assists": "Our Assists",
	"our_gold": "Our Gold",
	"our_last_hits": "Our Last Hits",
	"our_denies": "Our Denies",
	"our_xpm": "Our XPM",
	"our_gpm": "Our GPM",
	"our_hero_damage": "Our Hero Damage",
	"our_tower_damage": "Our Tower Damage",
	"our_hero_healing": "Our Hero Healing",
	"our_level": "Our Level",
	"their_kills": "Their Kills",
	"their_deaths": "Their Deaths",
	"their_assists": "Their Assists",
	"their_gold": "Their Gold",
	"their_last_hits": "Their Last Hits",
	"their_denies": "Their Denies",
	"their_xpm": "Their XPM",
	"their_gpm": "Their GPM",
	"their_hero_damage": "Their Hero Damage",
	"their_tower_damage": "Their Tower Damage",
	"their_hero_healing": "Their Hero Healing",
	"their_level": "Their Level",
	"won": "Won?",
	"duration": "Game Duration",
	"start_time": "Start Time",
	"game_mode": "Game Mode",
	"ranked": "Ranked?",
	"lobby_type": "Lobby Type",
	"first_blood_time": "Time to First Blood",
	"leaver_status": "Has Abandon?",
	"have_mega_creeps": "Have Mega Creeps?",
	"against_mega_creeps": "Against Mega Creeps?",
}

TEAMS = ["Radiant", "Dire"]

# based from https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails
GAME_MODES = {
	0: "N/A",
	1: "All Pick (Legacy)",
	2: "Captains Mode",
	3: "Random Draft",
	4: "Single Draft",
	5: "All Random",
	6: "Intro",
	7: "Diretide",
	8: "Reverse Captains Mode",
	9: "The Greeviling",
	10: "Tutorial",
	11: "Mid Only",
	12: "Least Played",
	13: "New Player Pool",
	14: "Compendium Matchmaking",
	16: "Captains Draft",
	18: "Ability Draft",
	19: "Event",
	20: "All Random Deathmatch",
	22: "All Pick",
	23: "Turbo",
	24: "Mutation",
}

# based from https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails
LOBBY_TYPES = {
	-1: "N/A",
	0: "Normal",
	1: "Practice",
	2: "Tournament",
	3: "Tutorial",
	4: "Bot",
	5: "Team Queue",
	6: "Solo Queue",
	7: "Ranked",
	8: "1v1 Mid",
	9: "Battle Cup",
	12: "Mo'rokai",
}
