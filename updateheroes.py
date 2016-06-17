# Part of the Dota 2 match scraper/local DB project
# This creates a table containing the list of heroes.

import d2mdb_common as common
import json
import requests
import sqlite3

def main():
	db = sqlite3.connect(common.HEROES_DB_FILE)
	cur = db.cursor()
	print("Opened %s" % common.HEROES_DB_FILE)

	cur.execute("DROP TABLE IF EXISTS heroes")
	cur.execute(common.SQL_HERO_SCHEMA)

	qs = {"key": common.API_KEY, "language": "en"}
	r = requests.get(common.HEROES_URL, params=qs)

	heroes = r.json().get("result").get("heroes")
	print("Found %d heroes" % len(heroes))
	for h in heroes:
		row_obj = dict()
		row_obj["id"] = h.get("id")
		row_obj["name"] = h.get("localized_name")
		row_obj["internal_name"] = h.get("name")

		sql_query = "INSERT INTO heroes ({0}) VALUES ({1})".format(','.join(row_obj.keys()), ','.join('?'*len(row_obj)))
		cur.execute(sql_query, tuple(row_obj.values()))

	print("Done")

	db.commit()
	db.close()

if __name__ == '__main__':
	main()
