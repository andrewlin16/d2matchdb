# Dota 2 local DB pretty-print shell

import d2mdb_const as const
import sqlite3
import sys
import time

heroes = dict()

# a bunch of lambdas to convert from values in the DB to proper representations
FIELD_CONV = {
	"hero": (lambda x: "%s (%d)" % (heroes[x], x)),
	"team": (lambda x: const.TEAMS[x]),
	"won": bool,
	"start_time": time.ctime,
	"game_mode": (lambda x: const.GAME_MODES[x] if x in const.GAME_MODES else "? (%s)" % x),
	"ranked": bool,
}

def print_match(row):
	for k in row.keys():
		label = const.DB_FIELD_NAMES[k] if k in const.DB_FIELD_NAMES else k
		v = row[k]
		value = FIELD_CONV[k](v) if k in FIELD_CONV else v
		print("%s: %s" % (label, value))

def main():
	global heroes

	# check command line arguments
	if len(sys.argv) < 2:
		print("Usage: %s <db file>" % sys.argv[0])
		return

	hero_db = sqlite3.connect(const.HEROES_DB_FILE)
	hero_db_cur = hero_db.cursor()
	heroes = hero_db_cur.execute("SELECT id, name FROM heroes").fetchall()

	heroes = dict(heroes)

	db_file = sys.argv[1]
	db = sqlite3.connect(db_file)
	db.row_factory = sqlite3.Row
	cur = db.cursor()

	while True:
		try:
			sql = input("> ")
			rows = cur.execute(sql)
			num_results = 0
			for row in rows:
				print_match(row)
				print()
				num_results = num_results + 1
			print("%s result(s)" % num_results)
		except EOFError:
			print("Bye")
			break
		except KeyboardInterrupt:
			print()
			pass
		except sqlite3.OperationalError as sqlerror:
			print("? - %s" % sqlerror)

	db.close()

if __name__ == '__main__':
	main()
