# Dota 2 match scraper/local DB
# WebAPI info: http://dev.dota2.com/showthread.php?t=47115
# API details (may be old?): https://wiki.teamfortress.com/wiki/WebAPI#Dota_2

# imports
from functools import reduce
import d2mdb_const as const
import json
import os.path
import random
import requests
import sqlite3
import sys
import time
import traceback

RANKED_LOBBY_TYPE = 7
UNRANKED_LOBBY_TYPE = 0

last_request = time.time()

# schema upgrade functions

def schema_upgrade_to_v2(cur):
	print("Upgrading DB to v2...")

	# add new columns
	for column in ["lobby_type INT UNSIGNED", "first_blood_time INT UNSIGNED", "leaver_status BOOLEAN"]:
		cur.execute("ALTER TABLE matches ADD %s" % column)

	# update matches
	cur.execute("SELECT id FROM matches")
	rows = cur.fetchall()
	for row in rows:
		# get match id and details
		match_id = row[0]
		match_details = get_match(match_id)

		# fill in row object with new fields
		row_obj = dict()
		row_obj["lobby_type"] = match_details.get("lobby_type")
		row_obj["first_blood_time"] = match_details.get("first_blood_time")
		row_obj["leaver_status"] = bool(reduce(lambda a, b: a or b.get("leaver_status", 0) > 1, match_details.get("players"), False))

		# update match with new fields
		sql_query = "UPDATE matches SET ({0}) = ({1}) WHERE id = ?".format(','.join(row_obj.keys()), ','.join('?'*len(row_obj)))
		cur.execute(sql_query, tuple(row_obj.values()) + (match_id,))
		print("Updated %d in db" % match_id)

	return 2

def schema_upgrade_to_v3(cur):
	print("Upgrading DB to v3...")

	# add new column
	for column in ["have_mega_creeps BOOLEAN", "against_mega_creeps BOOLEAN"]:
		cur.execute("ALTER TABLE matches ADD %s" % column)

	# update matches
	cur.execute("SELECT id, team FROM matches")
	rows = cur.fetchall()
	for row in rows:
		# get match id and details
		match_id = row[0]
		match_details = get_match(match_id)

		# fill in row object with new mega creeps fields
		team = row[1]
		have_mega_creeps_field = "barracks_status_radiant" if team else "barracks_status_dire"
		against_mega_creeps_field = "barracks_status_dire" if team else "barracks_status_radiant"

		row_obj = dict()
		row_obj["have_mega_creeps"] = match_details[have_mega_creeps_field] == 0
		row_obj["against_mega_creeps"] = match_details[against_mega_creeps_field] == 0

		# update match with new fields
		sql_query = "UPDATE matches SET ({0}) = ({1}) WHERE id = ?".format(','.join(row_obj.keys()), ','.join('?'*len(row_obj)))
		cur.execute(sql_query, tuple(row_obj.values()) + (match_id,))
		print("Updated %d in db" % match_id)

	return 3

SCHEMA_UPGRADE_TABLE = {
	0: schema_upgrade_to_v2,
	2: schema_upgrade_to_v3,
}

# network helper functions

def rate_limit():
	global last_request
	time_diff = time.time() - last_request
	if (time_diff < const.API_RATE_LIMIT):
		time.sleep(const.API_RATE_LIMIT - time_diff)
	last_request = time.time()

def send_request(url, qs):
	global last_request
	for _ in range(const.API_NUM_RETRIES):
		rate_limit()
		r = requests.get(url, params=qs)
		if r.status_code == 200:
			return r
		last_request = last_request + random.random()
	raise Exception("Failed to get request after %d tries (last attempt was %s)" % (const.API_NUM_RETRIES, r.status_code))

def get_match(match_id):
	qs = {"key": const.API_KEY, "match_id": match_id}
	r = send_request(const.DETAILS_URL, qs)
	return r.json().get("result")

# data processing functions

def fill_in(row_obj, player, prefix):
	for attr in const.PLAYER_ATTRS:
		row_obj[prefix + const.PLAYER_ATTRS.get(attr)] = player.get(attr, 0)

def combine_players(a, b):
	val = dict()
	for attr in const.PLAYER_ATTRS:
		val[attr] = a.get(attr) + b.get(attr)
	return val

def is_dire(player):
	return player.get("player_slot") & 128 != 0

