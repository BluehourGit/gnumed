"""GNUmed PostgreSQL connection handling.

TODO: iterator/generator batch fetching:
	- http://groups-beta.google.com/group/comp.lang.python/msg/7ff516d7d9387dad
	- search Google for "Geneator/Iterator Nesting Problem - Any Ideas? 2.4"

winner:
def resultset_functional_batchgenerator(cursor, size=100):
	for results in iter(lambda: cursor.fetchmany(size), []):
		for rec in results:
			yield rec
"""
# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmPG2.py,v $
__version__ = "$Revision: 1.124 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

### imports ###
# stdlib
import time, locale, sys, re as regex, os, codecs, types, datetime as pydt, logging, locale

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLoginInfo, gmExceptions, gmDateTime, gmBorg, gmI18N, gmLog2

_log = logging.getLogger('gm.db')
_log.info(__version__)

# 3rd party
try:
	import psycopg2 as dbapi
except ImportError:
	_log.exception("Python database adapter psycopg2 not found.")
	print "CRITICAL ERROR: Cannot find module psycopg2 for connecting to the database server."
	raise
### imports ###


_log.info('psycopg2 version: %s' % dbapi.__version__)
_log.info('PostgreSQL via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
if not (float(dbapi.apilevel) >= 2.0):
	raise ImportError('gmPG2: supported DB-API level too low')
if not (dbapi.threadsafety > 0):
	raise ImportError('gmPG2: lacking minimum thread safety in psycopg2')
if not (dbapi.paramstyle == 'pyformat'):
	raise ImportError('gmPG2: lacking pyformat (%%(<name>)s style) placeholder support in psycopg2')
try:
	dbapi.__version__.index('dt')
except ValueError:
	raise ImportError('gmPG2: lacking datetime support in psycopg2')
try:
	dbapi.__version__.index('ext')
except ValueError:
	raise ImportError('gmPG2: lacking extensions support in psycopg2')
try:
	dbapi.__version__.index('pq3')
except ValueError:
	raise ImportError('gmPG2: lacking v3 backend protocol support in psycopg2')

import psycopg2.extras
import psycopg2.extensions
import psycopg2.pool
import psycopg2.errorcodes as sql_error_codes

# =======================================================================
_default_client_encoding = 'UTF8'
_log.info('assuming default client encoding of [%s]' % _default_client_encoding)

# things timezone
_default_client_timezone = None			# default time zone for connections
_sql_set_timezone = None
_timestamp_template = "cast('%s' as timestamp with time zone)"		# MUST NOT be uniocde or else getquoted will not work
FixedOffsetTimezone = dbapi.tz.FixedOffsetTimezone

_default_dsn = None
_default_login = None

postgresql_version_string = None
postgresql_version = None			# accuracy: major.minor

__ro_conn_pool = None

# =======================================================================
# global data
# =======================================================================

known_schema_hashes = {
	'devel': 'not released, testing only',
	'v2': 'b09d50d7ed3f91ddf4c4ddb8ea507720',
	'v3': 'e73718eaf230d8f1d2d01afa8462e176',
	'v4': '4428ccf2e54c289136819e701bb095ea',
	'v5': '7e7b093af57aea48c288e76632a382e5',	# ... old (v1) style hashes
	'v6': '90e2026ac2efd236da9c8608b8685b2d',	# new (v2) style hashes ...
	'v7': '6c9f6d3981483f8e9433df99d1947b27',
	'v8': '89b13a7af83337c3aad153b717e52360',
	'v9': '641a9b2be3c378ffc2bb2f0b1c9f051d',
	'v10': '7ef42a8fb2bd929a2cdd0c63864b4e8a',
	'v11': '03042ae24f3f92877d986fb0a6184d76',
	'v12': '06183a6616db62257e22814007a8ed07'
}

map_schema_hash2version = {
	'b09d50d7ed3f91ddf4c4ddb8ea507720': 'v2',
	'e73718eaf230d8f1d2d01afa8462e176': 'v3',
	'4428ccf2e54c289136819e701bb095ea': 'v4',
	'7e7b093af57aea48c288e76632a382e5': 'v5',
	'90e2026ac2efd236da9c8608b8685b2d': 'v6',
	'6c9f6d3981483f8e9433df99d1947b27': 'v7',
	'89b13a7af83337c3aad153b717e52360': 'v8',
	'641a9b2be3c378ffc2bb2f0b1c9f051d': 'v9',
	'7ef42a8fb2bd929a2cdd0c63864b4e8a': 'v10',
	'03042ae24f3f92877d986fb0a6184d76': 'v11',
	'06183a6616db62257e22814007a8ed07': 'v12'
}

map_client_branch2required_db_version = {
	u'CVS HEAD': u'devel',
	u'0.3': u'v9',
	u'0.4': u'v10',
	u'0.5': u'v11',
	u'0.6': u'v12'
}

# get columns and data types for a given table
query_table_col_defs = u"""select
	cols.column_name,
	cols.udt_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

query_table_attributes = u"""select
	cols.column_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

# =======================================================================
# module globals API
# =======================================================================
def set_default_client_encoding(encoding = None):
	# check whether psycopg2 can handle this encoding
	if encoding not in psycopg2.extensions.encodings:
		raise ValueError('psycopg2 does not know how to handle client (wire) encoding [%s]' % encoding)
	# check whether Python can handle this encoding
	py_enc = psycopg2.extensions.encodings[encoding]
	try:
		codecs.lookup(py_enc)
	except LookupError:
		_log.warning('<codecs> module can NOT handle encoding [psycopg2::<%s> -> Python::<%s>]' % (encoding, py_enc))
		raise
	# FIXME: check encoding against the database
	# FIXME: - but we may not yet have access
	# FIXME: - psycopg2 will pull its encodings from the database eventually
	# it seems save to set it
	global _default_client_encoding
	_log.info('setting default client encoding from [%s] to [%s]' % (_default_client_encoding, str(encoding)))
	_default_client_encoding = encoding
	return True
#---------------------------------------------------
def set_default_client_timezone(timezone = None):

	# FIXME: use __validate
	global _default_client_timezone
	_log.info('setting default client time zone from [%s] to [%s]' % (_default_client_timezone, timezone))
	_default_client_timezone = timezone

	global _sql_set_timezone
	_sql_set_timezone = u'set timezone to %s'

	return True
#---------------------------------------------------
def __validate_timezone(conn=None, timezone=None):

	_log.debug(u'validating time zone [%s]', timezone)

	cmd = u'set timezone to %(tz)s'
	args = {u'tz': timezone}

	conn.commit()
	curs = conn.cursor()
	is_valid = False
	try:
		curs.execute(cmd, args)
		_log.info(u'time zone [%s] is settable', timezone)
		# can we actually use it, though ?
		cmd = u"""select '1920-01-19 23:00:00+01'::timestamp with time zone"""
		try:
			curs.execute(cmd)
			curs.fetchone()
			_log.info(u'time zone [%s] is usable', timezone)
			is_valid = True
		except:
			_log.error('error using time zone [%s]', timezone)
	except dbapi.DataError:
		_log.warning(u'time zone [%s] is not settable', timezone)
	except:
		_log.error(u'failed to set time zone to [%s]', timezone)
		_log.exception(u'')

	curs.close()
	conn.rollback()

	return is_valid
#---------------------------------------------------
def __expand_timezone(conn=None, timezone=None):
	"""some timezone defs are abbreviations so try to expand
	them because "set time zone" doesn't take abbreviations"""

	cmd = u"""
select distinct on (abbrev) name
from pg_timezone_names
where
	abbrev = %(tz)s and
	name ~ '^[^/]+/[^/]+$' and
	name !~ '^Etc/'
"""
	args = {u'tz': timezone}

	conn.commit()
	curs = conn.cursor()

	result = timezone
	try:
		curs.execute(cmd, args)
		rows = curs.fetchall()
		if len(rows) > 0:
			result = rows[0][0]
			_log.debug(u'[%s] maps to [%s]', timezone, result)
	except:
		_log.exception(u'cannot expand timezone abbreviation [%s]', timezone)

	curs.close()
	conn.rollback()

	return result
#---------------------------------------------------
def __detect_client_timezone(conn=None):
	"""This is run on the very first connection."""

	# FIXME: check whether server.timezone is the same
	# FIXME: value as what we eventually detect

	# we need gmDateTime to be initialized
	if gmDateTime.current_local_iso_numeric_timezone_string is None:
		gmDateTime.init()

	_log.debug('trying to detect timezone from system')

	tz_candidates = []
	try:
		tz = os.environ['TZ'].decode(gmI18N.get_encoding(), 'replace')
		tz_candidates.append(tz)
		expanded = __expand_timezone(conn = conn, timezone = tz)
		if expanded != tz:
			tz_candidates.append(expanded)
	except KeyError:
		pass

	tz_candidates.append(gmDateTime.current_local_timezone_name)
	expanded = __expand_timezone(conn = conn, timezone = gmDateTime.current_local_timezone_name)
	if expanded != gmDateTime.current_local_timezone_name:
		tz_candidates.append(expanded)

	_log.debug('candidates: %s', str(tz_candidates))

	# find best among candidates
	global _default_client_timezone
	global _sql_set_timezone
	found = False
	for tz in tz_candidates:
		if __validate_timezone(conn = conn, timezone = tz):
			_default_client_timezone = tz
			_sql_set_timezone = u'set timezone to %s'
			found = True
			break

	if not found:
		_default_client_timezone = gmDateTime.current_local_iso_numeric_timezone_string
		_sql_set_timezone = u"set time zone interval %s hour to minute"

	_log.info('client system time zone detected as equivalent to [%s]', _default_client_timezone)
# =======================================================================
# login API
# =======================================================================
def __prompted_input(prompt, default=None):
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#---------------------------------------------------
def __request_login_params_tui():
	"""Text mode request of database login parameters"""
	import getpass
	login = gmLoginInfo.LoginInfo()

	print "\nPlease enter the required login parameters:"
	try:
		login.host = __prompted_input("host ['' = non-TCP/IP]: ", '')
		login.database = __prompted_input("database [gnumed_v12]: ", 'gnumed_v12')
		login.user = __prompted_input("user name: ", '')
		tmp = 'password for "%s" (not shown): ' % login.user
		login.password = getpass.getpass(tmp)
		login.port = __prompted_input("port [5432]: ", 5432)
	except KeyboardInterrupt:
		_log.warning("user cancelled text mode login dialog")
		print "user cancelled text mode login dialog"
		raise gmExceptions.ConnectionError(_("Cannot connect to database without login information!"))

	return login
#---------------------------------------------------
def __request_login_params_gui_wx():
	"""GUI (wx) input request for database login parameters.

	Returns gmLoginInfo.LoginInfo object
	"""
	import wx
	# OK, wxPython was already loaded. But has the main Application instance
	# been initialized yet ? if not, the exception will kick us out
	if wx.GetApp() is None:
		raise gmExceptions.NoGuiError(_("The wxPython GUI framework hasn't been initialized yet!"))

	# Let's launch the login dialog
	# if wx was not initialized /no main App loop, an exception should be raised anyway
	import gmAuthWidgets
	dlg = gmAuthWidgets.cLoginDialog(None, -1)
	dlg.ShowModal()
	login = dlg.panel.GetLoginInfo()
	dlg.Destroy()

	#if user cancelled or something else went wrong, raise an exception
	if login is None:
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))

	return login
