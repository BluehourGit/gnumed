"""GnuMed allergy related business object.

"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmAllergy.py,v $
# $Id: gmAllergy.py,v 1.15 2004-11-03 22:32:34 ncq Exp $
__version__ = "$Revision: 1.15 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL"

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions, gmI18N
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cAllergy(gmClinItem.cClinItem):
	"""Represents one allergy event.
	"""
	_cmd_fetch_payload = """
		select *, xmin_allergy from v_pat_allergies
		where pk_allergy=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from allergy where id=%(id)s and xmin=%(xmin_allergy)s for update"""
	]
	_cmds_store_payload = [
		"""update allergy set
				clin_when=%(date)s,
				substance=%(substance)s,
				substance_code=%(substance_code)s,
				generics=%(generics)s,
				allergene=%(allergene)s,
				atc_code=%(atc_code)s,
				id_type=%(pk_type)s,
				generic_specific=%(generic_specific)s::boolean,
				definite=%(definite)s::boolean,
				narrative=%(reaction)s
			where id=%(pk_allergy)s"""
	]
	_updatable_fields = [
		'date',
		'substance',
		'substance_code',	
		'generics',
		'allergene',
		'atc_code',
		'pk_type',
		'generic_specific',
		'definite',
		'reaction'
	]
#============================================================
# convenience functions
#------------------------------------------------------------
def create_allergy(substance=None, allg_type=None, episode_id=None, encounter_id=None):
	"""Creates a new allergy clinical item.

	substance - allergic substance
	allg_type - allergy or sensitivity, pk or string
	encounter_id - encounter's primary key
	episode_id - episode's primary key
	"""
	# sanity checks:
	# 1) any of the args being None should fail the SQL code
	# 2) do episode/encounter belong to the same patient ?
	cmd = """
		select id_patient from v_pat_episodes where pk_episode=%s
			union
		select pk_patient from v_pat_encounters where pk_encounter=%s"""
	rows = gmPG.run_ro_query('historica', cmd, None, episode_id, encounter_id)
	if (rows is None) or (len(rows) == 0):
		_log.Log(gmLog.lErr, 'error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (None, _('internal error, check log'))
	if len(rows) > 1:
		_log.Log(gmLog.lErr, 'episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
		return (None, _('consistency error, check log'))
	pat_id = rows[0][0]
	# insert new allergy
	queries = []
	if type(allg_type) == types.IntType:
		cmd = """
			insert into allergy (id_type, fk_encounter, fk_episode, substance)
			values (%s, %s, %s, %s)"""
	else:
		cmd = """
			insert into allergy (id_type, fk_encounter, fk_episode,  substance)
			values ((select id from _enum_allergy_type where value=%s), %s, %s, %s)"""
		allg_type = str(allg_type)
	queries.append((cmd, [allg_type, encounter_id, episode_id, substance]))
	# set patient has_allergy status
	cmd = """delete from allergy_state where fk_patient=%s"""
	queries.append((cmd, [pat_id]))
	cmd = """insert into allergy_state (fk_patient, has_allergy) values (%s, 1)"""
	queries.append((cmd, [pat_id]))
	# get PK of inserted row
	cmd = "select currval('allergy_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (None, msg)
	try:
		allergy = cAllergy(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate allergy [%s]' % result[0][0], sys.exc_info(), verbose=0)
		return (None, _('internal error, check log'))
	return (True, allergy)
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

	gmPG.set_default_client_encoding('latin1')
	allg = cAllergy(aPK_obj=1)
	print allg
	fields = allg.get_fields()
	for field in fields:
		print field, ':', allg[field]
	print "updatable:", allg.get_updatable_fields()
	enc_id = allg['pk_encounter']
	epi_id = allg['pk_episode']
	status, allg = create_allergy (
		substance = 'test substance',
		allg_type=1,
		episode_id = epi_id,
		encounter_id = enc_id
	)
	print allg
	allg['reaction'] = 'hehehe'
	allg.save_payload()
	print allg
#============================================================
# $Log: gmAllergy.py,v $
# Revision 1.15  2004-11-03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.14  2004/10/11 19:42:32  ncq
# - add license
# - adapt field names
# - some cleanup
#
# Revision 1.13  2004/06/28 12:18:41  ncq
# - more id_* -> fk_*
#
# Revision 1.12  2004/06/26 07:33:54  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.11  2004/06/14 08:22:10  ncq
# - cast to boolean in save payload
#
# Revision 1.10  2004/06/09 14:32:24  ncq
# - remove extraneous ()'s
#
# Revision 1.9  2004/06/08 00:41:38  ncq
# - fix imports, cleanup, improved self-test
#
# Revision 1.8  2004/06/02 21:47:27  ncq
# - improved sanity check in create_allergy() contributed by Carlos
#
# Revision 1.7  2004/05/30 18:33:28  ncq
# - cleanup, create_allergy, done mostly by Carlos
#
# Revision 1.6  2004/05/12 14:28:52  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.5  2004/04/20 13:32:33  ncq
# - improved __str__ output
#
# Revision 1.4  2004/04/20 00:17:55  ncq
# - allergies API revamped, kudos to Carlos
#
# Revision 1.3  2004/04/16 16:17:33  ncq
# - test save_payload
#
# Revision 1.2  2004/04/16 00:00:59  ncq
# - Carlos fixes
# - save_payload should now work
#
# Revision 1.1  2004/04/12 22:58:55  ncq
# - Carlos sent me this
#
