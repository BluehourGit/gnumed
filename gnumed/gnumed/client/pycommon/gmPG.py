"""Broker for Postgres distributed backend connections.

@copyright: author
@license: GPL (details at http://www.gnu.org)
"""
# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmPG.py,v $
__version__ = "$Revision: 1.26 $"
__author__  = "H.Herb <hherb@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"

#python standard modules
import string, copy, os, sys, time

#gnumed specific modules
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	_ = lambda x:x
_log.Log(gmLog.lData, __version__)

import gmLoginInfo, gmExceptions

import gmCLI
if gmCLI.has_arg("--debug"):
	_query_logging_verbosity = 1
else:
	_query_logging_verbosity = 0
del gmCLI

#3rd party dependencies

# FIXME: this needs a better way of specifying which library to load
# add SQL-relay, too

# first, do we have the preferred postgres-python library available ?
try:
	import pyPgSQL
	_log.Log(gmLog.lData, 'pyPgSQL version: %s' % pyPgSQL.__version__)
	del pyPgSQL
	import pyPgSQL.PgSQL # try preferred backend library
	dbapi = pyPgSQL.PgSQL
	_isPGDB = 0
except ImportError:
	try:
		import psycopg # try Zope library
		dbapi = psycopg
		_isPGDB = 0
	except ImportError:
		try:
			# well, well, no such luck - fall back to stock pgdb library
			import pgdb # try standard Postgres binding
			dbapi = pgdb
			_isPGDB = 1
		except ImportError:
			print "Cannot find any Python module for connecting to the database server. Program halted."
			_log.LogException("No Python database adapter found.", sys.exc_info(), verbose=1)
			raise

# FIXME: DBMS should eventually be configurable
__backend = 'PostgreSQL'