#---------------------------------------------------
def request_login_params():
	"""Request login parameters for database connection.
	"""
	# are we inside X ?
	# (if we aren't wxGTK will crash hard at
	# C-level with "can't open Display")
	if os.environ.has_key('DISPLAY'):
		# try GUI
		try:
			return __request_login_params_gui_wx()
		except:
			pass
	# well, either we are on the console or
	# wxPython does not work, use text mode
	return __request_login_params_tui()

# =======================================================================
# DSN API
# -----------------------------------------------------------------------
def make_psycopg2_dsn(database=None, host=None, port=5432, user=None, password=None):
	dsn_parts = []

	if (database is not None) and (database.strip() != ''):
		dsn_parts.append('dbname=%s' % database)

	if (host is not None) and (host.strip() != ''):
		dsn_parts.append('host=%s' % host)

	if (port is not None) and (str(port).strip() != ''):
		dsn_parts.append('port=%s' % port)

	if (user is not None) and (user.strip() != ''):
		dsn_parts.append('user=%s' % user)

	if (password is not None) and (password.strip() != ''):
		dsn_parts.append('password=%s' % password)

	dsn_parts.append('sslmode=prefer')

	return ' '.join(dsn_parts)
# ------------------------------------------------------
def get_default_login():
	# make sure we do have a login
	get_default_dsn()
	return _default_login
# ------------------------------------------------------
def get_default_dsn():
	global _default_dsn
	if _default_dsn is not None:
		return _default_dsn

	login = request_login_params()
	set_default_login(login=login)

	return _default_dsn
# ------------------------------------------------------
def set_default_login(login=None):
	if login is None:
		return False

	if login.host is not None:
		if login.host.strip() == u'':
			login.host = None

	global _default_login
	_default_login = login
	_log.info('setting default login from [%s] to [%s]' % (_default_login, login))

	dsn = make_psycopg2_dsn(login.database, login.host, login.port, login.user, login.password)

	global _default_dsn
	_default_dsn = dsn
	_log.info('setting default DSN from [%s] to [%s]' % (_default_dsn, dsn))

	return True
# =======================================================================
# netadata API
# =======================================================================
def database_schema_compatible(link_obj=None, version=None, verbose=True):
	expected_hash = known_schema_hashes[version]
	if version == 'devel':
		args = {'ver': '9999'}
	else:
		args = {'ver': version.strip('v')}
	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [{
			'cmd': u'select md5(gm.concat_table_structure(%(ver)s::integer)) as md5',
			'args': args
		}]
	)
	if rows[0]['md5'] != expected_hash:
		_log.error('database schema version mismatch')
		_log.error('expected: %s (%s)' % (version, expected_hash))
		_log.error('detected: %s (%s)' % (get_schema_version(link_obj=link_obj), rows[0]['md5']))
		if verbose:
			_log.debug('schema dump follows:')
			for line in get_schema_structure(link_obj=link_obj).split():
				_log.debug(line)
			_log.debug('schema revision history dump follows:')
			for line in get_schema_revision_history(link_obj=link_obj):
				_log.debug(u' - '.join(line))
		return False
	_log.info('detected schema version [%s], hash [%s]' % (map_schema_hash2version[rows[0]['md5']], rows[0]['md5']))
	return True
