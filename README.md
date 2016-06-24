d2matchdb
=========

d2matchdb is a small Python 3 project consisting of a few scripts to fetch,
store, and query information about Dota 2 matches.

Usage
-----

1. Install the Requests Python library.
2. You need a Steam API key to be able to fetch data from the Dota 2 API. You
can [register for an API key here](http://steamcommunity.com/dev/apikey).
3. Create a file named `api_key.py` with the contents `API_KEY = "<your API key
here>"`.
4. Run `python d2matchdb.py <your friend ID>` to fetch and store your match
history and match data. Your friend ID can be found by going into your profile
page in Dota 2 and looking under the "Edit Profile" button near the top-right of
the screen. This script writes the database to a .db file named after your
friend ID. For example, if your friend ID is 123456, then you would run `python
d2matchdb.py 123456`, which would fetch and store the results into a file named
`123456.db`.

The fetcher uses SQLite to store the results it gets, so you can use the
`sqlite3` command line tool to directly run queries against the database. The
results are stored into a table named `matches`.

If you want to be able to use the pretty-print shell, which displays results in
a more human-readable format, then:

1. Run `python updateheroes.py`. This will create heroes.db, a file which
contains a table of hero IDs and names. This is used by the shell to print hero
information.
2. Run `python ppshell.py <your friend ID>.db`. This will bring you to a command
interpreter/shell with a few basic commands.
3. You can type `help` to get some basic information on the supported commands.
4. Once you're done, you can type `exit` or send a ^D to exit the shell.

Some example commands:

* `last`: Show the latest match that was fetched.
* `id <match id>`: Show match information for the given match id (from the
database).
* `at <time>`: Show the match that started closest to the given time (time must
be in format "YYYY-MM-DD hh-mm-ss"
* `select * from matches order by id desc limit 5`: Show the last 5 matches.

Misc
----

This was initially a small mini-project of mine to familiarize myself with some
Python. I also thought it would be nice to have a local database of my matches
to run a bunch of queries on and derive some random data/statistics on my games.

The main libraries used in this project are the [Requests
library](http://docs.python-requests.org/en/master/) and the [SQLite
module](https://docs.python.org/3/library/sqlite3.html) from the Python Standard
Library.

License/Legal
-------------

d2matchdb is licensed under the MIT license. See the LICENSE file.

Dota is a trademark of Valve Corporation.
