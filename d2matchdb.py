# imports
import json
import os.path
import requests
import sqlite3

# settings constants
API_KEY = "79A89606470D44E6BBE64BEC2D73D5BB" # your api key - http://steamcommunity.com/dev/apikey
ACCOUNT_ID = 388221 # your account id - get from Dota 2
DB_FILE = "matches.db" # db file to read/write

# other constants - do not touch
HISTORY_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/"
DETAILS_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/"

SQL_CREATE_TABLE = (
	"CREATE TABLE matches ("
		"id INT UNSIGNED,"
		"seq INT UNSIGNED,"
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
		"healing INT UNSIGNED,"
		"level INT UNSIGNED,"
		"won BOOLEAN,"
		"duration INT UNSIGNED,"
		"start_time TIMESTAMP,"
		"game_mode INT UNSIGNED,"
		"ranked BOOLEAN,"
		"PRIMARY KEY(id)"
	")"
)

SQL_LAST_SEQ = "SELECT seq FROM matches ORDER BY seq DESC LIMIT 1"

RANKED_LOBBY_TYPE = 7
UNRANKED_LOBBY_TYPE = 0

# create/open SQLite db
if not os.path.exists(DB_FILE):
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	c.execute(SQL_CREATE_TABLE)
	print("New db created as " + DB_FILE)
else:
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	print("Opened " + DB_FILE)

# get latest match sequence number

last_seq = c.execute(SQL_LAST_SEQ).fetchone()
if last_seq is None:
	last_seq = 0
else:
	last_seq = last_seq[0]
print("Last match sequence was " + str(last_seq));

#qs = {"account_id": ACCOUNT_ID, "key": API_KEY}
#r = requests.get(HISTORY_URL, params=qs)
#print(json.dumps(r.json(), indent=4))

# cleanup

db.commit()
db.close()
