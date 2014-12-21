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
HISTORY_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/"
DETAILS_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/"
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

RANKED_LOBBY_TYPE = 7
UNRANKED_LOBBY_TYPE = 0

last_request = time.time()

# functions

def rate_limit():
	global last_request
	time_diff = time.time() - last_request
	if (time_diff < API_RATE_LIMIT):
		time.sleep(API_RATE_LIMIT - time_diff)
	last_request = time.time()

# (API attribute to table field)
PLAYER_ATTRS = {"kills": "kills", "deaths": "deaths", "assists": "assists", "gold": "gold", "last_hits": "last_hits", "denies": "denies", "gold_per_min": "gpm", "xp_per_min": "xpm", "hero_damage": "hero_damage", "tower_damage": "tower_damage", "hero_healing": "hero_healing", "level": "level"}

def fill_in(row_obj, player, prefix):
	for attr in PLAYER_ATTRS:
		row_obj[prefix + PLAYER_ATTRS.get(attr)] = players.get(attr)

def combine_players(a, b):
	val = dict()
	for attr in PLAYER_ATTRS:
		val[attr] = a.get(attr) + b.get(attr)
	return val;

def is_dire(player):
	return player.get("player_slot") & 128 != 0

def process_match(cur, match):
	# print out summary of match
	match_id = match.get("match_id")
	print("Found match " + str(match_id))

	# only get match if it does not already exist in db
	cur.execute("SELECT 1 FROM matches WHERE id = ?", match_id)
	if (cur.fetchone() is None):
		# get match details
		qs = {"account_id": ACCOUNT_ID, "key": API_KEY, "date_min": last_time + 1}
		rate_limit()
		match_details = requests.get(HISTORY_URL, params=qs).json().get("result")

		all_players = match_details.get("players")
		player = next(filter(lambda o: o.get("account_id") == ACCOUNT_ID, all_players))
		player_team = is_dire(player)
		our_team = reduce(combine_players, filter(lambda p: is_dire(p) == player_team, players));
		their_team = reduce(combine_players, filter(lambda p: is_dire(p) != player_team, players));

		# fill in row object with fields
		row_obj = dict()
		row_obj["id"] = match_id
		row_obj["hero"] = player.get("hero_id")
		fill_in(row_obj, player, "")
		row_obj["team"] = player_team
		fill_in(row_obj, our_team, "our_")
		fill_in(row_obj, their_team, "their_")
		row_obj["won"] = match_details.get("radiant_win") ^ is_dire(player)
		row_obj["duration"] = match_details.get("duration")
		row_obj["start_time"] = match_details.get("start_time")
		row_obj["game_mode"] = match_details.get("game_mode")
		row_obj["ranked"] = match_details.get("lobby_type") == RANKED_LOBBY_TYPE

def process_match_history(cur, history):
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
		process_match(cur, match)

def main():
	# create/open SQLite db
	if not os.path.exists(DB_FILE):
		db = sqlite3.connect(DB_FILE)
		cur = db.cursor()
		cur.execute(SQL_CREATE_TABLE)
		print("New db created as " + DB_FILE)
	else:
		db = sqlite3.connect(DB_FILE)
		cur = db.cursor()
		print("Opened " + DB_FILE)

	# get latest match time
	last_time = cur.execute("SELECT start_time FROM matches ORDER BY start_time DESC LIMIT 1").fetchone()
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
	process_match_history(cur, r)

	# keep processing rest of match history while there are more
	while r.get("results_remaining") > 0:
		print("Getting more match history...")
		last_match = r.get("matches")[-1];
		qs = {"account_id": ACCOUNT_ID, "key": API_KEY, "date_min": last_time + 1, "date_max": last_match.get("start_time") - 1, "start_at_match_id": last_match.get("match_id") - 1}
		rate_limit()
		r = requests.get(HISTORY_URL, params=qs).json().get("result")
		process_match_history(cur, r)

	# cleanup
	db.commit()
	db.close()

if __name__ == '__main__':
	main()