_log.Log(gmLog.lInfo, 'DBMS [%s] via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (__backend, dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))

# check whether this adapter module suits our needs
assert(float(dbapi.apilevel) >= 2.0)
assert(dbapi.threadsafety > 0)
assert(dbapi.paramstyle == 'pyformat')

_listener_api = None

# default encoding for connections
_default_client_encoding = None

# default time zone for connections
# OR: mxDT.now().gmtoffset()
if time.daylight:
	tz = time.altzone
else:
	tz = time.timezone
# do some magic to convert Python's timezone to a valid ISO timezone
# is this safe or will it return things like 13.5 hours ?
_default_time_zone = "%+.1f" % (-tz / 3600.0)

#======================================================================
# a bunch of useful queries
#----------------------------------------------------------------------
QTablePrimaryKeyIndex = """
SELECT
	indkey
FROM
	pg_index
WHERE
	indrelid =
	(SELECT oid FROM pg_class WHERE relname = '%s');
"""

query_pkey_name = """
SELECT
	pga.attname
FROM
	(pg_attribute pga inner join pg_index pgi on (pga.attrelid=pgi.indrelid))
WHERE
	pga.attnum=pgi.indkey[0]
		and
	pgi.indisprimary is true
		and
	pga.attrelid=(SELECT oid FROM pg_class WHERE relname = %s)"""


#query_fkey_names = """
#SELECT
#	pg_trigger.*, pg_proc.proname, pg_class.relname, pg_type.typname
#FROM
#	pg_proc
#		INNER JOIN pg_trigger ON pg_proc.oid = pg_trigger.tgfoid
#		INNER JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
#		INNER JOIN pg_type ON pg_trigger.tgtype = pg_type.oid
#WHERE
#	pg_class.relname = %s
#"""

query_fkey_names = """
select tgargs from pg_trigger where
	tgname like 'RI%%'
		and
	tgrelid = (
		select oid from pg_class where relname=%s
	)
"""

#======================================================================
class ConnectionPool:
	"maintains a static dictionary of available database connections"

	# cached read-only connection objects
	__ro_conns = {}
	# maps service names to physical databases
	__service2db_map = {}
	# connections in use per service (for reference counting)
	__conn_use_count = {}
	#variable used to check whether a first connection has been initialized yet or not
	__is_connected = None
	# maps backend listening threads to database ids
	__listeners = {}
	# gmLoginInfo.LoginInfo instance
	__login = None
	#-----------------------------
	def __init__(self, login=None, encoding=None):
		"""parameter login is of type gmLoginInfo.LoginInfo"""
		# if login data is given: re-establish connections
		if login is not None:
			self.__disconnect()
		if ConnectionPool.__is_connected is None:
			self.SetFetchReturnsList()
			# only change encoding when also setting up connections
			if encoding is not None:
				_default_client_encoding = encoding
			ConnectionPool.__is_connected = self.__setup_default_ro_conns(login)
	#-----------------------------
	def __del__(self):
		pass
		# NOTE: do not kill listeners here which would mean to
		# kill them when we throw away *any* ConnectionPool
		# instance - not what we want
	#-----------------------------
	# connection API
	#-----------------------------
	def GetConnection(self, service = "default", readonly = 1, encoding = None, extra_verbose = None):
		"""Get a connection."""
		# use default encoding if none given
		if encoding is None:
			encoding = _default_client_encoding

		logininfo = self.GetLoginInfoFor(service)

		# either get a cached read-only connection
		if readonly:
#			_log.Log(gmLog.lData, "requesting RO connection to service [%s]" % service)
			if ConnectionPool.__ro_conns.has_key(service):
				try:
					ConnectionPool.__conn_use_count[service] += 1
				except KeyError:
					ConnectionPool.__conn_use_count[service] = 1
				conn = ConnectionPool.__ro_conns[service]
			else:
#				_log.Log(gmLog.lData, 'using service [default] instead of [%s]' % service)
				try:
					ConnectionPool.__conn_use_count['default'] += 1
				except KeyError:
					ConnectionPool.__conn_use_count['default'] = 1
				conn = ConnectionPool.__ro_conns['default']

		# or a brand-new read-write connection
		else:
			_log.Log(gmLog.lData, "requesting RW connection to service [%s]" % service)
			conn = self.__pgconnect(logininfo, readonly = 0, encoding = encoding)
			if conn is None:
				return None

		if extra_verbose:
			if dbapi == pyPgSQL.PgSQL:
				conn.conn.toggleShowQuery
			else:
				_log.Log(gmLog.lInfo, 'extra_verbose not supported by DB API adapter [%s]' % dbapi)

		return conn
	#-----------------------------
	def ReleaseConnection(self, service):
		"""decrease reference counter of active connection"""
		if ConnectionPool.__ro_conns.has_key(service):
			try:
				ConnectionPool.__conn_use_count[service] -= 1
			except:
				ConnectionPool.__conn_use_count[service] = 0
		else:
			try:
				ConnectionPool.__conn_use_count['default'] -= 1
			except:
				ConnectionPool.__conn_use_count['default'] = 0
	#-----------------------------
	def Connected(self):
		return ConnectionPool.__is_connected	
	#-----------------------------
	# notification API
	#-----------------------------
	def Listen(self, service, signal, callback):
		"""Listen to 'signal' from backend in an asynchronous thread.

		If 'signal' is received from database 'service', activate
		the 'callback' function"""
		# FIXME: error handling

		# lazy import of gmBackendListener
		if _listener_api is None:
			if not _import_listener_engine():
				_log.Log(gmLog.lErr, 'cannot load backend listener code')
				return None

		# get physical database for service
		try:
			backend = ConnectionPool.__service2db_map[service]
		except KeyError:
			backend = 0
		_log.Log(gmLog.lData, "connecting notification [%s] from service [%s] (id %s) with callback %s" % (signal, service, backend, callback))
		# start thread if not listening yet,
		# but only one per physical database
		if backend not in ConnectionPool.__listeners.keys():
			auth = self.GetLoginInfoFor(service)
			listener = _listener_api.BackendListener(
				service,
				auth.GetDatabase(),
				auth.GetUser(),
				auth.GetPassword(),
				auth.GetHost(),
				int(auth.GetPort())
			)
			ConnectionPool.__listeners[backend] = listener
		# actually start listening
		listener = ConnectionPool.__listeners[backend]
		listener.register_callback(signal, callback)
		return 1
	#-----------------------------
	def Unlisten(self, service, signal, callback):
		# get physical database for service
		try:
			backend = ConnectionPool.__service2db_map[service]
		except KeyError:
			backend = 0
		_log.Log(gmLog.lData, "disconnecting notification [%s] from service [%s] (id %s) from callback %s" % (signal, service, backend, callback))
		if backend not in ConnectionPool.__listeners.keys():
			return 1
		listener = ConnectionPool.__listeners[backend]
		listener.unregister_callback(signal, callback)
	#-----------------------------
	def StopListener(self, service):
		try:
			backend = self.__service2db_map[service]
		except KeyError:
			_log.Log(gmLog.lWarn, 'cannot stop listener on backend [%s]' % backend)
			return None
		try:
			ConnectionPool.__listeners[backend].stop_thread()
			del ConnectionPool.__listeners[backend]
		except:
			_log.LogException('cannot stop listener on backend [%s]' % backend, sys.exc_info(), verbose = 0)
			return None
		return 1
	#-----------------------------
	def StopListeners(self):
		for backend in ConnectionPool.__listeners.keys():
			try:
				ConnectionPool.__listeners[backend].stop_thread()
				del ConnectionPool.__listeners[backend]
			except:
				_log.LogException('cannot stop listener on backend [%s]' % backend, sys.exc_info(), verbose = 0)
		return 1
	#-----------------------------
	# misc API
	#-----------------------------
	def GetAvailableServices(self):
		"""list all distributed services available on this system
		(according to configuration database)"""
		return ConnectionPool.__ro_conns.keys()
	#-----------------------------		
	def SetFetchReturnsList(self, on=1):
		"""when performance is crucial, let the db adapter
		return a list of lists instead a list of database objects.
		CAREFUL: this affects the whole connection!!!"""
		if dbapi is pyPgSQL.PgSQL:
			dbapi.fetchReturnsList = on
		else:
			_log.Log(gmLog.lWarn, 'not supported with DB-API [%s], please supply a patch' % dbapi)
	#-----------------------------		
	def GetLoginInfoFor(self, service, login = None):
		"""return login information for a particular service"""
		if login is None:
			dblogin = ConnectionPool.__login
		else:
			dblogin = copy.deepcopy(login)
		# if service not mapped, return default login information
		try:
			srvc_id = ConnectionPool.__service2db_map[service]
		except KeyError:
			return dblogin
		# a service in the default database
		if srvc_id == 0:
			return dblogin
		# actually fetch parameters for db where service
		# is located from config DB
		cfg_db = ConnectionPool.__ro_conns['default']
		cursor = cfg_db.cursor()
		cmd = "select name, host, port, opt, tty from db where id = %s ;"
		if not run_query(cursor, None, cmd, srvc_id):
			_log.Log(gmLog.lPanic, 'cannot get login info for service [%s] with id [%s] from config database' % (service, srvc_id))
			_log.Log(gmLog.lPanic, 'make sure your service-to-database mappings are properly configured')
			_log.Log(gmLog.lWarn, 'trying to make do with default login parameters')
			return dblogin
		auth_data = cursor.fetchone()
		idx = get_col_indices(cursor)
		cursor.close()
		# substitute values into default login data
		try: # db name
			dblogin.SetDatabase(string.strip(auth_data[idx['name']]))
		except: pass
		try: # host name
			dblogin.SetHost(string.strip(auth_data[idx['host']]))
		except: pass
		try: # port
			dblogin.SetPort(auth_data[idx['port']])
		except: pass
		try: # backend options (not that I have any idea what we'd need them for, but hey :-)
			dblogin.SetOptions(string.strip(auth_data[idx['opt']]))
		except: pass
		try: # tty option (what's that, actually ?)
			dblogin.SetTTY(string.strip(auth_data[idx['tty']]))
		except:pass
		# and return what we thus got - which may very well be identical to the default login ...
		return dblogin			
	#-----------------------------
	# private methods
	#-----------------------------
	def __setup_default_ro_conns(self, login):
		"""Initialize connections to all servers."""
		if login is None and ConnectionPool.__is_connected is None:
			try:
				login = request_login_params()
			except:
				_log.LogException("Exception: Cannot connect to databases without login information !", sys.exc_info(), verbose=1)
				raise gmExceptions.ConnectionError("Can't connect to database without login information!")

		_log.Log(gmLog.lData, login.GetInfoStr())
		ConnectionPool.__login = login

		# connect to the configuration server
		cfg_db = self.__pgconnect(login, readonly=1, encoding=_default_client_encoding)
		if cfg_db is None:
			raise gmExceptions.ConnectionError, _('Cannot connect to configuration database with:\n\n[%s]') % login.GetInfoStr()

		# this is the default gnumed server now
		ConnectionPool.__ro_conns['default'] = cfg_db
		cursor = cfg_db.cursor()
		# document DB version
		cursor.execute("select version()")
		_log.Log(gmLog.lInfo, 'service [default/config] running on [%s]' % cursor.fetchone()[0])
		# preload all services with database id 0 (default)
		cmd = "select name from distributed_db"
		if not run_query(cursor, None, cmd):
			cursor.close()
			raise gmExceptions.ConnectionError("cannot load service names from configuration database")
		services = cursor.fetchall()
		for service in services:
			ConnectionPool.__service2db_map[service[0]] = 0

		# establish connections to all servers we need
		# according to configuration database
		cmd = "select * from config where profile=%s"
		if not run_query(cursor, None, cmd, login.GetProfile()):
			cursor.close()
			raise gmExceptions.ConnectionError("cannot load user profile [%s] from database" % login.GetProfile())
		databases = cursor.fetchall()
		dbidx = get_col_indices(cursor)

		# for all configuration entries that match given user and profile
		for db in databases:
			# - get symbolic name of distributed service
			cursor.execute("select name from distributed_db where id = %d" %  db[dbidx['ddb']])
			service = string.strip(cursor.fetchone()[0])
			# - map service name to id of real database
			_log.Log(gmLog.lData, "mapping service [%s] to DB ID [%s]" % (service, db[dbidx['db']]))
			ConnectionPool.__service2db_map[service] = db[dbidx['db']]
			# - init ref counter
			ConnectionPool.__conn_use_count[service] = 0
			dblogin = self.GetLoginInfoFor(service, login)
			# - update 'Database Broker' dictionary
			conn = self.__pgconnect(dblogin, readonly=1, encoding=_default_client_encoding)
			if conn is None:
				raise gmExceptions.ConnectionError, _('Cannot connect to database with:\n\n[%s]') % login.GetInfoStr()
			ConnectionPool.__ro_conns[service] = conn
			# - document DB version
			cursor.execute("select version()")
			_log.Log(gmLog.lInfo, 'service [%s] running on [%s]' % (service, cursor.fetchone()[0]))
		cursor.close()
		ConnectionPool.__is_connected = 1
		return ConnectionPool.__is_connected
	#-----------------------------
	def __pgconnect(self, login, readonly=1, encoding=None):
		"""connect to a postgres backend as specified by login object; return a connection object"""
		dsn = ""
		hostport = ""
		if _isPGDB:
			dsn, hostport = login.GetPGDB_DSN()
		else:
			dsn = login.GetDBAPI_DSN()
			hostport = "0"

		try:
			if _isPGDB:
				conn = dbapi.connect(dsn, host=hostport)
			else:
				conn = dbapi.connect(dsn)
		except StandardError:
			_log.LogException("database connection failed: DSN = [%s], host:port = [%s]" % (dsn, hostport), sys.exc_info(), verbose = 1)
			return None

		# set the default characteristics of our sessions
		curs = conn.cursor()
		# - client encoding
		if encoding in (None, ''):
			_log.Log(gmLog.lWarn, 'client encoding not specified, this may lead to data corruption in some cases')
		else:
			cmd = "set client_encoding to '%s'" % encoding
			if not run_query(curs, None, cmd):
				_log.Log(gmLog.lWarn, 'cannot set client_encoding on connection to [%s]' % encoding)
				_log.Log(gmLog.lWarn, 'not setting this may in some cases lead to data corruption')
		# - client time zone
#		cmd = "set session time zone interval '%s'" % _default_time_zone
		cmd = "set time zone '%s'" % _default_time_zone
		if not run_query(curs, None, cmd):
			_log.Log(gmLog.lErr, 'cannot set client time zone to [%s]' % _default_time_zone)
			_log.Log(gmLog.lWarn, 'not setting this will lead to incorrect dates/times')
		else:
			_log.Log (gmLog.lData, 'time zone set to [%s]' % _default_time_zone)
		# - datestyle
		# FIXME: add DMY/YMD handling
		cmd = "set datestyle to 'ISO'"
		if not run_query(curs, None, cmd):
			_log.Log(gmLog.lErr, 'cannot set client date style to ISO')
			_log.Log(gmLog.lWarn, 'you better use other means to make your server delivers valid ISO timestamps with time zone')
		# - transaction isolation level
		if readonly:
			isolation_level = 'READ COMMITTED'
		else:
			isolation_level = 'SERIALIZABLE'
		cmd = 'set session characteristics as transaction isolation level %s' % isolation_level
		if not run_query(curs, None, cmd):
			curs.close()
			conn.close()
			_log.Log(gmLog.lErr, 'cannot set connection characteristics to [%s]' % isolation_level)
			return None

		if readonly:
			access_mode = 'READ ONLY'
		else:
			access_mode = 'READ WRITE'
		_log.Log(gmLog.lData, "setting session to [%s] for %s@%s:%s" % (access_mode, login.GetUser(), login.GetHost(), login.GetDatabase()))
		cmd = 'set session characteristics as transaction %s' % access_mode
		if not run_query(curs, 0, cmd):
			_log.Log(gmLog.lErr, 'cannot set connection characteristics to [%s]' % access_mode)
			# FIXME: once 7.4 is minimum, close connection and return None

		conn.commit()
		curs.close()
		return conn
	#-----------------------------
	def __disconnect(self, force_it=0):
		"""safe disconnect (respecting possibly active connections) unless the force flag is set"""
		# are we connected at all?
		if ConnectionPool.__is_connected is None:
			# just in case
			ConnectionPool.__ro_conns.clear()
			return
		# stop all background threads
		for backend in ConnectionPool.__listeners.keys():
			ConnectionPool.__listeners[backend].stop_thread()
			del ConnectionPool.__listeners[backend]
		# disconnect from all databases
		for key in ConnectionPool.__ro_conns.keys():
			# check whether this connection might still be in use ...
			if ConnectionPool.__conn_use_count[key] > 0 :
				# unless we are really mean
				if force_it == 0:
					# let the end user know that shit is happening
					raise gmExceptions.ConnectionError, "Attempting to close a database connection that is still in use"
			else:
				# close the connection
				ConnectionPool.__ro_conns[key].close()

		# clear the dictionary (would close all connections anyway)
		ConnectionPool.__ro_conns.clear()
		ConnectionPool.__is_connected = None

#---------------------------------------------------
# database helper functions
#---------------------------------------------------
def descriptionIndex(cursordescription):
	"""returns a dictionary of row atribute names and their row indices"""
	i=0
	dict={}
	for d in cursordescription:
		dict[d[0]] = i
		i+=1
	return dict
#---------------------------------------------------
def dictResult(cursor, fetched=None):
	"returns the all rows fetchable by the cursor as dictionary (attribute:value)"
	if fetched is None:
		fetched = cursor.fetchall()
	attr = fieldNames(cursor)
	dictres = []
	for f in fetched:
		dict = {}
		i=0
		for a in attr:
			dict[a]=f[i]
			i+=1
		dictres.append(dict)
	return dictres
#---------------------------------------------------
def fieldNames(cursor):
	"returns the attribute names of the fetched rows in natural sequence as a list"
	names=[]
	for d in cursor.description:
		names.append(d[0])
	return names
#---------------------------------------------------
def listDatabases(service='default'):
	"""list all accessible databases on the database backend of the specified service"""
	assert(__backend == 'PostgreSQL')
	return run_ro_query(service, "select * from pg_database")
#---------------------------------------------------
def listUserTables(service='default'):
	"""list the tables except all system tables of the specified service"""
	assert(__backend == 'PostgreSQL')
	return run_ro_query(service, "select * from pg_tables where tablename not like 'pg_%'")
#---------------------------------------------------
def listSystemTables(service='default'):
	"""list the system tables of the specified service"""
	assert(__backend == 'PostgreSQL')
	return run_ro_query(service, "select * from pg_tables where tablename like 'pg_%'")
#---------------------------------------------------
def listTables(service='default'):
	"""list all tables available in the specified service"""
	return run_ro_query(service, "select * from pg_tables")
#---------------------------------------------------
def _import_listener_engine():
	try:
		import gmBackendListener
	except ImportError:
		_log.LogException('cannot import gmBackendListener')
		return None
	global _listener_api
	_listener_api = gmBackendListener
	return 1
#---------------------------------------------------
def __log_PG_settings(curs=None):
	if _query_logging_verbosity < 1:
		return 1
	if curs is None:
		_log.Log(gmLog.lErr, 'need cursor to log PG settings')
		return None
	# don't use any of the run_*()s since that might
	# create a loop if we fail here
	try:
		curs.execute('show all')
	except:
		_log.LogException("cannot log PG settings (>>>show all<<< failed)", sys.exc_info(), verbose = 0)
		return None
	settings = curs.fetchall()
	if settings is None:
		_log.Log(gmLog.lErr, 'cannot log PG settings (>>>show all<<< did not return rows)')
		return None
	for setting in settings:
		_log.Log(gmLog.lData, "PG option [%s]: %s" % (setting[0], setting[1]))
	return 1
#---------------------------------------------------
def run_query(aCursor=None, verbosity=None, aQuery=None, *args):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to run query')
		return None
	if aQuery is None:
		_log.Log(gmLog.lErr, 'need query to run it')
		return None
	if verbosity is None:
		verbosity = _query_logging_verbosity

#	t1 = time.time()
	try:
		aCursor.execute(aQuery, *args)
	except:
		_log.LogException("query >>>%s<<< with args >>>%s<<< failed" % (aQuery, args), sys.exc_info(), verbose = verbosity)
		return None
#	t2 = time.time()
#	print t2-t1, aQuery
	return 1
#---------------------------------------------------
def noop(*args, **kargs):
	pass
#---------------------------------------------------
def run_commit (link_obj = None, queries = None, return_err_msg = None):
	"""Convenience function for running a transaction
	   that is supposed to get committed.

	- link_obj can be
	  - a cursor: rollback/commit must be done by the caller
	  - a connection: rollback/commit is handled
	  - a service name: rollback/commit is handled

	- queries is a list of (query, [args]) tuples
	  - executed as a single transaction

	- returns:
	  - a tuple (<value>, error) if return_err_msg is True
	  - a scalar <value> if return_err_msg is False

	- <value> will be
	  - None: if any query failed
	  - 1: if all queries succeeded (also 0 queries)
      - data: if the last query returned rows
	"""
	# sanity checks
	if link_obj is None:
		raise TypeError, 'gmPG.run_commit(): link_obj must be of type service name, connection or cursor'
	if queries is None:
		raise TypeError, 'gmPG.run_commit(): forgot to pass in queries'
	if len(queries) == 0:
		_log.Log(gmLog.lWarn, 'no queries to execute ?!?')
		if return_err_msg:
			return (1, 'no queries to execute ?!?')
		return 1

	close_cursor = noop
	close_conn = noop
	commit = noop
	rollback = noop
	# is it a cursor ?
	if hasattr(link_obj, 'fetchone') and hasattr(link_obj, 'description'):
		curs = link_obj
	# is it a connection ?
	elif (hasattr(link_obj, 'commit') and hasattr(link_obj, 'cursor')):
		curs = link_obj.cursor()
		close_cursor = curs.close
		conn = link_obj
		commit = link_obj.commit
		rollback = link_obj.rollback
	# take it to be a service name then
	else:
		pool = ConnectionPool()
		conn = pool.GetConnection(link_obj, readonly = 0)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot connect to service [%s]' % link_obj)
			if return_err_msg:
				return (None, _('cannot connect to service [%s]') % link_obj)
			return None
		curs = conn.cursor()
		close_cursor = curs.close
		close_conn = conn.close
		commit = conn.commit
		rollback = conn.rollback
	# run queries
	for query, args in queries:
#		t1 = time.time()
		try:
			curs.execute (query, *args)
		except:
			rollback()
			exc_info = sys.exc_info()
			_log.LogException ("RW query >>>%s<<< with args >>>%s<<< failed on link [%s]" % (query[:250], str(args)[:250], link_obj), exc_info, verbose = _query_logging_verbosity)
			__log_PG_settings(curs)
			close_cursor()
			close_conn()
			if return_err_msg:
				typ, val, tb = exc_info
				tmp = string.replace(str(val), 'ERROR:', '')
				tmp = string.replace(tmp, 'ExecAppend:', '')
				tmp = string.strip(tmp)
				return (None, 'SQL: %s' % tmp)
			return None
#		t2 = time.time()
#		print t2-t1, query
		if _query_logging_verbosity == 1:
			_log.Log(gmLog.lData, '%s rows affected by >>>%s<<<' % (curs.rowcount, query))
	# did we get result rows in the last query ?
	data = None
	# now, the DB-API is ambigous about whether cursor.description
	# and cursor.rowcount apply to the most recent query in a cursor
	# (does that statement make any sense ?!?) or to the entire lifetime
	# of said cursor, pyPgSQL thinks the latter, hence we need to catch
	# exceptions when there's no data from the *last* query
	try:
		data = curs.fetchall()
		if _query_logging_verbosity == 1:
			_log.Log(gmLog.lData, 'last query returned %s rows' % curs.rowcount)
	except:
		if _query_logging_verbosity == 1:
			_log.Log(gmLog.lData, 'fetchall(): last query did not return rows')
		# something seems odd
		if curs.description is not None:
			if curs.rowcount > 0:
				_log.Log(gmLog.lData, 'there seem to be rows but fetchall() failed -- DB API violation ?')
				_log.Log(gmLog.lData, 'rowcount: %s, description: %s' % (curs.rowcount, curs.description))

	# clean up
	commit()
	close_cursor()
	close_conn()

	if data is None: status = 1
	else: status = data
	if return_err_msg: return (status, '')
	return status
#---------------------------------------------------
def run_ro_query(link_obj = None, aQuery = None, get_col_idx = None, *args):
	"""Runs a read-only query.

	- link_obj can be a service name, connection or cursor object

	- return status:
		- return data			if get_col_idx is None
		- return (data, idx)	if get_col_idx != None

	- if query fails: data is None
	- if query is not a row-returning SQL statement: data is None

	- data is a list of tuples [(w,x,y,z), (a,b,c,d), ...] where each tuple is a table row
	- idx is a map of column name to their position in the row tuples
		e.g. { 'name': 3, 'id':0, 'job_description': 2, 'location':1 }
		
		usage:  e.g. data[0][idx['name']] would return z from [(w,x,y,z ),(a,b,c,d)]
	
	"""
	# sanity checks
	if link_obj is None:
		raise TypeError, 'gmPG.run_ro_query(): link_obj must be of type service name, connection or cursor'
	if aQuery is None:
		raise TypeError, 'gmPG.run_ro_query(): forgot to pass in aQuery'

	close_cursor = noop
	close_conn = noop
	# is it a cursor ?
	if hasattr(link_obj, 'fetchone') and hasattr(link_obj, 'description'):
		curs = link_obj
	# is it a connection ?
	elif (hasattr(link_obj, 'commit') and hasattr(link_obj, 'cursor')):
		curs = link_obj.cursor()
		close_cursor = curs.close
	# take it to be a service name then
	else:
		pool = ConnectionPool()
		conn = pool.GetConnection(link_obj, readonly = 1)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot get connection to service [%s]' % link_obj)
			if get_col_idx is None:
				return None
			else:
				return None, None
		curs = conn.cursor()
		close_cursor = curs.close
		close_conn = pool.ReleaseConnection
#	t1 = time.time()
	# run the query
	try:
		curs.execute(aQuery, *args)
	except:
		_log.LogException("query >>>%s<<< with args >>>%s<<< failed on link [%s]" % (aQuery[:250], str(args)[:250], link_obj), sys.exc_info(), verbose = _query_logging_verbosity)
		__log_PG_settings(curs)
		close_cursor()
		close_conn(link_obj)
		if get_col_idx is None:
			return None
		else:
			return None, None
#	t2 = time.time()
#	print t2-t1, aQuery
	# and return the data, possibly including the column index
	if curs.description is None:
		data = None
		_log.Log(gmLog.lErr, 'query did not return rows')
	else:
		data = curs.fetchall()
	# can "close" before closing cursor since it just decrements the ref counter
	close_conn(link_obj)
	if get_col_idx:
		col_idx = get_col_indices(curs)
		close_cursor()
		return data, col_idx
	else:
		close_cursor()
		return data
#---------------------------------------------------
def get_col_indices(aCursor = None):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to get column indices')
		return None
	if aCursor.description is None:
		_log.Log(gmLog.lErr, 'no result description available: cursor unused or last query did not select rows')
		return None
	col_indices = {}
	col_index = 0
	for col_desc in aCursor.description:
		col_indices[col_desc[0]] = col_index
		col_index += 1
	return col_indices
#---------------------------------------------------
def get_pkey_name(aCursor = None, aTable = None):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to determine primary key')
		return None
	if aTable is None:
		_log.Log(gmLog.lErr, 'need table name for which to determine primary key')

	if not run_query(aCursor, None, query_pkey_name, aTable):
		_log.Log(gmLog.lErr, 'cannot determine primary key')
		return -1
	result = aCursor.fetchone()
	if result is None:
		return None
	return result[0]
#---------------------------------------------------
def get_fkey_defs(source, table):
	"""Returns a dictionary of referenced foreign keys.

	key = column name of this table
	value = (referenced table name, referenced column name) tuple
	"""
	manage_connection = 0
	close_cursor = 1
	# is it a cursor ?
	if hasattr(source, 'fetchone') and hasattr(source, 'description'):
		close_cursor = 0
		curs = source
	# is it a connection ?
	elif (hasattr(source, 'commit') and hasattr(source, 'cursor')):
		curs = source.cursor()
	# take it to be a service name then
	else:
		manage_connection = 1
		pool = ConnectionPool()
		conn = pool.GetConnection(source)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot get fkey names on table [%s] from source [%s]' % (table, source))
			return None
		curs = conn.cursor()

	if not run_query(curs, None, query_fkey_names, table):
		if close_cursor:
			curs.close()
		if manage_connection:
			pool.ReleaseConnection(source)
		_log.Log(gmLog.lErr, 'cannot get foreign keys on table [%s] from source [%s]' % (table, source))
		return None

	fks = curs.fetchall()
	if close_cursor:
		curs.close()
	if manage_connection:
		pool.ReleaseConnection(source)

	references = {}
	for fk in fks:
		fkname, src_table, target_table, tmp, src_col, target_col, tmp = string.split(fk[0], '\x00')
		references[src_col] = (target_table, target_col)

	return references
#---------------------------------------------------
def table_exists(source, table):
	"""Returns false or true.

	source: cursor, connection or GnuMed service name
	"""
	manage_connection = 0
	close_cursor = 1
	# is it a cursor ?
	if hasattr(source, 'fetchone') and hasattr(source, 'description'):
		close_cursor = 0
		curs = source
	# is it a connection ?
	elif (hasattr(source, 'commit') and hasattr(source, 'cursor')):
		curs = source.cursor()
	# take it to be a service name then
	else:
		manage_connection = 1
		pool = ConnectionPool()
		conn = pool.GetConnection(source)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot check for table [%s] in source [%s]' % (table, source))
			return None
		curs = conn.cursor()

	cmd = "SELECT exists(select oid FROM pg_class where relname = %s)"
	if not run_query(curs, None, cmd, table):
		if close_cursor:
			curs.close()
		if manage_connection:
			pool.ReleaseConnection(source)
		_log.Log(gmLog.lErr, 'cannot check for table [%s] in source [%s]' % (table, source))
		return None

	exists = curs.fetchone()[0]
	if close_cursor:
		curs.close()
	if manage_connection:
		pool.ReleaseConnection(source)

	return exists
#---------------------------------------------------
def add_housekeeping_todo(
	reporter='$RCSfile: gmPG.py,v $ $Revision: 1.26 $',
	receiver='DEFAULT',
	problem='lazy programmer',
	solution='lazy programmer',
	context='lazy programmer',
	category='lazy programmer'
):
	queries = []
	cmd = "insert into housekeeping_todo (reported_by, reported_to, problem, solution, context, category) values (%s, %s, %s, %s, %s, %s)"
	queries.append((cmd, [reporter, receiver, problem, solution, context, category]))
	cmd = "select currval('housekeeping_todo_pk_seq')"
	queries.append((cmd, []))
	result, err = run_commit('historica', queries, 1)
	if result is None:
		_log.Log(gmLog.lErr, err)
		return (None, err)
	return (1, result[0][0])
#---------------------------------------------------
#---------------------------------------------------
def getBackendName():
	return __backend
#---------------------------------------------------
def set_default_client_encoding(encoding = None):
	if encoding is not None:
		_log.Log(gmLog.lInfo, 'setting default client encoding to [%s]' % encoding)
		global _default_client_encoding
		_default_client_encoding = encoding
		return 1
	return None
#===================================================
def __prompted_input(prompt, default=None):
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#---------------------------------------------------
def __request_login_params_tui():
	"""text mode request of database login parameters
	"""
	import getpass
	login = gmLoginInfo.LoginInfo('', '', '')

	print "\nPlease enter the required login parameters:"
	try:
		host = __prompted_input("host [localhost]: ", 'localhost')
		database = __prompted_input("database [gnumed]: ", 'gnumed')
		user = __prompted_input("user name: ", '')
		password = getpass.getpass("password (not shown): ")
		port = __prompted_input("port [5432]: ", 5432)
	except KeyboardInterrupt:
		_log.Log(gmLog.lWarn, "user cancelled text mode login dialog")
		print "user cancelled text mode login dialog"
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))

	login.SetInfo(user, password, dbname=database, host=host, port=port)
	return login
