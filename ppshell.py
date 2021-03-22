# Dota 2 local DB pretty-print shell

import cmd
import d2mdb_const as const
import datetime
import functools
import random
import shlex
import sqlite3
import sys
import time

heroes = dict()

hero_db = sqlite3.connect(const.HEROES_DB_FILE)
hero_db_cur = hero_db.cursor()
heroes = dict(hero_db_cur.execute("SELECT id, name FROM heroes").fetchall())

show_enum = lambda e, x: "%s (%s)" % (e[x] if x in e else "?", str(x))

# a bunch of lambdas to convert from values in the DB to proper representations
FIELD_CONV = {
	"hero": functools.partial(show_enum, heroes),
	"team": (lambda x: const.TEAMS[x]),
	"won": bool,
	"duration": (lambda x: datetime.timedelta(seconds=int(x or 0))),
	"start_time": time.ctime,
	"game_mode": functools.partial(show_enum, const.GAME_MODES),
	"ranked": bool,
	"lobby_type": functools.partial(show_enum, const.LOBBY_TYPES),
	"first_blood_time": (lambda x: datetime.timedelta(seconds=int(x or 0))),
	"leaver_status": bool,
	"have_mega_creeps": bool,
	"against_mega_creeps": bool,
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

	def do_query(self, s):
		'Build and execute a SQL SELECT query. Usage: fields, predicate, asc/desc, limit.'
		args = shlex.split(s)
		fields = args[0] if len(args) >= 1 else "*"
		where = "WHERE %s " % args[1] if len(args) >= 2 else ""
		desc = 'ASC' if len(args) >= 3 and (args[2].lower() == 'asc' or args[2].lower() == 'false' or args[2] == '0') else 'DESC'
		limit = ("" if args[3].lower() == 'all' else " LIMIT %s" % args[3]) if len(args) >= 4 else " LIMIT 10"

		query = "SELECT %s FROM matches %sORDER BY id %s%s" % (fields, where, desc, limit)
		print(query)
		self.do_raw(query)

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

	def do_heroes(self, s):
		'Get the ID to hero mapping.'
		rev_map = sorted([(b, a) for (a, b) in heroes.items()], key=lambda el: el[0])
		for hero, hero_id in rev_map:
			print("%s: %d" % (hero, hero_id))

	def do_hero(self, s):
		'Search for a hero (ID or substring).'
		if s.isdigit():
			try:
				print(heroes[int(s)])
			except KeyError:
				print("No hero with ID %s." % s)
		else:
			for hero_id, hero in heroes.items():
				if hero.lower().find(s.lower()) != -1:
					print("%d (%s)" % (hero_id, hero))
					return
			print("Couldn't find hero with name \"%s\"." % s)

	def do_rollhero(self, s):
		'Roll/pick a random hero.'
		print(random.choice(list(heroes.values())))

	def do_schema(self, s):
		'Print out the schema (as expected by the program).'
		print(const.SQL_MATCH_SCHEMA)

	def do_exit(self, s):
		'Exit the shell.'
		print('Bye')
		return True

	def do_EOF(self, s):
		return self.do_exit(s)

	def emptyline(self):
		pass


def main():
	# check command line arguments
	if len(sys.argv) < 2:
		print("Usage: %s <db file>" % sys.argv[0])
		return

	db_file = sys.argv[1]
	db = sqlite3.connect(db_file)
	db.row_factory = sqlite3.Row
	cur = db.cursor()

	# check schema version
	schema_version = 0
	try:
		cur.execute("SELECT * FROM version")
		schema_row = cur.fetchone() or (0,)
		schema_version = schema_row[0]
	except sqlite3.OperationalError:
		# no version table found, assuming v0
		pass

	if schema_version != const.DB_SCHEMA_VERSION:
		print("NOTE: Schema version mismatch found (expected %d, got %d)!" % (const.DB_SCHEMA_VERSION, schema_version))

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
