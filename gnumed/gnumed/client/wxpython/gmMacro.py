"""GnuMed macro primitives.

This module implements functions a macro can legally use.
"""
#FIXME: semaphore f�r Gui-Aktionen :-)

#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMacro.py,v $
__version__ = "$Revision: 1.11 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, random, types

from Gnumed.pycommon import gmLog, gmI18N, gmGuiBroker, gmExceptions
from Gnumed.business import gmPatient
from Gnumed.wxpython import gmGuiHelpers, gmPlugin

_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

import wxPython.wx as wx
#=====================================================================
class cMacroPrimitives:
	"""Functions a macro can legally use.

	An instance of this class is passed to the GnuMed scripting
	listener. Hence, all actions a macro can legally take must
	be defined in this class. Thus we achieve some screening for
	security and also thread safety handling.
	"""
	#-----------------------------------------------------------------
	def __init__(self, personality = None):
		if personality is None:
			raise gmExceptions.ConstructorError, 'must specify personality'
		self.__personality = personality
		self.__attached = 0
		self.__auth_cookie = None
		self._get_source_personality = None
	#-----------------------------------------------------------------
	# public API
	#-----------------------------------------------------------------
	def attach(self, personality = None):
		if self.__attached:
			_log.Log(gmLog.lErr, 'attach with [%s] rejected, already serving a client' % personality)
			return (0, _('attach rejected, already serving a client'))
		if personality != self.__personality:
			_log.Log(gmLog.lErr, 'rejecting attach with cookie [%s], only servicing [%s]' % (personality, self.__personality))
			return (0, _('attach with cookie [%s] rejected') % personality)
		self.__attached = 1
		self.__auth_cookie = str(random.random())
		return (1, self.__auth_cookie)
	#-----------------------------------------------------------------
	def detach(self, auth_cookie=None):
		if not self.__attached:
			return 1
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'rejecting detach() with cookie [%s]' % auth_cookie)
			return 0
		self.__attached = 0
		return 1
	#-----------------------------------------------------------------
	def force_detach(self):
		if not self.__attached:
			return 1
		msg = _(
			'Someone tries to forcibly break the existing\n'
			'controlling connection. This may or may not\n'
			'have legitimate reasons.\n\n'
			'Do you want to allow breaking the connection ?'
		)
		can_break_conn = wx.wxCallAfter(gmGuiHelpers.gm_show_question, msg, _('forced detach attempt'))
		if can_break_conn:
			self.__attached = 0
			return 1
		return 0
	#-----------------------------------------------------------------
	def version(self):
		return "%s $Revision: 1.11 $" % self.__class__.__name__
	#-----------------------------------------------------------------
	def raise_gnumed(self, auth_cookie = None):
		"""Raise ourselves to the top of the desktop."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'non-authenticated raise_gnumed()')
			return 0
		return "cMacroPrimitives.raise_gnumed() not implemented"
	#-----------------------------------------------------------------
	def get_loaded_plugins(self, auth_cookie = None):
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'non-authenticated get_loaded_plugins()')
			return 0
		gb = gmGuiBroker.GuiBroker()
		return gb['modules.gui'].keys()
	#-----------------------------------------------------------------
	def raise_plugin(self, auth_cookie = None, a_plugin = None):
		"""Raise a notebook plugin within GnuMed."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'non-authenticated raise_plugin()')
			return 0
		success = wx.wxCallAfter(gmPlugin.raise_plugin, a_plugin)
		if not success:
			return 0
		return 1
	#-----------------------------------------------------------------
	def lock_into_patient(self, auth_cookie = None, search_params = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'non-authenticated lock_into_patient()')
			return (0, _('rejected lock_into_patient(), not authenticated'))
		pat = gmPatient.gmCurrentPatient()
		if pat.is_locked():
			_log.Log(gmLog.lErr, 'patient is already locked')
			return (0, _('already locked into a patient'))
		searcher = gmPatient.cPatientSearcher_SQL()
		if type(search_params) == types.DictType:
			pat_id = searcher.get_patient_ids(search_dict=search_params)
		else:
			pat_id = searcher.get_patient_ids(search_term=search_params)
		if pat_id is None:
			return (0, _('error searching for patient with [%s]/%s') % (search_term, search_dict))
		if len(pat_id) == 0:
			return (0, _('no patient found for [%s]/%s') % (search_term, search_dict))
		# FIXME: let user select patient
		if len(pat_id) > 1:
			return (0, _('several matching patients found for [%s]/%s') % (search_term, search_dict))
		if not gmPatient.set_active_patient(pat_id[0][0]):
			return (0, _('cannot activate patient [%s] (%s/%s)') % (pat_id[0], search_term, search_dict))
		pat.lock()
		self.__pat_lock_cookie = str(random.random())
		return (1, self.__pat_lock_cookie)
	#-----------------------------------------------------------------
	def unlock_patient(self, auth_cookie = None, unlock_cookie = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'non-authenticated unlock_patient()')
			return (0, _('rejected unlock_patient, not authenticated'))
		pat = gmPatient.gmCurrentPatient()
		# we ain't locked anyways, so succeed
		if not pat.is_locked():
			return (1, '')
		# FIXME: ask user what to do about wrong cookie
		if unlock_cookie != self.__pat_lock_cookie:
			_log.Log(gmLog.lWarn, 'patient unlock request rejected due to wrong cookie [%s]' % unlock_cookie)
			return (0, 'patient unlock request rejected, wrong cookie provided')
		pat.unlock()
		return (1, '')
	#-----------------------------------------------------------------
	def assume_staff_identity(self, auth_cookie = None, staff_name = "Dr.Jekyll", staff_creds = None):
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.Log(gmLog.lErr, 'non-authenticated select_identity()')
			return 0
		return "cMacroPrimitives.assume_staff_identity() not implemented"
	#-----------------------------------------------------------------
	def wait_until_user_done():
		return 0
	#-----------------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------------
