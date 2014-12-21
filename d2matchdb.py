# Dota 2 match scraper/local DB
# WebAPI info: http://dev.dota2.com/showthread.php?t=47115
# API details (may be old?): https://wiki.teamfortress.com/wiki/WebAPI#Dota_2

# imports
import json
import os.path
import requests
import sqlite3
import time

# settings constants
API_KEY = "79A89606470D44E6BBE64BEC2D73D5BB" # your api key - http://steamcommunity.com/dev/apikey
ACCOUNT_ID = 388221 # your account id - get from Dota 2
DB_FILE = "matches.db" # db file to read/write

# other constants - do not touch
#HISTORY_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/"
#DETAILS_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/"
HISTORY_URL = "https://api.steampowered.com/IDOTA2Match_205790/GetMatchHistory/V001/"
DETAILS_URL = "https://api.steampowered.com/IDOTA2Match_205790/GetMatchDetails/V001/"
API_RATE_LIMIT = 1 # (in seconds)

SQL_CREATE_TABLE = (
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

RANKED_LOBBY_TYPE = 7
UNRANKED_LOBBY_TYPE = 0

last_request = time.time()

def rate_limit():
	global last_request
	time_diff = time.time() - last_request
	if (time_diff < API_RATE_LIMIT):
		time.sleep(API_RATE_LIMIT - time_diff)
	last_request = time.time()

def process_match(match):
	# print out summary of match
	match_id = match.get("match_id")
	print("Found match " + str(match_id))

def process_match_history(history):
	# throw exception is status is not OK
	if history.get("status") is not 1:
		raise Exception(history.get("statusDetail"))

	# print out summary of match history status
	results = history.get("num_results")
	results_total = history.get("total_results")
	results_left = history.get("results_remaining")
	print("Got " + str(results) + " matches, " + str(results_left) + " of " + str(results_total) + " remaining")

	# process each match in history
	matches = history.get("matches")
	for match in matches:
		process_match(match)

def main():
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

	# get latest match time
	last_time = c.execute("SELECT start_time FROM matches ORDER BY start_time DESC LIMIT 1").fetchone()
	if last_time is None:
		last_time = 0
	else:
		last_time = last_time[0]
	print("Last match time was " + str(last_time))

	# process initial list of match history from match sequence
	print("Getting match history...")
	qs = {"account_id": ACCOUNT_ID, "key": API_KEY, "date_min": last_time + 1}
	rate_limit()
	r = requests.get(HISTORY_URL, params=qs).json().get("result")
	process_match_history(r)

	# keep processing rest of match history while there are more
	while r.get("results_remaining") > 0:
		print("Getting more match history...")
		last_match = r.get("matches")[-1];
		qs = {"account_id": ACCOUNT_ID, "key": API_KEY, "date_min": last_time + 1, "date_max": last_match.get("start_time") - 1, "start_at_match_id": last_match.get("match_id") - 1}
		rate_limit()
		r = requests.get(HISTORY_URL, params=qs).json().get("result")
		process_match_history(r)

	# cleanup
	db.commit()
	db.close()

if __name__ == '__main__':
	main()
