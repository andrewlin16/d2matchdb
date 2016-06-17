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
		"PRIMARY KEY(id)"
	")"
)

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