#---------------------------------------------------
def __request_login_params_gui_wx():
	"""GUI (wx) input request for database login parameters.

	Returns gmLoginInfo.LoginInfo object
	"""
	import wxPython.wx
	# the next statement will raise an exception if wxPython is not loaded yet
	sys.modules['wxPython']
	# OK, wxPython was already loaded. But has the main Application instance
	# been initialized yet ? if not, the exception will kick us out
	if wxPython.wx.wxGetApp() is None:
		raise gmExceptions.NoGuiError(_("The wx GUI framework hasn't been initialized yet!"))

	# Let's launch the login dialog
	# if wx was not initialized /no main App loop, an exception should be raised anyway
	import gmLoginDialog
	dlg = gmLoginDialog.LoginDialog(None, -1, png_bitmap = 'bitmaps/gnumedlogo.png')
	dlg.ShowModal()
	login = dlg.panel.GetLoginInfo()
	dlg.Destroy()
	del gmLoginDialog

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
			login = __request_login_params_gui_wx()
			return login
		except:
			pass
	# well, either we are on the console or
	# wxPython does not work, use text mode
	login = __request_login_params_tui()
	return login
#==================================================================
def __run_notifications_debugger():
	#-------------------------------
	def myCallback(**kwds):
		sys.stdout.flush()
		print "\n=== myCallback: got called ==="
		print kwds
	#-------------------------------

	dbpool = ConnectionPool()
	roconn = dbpool.GetConnection('default', extra_verbose=1)
	rocurs = roconn.cursor()

	# main shell loop
	print "PostgreSQL backend listener debug shell"
	while 1:
		print "---------------------------------------"
		typed = raw_input("=> ")
		args = typed.split(' ')
		# mothing typed ?
		if len(args) == 0:
			continue
		# help
		if args[0] in ('help', '?'):
			print "known commands"
			print "--------------"
			print "'listen' - start listening to a signal"
			print "'ignore' - stop listening to a signal"
			print "'send'   - send a signal"
			print "'quit', 'exit', 'done' - well, chicken out"
			continue
		# exit
		if args[0] in ('quit', 'exit', 'done'):
			break
		# signal stuff
		if args[0] in ("listen", "ignore", "send"):
			typed = raw_input("signal name: ")
			sig_names = typed.split(' ')
			# mothing typed ?
			if len(sig_names) == 0:
				continue
			if args[0] == "listen":
				dbpool.Listen('default', sig_names[0], myCallback)
			if args[0] == "ignore":
				dbpool.Unlisten('default', sig_names[0], myCallback)
			if args[0] == "send":
				cmd = 'NOTIFY "%s"' % sig_names[0]
				print "... running >>>%s<<<" % (cmd)
				if not run_query(rocurs, None, cmd):
					print "... error sending [%s]" % cmd
				roconn.commit()
			continue
		print 'unknown command [%s]' % typed

	# clean up
	print "please wait a second or two for threads to sync and die"
	dbpool.StopListener('default')
	rocurs.close()
	roconn.close()
	dbpool.ReleaseConnection('default')
