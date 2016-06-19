# Dota 2 local DB pretty-print shell

import cmd
import d2mdb_const as const
import datetime
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

class Ppshell(cmd.Cmd):
	def __init__(self, cur):
		super(Ppshell, self).__init__()
		self.cur = cur
		self.prompt = '> '

	def print_match(self, row):
		for k in row.keys():
			label = const.DB_FIELD_NAMES[k] if k in const.DB_FIELD_NAMES else k
			v = row[k]
			value = FIELD_CONV[k](v) if k in FIELD_CONV else v
			print("%s: %s" % (label, value))

	def do_raw(self, s):
		'Execute a raw SQL query.'
		try:
			rows = self.cur.execute(s)
			num_results = 0
			for row in rows:
				self.print_match(row)
				print()
				num_results = num_results + 1
			print("%s result(s)" % num_results)
		except sqlite3.OperationalError as sqlerror:
			print("? - %s" % sqlerror)

	def do_select(self, s):
		'Execute a SQL SELECT query.'
		self.do_raw("SELECT %s" % s)

	def do_id(self, s):
		'Get a single match result for a match ID.'
		if len(s) == 0:
			print("No ID specified.")
			return
		self.do_select("* FROM matches WHERE id=%s" % s)

	def do_last(self, s):
		'Get the latest match recorded.'
		self.do_select("* FROM matches ORDER BY id DESC LIMIT 1")

	def do_at(self, s):
		'Get the match closest to the given time (in format YYYY-MM-DD hh-mm-ss)'
		try:
			time = datetime.datetime.strptime(s, "%Y-%m-%d %H-%M-%S").timestamp()
			rows = self.cur.execute("SELECT id FROM matches ORDER BY ABS(start_time - ?) ASC LIMIT 1", (time,))
			match_id = str(rows.fetchone()['id'])
			self.do_id(match_id)
		except ValueError as error:
			print("? - %s" % error)
			print("(Date needs to be in 'YYYY-MM-DD hh-mm-ss' format.)")

	def do_exit(self, s):
		'Exit the shell.'
		print('Bye')
		return True

	def do_EOF(self, s):
		return self.do_exit(s)

	def emptyline(self):
		pass


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

	shell = Ppshell(cur)

	go = True
	while go:
		try:
			shell.cmdloop()
			go = False
		except KeyboardInterrupt:
			print("^C")
			pass

	db.close()

if __name__ == '__main__':
	main()