def process_match(cur, match_id, account_id):
	# print out summary of match
	print("Processing match %d..." % match_id)

	# only get match if it does not already exist in db
	cur.execute("SELECT 1 FROM matches WHERE id = ?", (match_id,))
	if (cur.fetchone() is None):
		# get match details
		match_details = get_match(match_id)

		# get player + team details
		all_players = match_details.get("players")
		player = next(filter(lambda o: o.get("account_id") == account_id, all_players))
		player_team = is_dire(player)
		our_team = reduce(combine_players, filter(lambda p: is_dire(p) == player_team, all_players))
		their_team = reduce(combine_players, filter(lambda p: is_dire(p) != player_team, all_players), {attr: 0 for attr in const.PLAYER_ATTRS})

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
		row_obj["lobby_type"] = match_details.get("lobby_type")
		row_obj["first_blood_time"] = match_details.get("first_blood_time")
		row_obj["leaver_status"] = bool(reduce(lambda a, b: a | b.get("leaver_status", 0) > 1, all_players, 0))
		row_obj["have_mega_creeps"] = match_details.get("barracks_status_radiant" if player_team else "barracks_status_dire") == 0
		row_obj["against_mega_creeps"] = match_details.get("barracks_status_dire" if player_team else "barracks_status_radiant") == 0

		# store in db
		sql_query = "INSERT INTO matches ({0}) VALUES ({1})".format(','.join(row_obj.keys()), ','.join('?'*len(row_obj)))
		cur.execute(sql_query, tuple(row_obj.values()))
		print("Stored %d in db" % match_id)

def process_match_history(cur, history, account_id):
	# throw exception is status is not OK
	if history.get("status") != 1:
		raise Exception(history.get("statusDetail"))

	# print out summary of match history status
	results = history.get("num_results")
	results_total = history.get("total_results")
	results_left = history.get("results_remaining")
	print("Got %d matches, %d of %d remaining" % (results, results_left, results_total))

	# process each match in history
	matches = history.get("matches")
	for match in matches:
		match_id = match.get("match_id")
		try:
			process_match(cur, match_id, account_id)
		except Exception as e:
			print("Something went wrong processing {}, skipping...".format(match_id))
			traceback.print_exc()

# the main function

def main():
	# check command line arguments
	if len(sys.argv) < 2:
		print("Usage: %s <account id>" % sys.argv[0])
		print("You can get account id from Dota 2.")
		sys.exit(1)

	account_id = int(sys.argv[1])
	db_file = str(account_id) + ".db"

	# create/open SQLite db
	if not os.path.exists(db_file):
		db = sqlite3.connect(db_file)
		cur = db.cursor()
		cur.execute(const.SQL_MATCH_SCHEMA)
		cur.execute(const.SQL_VERSION_SCHEMA)
		cur.execute("INSERT INTO version VALUES (?)", (const.DB_SCHEMA_VERSION,))
		print("New db created as %s" % db_file)
	else:
		db = sqlite3.connect(db_file)
		cur = db.cursor()
		print("Opened %s" % db_file)

	# check for schema upgrades
	try:
		cur.execute("SELECT * FROM version")
		schema_row = cur.fetchone() or (0,)
		schema_version = schema_row[0]
	except sqlite3.OperationalError:
		# no version table found, assuming v0
		cur.execute(const.SQL_VERSION_SCHEMA)
		schema_version = 0

	print("DB schema v%d" % schema_version)
	while schema_version in SCHEMA_UPGRADE_TABLE:
		schema_version = SCHEMA_UPGRADE_TABLE[schema_version](cur)
		cur.execute("DELETE FROM version")
		cur.execute("INSERT INTO version VALUES (?)", (schema_version,))

	# get latest match time
	last_time = cur.execute("SELECT start_time FROM matches ORDER BY start_time DESC LIMIT 1").fetchone()
	if last_time is None:
		last_time = 0
	else:
		last_time = last_time[0]
	print("Last match time was %d" % last_time)

	# process initial list of match history from match sequence
	print("Getting match history...")
	qs = {"account_id": account_id, "key": const.API_KEY, "date_min": last_time + 1}
	history = send_request(const.HISTORY_URL, qs).json().get("result")
	process_match_history(cur, history, account_id)

	# keep processing rest of match history while there are more
	while history.get("results_remaining") > 0:
		print("Getting more match history...")
		last_match = history.get("matches")[-1];
		qs = {"account_id": account_id, "key": const.API_KEY, "date_min": last_time + 1, "date_max": last_match.get("start_time") - 1, "start_at_match_id": last_match.get("match_id") - 1}
		history = send_request(const.HISTORY_URL, qs).json().get("result")
		process_match_history(cur, history, account_id)

	# cleanup
	db.commit()
	db.close()

if __name__ == '__main__':
	main()