#==================================================================
# Main - unit testing
#------------------------------------------------------------------
if __name__ == "__main__":
	_log.Log(gmLog.lData, 'DBMS "%s" via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (__backend, dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))

	print "Do you want to test the backend notification code ?"
	yes_no = raw_input('y/n: ')
	if yes_no == 'y':
		__run_notifications_debugger()
		sys.exit()

	dbpool = ConnectionPool()
	### Let's see what services are distributed in this system:
	print "\n\nServices available on this system:"
	print '-----------------------------------------'
	for service in dbpool.GetAvailableServices():
		print service
		dummy = dbpool.GetConnection(service)
		print "Available tables within service: ", service
		tables, cd = listUserTables(service)
		idx = descriptionIndex(cd)
		for table in tables:
			print "%s (owned by user %s)" % (table[idx['tablename']], table[idx['tableowner']])
		print "\n.......................................\n"

	### We have probably not distributed the services in full:
	db = dbpool.GetConnection('config')
	print "\n\nPossible services on any gnumed system:"
	print '-----------------------------------------'
	cursor = db.cursor()
	cursor.execute("select name from distributed_db")
	for service in  cursor.fetchall():
		print service[0]

	print "\nTesting convenience funtions:\n============================\n"
	print "Databases:\n============\n"
	res, descr = listDatabases()
	for r in res: print r
	print "\nTables:\n========\n"
	res, descr = listTables()
	for r in res: print r
	print "\nResult as dictionary\n==================\n"
	cur = db.cursor()
	cursor.execute("select * from db")
	d = dictResult(cursor)
	print d
	print "\nResult attributes\n==================\n"
	n = fieldNames(cursor)
	#-------------------------------
	def TestCallback():
		print "[Backend notification received!]"
	#-------------------------------
	print "\n-------------------------------------"
	print "Testing asynchronous notification for approx. 20 seconds"
	print "start psql in another window connect to gnumed"
	print "and type 'notify test'; if everything works,"
	print "a message [Backend notification received!] should appear\n"
	dbpool.Listen('default', 'test', TestCallback)
	time.sleep(20)
	dbpool.StopListener('default')
	print "Requesting write access connection:"
	con = dbpool.GetConnection('default', readonly=0)

#==================================================================
# $Log: gmPG.py,v $
# Revision 1.26  2004-09-06 18:56:16  ncq
# - improve inline docs
#
# Revision 1.25  2004/09/01 22:00:10  ncq
# - prompt for host first in textmode login dialog
#
# Revision 1.24  2004/07/17 20:54:50  ncq
# - remove user/_user workaround
#
# Revision 1.23  2004/06/20 16:54:55  ncq
# - restrict length of logged data in run_ro_query and run_commit
#
# Revision 1.22  2004/06/09 14:55:44  ncq
# - cleanup, typos
# - commented out connection lifeness check as per Syan's suggestion
# - adapt StopListener(s)() to gmBackendListener changes
#
# Revision 1.21  2004/05/16 14:32:07  ncq
# - cleanup
#
# Revision 1.20  2004/05/15 15:07:53  sjtan
#
# more comments on run_ro_query return values.
#
# Revision 1.19  2004/05/13 00:00:54  ncq
# - deescalate apparent DB API violation to lData as it seems very common and harmless
#
# Revision 1.18  2004/05/06 23:26:09  ncq
# - cleanup _setup_default_ro_conns()
#
# Revision 1.17  2004/04/28 03:25:01  ihaywood
# ensure sane timezone
#
# Revision 1.16  2004/04/27 22:43:28  ncq
# - with PG versions that support it failing queries now log the PG settings if --debug
#
# Revision 1.15  2004/04/27 22:03:27  ncq
# - we now set the datestyle to ISO on a hard connect()
#
# Revision 1.14  2004/04/26 21:59:46  ncq
# - add_housekeeping_todo()
#
# Revision 1.13  2004/04/24 13:17:02  ncq
# - logininfo() needs host= in request_login_params_tui()
#
# Revision 1.12  2004/04/22 13:14:38  ncq
# - cleanup
#
# Revision 1.11  2004/04/21 14:27:15  ihaywood
# bug preventing backendlistener working on local socket connections
#
# Revision 1.10  2004/04/19 12:46:24  ncq
# - much improved docs on run_commit()
 # - use noop() in run_commit()
# - fix rollback/commit behaviour in run_commit() - I wonder why it ever worked !?!
#
# Revision 1.9  2004/04/16 16:18:37  ncq
# - correctly check for returned rows in run_commit()
#
# Revision 1.8  2004/04/16 00:21:22  ncq
# - fix access to "data" in run_commit
#
# Revision 1.7  2004/04/15 23:38:07  ncq
# - debug odd rowcount vs description behaviour in row-returning commits
#
# Revision 1.6  2004/04/11 10:13:32  ncq
# - document run_ro_query API
# - streamline run_ro_query link_obj handling via noop()
# - __-ize prompted_input, req*tui, req*gui, run_not*debugger
#
# Revision 1.5  2004/04/08 23:42:13  ncq
# - set time zone during connect
#
# Revision 1.4  2004/03/27 21:40:01  ncq
# - upon first connect log PG version services run on
#
# Revision 1.3  2004/03/03 14:49:22  ncq
# - need to commit() before curs.close() in run_commit()
# - micro-optimize when to commit() [eg, link_obj not a cursor]
#
# Revision 1.2  2004/03/03 05:24:01  ihaywood
# patient photograph support
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.92  2004/02/18 13:43:33  ncq
# - fail with consistent return struct in run_commit()
#
# Revision 1.91  2004/01/22 23:41:06  ncq
# - add commented out query timing code
#
# Revision 1.90  2004/01/18 21:48:42  ncq
# - some important comments on what to do and not to do where
# - StopListeners()
# - remove dead code, cleanup
#
# Revision 1.89  2004/01/12 13:12:07  ncq
# - remove unhelpful phrases from PG < 7.4 error messages
#
# Revision 1.88  2004/01/09 23:50:25  ncq
# - run_commit() now returns the database level error
#   message if return_err_msg is true, default false
#
# Revision 1.87  2004/01/06 10:03:44  ncq
# - don't log use of RO conns anymore
#
# Revision 1.86  2003/12/29 16:31:10  uid66147
# - better logging, cleanup, better encoding handling
# - run_commit/ro_query() now accept either cursor, connection or service name
# - run_ro_query() now sanity checks if the query returned rows before calling fetchall()
#
# Revision 1.85  2003/11/20 00:48:45  ncq
# - re-added run_commit() returning rows if last DML returned rows
#
# Revision 1.84  2003/11/17 20:22:59  ncq
# - remove print()
#
# Revision 1.83  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.83
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# manual edit areas modelled after r.terry's specs.
# Revision 1.82  2003/11/07 20:34:04  ncq
# - more logging yet
#
# Revision 1.81  2003/11/04 00:19:24  ncq
# - GetConnection now toggles query printing via extra_verbose if dbapi=pyPgSql
#
# Revision 1.80  2003/10/26 15:07:47  ncq
# - in run_commit() if the last command returned rows (e.g. was a SELECT) return those rows to the caller
#
# Revision 1.79  2003/10/19 12:13:24  ncq
# - add table_exists() helper
#
# Revision 1.78  2003/09/30 19:08:31  ncq
# - add helper get_fkey_defs()
#
# Revision 1.77  2003/09/23 14:40:30  ncq
# - just some comments
#
# Revision 1.76  2003/09/23 12:09:27  ihaywood
# Karsten, we've been tripping over each other again
#
# Revision 1.75  2003/09/23 11:30:32  ncq
# - make run_ro_query return either a tuple or just the data depending on
#   the value of get_col_idx as per Ian's suggestion
#
# Revision 1.74  2003/09/23 06:43:45  ihaywood
# merging changes
#
# Revision 1.73  2003/09/23 06:41:27  ihaywood
# merging overlapped changes
#
# Revision 1.72  2003/09/22 23:31:44  ncq
# - remove some duplicate code
# - new style run_ro_query() use
#
# Revision 1.71  2003/09/21 12:47:48  ncq
# - iron out bugs
#
# Revision 1.70  2003/09/21 11:23:10  ncq
# - add run_ro_query() helper as suggested by Ian
#
# Revision 1.69  2003/09/16 22:41:11  ncq
# - get_pkey -> get_pkey_name
#
# Revision 1.68  2003/08/17 18:02:33  ncq
# - don't handle service "config" different from the others
# - add helper get_pkey()
#
# Revision 1.67  2003/08/13 14:07:43  ncq
# - removed some dead code
#
# Revision 1.66  2003/07/21 20:55:39  ncq
# - add helper set_default_client_encoding()
#
# Revision 1.65  2003/07/21 19:21:22  ncq
# - remove esc(), correct quoting needs to be left to DB-API module
# - set client_encoding on connections
# - consolidate GetConnection()/GetConnectionUnchecked()
#
# Revision 1.64  2003/07/09 15:44:31  ncq
# - our RO connections need to be READ COMMITTED so they can
#   see concurrent committed writes
#
# Revision 1.63  2003/07/05 12:55:58  ncq
# - improved exception reporting on failing queries
#
# Revision 1.62  2003/06/27 16:05:22  ncq
# - get_col_indices() helper to be used after a select
#
# Revision 1.61  2003/06/26 21:37:00  ncq
# - fatal->verbose, curs(cmd, arg) style
#
# Revision 1.60  2003/06/26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.59  2003/06/25 22:24:55  ncq
# - improve logging in run_query() depending on --debug (yuck !)
#
# Revision 1.58  2003/06/23 21:21:55  ncq
# - missing "return None" in run_query added
#
# Revision 1.57  2003/06/23 14:25:40  ncq
# - let DB-API do the quoting
#
# Revision 1.56  2003/06/21 10:53:03  ncq
# - correctly handle failing connections to cfg db
#
# Revision 1.55  2003/06/14 22:41:51  ncq
# - remove dead code
#
# Revision 1.54  2003/06/10 08:48:12  ncq
# - on-demand import of gmBackendListener so we can use gmPG generically
#   without having to have pyPgSQL available (as long as we don't use
#   notifications)
#
# Revision 1.53  2003/06/03 13:59:20  ncq
# - rewrite the lifeness check to look much cleaner
#
# Revision 1.52  2003/06/03 13:46:52  ncq
# - some more fixes to Syans connection liveness check in GetConnection()
#
# Revision 1.51  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.50  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.49  2003/06/01 12:21:25  ncq
# - re-enable listening to async backend notifies
# - what do you mean "reactivate when needed" ?! this is used *already*
#
# Revision 1.48  2003/06/01 01:47:32  sjtan
#
# starting allergy connections.
#
# Revision 1.47  2003/05/17 17:29:28  ncq
# - teach it new-style ro/rw connection handling, mainly __pgconnect()
#
# Revision 1.46  2003/05/17 09:49:10  ncq
# - set default transaction isolation level to serializable
# - prepare for 7.4 read-only/read-write support on connections
#
# Revision 1.45  2003/05/05 15:23:39  ncq
# - close cursor as early as possible in GetLoginInfoFor()
#
# Revision 1.44  2003/05/05 14:08:19  hinnef
# bug fixes in cursorIndex and getLoginInfo
#
# Revision 1.43  2003/05/03 14:15:31  ncq
# - sync and stop threads in __del__
#
# Revision 1.42  2003/05/01 15:01:10  ncq
# - port must be int in backend.listener()
# - remove printk()s
#
# Revision 1.41  2003/04/28 13:23:53  ncq
# - make backend listener shell work by committing after notifying
#
# Revision 1.40  2003/04/27 11:52:26  ncq
# - added notifications debugger shell in test environment
#
# Revision 1.39  2003/04/27 11:37:46  ncq
# - heaps of cleanup, __service_mapping -> __service2db_map, cdb -> cfg_db
# - merge _ListenTo and _StartListeningThread into Listen()
# - add Unlisten()
#
# Revision 1.38  2003/04/25 13:02:10  ncq
# - cleanup and adaptation to cleaned up backend listener code
#
# Revision 1.37  2003/04/08 08:58:00  ncq
# - added comment
#
# Revision 1.36  2003/04/07 00:40:45  ncq
# - now finally also support running on the console (not within a terminal window inside X)
#
# Revision 1.35  2003/03/27 21:11:26  ncq
# - audit for connection object leaks
#
# Revision 1.34  2003/02/24 23:17:32  ncq
# - moved some comments out of the way
# - convenience function run_query()
#
# Revision 1.33  2003/02/19 23:41:23  ncq
# - removed excessive printk's
#
# Revision 1.32  2003/02/07 14:23:48  ncq
# - == None -> is None
#
# Revision 1.31  2003/01/16 14:45:04  ncq
# - debianized
#
# Revision 1.30  2003/01/06 14:35:02  ncq
# - fail gracefully on not being able to connect RW
#
# Revision 1.29  2003/01/05 09:58:19  ncq
# - explicitely use service=default on empty Get/ReleaseConnection()
#
# Revision 1.28  2002/10/29 23:12:25  ncq
# - a bit of cleanup
#
# Revision 1.27  2002/10/26 16:17:13  ncq
# - more explicit error reporting
#
# Revision 1.26  2002/10/26 02:45:52  hherb
# error in name mangling for writeable connections fixed (persisting "_" prepended to user name when connection reused)
#
# Revision 1.25  2002/10/25 13:02:35  hherb
# FetchReturnsList now default on connection creation
#
# Revision 1.24  2002/10/20 16:10:46  ncq
# - a few bits here and there
# - cleaner logging
# - raise ImportError on failing to import a database adapter instead of dying immediately
#
# Revision 1.23  2002/09/30 16:20:30  ncq
# - wrap printk()s in <DEBUG>
#
# Revision 1.22  2002/09/30 15:48:16  ncq
# - fix dumb bug regarding assignment of local variable logininfo
#
# Revision 1.21  2002/09/30 08:26:57  ncq
# - a bit saner logging
#
# Revision 1.20  2002/09/29 14:39:44  ncq
# - cleanup, clarification
#
# Revision 1.19  2002/09/26 13:14:59  ncq
# - log version
#
# Revision 1.18  2002/09/19 18:07:48  hinnef
# fixed two bugs that prevented distributed services from working (HB)
#
# Revision 1.17  2002/09/15 13:20:17  hherb
# option to return results as list instead of result set objects added
#
# Revision 1.16  2002/09/10 07:44:29  ncq
# - added changelog keyword
#
# @change log:
#	25.10.2001 hherb first draft, untested
#	29.10.2001 hherb crude functionality achieved (works ! (sortof))
#	30.10.2001 hherb reference counting to prevent disconnection of active connections
#	==========================================================================
#	significant version change!
#	==========================================================================
#	08.02.2002 hherb made DB API 2.0 compatible.
#	01.09.2002 hherb pyPgSQL preferred adapter
#	01.09.2002 hherb writeable connections, start work on asynchronous part