#=====================================================================
# main
#=====================================================================
if __name__ == '__main__':
	from Gnumed.pycommon import gmScriptingListener
	import xmlrpclib
	listener = gmScriptingListener.cScriptingListener(macro_executor = cMacroPrimitives(personality='unit test'), port=9999)

	s = xmlrpclib.ServerProxy('http://localhost:9999')
	print "should fail:", s.attach()
	print "should fail:", s.attach('wrong cookie')
	print "should work:", s.version()
	print "should fail:", s.raise_gnumed()
	print "should fail:", s.raise_plugin('test plugin')
	print "should fail:", s.lock_into_patient('kirk, james')
	print "should fail:", s.unlock_patient()
	status, conn_auth = s.attach('unit test')
	print "should work:", status, conn_auth
	print "should work:", s.version()
	print "should work:", s.raise_gnumed(conn_auth)
	status, pat_auth = s.lock_into_patient(conn_auth, 'kirk, james')
	print "should work:", status, pat_auth
	print "should fail:", s.unlock_patient(conn_auth, 'bogus patient unlock cookie')
	print "should work", s.unlock_patient(conn_auth, pat_auth)
	data = {'firstname': 'jame', 'lastnames': 'Kirk', 'gender': 'm'}
	status, pat_auth = s.lock_into_patient(conn_auth, data)
	print "should work:", status, pat_auth
	print "should work", s.unlock_patient(conn_auth, pat_auth)
	print s.detach('bogus detach cookie')
	print s.detach(conn_auth)
	del s

	listener.tell_thread_to_stop()
#=====================================================================
# $Log: gmMacro.py,v $
# Revision 1.11  2004-03-20 19:48:07  ncq
# - adapt to flat id list from get_patient_ids
#
# Revision 1.10  2004/03/20 17:54:18  ncq
# - lock_into_patient now supports dicts and strings
# - fix unit test
#
# Revision 1.9  2004/03/12 13:22:38  ncq
# - comment on semaphore for GUI actions
#
# Revision 1.8  2004/03/05 11:22:35  ncq
# - import from Gnumed.<pkg>
#
# Revision 1.7  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.6  2004/02/17 10:45:30  ncq
# - return authentication cookie from attach()
# - use that cookie in all RPCs
# - add assume_staff_identity()
#
# Revision 1.5  2004/02/12 23:57:22  ncq
# - now also use random cookie for attach/detach
# - add force_detach() with user feedback
# - add get_loaded_plugins()
# - implement raise_plugin()
#
# Revision 1.4  2004/02/05 23:52:05  ncq
# - remove spurious return 0
#
# Revision 1.3  2004/02/05 20:46:18  ncq
# - require attach() cookie for detach(), too
#
# Revision 1.2  2004/02/05 20:40:34  ncq
# - added attach()
# - only allow attach()ed clients to call methods
# - introduce patient locking/unlocking cookie
# - enhance unit test
#
# Revision 1.1  2004/02/05 18:10:44  ncq
# - actually minimally functional macro executor with test code
#
