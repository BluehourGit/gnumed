"""GnuMed clinical narrative business object.

"""
#============================================================
__version__ = "$Revision: 1.7 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (for details see http://gnu.org)'

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cDiag(gmClinItem.cClinItem):
	"""
		Represents one real diagnosis
	"""
	_cmd_fetch_payload = """
		select * from v_pat_diag where pk_diag=%s"""
	_cmds_store_payload = [
		"""select 1 from clin_diag where pk=%(pk_diag)s for update""",
		"""update clin_diag set
				laterality=%()s,
				laterality=%(laterality)s,
				is_chronic=%(is_chronic)s::boolean,
				is_active=%(is_active)s::boolean,
				is_definite=%(is_definite)s::boolean,
				is_significant=%(is_significant)s::boolean
			where pk=%(pk_diag)s""",
		"""select 1 from clin_narrative where pk=%(pk_diagnosis)s for update""",
		"""update clin_narrative set
				narrative=%(diagnosis)s
			where pk=%(pk_diagnosis)s"""
		]

	_updatable_fields = [
		'diagnosis',
		'laterality',
		'is_chronic',
		'is_active',
		'is_definite',
		'is_significant'
	]
	#--------------------------------------------------------
	def get_codes(self):
		"""
			Retrieves codes linked to *this* diagnosis
		"""
		# Note: caching won't work without having a mechanism
		# to evict the cache when the backend changes
		cmd = "select code, coding_system from v_pat_diag_codes where pk_diag=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self.pk_obj)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get codes linked to diagnosis [%s] (%s)' % (self._payload[self._idx['diagnosis']], self.pk_obj))
			return []
		return rows
	#--------------------------------------------------------
	def get_possible_codes(self):
		"""
			Retrieves codes linked to *any* diagnosis of this name
		"""
		# Note: caching won't work without a having a mechanism
		# to evict the cache when the backend changes
		cmd = "select code, coding_system from v_codes4diag where diagnosis=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['diagnosis']])
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get codes for diagnosis [%s]' % self._payload[self._idx['diagnosis']])
			return []
		return rows
	#--------------------------------------------------------
	def add_code(self, code=None, coding_system=None):
		"""
			Associates a code (from coding system) with this diagnosis.
		"""
		# insert new code
		queries = []
		cmd = """insert into lnk_code2diag (fk_diag, code, xfk_coding_system) values (%s, %s, %s)"""
		queries.append((cmd, [self._payload[self._idx['pk_diag']], code, coding_system]))
		result, msg = gmPG.run_commit('historica', queries, True)
		if result is None:
			return (False, msg)
		return (True, msg)
#============================================================
class cNarrative(gmClinItem.cClinItem):
	"""
		Represents one clinical free text entry
	"""
	_cmd_fetch_payload = """
		select * from v_pat_narrative where pk_narrative=%s"""
	_cmds_store_payload = [
		"""select 1 from clin_narrative where pk=%(pk)s for update""",
		"""update clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(date)s,
				is_rfe=%(is_rfe)s::boolean,
				is_aoe=%(is_aoe)s::boolean,
				soap_cat=lower(%(soap_cat))
			where pk=%(pk_narrative)s"""
		]

	_updatable_fields = [
		'narrative',
		'date',
		'is_rfe',
		'is_aoe',
		'soap_cat'
	]
	#--------------------------------------------------------
	def get_codes(self):
		"""
			Retrieves codes linked to *this* narrative
		"""
		# Note: caching won't work without having a mechanism
		# to evict the cache when the backend changes
		cmd = "select code, xfk_coding_system from lnk_code2narr where fk_narrative=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self.pk_obj)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get codes linked to narrative [%s]' % self.pk_obj)
			return []
		return rows
	#--------------------------------------------------------
	def add_code(self, code=None, coding_system=None):
		"""
			Associates a code (from coding system) with this narrative.
		"""
		# insert new code
		queries = []
		cmd = """insert into lnk_code2narr (fk_narrative, code, xfk_coding_system) values (%s, %s, %s)"""
		queries.append((cmd, [self.pk_obj, code, coding_system]))
		result, msg = gmPG.run_commit('historica', queries, True)
		if result is None:
			return (False, msg)
		return (True, msg)
#============================================================
class cRFE(gmClinItem.cClinItem):
	"""
		Represents one Reason For Encounter
	"""
	_cmd_fetch_payload = """
		select * from v_pat_rfe
		where pk_narrative=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_narrative where pk=%(pk_narrative)s for update""",
		"""update clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(clin_when)s
			where pk=%(pk_narrative)s"""
		]

	_updatable_fields = [
		'narrative',
		'clin_when'
	]