#------------------------------------------------------------------------
def get_schema_version(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': u'select md5(gm.concat_table_structure()) as md5'}])
	try:
		return map_schema_hash2version[rows[0]['md5']]
	except KeyError:
		return u'unknown database schema version, MD5 hash is [%s]' % rows[0]['md5']
#------------------------------------------------------------------------
def get_schema_structure(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': u'select gm.concat_table_structure()'}])
	return rows[0][0]
#------------------------------------------------------------------------
def get_schema_revision_history(link_obj=None):
	cmd = u"""
select
	imported::text,
	version,
	filename
from gm.schema_revision
order by imported
"""
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': cmd}])
	return rows
#------------------------------------------------------------------------
def get_current_user():
	rows, idx = run_ro_queries(queries = [{'cmd': u'select CURRENT_USER'}])
	return rows[0][0]
#------------------------------------------------------------------------
def get_foreign_keys2column(schema='public', table=None, column=None, link_obj=None):
	"""Get the foreign keys pointing to schema.table.column.

	Does not properly work with multi-column FKs.
	GNUmed doesn't use any, however.
	"""
	cmd = u"""
select
	%(schema)s as referenced_schema,
	%(tbl)s as referenced_table,
	%(col)s as referenced_column,
	pgc.confkey as referenced_column_list,
	pgc.conrelid::regclass as referencing_table,
	pgc.conkey as referencing_column_list,
	(select attname from pg_attribute where attnum = pgc.conkey[1] and attrelid = pgc.conrelid) as referencing_column
from
	pg_constraint pgc
where
	pgc.contype = 'f'
		and
	pgc.confrelid = (
		select oid from pg_class where relname = %(tbl)s and relnamespace = (
			select oid from pg_namespace where nspname = %(schema)s
		 )
	)	and
	(
		select attnum
		from pg_attribute
		where
			attrelid = (select oid from pg_class where relname = %(tbl)s and relnamespace = (
				select oid from pg_namespace where nspname = %(schema)s
			))
				and
			attname = %(col)s
	) = any(pgc.confkey)
"""

	args = {
		'schema': schema,
		'tbl': table,
		'col': column
	}

	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [
			{'cmd': cmd, 'args': args}
		]
	)

	return rows
#------------------------------------------------------------------------
def get_child_tables(schema='public', table=None, link_obj=None):
	"""Return child tables of <table>."""
	cmd = u"""
select
	pgn.nspname as namespace,
	pgc.relname as table
from
	pg_namespace pgn,
	pg_class pgc
where
	pgc.relnamespace = pgn.oid
		and
	pgc.oid in (
		select inhrelid from pg_inherits where inhparent = (
			select oid from pg_class where
				relnamespace = (select oid from pg_namespace where nspname = %(schema)s) and
				relname = %(table)s
		)
	)"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': {'schema': schema, 'table': table}}])
	return rows
#------------------------------------------------------------------------
def table_exists(link_obj=None, schema=None, table=None):
	"""Returns false, true."""
	cmd = u"""
select exists (
	select 1 from information_schema.tables
	where
		table_schema = %s and
		table_name = %s and
		table_type = 'BASE TABLE'
)"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': (schema, table)}])
	return rows[0][0]
#------------------------------------------------------------------------
def get_col_indices(cursor = None):
	if cursor.description is None:
		_log.error('no result description available: unused cursor or last query did not select rows')
		return None
	col_indices = {}
	col_index = 0
	for col_desc in cursor.description:
		col_name = col_desc[0]
		# a query like "select 1,2;" will return two columns of the same name !
		# hence adjust to that, note, however, that dict-style access won't work
		# on results of such queries ...
		if col_indices.has_key(col_name):
			col_name = '%s_%s' % (col_name, col_index)
		col_indices[col_name] = col_index
		col_index += 1

	return col_indices
#------------------------------------------------------------------------
def get_col_defs(link_obj=None, schema='public', table=None):
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': query_table_col_defs, 'args': (schema, table)}])
	col_names = []
	col_type = {}
	for row in rows:
		col_names.append(row[0])
		# map array types
		if row[1].startswith('_'):
			col_type[row[0]] = row[1][1:] + '[]'
		else:
			col_type[row[0]] = row[1]
	col_defs = []
	col_defs.append(col_names)
	col_defs.append(col_type)
	return col_defs
#------------------------------------------------------------------------
def get_col_names(link_obj=None, schema='public', table=None):
	"""Return column attributes of table"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': query_table_attributes, 'args': (schema, table)}])
	cols = []
	for row in rows:
		cols.append(row[0])
	return cols
#------------------------------------------------------------------------
def get_translation_languages():
	rows, idx = run_ro_queries (
		queries = [{'cmd': u'select distinct lang from i18n.translations'}]
	)
	return [ r[0] for r in rows ]
#------------------------------------------------------------------------
def get_current_user_language():
	cmd = u'select i18n.get_curr_lang()'
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}])
	return rows[0][0]
#------------------------------------------------------------------------
def set_user_language(user=None, language=None):
	"""Set the user language in the database.

	user = None: current db user
	language = None: unset
	"""
	_log.info('setting database language for user [%s] to [%s]', user, language)

	args = {
		'usr': user,
		'lang': language
	}

	if language is None:
		if user is None:
			queries = [{'cmd': u'select i18n.unset_curr_lang()'}]
		else:
			queries = [{'cmd': u'select i18n.unset_curr_lang(%(usr)s)', 'args': args}]
		queries.append({'cmd': u'select True'})
	else:
		if user is None:
			queries = [{'cmd': u'select i18n.set_curr_lang(%(lang)s)', 'args': args}]
		else:
			queries = [{'cmd': u'select i18n.set_curr_lang(%(lang)s, %(usr)s)', 'args': args}]

	rows, idx = run_rw_queries(queries = queries, return_data = True)

	if not rows[0][0]:
		_log.error('cannot set database language to [%s] for user [%s]', language, user)

	return rows[0][0]
#------------------------------------------------------------------------
def force_user_language(language=None):
	"""Set the user language in the database.

	- regardless of whether there is any translation available.
	- only for the current user
	"""
	_log.info('forcing database language for current db user to [%s]', language)

	run_rw_queries(queries = [{
		'cmd': u'select i18n.force_curr_lang(%(lang)s)',
		'args': {'lang': language}
	}])
#------------------------------------------------------------------------
#------------------------------------------------------------------------
text_expansion_keywords = None

def get_text_expansion_keywords():
	global text_expansion_keywords
	if text_expansion_keywords is not None:
		return text_expansion_keywords

	cmd = u"""select keyword, public_expansion, private_expansion, owner from clin.v_keyword_expansions"""
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}])
	text_expansion_keywords = rows

	_log.info('retrieved %s text expansion keywords', len(text_expansion_keywords))

	return text_expansion_keywords
#------------------------------------------------------------------------
def expand_keyword(keyword = None):

	# Easter Egg ;-)
	if keyword == u'$$steffi':
		return u'Hai, play !  Versucht das ! (Keks dazu ?)  :-)'

	cmd = u"""select expansion from clin.v_your_keyword_expansions where keyword = %(kwd)s"""
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword}}])

	if len(rows) == 0:
		return None

	return rows[0]['expansion']
#------------------------------------------------------------------------
def get_keyword_expansion_candidates(keyword = None):

	if keyword is None:
		return []

	get_text_expansion_keywords()

	candidates = []
	for kwd in text_expansion_keywords:
		if kwd['keyword'].startswith(keyword):
			candidates.append(kwd['keyword'])

	return candidates
#------------------------------------------------------------------------
def add_text_expansion(keyword=None, expansion=None, public=None):

	if public:
		cmd = u"select 1 from clin.v_keyword_expansions where public_expansion is true and keyword = %(kwd)s"
	else:
		cmd = u"select 1 from clin.v_your_keyword_expansions where private_expansion is true and keyword = %(kwd)s"

	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword}}])
	if len(rows) != 0:
		return False

	if public:
		cmd = u"""
insert into clin.keyword_expansion (keyword, expansion, fk_staff)
values (%(kwd)s, %(exp)s, null)"""
	else:
		cmd = u"""
insert into clin.keyword_expansion (keyword, expansion, fk_staff)
values (%(kwd)s, %(exp)s, (select pk from dem.staff where db_user = current_user))"""

	rows, idx = run_rw_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword, 'exp': expansion}}])

	global text_expansion_keywords
	text_expansion_keywords = None

	return True
#------------------------------------------------------------------------
def delete_text_expansion(keyword):
	cmd = u"""
delete from clin.keyword_expansion where
	keyword = %(kwd)s and (
		(fk_staff = (select pk from dem.staff where db_user = current_user))
			or
		(fk_staff is null and owner = current_user)
	)"""
	rows, idx = run_rw_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword}}])

	global text_expansion_keywords
	text_expansion_keywords = None
#------------------------------------------------------------------------
def edit_text_expansion(keyword, expansion):

	cmd1 = u"""
delete from clin.keyword_expansion where
	keyword = %(kwd)s and 
	fk_staff = (select pk from dem.staff where db_user = current_user)"""

	cmd2 = u"""
insert into clin.keyword_expansion (keyword, expansion, fk_staff)
values (%(kwd)s, %(exp)s, (select pk from dem.staff where db_user = current_user))"""

	rows, idx = run_rw_queries(queries = [
		{'cmd': cmd1, 'args': {'kwd': keyword}},
		{'cmd': cmd2, 'args': {'kwd': keyword, 'exp': expansion}},
	])

	global text_expansion_keywords
	text_expansion_keywords = None
# =======================================================================
# query runners and helpers
# =======================================================================
def send_maintenance_notification():
	cmd = u'notify "db_maintenance_warning:"'
	run_rw_queries(queries = [{'cmd': cmd}], return_data = False)
#------------------------------------------------------------------------
def send_maintenance_shutdown():
	cmd = u'notify "db_maintenance_disconnect:"'
	run_rw_queries(queries = [{'cmd': cmd}], return_data = False)
#------------------------------------------------------------------------
def is_pg_interval(candidate=None):
	cmd = u'select %(candidate)s::interval'
	try:
		rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
		return True
	except:
		cmd = u'select %(candidate)s::text::interval'
		try:
			rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
			return True
		except:
			return False
#------------------------------------------------------------------------
def bytea2file(data_query=None, filename=None, chunk_size=0, data_size=None, data_size_query=None):
	outfile = file(filename, 'wb')
	result = bytea2file_object(data_query=data_query, file_obj=outfile, chunk_size=chunk_size, data_size=data_size, data_size_query=data_size_query)
	outfile.close()
	return result
#------------------------------------------------------------------------
def bytea2file_object(data_query=None, file_obj=None, chunk_size=0, data_size=None, data_size_query=None):
	"""Store data from a bytea field into a file.

	<data_query>
	- dict {'cmd': ..., 'args': ...}
	- 'cmd' must be unicode containing "... substring(data from %(start)s for %(size)s) ..."
	- 'args' must be a dict
	- must return one row with one field of type bytea
	<file>
	- must be a file like Python object
	<data_size>
	- integer of the total size of the expected data or None
	<data_size_query>
	- dict {'cmd': ..., 'args': ...}
	- cmd must be unicode
	- must return one row with one field with the octet_length() of the data field
	- used only when <data_size> is None
	"""
	if data_size == 0:
		return True

	# If the client sets an encoding other than the default we
	# will receive encoding-parsed data which isn't the binary
	# content we want. Hence we need to get our own connection.
	# It must be a read-write one so that we don't affect the
	# encoding for other users of the shared read-only
	# connections.
	# Actually, encodings shouldn't be applied to binary data
	# (eg. bytea types) in the first place but that is only
	# reported to be fixed > v7.4.
	# further tests reveal that at least on PG 8.0 this bug still
	# manifests itself
	conn = get_raw_connection(readonly=True)

	if data_size is None:
		rows, idx = run_ro_queries(link_obj = conn, queries = [data_size_query])
		data_size = rows[0][0]
		if data_size in [None, 0]:
			conn.rollback()
			return True

	_log.debug('expecting bytea data of size: [%s] bytes' % data_size)
	_log.debug('using chunk size of: [%s] bytes' % chunk_size)

	# chunk size of 0 means "retrieve whole field at once"
	if chunk_size == 0:
		chunk_size = data_size
		_log.debug('chunk size [0] bytes: retrieving all data at once')

	# Windoze sucks: it can't transfer objects of arbitrary size,
	# anyways, we need to split the transfer,
	# however, only possible if postgres >= 7.2
	needed_chunks, remainder = divmod(data_size, chunk_size)
	_log.debug('chunks to retrieve: [%s]' % needed_chunks)
	_log.debug('remainder to retrieve: [%s] bytes' % remainder)

	# retrieve chunks, skipped if data size < chunk size,
	# does this not carry the danger of cutting up multi-byte escape sequences ?
	# no, since bytea is binary,
	# yes, since in bytea there are *some* escaped values, still
	# no, since those are only escaped during *transfer*, not on-disk, hence
	# only complete escape sequences are put on the wire
	for chunk_id in range(needed_chunks):
		chunk_start = (chunk_id * chunk_size) + 1
		data_query['args']['start'] = chunk_start
		data_query['args']['size'] = chunk_size
		try:
			rows, idx = run_ro_queries(link_obj=conn, queries=[data_query])
		except:
			_log.error('cannot retrieve chunk [%s/%s], size [%s], try decreasing chunk size' % (chunk_id+1, needed_chunks, chunk_size))
			conn.rollback()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(str(rows[0][0]))

	# retrieve remainder
	if remainder > 0:
		chunk_start = (needed_chunks * chunk_size) + 1
		data_query['args']['start'] = chunk_start
		data_query['args']['size'] = remainder
		try:
			rows, idx = run_ro_queries(link_obj=conn, queries=[data_query])
		except:
			_log.error('cannot retrieve remaining [%s] bytes' % remainder)
			conn.rollback()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(str(rows[0][0]))

	conn.rollback()
	return True
#------------------------------------------------------------------------
def file2bytea(query=None, filename=None, args=None, conn=None):
	"""Store data from a file into a bytea field.

	The query must:
	- be in unicode
	- contain a format spec identifying the row (eg a primary key)
	  matching <args> if it is an UPDATE
	- contain a format spec %(data)s::bytea
	"""
	# read data from file
	infile = file(filename, "rb")
	data_as_byte_string = infile.read()
	infile.close()
	if args is None:
		args = {}
	args['data'] = buffer(data_as_byte_string)
	del(data_as_byte_string)

	# insert the data
	if conn is None:
		conn = get_raw_connection(readonly=False)
	run_rw_queries(link_obj=conn, queries = [{'cmd': query, 'args': args}], end_tx=True)
	conn.close()

	return
#------------------------------------------------------------------------
def sanitize_pg_regex(expression=None, escape_all=False):
	"""Escape input for use in a PostgreSQL regular expression.

	If a fragment comes from user input and is to be used
	as a regular expression we need to make sure it doesn't
	contain invalid regex patterns such as unbalanced ('s.

	<escape_all>
		True: try to escape *all* metacharacters
		False: only escape those which render the regex invalid
	"""
	return expression.replace (
			'(', '\('
		).replace (
			')', '\)'
		).replace (
			'[', '\['
		).replace (
			'+', '\+'
		).replace (
			'.', '\.'
		).replace (
			'*', '\*'
		)
		#']', '\]',			# not needed
#------------------------------------------------------------------------
def run_ro_queries(link_obj=None, queries=None, verbose=False, return_data=True, get_col_idx=False):
	"""Run read-only queries.

	<queries> must be a list of dicts:
		[
			{'cmd': <string>, 'args': <dict> or <tuple>},
			{...},
			...
		]
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		curs = link_obj
		curs_close = __noop
		tx_rollback = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		curs = link_obj.cursor()
		curs_close = curs.close
		tx_rollback = link_obj.rollback
	elif link_obj is None:
		conn = get_connection(readonly=True, verbose=verbose)
		curs = conn.cursor()
		curs_close = curs.close
		tx_rollback = conn.rollback
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	if verbose:
		_log.debug('cursor: %s', curs)

	for query in queries:
		if type(query['cmd']) is not types.UnicodeType:
			print "run_ro_queries(): non-unicode query"
			print query['cmd']
		try:
			args = query['args']
		except KeyError:
			args = None
		try:
			curs.execute(query['cmd'], args)
			if verbose:
				_log.debug('ran query: [%s]', curs.query)
				_log.debug('PG status message: %s', curs.statusmessage)
				_log.debug('cursor description: %s', str(curs.description))
		except:
			# FIXME: use .pgcode
			try:
				curs_close()
			except dbapi.InterfaceError:
				_log.exception('cannot close cursor')
			tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			_log.error('query failed: [%s]', curs.query)
			_log.error('PG status message: %s', curs.statusmessage)
			raise

	data = None
	col_idx = None
	if return_data:
		data = curs.fetchall()
		if verbose:
			_log.debug('last query returned [%s (%s)] rows', curs.rowcount, len(data))
			_log.debug('cursor description: %s', str(curs.description))
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	tx_rollback()		# rollback just so that we don't stay IDLE IN TRANSACTION forever
	return (data, col_idx)
#------------------------------------------------------------------------
def run_rw_queries(link_obj=None, queries=None, end_tx=False, return_data=None, get_col_idx=False, verbose=False):
	"""Convenience function for running a transaction
	   that is supposed to get committed.

	<link_obj>
		can be either:
		- a cursor
		- a connection

	<queries>
		is a list of dicts [{'cmd': <string>, 'args': <dict> or <tuple>)
		to be executed as a single transaction, the last
		query may usefully return rows (such as a
		"select currval('some_sequence')" statement)

	<end_tx>
		- controls whether the transaction is finalized (eg.
		  committed/rolled back) or not, this allows the
		  call to run_rw_queries() to be part of a framing
		  transaction
		- if link_obj is a connection then <end_tx> will
		  default to False unless it is explicitly set to
		  True which is taken to mean "yes, you do have full
		  control over the transaction" in which case the
		  transaction is properly finalized
		- if link_obj is a cursor we CANNOT finalize the
		  transaction because we would need the connection for that
		- if link_obj is None <end_tx> will, of course, always be True

	<return_data>
		- if true, the returned data will include the rows
		  the last query selected
		- if false, it returns None instead

	<get_col_idx>
		- if true, the returned data will include a dictionary
		  mapping field names to column positions
		- if false, the returned data returns None instead

	method result:
		- returns a tuple (data, idx)
		- <data>:
			* (None, None) if last query did not return rows
			* ("fetchall() result", <index>) if last query returned any rows
			* for <index> see <get_col_idx>
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		conn_close = __noop
		conn_commit = __noop
		conn_rollback = __noop
		curs = link_obj
		curs_close = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		conn_close = __noop
		if end_tx:
			conn_commit = link_obj.commit
			conn_rollback = link_obj.rollback
		else:
			conn_commit = __noop
			conn_rollback = __noop
		curs = link_obj.cursor()
		curs_close = curs.close
	elif link_obj is None:
		conn = get_connection(readonly=False)
		conn_close = conn.close
		conn_commit = conn.commit
		conn_rollback = conn.rollback
		curs = conn.cursor()
		curs_close = curs.close
	else:
		raise ValueError('link_obj must be cursor, connection or None and not [%s]' % link_obj)

	for query in queries:
		if type(query['cmd']) is not types.UnicodeType:
			print "run_rw_queries(): non-unicode query"
			print query['cmd']
		try:
			args = query['args']
		except KeyError:
			args = None
		try:
			curs.execute(query['cmd'], args)
		except:
			_log.exception('error running RW query')
			gmLog2.log_stack_trace()
			try:
				curs_close()
				conn_rollback()
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
				raise
			raise

	data = None
	col_idx = None
	if return_data:
		try:
			data = curs.fetchall()
		except:
			_log.exception('error fetching data from RW query')
			gmLog2.log_stack_trace()
			try:
				curs_close()
				conn_rollback()
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
				raise
			raise
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	conn_commit()
	conn_close()

	return (data, col_idx)
# =======================================================================
# connection handling API
# -----------------------------------------------------------------------
class cConnectionPool(psycopg2.pool.PersistentConnectionPool):
	"""
	GNUmed database connection pool.

	Extends psycopg2's PersistentConnectionPool with
	a custom _connect() function. Supports one connection
	per thread - which also ties it to one particular DSN.
	"""
	#--------------------------------------------------
	def _connect(self, key=None):

		conn = get_raw_connection(dsn = self._kwargs['dsn'], verbose = self._kwargs['verbose'], readonly=True)

		conn.original_close = conn.close
		conn.close = _raise_exception_on_ro_conn_close

		if key is not None:
			self._used[key] = conn
			self._rused[id(conn)] = key
		else:
			self._pool.append(conn)

		return conn
	#--------------------------------------------------
	def shutdown(self):
		for conn_key in self._used.keys():
			_log.debug('closing pooled database connection, pool key: %s, backend PID: %s', conn_key, self._used[conn_key].get_backend_pid())
			self._used[conn_key].original_close()
# -----------------------------------------------------------------------
def get_raw_connection(dsn=None, verbose=False, readonly=True):
	"""Get a raw, unadorned connection.

	- this will not set any parameters such as encoding, timezone, datestyle
	- the only requirement is a valid DSN
	- hence it can be used for "service" connections
	  for verifying encodings etc
	"""
	# FIXME: support verbose
	if dsn is None:
		dsn = get_default_dsn()

	try:
		conn = dbapi.connect(dsn=dsn, connection_factory=psycopg2.extras.DictConnection)
	except dbapi.OperationalError, e:

		t, v, tb = sys.exc_info()
		try:
			msg = e.args[0]
		except (AttributeError, IndexError, TypeError):
			raise

		msg = unicode(msg, gmI18N.get_encoding(), 'replace')

		if msg.find('fe_sendauth') != -1:
			raise cAuthenticationError, (dsn, msg), tb

		if regex.search('user ".*" does not exist', msg) is not None:
			raise cAuthenticationError, (dsn, msg), tb

		if msg.find('uthenti') != -1:
			raise cAuthenticationError, (dsn, msg), tb

		raise

	_log.debug('new database connection, backend PID: %s, readonly: %s', conn.get_backend_pid(), readonly)

	# do first-time stuff
	global postgresql_version
	if postgresql_version is None:
		curs = conn.cursor()
		curs.execute ("""
			select
				(split_part(setting, '.', 1) || '.' || split_part(setting, '.', 2))::numeric as version
			from pg_settings
			where name='server_version'"""
		)
		postgresql_version = curs.fetchone()['version']
		_log.info('PostgreSQL version (numeric): %s' % postgresql_version)
		try:
			curs.execute("select pg_size_pretty(pg_database_size(current_database()))")
			_log.info('database size: %s', curs.fetchone()[0])
		except:
			pass
		if verbose:
			__log_PG_settings(curs=curs)
		curs.close()
		conn.commit()

	if _default_client_timezone is None:
		__detect_client_timezone(conn = conn)

	curs = conn.cursor()

	# set access mode
	if readonly:
		_log.debug('access mode [READ ONLY]')
		cmd = 'set session characteristics as transaction READ ONLY'
		curs.execute(cmd)
		cmd = 'set default_transaction_read_only to on'
		curs.execute(cmd)
	else:
		_log.debug('access mode [READ WRITE]')
		cmd = 'set session characteristics as transaction READ WRITE'
		curs.execute(cmd)
		cmd = 'set default_transaction_read_only to off'
		curs.execute(cmd)

	curs.close()
	conn.commit()

	conn.is_decorated = False

	return conn
# =======================================================================
def get_connection(dsn=None, readonly=True, encoding=None, verbose=False, pooled=True):
	"""Get a new connection.

	This assumes the locale system has been initialzied
	unless an encoding is specified.
	"""
	# FIXME: support pooled on RW, too
	# FIXME: for now, support the default DSN only
	if pooled and readonly and (dsn is None):
		global __ro_conn_pool
		if __ro_conn_pool is None:
			__ro_conn_pool = cConnectionPool (
				minconn = 1,
				maxconn = 2,
				dsn = dsn,
				verbose = verbose
			)
		conn = __ro_conn_pool.getconn()
	else:
		conn = get_raw_connection(dsn=dsn, verbose=verbose, readonly=False)

	if conn.is_decorated:
		return conn

	if encoding is None:
		encoding = _default_client_encoding
	if encoding is None:
		encoding = gmI18N.get_encoding()
		_log.warning('client encoding not specified')
		_log.warning('the string encoding currently set in the active locale is used: [%s]' % encoding)
		_log.warning('for this to work properly the application MUST have called locale.setlocale() before')

	# set connection properties
	# 1) client encoding
	_log.debug('client string encoding [%s]' % encoding)
	try:
		conn.set_client_encoding(encoding)
	except dbapi.OperationalError:
		t, v, tb = sys.exc_info()
		if str(v).find("can't set encoding to") != -1:
			raise cEncodingError, (encoding, v), tb
		raise

	# 2) transaction isolation level
	if readonly:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
		_log.debug('isolation level [read committed]')
	else:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
		_log.debug('isolation level [serializable]')

	curs = conn.cursor()

	# client time zone
	_log.debug('time zone [%s]' % _default_client_timezone)
	curs.execute(_sql_set_timezone, [_default_client_timezone])

	# datestyle
	# regarding DMY/YMD handling: since we force *input* to
	# ISO, too, the DMY/YMD setting is not needed
	_log.debug('datestyle [ISO]')
	cmd = "set datestyle to 'ISO'"
	curs.execute(cmd)

	# SQL inheritance mode
	_log.debug('sql_inheritance [on]')
	cmd = 'set sql_inheritance to on'
	curs.execute(cmd)

	# version string
	global postgresql_version_string
	if postgresql_version_string is None:
		curs.execute('select version()')
		postgresql_version_string = curs.fetchone()['version']
		_log.info('PostgreSQL version (string): "%s"' % postgresql_version_string)

	curs.close()
	conn.commit()

	conn.is_decorated = True

	return conn
#-----------------------------------------------------------------------
def shutdown():
	if __ro_conn_pool is None:
		return
	__ro_conn_pool.shutdown()
# ======================================================================
# internal helpers
#-----------------------------------------------------------------------
def __noop():
	pass
#-----------------------------------------------------------------------
def _raise_exception_on_ro_conn_close():
	raise TypeError(u'close() called on read-only connection')
#-----------------------------------------------------------------------
def sanity_check_time_skew(tolerance=60):
	"""Check server time and local time to be within
	the given tolerance of each other.

	tolerance: seconds
	"""
	_log.debug('maximum skew tolerance (seconds): %s', tolerance)

	cmd = u"select now() at time zone 'UTC'"
	conn = get_raw_connection(readonly=True)
	curs = conn.cursor()

	start = time.time()
	rows, idx = run_ro_queries(link_obj = curs, queries = [{'cmd': cmd}])
	end = time.time()
	client_now_as_utc = pydt.datetime.utcnow()

	curs.close()
	conn.commit()

	server_now_as_utc = rows[0][0]
	query_duration = end - start
	_log.info('server "now" (UTC): %s', server_now_as_utc)
	_log.info('client "now" (UTC): %s', client_now_as_utc)
	_log.debug('wire roundtrip (seconds): %s', query_duration)

	if query_duration > tolerance:
		_log.error('useless to check client/server time skew, wire roundtrip > tolerance')
		return False

	if server_now_as_utc > client_now_as_utc:
		real_skew = server_now_as_utc - client_now_as_utc
	else:
		real_skew = client_now_as_utc - server_now_as_utc

	_log.debug('client/server time skew: %s', real_skew)

	if real_skew > pydt.timedelta(seconds = tolerance):
		_log.error('client/server time skew > tolerance')
		return False

	return True
#-----------------------------------------------------------------------
def sanity_check_database_settings():
	"""Checks database settings.

	returns (status, message)
	status:
		0: no problem
		1: non-fatal problem
		2: fatal problem
	"""
	_log.debug('checking database settings')
	settings = {
		# setting: [expected value, risk, fatal?]
		u'allow_system_table_mods': [u'off', u'system breakage', False],
		u'check_function_bodies': [u'on', u'suboptimal error detection', False],
		u'default_transaction_read_only': [u'on', u'accidental database writes', False],
		u'fsync': [u'on', u'data loss/corruption', True],
		u'full_page_writes': [u'on', u'data loss/corruption', False],
		u'lc_messages': [u'C', u'suboptimal error detection', False],
		u'password_encryption': [u'on', u'breach of confidentiality', False],
		u'regex_flavor': [u'advanced', u'query breakage', False],
		u'synchronous_commit': [u'on', u'data loss/corruption', False],
		u'sql_inheritance': [u'on', u'query breakage, data loss/corruption', True]
	}

	from Gnumed.pycommon import gmCfg2
	_cfg = gmCfg2.gmCfgData()
	if _cfg.get(option = u'hipaa'):
		settings[u'log_connections'] = [u'on', u'non-compliance with HIPAA', True]
		settings[u'log_disconnections'] = [u'on', u'non-compliance with HIPAA', True]
	else:
		settings[u'log_connections'] = [u'on', u'non-compliance with HIPAA', None]
		settings[u'log_disconnections'] = [u'on', u'non-compliance with HIPAA', None]

	cmd = u"select name, setting from pg_settings where name in %(settings)s"
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'settings': tuple(settings.keys())}}])

	found_error = False
	found_problem = False
	msg = []
	for row in rows:
		if row[1] != settings[row[0]][0]:
			if settings[row[0]][2] is True:
				found_error = True
			elif settings[row[0]][2] is False:
				found_problem = True
			elif settings[row[0]][2] is None:
				pass
			else:
				_log.error(settings[row[0]])
				raise ValueError(u'invalid database configuration sanity check')
			msg.append(_(' option [%s]: %s') % (row[0], row[1]))
			msg.append(_('  risk: %s') % settings[row[0]][1])
			_log.warning('PG option [%s] set to [%s], expected [%s], risk: <%s>' % (row[0], row[1], settings[row[0]][0], settings[row[0]][1]))

	if found_error:
		return 2, u'\n'.join(msg)

	if found_problem:
		return 1, u'\n'.join(msg)

	return 0, u''
#------------------------------------------------------------------------
def __log_PG_settings(curs=None):
	# don't use any of the run_*()s since that might
	# create a loop if we fail here
	# FIXME: use pg_settings
	try:
		curs.execute(u'show all')
	except:
		_log.exception(u'cannot log PG settings (>>>show all<<< failed)')
		return False
	settings = curs.fetchall()
	if settings is None:
		_log.error(u'cannot log PG settings (>>>show all<<< did not return rows)')
		return False
	for setting in settings:
		_log.debug(u'PG option [%s]: %s', setting[0], setting[1])
	return True
# =======================================================================
def extract_msg_from_pg_exception(exc=None):

	try:
		msg = exc.args[0]
	except (AttributeError, IndexError, TypeError):
		return u'cannot extract message from exception'

	return unicode(msg, gmI18N.get_encoding(), 'replace')
# =======================================================================
class cAuthenticationError(dbapi.OperationalError):

	def __init__(self, dsn=None, prev_val=None):
		self.dsn = dsn
		self.prev_val = prev_val

	def __str__(self):
		_log.warning('%s.__str__() called', self.__class__.__name__)
		tmp = u'PostgreSQL: %sDSN: %s' % (self.prev_val, self.dsn)
		_log.error(tmp)
		return tmp.encode(gmI18N.get_encoding(), 'replace')

	def __unicode__(self):
		return u'PostgreSQL: %sDSN: %s' % (self.prev_val, self.dsn)

# =======================================================================
# custom psycopg2 extensions
# =======================================================================
class cEncodingError(dbapi.OperationalError):

	def __init__(self, encoding=None, prev_val=None):
		self.encoding = encoding
		self.prev_val = prev_val

	def __str__(self):
		_log.warning('%s.__str__() called', self.__class__.__name__)
		return 'PostgreSQL: %s\nencoding: %s' % (self.prev_val.encode(gmI18N.get_encoding(), 'replace'), self.encoding.encode(gmI18N.get_encoding(), 'replace'))

	def __unicode__(self):
		return u'PostgreSQL: %s\nencoding: %s' % (self.prev_val, self.encoding)

# -----------------------------------------------------------------------
# Python -> PostgreSQL
# -----------------------------------------------------------------------
class cAdapterPyDateTime(object):

	def __init__(self, dt):
		if dt.tzinfo is None:
			raise ValueError(u'datetime.datetime instance is lacking a time zone: [%s]' % _timestamp_template % dt.isoformat())
		self.__dt = dt

	def getquoted(self):
		return _timestamp_template % self.__dt.isoformat()

# ----------------------------------------------------------------------
class cAdapterMxDateTime(object):

	def __init__(self, dt):
		if dt.tz == '???':
			_log.info('[%s]: no time zone string available in (%s), assuming local time zone', self.__class__.__name__, dt)
		self.__dt = dt

	def getquoted(self):
		# under some locale settings the mx.DateTime ISO formatter
		# will insert "," into the ISO string,
		# while this is allowed per the ISO8601 spec PostgreSQL
		# cannot currently handle that,
		# so map those "," to "." to make things work:
		return mxDT.ISO.str(self.__dt).replace(',', '.')

# ----------------------------------------------------------------------
# PostgreSQL -> Python
# ----------------------------------------------------------------------

# We need this because some places once used time "zones"
# with true local time, IOW having seconds in the UTC offset.
# The Python datetime zone code cannot handle that, however,
# which makes psycopg2 fail when loading timestamps with such
# time zones from the backend ...
# So we (almost silently) drop the seconds and try again.
def convert_ts_with_odd_tz(string_value, cursor):
	#_log.debug('parsing [%s]' % string_value)
	try:
		return dbapi.DATETIME(string_value, cursor)
	except (dbapi.DataError,), exc:
		_log.error('unable to parse [%s]' % string_value)

		if string_value is None:
			raise

		if exc.message != "unable to parse time":
			raise

		_log.debug('unable to parse as <timestamp with time zone>')

		if regex.match('(\+|-)\d\d:\d\d:\d\d', string_value[-9:]) is None:
			raise

		if regex.match('-\d\d:\d\d:\d\d', string_value[-9:]) is not None:
			if string_value[-5:-3] != '00':
				_log.debug('psycopg2 versions < 2.0.8 may misinterpret this time zone: [%s]', string_value[-9:])

		# parsing doesn't succeed even if seconds
		# are ":00" so truncate in any case
		_log.debug('time zone with seconds detected (true local time ?): %s', string_value[-9:])
		truncated_string_value = string_value[:-3]
		_log.warning('truncating to [%s] and trying again', truncated_string_value)
		_log.warning('value will be off by %s seconds', string_value[-2:])
		return dbapi.DATETIME(truncated_string_value, cursor)


TIMESTAMPTZ_OID = 1184		# taken from PostgreSQL headers
if TIMESTAMPTZ_OID not in dbapi.DATETIME.values:
	raise ImportError('TIMESTAMPTZ_OID <%s> not in psycopg2.DATETIME.values [%s]' % (TIMESTAMPTZ_OID, dbapi.DATETIME.values))

DT_W_ODD_TZ = psycopg2.extensions.new_type((TIMESTAMPTZ_OID,), 'DT_W_ODD_TZ', convert_ts_with_odd_tz)
#psycopg2.extensions.register_type(DT_W_ODD_TZ)		# now done by psycopg2

#=======================================================================
#  main
#-----------------------------------------------------------------------

# make sure psycopg2 knows how to handle unicode ...
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2._psycopg.UNICODEARRAY)

# properly adapt *tuples* into (a, b, c, ...) for
# "where ... IN (...)" queries
# but only needed/possible in psycopg2 < 2.0.6
try:
	psycopg2.extensions.register_adapter(tuple, psycopg2.extras.SQL_IN)
except AttributeError:
	pass

# do NOT adapt *lists* to "... IN (*) ..." syntax because we want
# them adapted to "... ARRAY()..." so we can support PG arrays
#psycopg2.extensions.register_adapter(list, psycopg2.extras.SQL_IN)

# tell psycopg2 how to adapt datetime types with timestamps when locales are in use
psycopg2.extensions.register_adapter(pydt.datetime, cAdapterPyDateTime)
try:
	import mx.DateTime as mxDT
	psycopg2.extensions.register_adapter(mxDT.DateTimeType, cAdapterMxDateTime)
except ImportError:
	_log.warning('cannot import mx.DateTime')

#=======================================================================
if __name__ == "__main__":

	logging.basicConfig(level=logging.DEBUG)
	#--------------------------------------------------------------------
	def test_file2bytea():
		run_rw_queries(queries = [
			{'cmd': u'create table test_bytea (data bytea)'}
		])

		cmd = u'insert into test_bytea values (%(data)s::bytea)'
		try:
			file2bytea(query = cmd, filename = sys.argv[2])
		except:
			_log.exception('error')

		run_rw_queries(queries = [
			{'cmd': u'drop table test_bytea'}
		])
	#--------------------------------------------------------------------
	def test_get_connection():
		print "testing get_connection()"

		dsn = 'foo'
		try:
			conn = get_connection(dsn=dsn)
		except dbapi.OperationalError, e:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=any-doc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=any-doc password=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=True)

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=False)

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		encoding = 'foo'
		try:
			conn = get_connection(dsn=dsn, encoding=encoding)
		except cEncodingError:
			print "SUCCESS: get_connection(%s, %s) failed as expected" % (dsn, encoding)
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v
	#--------------------------------------------------------------------
	def test_exceptions():
		print "testing exceptions"

		try:
			raise cAuthenticationError('no dsn', 'no previous exception')
		except cAuthenticationError:
			t, v, tb = sys.exc_info()
			print t
			print v
			print tb

		try:
			raise cEncodingError('no dsn', 'no previous exception')
		except cEncodingError:
			t, v, tb = sys.exc_info()
			print t
			print v
			print tb
	#--------------------------------------------------------------------
	def test_ro_queries():
		print "testing run_ro_queries()"

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		conn = get_connection(dsn, readonly=True)

		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': u'select version()'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx
		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': u'select 1'}], return_data=True, get_col_idx=True)
		print data
		print idx

		curs = conn.cursor()

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'select version()'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'select 1'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx

		try:
			data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'selec 1'}], return_data=True, get_col_idx=True, verbose=True)
			print data
			print idx
		except psycopg2.ProgrammingError:
			print 'SUCCESS: run_ro_queries("selec 1") failed as expected'
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		curs.close()
	#--------------------------------------------------------------------
	def test_request_dsn():
		conn = get_connection()
		print conn
		conn.close()
	#--------------------------------------------------------------------
	def test_set_encoding():
		print "testing set_default_client_encoding()"

		enc = 'foo'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = ''
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'latin1'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'utf8'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'unicode'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'UNICODE'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v
	#--------------------------------------------------------------------
	def test_connection_pool():
		dsn = get_default_dsn()
		pool = cConnectionPool(minconn=1, maxconn=2, dsn=None, verbose=False)
		print pool
		print pool.getconn()
		print pool.getconn()
		print pool.getconn()
		print type(pool.getconn())
	#--------------------------------------------------------------------
	def test_list_args():
		dsn = get_default_dsn()
		conn = get_connection(dsn, readonly=True)
		curs = conn.cursor()
		curs.execute('select * from clin.clin_narrative where narrative = %s', ['a'])
	#--------------------------------------------------------------------
	def test_sanitize_pg_regex():
		tests = [
			['(', '\\(']
			, ['[', '\\[']
			, [')', '\\)']
		]
		for test in tests:
			result = sanitize_pg_regex(test[0])
			if result != test[1]:
				print 'ERROR: sanitize_pg_regex(%s) returned "%s", expected "%s"' % (test[0], result, test[1])
	#--------------------------------------------------------------------
	def test_is_pg_interval():
		status = True
		tests = [
			[None, True],		# None == NULL == succeeds !
			[1, True],
			['1', True],
			['abc', False]
		]

		if not is_pg_interval():
			print 'ERROR: is_pg_interval() returned "False", expected "True"'
			status = False

		for test in tests:
			result = is_pg_interval(test[0])
			if result != test[1]:
				print 'ERROR: is_pg_interval(%s) returned "%s", expected "%s"' % (test[0], result, test[1])
				status = False

		return status
	#--------------------------------------------------------------------
	def test_sanity_check_time_skew():
		sanity_check_time_skew()
	#--------------------------------------------------------------------
	def test_keyword_expansion():
		print "keywords, from database:"
		print get_text_expansion_keywords()
		print "keywords, cached:"
		print get_text_expansion_keywords()
		print "'$keyword' expands to:"
		print expand_keyword(keyword = u'$dvt')
	#--------------------------------------------------------------------
	def test_get_foreign_key_details():
		for row in get_foreign_keys2column (
			schema = u'dem',
			table = u'identity',
			column = u'pk'
		):
			print '%s.%s references %s.%s.%s' % (
				row['referencing_table'],
				row['referencing_column'],
				row['referenced_schema'],
				row['referenced_table'],
				row['referenced_column']
			)
	#--------------------------------------------------------------------
	def test_set_user_language():
		# (user, language, result, exception type)
		tests = [
			# current user
			[None, 'de_DE', True],
			[None, 'lang_w/o_tx', False],
			[None, None, True],
			# valid user
			['any-doc', 'de_DE', True],
			['any-doc', 'lang_w/o_tx', False],
			['any-doc', None, True],
			# invalid user
			['invalid user', 'de_DE', None],
			['invalid user', 'lang_w/o_tx', False], # lang checking happens before user checking
			['invalid user', None, True]
		]
		for test in tests:
			try:
				result = set_user_language(user = test[0], language = test[1])
				if result != test[2]:
					print "test:", test
					print "result:", result, "expected:", test[2]
			except psycopg2.IntegrityError, e:
				if test[2] is None:
					continue
				print "test:", test
				print "expected exception"
				print "result:", e
	#--------------------------------------------------------------------
	def test_get_schema_revision_history():
		for line in get_schema_revision_history():
			print u' - '.join(line)
	#--------------------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		# run tests
		#test_file2bytea()
		#test_get_connection()
		#test_exceptions()
		#test_ro_queries()
		#test_request_dsn()
		#test_set_encoding()
		#test_connection_pool()
		#test_list_args()
		#test_sanitize_pg_regex()
		#test_is_pg_interval()
		#test_sanity_check_time_skew()
		#test_keyword_expansion()
		#test_get_foreign_key_details()
		#test_set_user_language()
		test_get_schema_revision_history()

# =======================================================================
# $Log: gmPG2.py,v $
# Revision 1.124  2010-01-11 22:02:49  ncq
# - properly log stack trace
#
# Revision 1.123  2010/01/06 14:38:17  ncq
# - log database size
#
# Revision 1.122  2009/12/21 15:02:18  ncq
# - fix typo
#
# Revision 1.121  2009/12/03 17:46:37  ncq
# - somewhat better logging in run_rw_queries
#
# Revision 1.120  2009/12/01 22:06:22  ncq
# - adjust v12 hash
#
# Revision 1.119  2009/11/19 15:06:50  ncq
# - add 0.6/v12 client/server mapping and database hash
#
# Revision 1.118  2009/11/06 15:08:13  ncq
# - expect check-function-bodies to be on
#
# Revision 1.117  2009/09/01 22:24:35  ncq
# - better comment
#
# Revision 1.116  2009/08/24 20:11:27  ncq
# - bump db version
# - fix tag creation
# - provider inbox:
# 	enable filter-to-active-patient,
# 	listen to new signal,
# 	use cInboxMessage class
# - properly constrain LOINC phrasewheel SQL
# - include v12 scripts in release
# - install arriba jar to /usr/local/bin/
# - check for table existence in audit schema generator
# - include dem.message inbox with additional generic signals
#
# Revision 1.115  2009/07/30 12:02:30  ncq
# - better error handling
#
# Revision 1.114  2009/07/23 16:32:01  ncq
# - get_current_user_language
#
# Revision 1.113  2009/07/02 20:48:24  ncq
# - log creation/closure of connections with PID
#
# Revision 1.112  2009/06/29 15:01:33  ncq
# - better wording re time zones
#
# Revision 1.111  2009/06/11 13:03:52  ncq
# - add proper hash for v11
#
# Revision 1.110  2009/06/04 16:26:22  ncq
# - normalize login.host
#
# Revision 1.109  2009/05/24 16:28:06  ncq
# - better output
#
# Revision 1.108  2009/05/22 11:00:47  ncq
# - gm_schema_revision -> gm.schema_revision
#
# Revision 1.107  2009/04/03 09:34:26  ncq
# - bump DB version
#
# Revision 1.106  2009/03/18 14:28:49  ncq
# - add 0.5 -> v11
# - properly handle unfound timezone
#
# Revision 1.105  2009/03/10 14:19:29  ncq
# - improve comment
#
# Revision 1.104  2009/02/24 10:19:21  ncq
# - improved TZ caster
#
# Revision 1.103  2009/02/20 15:42:51  ncq
# - warn on negative non-whole-number timezones as those are
#   currently wrongly calculated by psycopg2
#
# Revision 1.102  2009/02/18 13:45:04  ncq
# - narrow down exception handler for odd time zones
#
# Revision 1.101  2009/02/17 17:46:42  ncq
# - work around Python datetime not being able
#   to use time zones with seconds
#
# Revision 1.100  2009/02/17 08:00:46  ncq
# - get_keyword_expansion_candidates
#
# Revision 1.99  2009/02/10 18:39:11  ncq
# - test time zone for usability, not just for settability ...
# - get_schema_revision_history and use it
#
# Revision 1.98  2009/02/05 13:00:56  ncq
# - add v10 hashes
#
# Revision 1.97  2008/12/25 17:43:08  ncq
# - add exception msg extraction function
#
# Revision 1.96  2008/12/25 16:54:01  ncq
# - support around user db language handling
#
# Revision 1.95  2008/12/17 21:55:38  ncq
# - get_foreign_keys2column
# - only check HIPAA compliance when --hipaa was given
#
# Revision 1.94  2008/12/12 16:35:06  ncq
# - add HIPAA compliance to db settings checks, needs configurability
#
# Revision 1.93  2008/12/01 12:13:24  ncq
# - log exeption on __str__ in auth error so we have *something*
#   on encoding errors
#
# Revision 1.92  2008/11/20 18:45:10  ncq
# - modernize read/write conn mode setting
#
# Revision 1.91  2008/11/17 23:12:29  ncq
# - need to unicodify "$TZ"
#
# Revision 1.90  2008/10/22 12:08:17  ncq
# - improved query logging
#
# Revision 1.89  2008/10/12 15:40:46  ncq
# - cleanup
# - add mapping for client to database version
#
# Revision 1.88  2008/09/02 20:19:37  ncq
# - send_maintenance_*
#
# Revision 1.87  2008/08/21 10:21:40  ncq
# - update v9 hash
#
# Revision 1.86  2008/07/30 12:51:14  ncq
# - set_default_client_timezone needs to set _sql_set_timezone,
#   too, as noticed by Gour
#
# Revision 1.85  2008/07/24 13:58:08  ncq
# - import SQL error codes
#
# Revision 1.84  2008/07/17 21:31:00  ncq
# - missing arg for log.exception
#
# Revision 1.83  2008/07/13 17:15:30  ncq
# - update v9 database hash
#
# Revision 1.82  2008/07/13 16:04:54  ncq
# - use views when handling keyword expansions
# - add/delete/edit_text_expansion,
#
# Revision 1.81  2008/07/10 19:52:50  ncq
# - add expansion keyword functions with tests
#
# Revision 1.80  2008/06/24 16:54:20  ncq
# - make v9 database hash known
#
# Revision 1.79  2008/06/15 20:32:46  ncq
# - improve sanitize_pg_regex
#
# Revision 1.78  2008/06/13 10:32:55  ncq
# - better time zone detection logging
#
# Revision 1.77  2008/05/31 17:45:03  ncq
# - log other sorts of time zone errors, too
#
# Revision 1.76  2008/05/19 15:55:01  ncq
# - some cleanup
# - redo timezone detection since numeric timezones will do the right
#   thing *now* but will not allow for DST boundary crossing detection
#   and correction, so try to find a TZ name first, but fallback to
#   numeric offset if no name is found and verifiable against PostgreSQL
# - don't close() RO conns and raise an error if we do (unless we
#   *know* what we are doing)
#
# Revision 1.75  2008/04/11 12:21:59  ncq
# - support link_obj in get_child_tables()
#
# Revision 1.74  2008/03/20 15:29:13  ncq
# - sanity_check_time_skew() and test
#
# Revision 1.73  2008/03/11 16:59:54  ncq
# - push readonly setting down into get_raw_connection() so callers
#   can now decide what to request since default transactions are
#   readonly now
# - add file2bytea() test
#
# Revision 1.72  2008/03/06 21:24:02  ncq
# - add shutdown() code
#
# Revision 1.71  2008/03/02 11:26:25  ncq
# - cleanup
#
# Revision 1.70  2008/02/25 17:32:50  ncq
# - improve database settings sanity checks
#
# Revision 1.69  2008/01/14 20:29:16  ncq
# - improve exception type detection in get_raw_connection()
#
# Revision 1.68  2008/01/13 01:15:58  ncq
# - remove faulty flush()
#
# Revision 1.67  2008/01/07 19:51:04  ncq
# - better comments
# - some cleanup
# - bump db version
# - add __unicode__ to exceptions
# - improve test suite
#
# Revision 1.66  2007/12/26 18:34:53  ncq
# - check for lc_messages being C
#
# Revision 1.65  2007/12/12 16:17:15  ncq
# - better logger names
#
# Revision 1.64  2007/12/11 15:38:11  ncq
# - use std logging
#
# Revision 1.63  2007/12/06 13:07:19  ncq
# - add v8 schema hash
#
# Revision 1.62  2007/12/04 16:14:24  ncq
# - use gmAuthWidgets
#
# Revision 1.61  2007/12/04 15:11:20  ncq
# - sanity_check_database_settings()
# - force sql_inheritance to on after connect
#
# Revision 1.60  2007/11/09 14:39:10  ncq
# - log schema dump if verbose on failed version detection
#
# Revision 1.59  2007/10/25 16:41:30  ncq
# - is_pg_interval() + test
#
# Revision 1.58  2007/10/22 12:37:59  ncq
# - default db change
#
# Revision 1.57  2007/09/24 18:29:42  ncq
# - select 1,2; will return two columns with the same name !
#   hence, mapping names to column indices in a dict will not work :-(
#   fix breakage but don't really support it, either
#
# Revision 1.56  2007/09/18 22:53:26  ncq
# - enhance file2bytea to accept conn argument
#
# Revision 1.55  2007/09/17 21:46:28  ncq
# - make hash for v7 known
#
# Revision 1.54  2007/08/31 14:28:29  ncq
# - improved docs
#
# Revision 1.53  2007/08/08 21:25:39  ncq
# - improve bytea2file()
#
# Revision 1.52  2007/07/22 09:03:33  ncq
# - bytea2file(_object)()
# - file2bytea()
#
# Revision 1.51  2007/07/03 15:53:50  ncq
# - import re as regex
# - sanitize_pg_regex() and test
#
# Revision 1.50  2007/06/28 12:35:38  ncq
# - optionalize SQL IN tuple adaptation as it's now builtin to 0.2.6 psycopg2
#
# Revision 1.49  2007/06/15 10:24:24  ncq
# - add a test to the test suite
#
# Revision 1.48  2007/06/12 16:02:12  ncq
# - fix case when there are no args for execute()
#
# Revision 1.47  2007/06/11 20:24:18  ncq
# - bump database version
#
# Revision 1.46  2007/05/07 16:45:12  ncq
# - add v6 schema hash
#
# Revision 1.45  2007/05/07 16:28:34  ncq
# - use database maintenance functions in schema "gm"
#
# Revision 1.44  2007/04/27 13:19:58  ncq
# - get_schema_structure()
#
# Revision 1.43  2007/04/02 18:36:17  ncq
# - fix comment
#
# Revision 1.42  2007/04/02 14:31:17  ncq
# - v5 -> v6
#
# Revision 1.41  2007/04/01 15:27:09  ncq
# - safely get_encoding()
#
# Revision 1.40  2007/03/26 16:08:06  ncq
# - added v5 hash
#
# Revision 1.39  2007/03/08 11:37:24  ncq
# - simplified gmLogin
# - log PG settings on first connection if verbose
#
# Revision 1.38  2007/03/01 14:05:53  ncq
# - rollback in run_ro_queries() even if no error occurred such that
#   we don't stay IDLE IN TRANSACTION
#
# Revision 1.37  2007/03/01 14:03:53  ncq
# - in run_ro_queries() we now need to rollback failed transactions due to
#   the connections being pooled - or else abort state could carry over into
#   the next use of that connection - since transactions aren't really
#   in need of ending
#
# Revision 1.36  2007/02/19 15:00:53  ncq
# - restrict pooling to the default DSN, too
#
# Revision 1.35  2007/02/18 16:56:21  ncq
# - add connection pool for read-only connections ...
#
# Revision 1.34  2007/02/06 12:11:25  ncq
# - gnumed_v5
#
# Revision 1.33  2007/01/24 11:03:55  ncq
# - add sslmode=prefer to DSN
#
# Revision 1.32  2007/01/23 14:03:14  ncq
# - add known v4 schema hash - backport from 0.2.4
#
# Revision 1.31  2007/01/17 13:26:02  ncq
# - note on MDY/DMY handling
# - slightly easier python datetime adaptation
#
# Revision 1.30  2007/01/16 12:45:21  ncq
# - properly import/adapt mx.DateTime
#
# Revision 1.29  2007/01/16 10:28:49  ncq
# - do not FAIL on mxDT timezone string being ??? as
#   it should then be assumed to be local time
# - use mx.DateTime.ISO.str() to include timestamp in output
#
# Revision 1.28  2007/01/04 22:51:10  ncq
# - change hash for unreleased v4
#
# Revision 1.27  2007/01/03 11:54:16  ncq
# - log successful schema hash, too
#
# Revision 1.26  2007/01/02 19:47:29  ncq
# - support (and use) <link_obj> in get_schema_version()
#
# Revision 1.25  2007/01/02 16:17:13  ncq
# - slightly improved logging
# - fix fatal typo in set_default_login()
# - add <link_obj> support to database_schema_compatible()
# - really apply end_tx to run_rw_queries !
#
# Revision 1.24  2006/12/29 16:25:35  ncq
# - add PostgreSQL version handling
#
# Revision 1.23  2006/12/27 16:41:15  ncq
# - make sure python datetime adapter does not put ',' into string
#
# Revision 1.22  2006/12/22 16:54:44  ncq
# - init gmDateTime if necessary
#
# Revision 1.21  2006/12/21 17:44:54  ncq
# - use gmDateTime.current_iso_timezone_*string* as that is ISO conformant
#
# Revision 1.20  2006/12/21 10:52:52  ncq
# - fix test suite
# - set default client encoding to "UTF8" which is more precise than "UNICODE"
# - use gmDateTime for timezone handling thereby fixing the time.daylight error
#
# Revision 1.19  2006/12/18 17:39:55  ncq
# - make v3 database have known hash
#
# Revision 1.18  2006/12/18 14:55:40  ncq
# - u''ify a query
#
# Revision 1.17  2006/12/15 15:23:50  ncq
# - improve database_schema_compatible()
#
# Revision 1.16  2006/12/12 13:14:32  ncq
# - u''ify queries
#
# Revision 1.15  2006/12/06 20:32:09  ncq
# - careful about port.strip()
#
# Revision 1.14  2006/12/06 16:06:30  ncq
# - cleanup
# - handle empty port def in make_psycopg2_dsn()
# - get_col_defs()
# - get_col_indices()
# - get_col_names()
# - table_exists()
#
# Revision 1.13  2006/12/05 13:58:45  ncq
# - add get_schema_version()
# - improve handling of known schema hashes
# - register UNICODEARRAY psycopg2 extension
#
# Revision 1.12  2006/11/24 09:51:16  ncq
# - whitespace fix
#
# Revision 1.11  2006/11/14 16:56:23  ncq
# - improved (and documented) rationale for registering SQL_IN adapter on tuples only
#
# Revision 1.10  2006/11/07 23:52:48  ncq
# - register our own adapters for mx.DateTime and datetime.datetime so
#   we can solve the "ss,ms" issue in locale-aware str(timestamp)
#
# Revision 1.9  2006/11/07 00:30:36  ncq
# - activate SQL_IN for lists only
#
# Revision 1.8  2006/11/05 17:03:26  ncq
# - register SQL_INI adapter for tuples and lists
#
# Revision 1.7  2006/10/24 13:20:07  ncq
# - fix get_current_user()
# - add default login handling
# - remove set_default_dsn() - now use set_default_login() which will create the DSN, too
# - slighly less verbose logging for log size sanity
#
# Revision 1.6  2006/10/23 13:22:38  ncq
# - add get_child_tables()
#
# Revision 1.5  2006/10/10 07:38:22  ncq
# - tighten checks on psycopg2 capabilities
#
# Revision 1.4  2006/10/08 09:23:40  ncq
# - default encoding UNICODE, not utf8
# - add database_schema_compatible()
# - smartify set_default_client_encoding()
# - support <verbose> in run_ro_queries()
# - non-fatally warn on non-unicode queries
# - register unicode type so psycopg2 knows how to deal with u''
# - improve test suite
#
# Revision 1.3  2006/09/30 11:57:48  ncq
# - document get_raw_connection()
#
# Revision 1.2  2006/09/30 11:52:40  ncq
# - factor out get_raw_connection()
# - reorder conecction customization in get_connection()
#
# Revision 1.1  2006/09/21 19:18:35  ncq
# - first psycopg2 version
#
#