#============================================================
class cAOE(gmClinItem.cClinItem):
	"""
		Represents one Assessment Of Encounter

	"""
	_cmd_fetch_payload = """
		select * from v_pat_aoe
		where pk_narrative=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_narrative where pk=%(pk_narrative)s for update""",
		"""update clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(clin_when)s
			where pk=%(pk_narrative)s"""
		]

	_updatable_fields = [
		'narrative',
		'clin_when'
	]
	#--------------------------------------------------------
	def is_diagnosis(self):
		"""
			Checks if the AOE is a real diagosis
		"""
		# Note: caching is dangerous in absence of a cache invalidation mechanism
		try:
			self.__diagnosis
			loaded = True
		except:
			loaded = self.__load_diagnosis()
		if loaded:
			return True
		return False
	#--------------------------------------------------------
	def get_diagnosis(self):
		"""
			Returns diagnosis for this AOE
		"""
		# Note: caching is dangerous in absence of a cache invalidation mechanism
		try:
			self.__diagnosis
			loaded = True
		except:
			loaded = self.__load_diagnosis()
		if loaded:
			return self.__diagnosis
		return None
	#--------------------------------------------------------
	def __load_diagnosis(self):
		"""
			Fetches from backend diagnosis associated with this AOE
		"""
		self.__diagnosis = None
		queries = []
		vals = {'pk_narrative': self['pk_narrative']}
		cmd = "select distinct on (diagnosis) pk_diag from v_pat_diag where pk_narrative=%(pk_narrative)s"
		rows = gmPG.run_ro_query('historica', cmd, None, vals)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get diagnosis for AOE [%s]' % self.pk_obj)
			del self.__diagnosis
			return False
		if len(rows) > 0:
			try:
				self.__diagnosis = cDiag(aPK_obj = rows[0][0])
				return True
			except gmExceptions.ConstructorError:
				_log.Log(gmLog.lErr, 'cannot instantiate diagnosis [%s] for AOE [%s]' % (rows[0][0], self.pk_obj))
				del self.__diagnosis
				return False
		del self.__diagnosis
		return None
#============================================================
# convenience functions
#============================================================
def create_clin_narrative(narrative = None, soap_cat = None, episode_id=None, encounter_id=None):
	"""
		Creates a new clinical narrative entry
		
		narrative - free text clinical narrative
		soap_cat - soap category
		episode_id - episodes's primary key
		encounter_id - encounter's primary key
	"""
	# sanity check
	# 1) any of the args being None should fail the SQL code
	# 2) do episode/encounter belong to the patient ?
	cmd = """select id_patient from v_pat_episodes where pk_episode=%s 
				 union 
			 select pk_patient from v_pat_encounters where pk_encounter=%s"""
	rows = gmPG.run_ro_query('historica', cmd, None, episode_id, encounter_id)
	if (rows is None) or (len(rows) == 0):
		_log.Log(gmLog.lErr, 'error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (False, _('internal error, check log'))
	if len(rows) > 1:
		_log.Log(gmLog.lErr, 'episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
		return (False, _('consistency error, check log'))
	# insert new narrative
	queries = []
	cmd = """insert into clin_narrative (fk_encounter, fk_episode, narrative, soap_cat)
				 values (%s, %s, %s, lower(%s))"""
	queries.append((cmd, [encounter_id, episode_id, narrative, soap_cat]))
	# get PK of inserted row
	cmd = "select currval('clin_narrative_pk_seq')"
	queries.append((cmd, []))

	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)

	try:
		narrative = cNarrative(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate narrative' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))

	return (True, narrative)
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	print "\ndiagnose test"
	print  "-------------"
	diagnose = cDiag(aPK_obj=2)
	fields = diagnose.get_fields()
	for field in fields:
		print field, ':', diagnose[field]
	print "updatable:", diagnose.get_updatable_fields()
	print "codes:", diagnose.get_codes()
	print "possible codes:", diagnose.get_possible_codes()
	#print "adding code..."
	#diagnose.add_code('Test code', 'Test coding system')
	#print "codes:", diagnose.get_codes()

	print "\nnarrative test"
	print	"--------------"
	narrative = cNarrative(aPK_obj=7)
	fields = narrative.get_fields()
	for field in fields:
		print field, ':', narrative[field]
	print "updatable:", narrative.get_updatable_fields()
	print "codes:", narrative.get_codes()
	#print "adding code..."
	#narrative.add_code('Test code', 'Test coding system')
	#print "codes:", diagnose.get_codes()
	
	#print "creating narrative..."
	#status, new_narrative = create_clin_narrative(narrative = 'Test narrative', soap_cat = 'a', episode_id=1, encounter_id=2)
	#print new_narrative
	
	# FIXME cRFE and cAOE tests
	
#============================================================
# $Log: gmClinNarrative.py,v $
# Revision 1.7  2004-08-11 09:42:50  ncq
# - point clin_narrative VO to v_pat_narrative
# - robustify by applying lower() to soap_cat on insert/update
#
# Revision 1.6  2004/07/25 23:23:39  ncq
# - Carlos made cAOE.get_diagnosis() return a cDiag instead of a list
#
# Revision 1.5	2004/07/14 09:10:21	 ncq
# - Carlos' relentless work brings us get_codes(),
#	get_possible_codes() and adjustions for the fact
#	that we can now code any soap row
#
# Revision 1.4	2004/07/07 15:05:51	 ncq
# - syntax fixes by Carlos
# - get_codes(), get_possible_codes()
# - talk to the right views
#
# Revision 1.3	2004/07/06 00:09:19	 ncq
# - Carlos added create_clin_narrative(), cDiag, cNarrative, and unit tests - nice work !
#
# Revision 1.2	2004/07/05 10:24:46	 ncq
# - use v_pat_rfe/aoe, by Carlos
#
# Revision 1.1	2004/07/04 13:24:31	 ncq
# - add cRFE/cAOE
# - use in get_rfes(), get_aoes()
#
