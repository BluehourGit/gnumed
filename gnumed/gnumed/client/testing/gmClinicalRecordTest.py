"""
Unit tests for GnuMed gmClinicalRecord
"""
#============================================================
# $Id: gmClinicalRecordTest.py,v 1.6 2004-06-26 23:45:50 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL"

import unittest, time

from Gnumed.pycommon import gmPG, gmExceptions, gmLog
from Gnumed.business import gmClinicalRecord, gmEMRStructItems, gmAllergy, gmVaccination, gmPathLab
from Gnumed.pycommon.gmPyCompat import *

gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
#============================================================
class EMR_StructureTests(unittest.TestCase):
	#--------------------------------------------------------
	# Fixture initializer and finalizer methods
	#--------------------------------------------------------
	def setUp(self):
		self.emr = gmClinicalRecord.cClinicalRecord(aPKey = patient_id)

	def tearDown(self):
		backend = gmPG.ConnectionPool()
		backend.StopListeners()
		del self.emr
	#--------------------------------------------------------
	def testInstantiateExistingEMR(self):
		"""Check that an existing patient clinical record can be instantiated"""
		self.assertEqual(self.emr.id_patient, patient_id, 'cannot instantiate existing clinical record')

	def testInstantiateNonExistingEMR(self):
		"""Check that a non existing patient clinical record can't be instantiated"""
		self.assertRaises(gmExceptions.ConstructorError, gmClinicalRecord.cClinicalRecord, aPKey = -1)
	#--------------------------------------------------------
	# health issues API
	#--------------------------------------------------------
	def testGetHealthIssues(self):
		"""Check that patient health issues can be obtained"""
		self.assertEqual(isinstance(self.emr.get_health_issues()[0], gmEMRStructItems.cHealthIssue), True, 'cannot obtain valid active health issue from EMR')

	def testAddHealthIssue(self):
		""" Check that a new health issue can be created"""
		# create new health issue
		new_health_issue = self.emr.add_health_issue(health_issue_name = 'TEST Health Issue')
		self.assertEqual(new_health_issue['description'], 'TEST Health Issue')
		# delete test health issue
		queries = []
		cmd = "delete from clin_health_issue where id=%s and description=%s"
		queries.append((cmd, [new_health_issue['id'], 'TEST Health Issue']))
		result, msg = gmPG.run_commit('historica', queries, True)		 
		self.assertEqual(result, True)
		# check deletion was successfull
		cmd = """select id from clin_health_issue where id=%s"""
		rows = gmPG.run_ro_query('historica', cmd, None, new_health_issue['id'])
		self.assertEqual(len(rows), 0)

	#--------------------------------------------------------
	# episodes API
	#--------------------------------------------------------	 
	def testGetEpisodes(self):
		"""Check that patient episodes can be obtained"""
		self.assertEqual(isinstance(self.emr.get_episodes()[0], gmEMRStructItems.cEpisode), True)

	def testSetActiveEpisode(self):
		"""Check that a concrete episode can be set as the active one"""
		an_episode = self.emr.get_episodes()[0]
		status = self.emr.set_active_episode(an_episode['description'])
		self.assertEqual(status, True)

	def testAddEpisode(self):
		""" Check that a new episode can be created"""
		# create new episode
		h_issue = self.emr.get_health_issues()[0]
		new_episode = self.emr.add_episode(episode_name = 'TEST Episode', pk_health_issue = h_issue['id'])
		self.assertEqual(isinstance(new_episode, gmEMRStructItems.cEpisode), True)
		self.assertEqual(new_episode['id_patient'], patient_id)
		# delete test episode
		queries = []
		cmd = "select id from clin_episode where id=%s and fk_health_issue=%s and description=%s"
		queries.append((cmd, [ new_episode['pk_episode'], h_issue['id'], 'TEST Episode']))
		result, msg = gmPG.run_commit('historica', queries, True)
		self.assertEqual(result[0][0], new_episode['pk_episode'])
		queries = []
		cmd = "delete from clin_episode where id=%s"
		queries.append((cmd, [result[0][0]]))
		result, msg = gmPG.run_commit('historica', queries, True)
		self.assertEqual(result, True)
		# check deletion was successfull
		cmd = """select id from clin_episode where id=%s"""
		rows = gmPG.run_ro_query('historica', cmd, None, new_episode['pk_episode'])
		self.assertEqual(len(rows), 0)
	#--------------------------------------------------------
	# encounters API
	#--------------------------------------------------------
	def testGetActiveEncounter(self):
		"""Check that active encounter can be obtained"""
		self.assertEqual(isinstance(self.emr.get_active_encounter(), gmEMRStructItems.cEncounter), True)
	#def testAttachToEncounter(self):
		#"""Check that a concrete encounter can be attached to"""
		#active_encounter = self.emr.get_active_encounter()
		#print active_encounter
		#status = self.emr.attach_to_encounter(anID = active_encounter['pk_encounter'])
		#self.assertEqual(status, True)
#============================================================
class AllergyTests(unittest.TestCase):
	#--------------------------------------------------------
	# Fixture initializer and finalizer methods
	#--------------------------------------------------------
	def setUp(self):
		self.emr = gmClinicalRecord.cClinicalRecord(aPKey = patient_id)

	def tearDown(self):
		backend = gmPG.ConnectionPool()
		backend.StopListeners()
		del self.emr
	#--------------------------------------------------------
	def testGetAllergies(self):
		"""Check that patient allergies can be obtained"""
		an_allergy = self.emr.get_allergies()[0]
		self.assertEqual(isinstance(an_allergy, gmAllergy.cAllergy), True)

	def testGetAllergiesRemovingSensitivities(self):
		"""Check that patient allergies, excluding sensitivities can be obtained"""
		allergies = self.emr.get_allergies(remove_sensitivities = True)
		for an_allergy in allergies:
			self.assertEqual(isinstance(an_allergy, gmAllergy.cAllergy), True, 'get_allergies() failed')
			self.assertEqual(an_allergy['type'], 'allergy', 'get_allergies() failed to remove sensitivies')

	def testZZzAddAllergy(self):
		"""Check that a new allergy can be created"""
		gmLog.gmDefLog.flush()
		# create new allergy
		id_encounter = self.emr.get_active_encounter()['pk_encounter']
		pk_episode = self.emr.get_active_episode()['pk_episode']
		new_allergy = self.emr.add_allergy (
			substance='Test substance',
			allg_type = 1,
			encounter_id = id_encounter,
			episode_id = pk_episode
		)
		self.assertEqual(isinstance(new_allergy, gmAllergy.cAllergy), True, 'add_allergy() failed')
		new_allergy['reaction'] = 'Test narrative'
		new_allergy['definite'] = True
		new_allergy.save_payload()
		#delete test allergy
		queries = []
		cmd = "delete from allergy where id=%s"
		queries.append((cmd, [new_allergy['id']]))
		result, msg = gmPG.run_commit('historica', queries, True)
		self.assertEqual(result, True, 'deleting newly inserted allergy failed: %s' % msg)
		# check deletion was successfull
		cmd = """select id from allergy where id=%s"""
		rows = gmPG.run_ro_query('historica', cmd, None, new_allergy['id'])
		self.assertEqual(len(rows), 0, 'deleting newly inserted allergy failed')
#============================================================
class VaccinationTests(unittest.TestCase):
	#--------------------------------------------------------
	# Fixture initializer and finalizer methods
	#--------------------------------------------------------
	def setUp(self):
		self.emr = gmClinicalRecord.cClinicalRecord(aPKey = patient_id)

	def tearDown(self):
		backend = gmPG.ConnectionPool()
		backend.StopListeners()
		del self.emr
	#--------------------------------------------------------
	def testGetVaccinatedIndications(self):
		"""Check if vaccinated indication list can be retrieved"""
		status, vacc_indications = self.emr.get_vaccinated_indications()
		self.assertEqual(status, True)
#		self.assertEqual(['tetanus','tetanus'] in vacc_indications, True)

	def testGetVaccinations(self):
		"""Check that patient vaccinations can be obtained"""
		a_vaccination = self.emr.get_vaccinations()[0]
		self.assertEqual(isinstance(a_vaccination, gmVaccination.cVaccination), True)
		
	def testGetVaccinationsByIndication(self):
		"""Check that patient vaccinations can be obtained filtered by indication"""
		status, vacc_indications = self.emr.get_vaccinated_indications()
		vaccinations = self.emr.get_vaccinations(indications=['tetanus'])
		for a_vacc in vaccinations:
			self.assertEqual(isinstance(a_vacc, gmVaccination.cVaccination), True)
			self.assertEqual(a_vacc['indication'], 'tetanus')

	def testGetMissingVaccinations(self):
		"""Check that patient missing vaccinations can be obtained"""
		missing_vacc = self.emr.get_missing_vaccinations()['due']
		missing_boost = self.emr.get_missing_vaccinations()['boosters']
		for a_vacc in missing_vacc:
			self.assertEqual(isinstance(a_vacc, gmVaccination.cMissingVaccination), True)
		for a_boost in missing_boost:
			self.assertEqual(isinstance(a_boost, gmVaccination.cMissingBooster), True)

	def testGetMissingVaccinationsByIndication(self):
		"""Check that patient missing vaccinations can be obtained filtered by indication"""
		missing_vacc = self.emr.get_missing_vaccinations(indications=['diphteria'])['due']
		missing_boost = self.emr.get_missing_vaccinations(indications=['influenza'])['boosters']
		for a_vacc in missing_vacc:
			self.assertEqual(isinstance(a_vacc, gmVaccination.cMissingVaccination), True)
			self.assertEqual(a_vacc['indication'], 'diphteria')
		for a_boost in missing_boost:
			self.assertEqual(isinstance(a_boost, gmVaccination.cMissingBooster), True)
			self.assertEqual(a_boost['indication'], 'influenza')
			
	def testAddVaccination(self):
		"""Check that a new vaccination can be created"""
		# create new vaccination
		status, new_vaccination = self.emr.add_vaccination(vaccine='Td-pur')
		self.assertEqual(status, True)
		self.assertEqual(isinstance(new_vaccination, gmVaccination.cVaccination), True)
		new_vaccination['narrative']='Test narrative'
		new_vaccination.save_payload()
		#delete test vaccination
		queries = []
		cmd = "delete from vaccination where id=%s and narrative=%s"
		queries.append((cmd, [new_vaccination['pk_vaccination'], 'Test narrative']))
		result, msg = gmPG.run_commit('historica', queries, True)
		self.assertEqual(result, True)
		# check deletion was successfull
		cmd = """select id from vaccination where id=%s"""
		rows = gmPG.run_ro_query('historica', cmd, None, new_vaccination['pk_vaccination'])
		self.assertEqual(len(rows), 0)		  
#============================================================
class LabAPITests(unittest.TestCase):
	#--------------------------------------------------------
	# Fixture initializer and finalizer methods
	#--------------------------------------------------------
	def setUp(self):
		self.emr = gmClinicalRecord.cClinicalRecord(aPKey = patient_id)

	def tearDown(self):
		backend = gmPG.ConnectionPool()
		backend.StopListeners()
		del self.emr
	#--------------------------------------------------------
	def testGetLabRequest(self):
		"""Check if a lab request can be retrieved"""
		lab_request = self.emr.get_lab_request(pk = 1, lab= 2, req_id= 'SC937-0176-CEC#15034')
		self.assertEqual(isinstance(lab_request, gmPathLab.cLabRequest), True)
		
	def testGetLabResults(self):
		"""Check if lab result list can be retrieved"""
		lab_result = self.emr.get_lab_results(limit = 2)[0]
		self.assertEqual(isinstance(lab_result, gmPathLab.cLabResult), True)
		
	def testAddLabRequest(self):
		"""Check that a new lab request can be created"""
		# create new lab request
		new_lab_request = self.emr.add_lab_request(lab=2, req_id='Test request')
		self.assertEqual(isinstance(new_lab_request, gmPathLab.cLabRequest), True)
		new_lab_request['narrative']='Test narrative'
		new_lab_request.save_payload()
		#delete test lab request
		queries = []
		cmd = "delete from lab_request where pk=%s and narrative=%s"
		queries.append((cmd, [new_lab_request['pk'], 'Test narrative']))
		result, msg = gmPG.run_commit('historica', queries, True)
		self.assertEqual(result, True)
		# check deletion was successfull
		cmd = """select pk from lab_request where pk=%s"""
		rows = gmPG.run_ro_query('historica', cmd, None, new_lab_request['pk'])
		self.assertEqual(len(rows), 0)

#============================================================
def suite():
	emr_struct_tests = unittest.makeSuite(EMR_StructureTests, 'test')
	allg_tests = unittest.makeSuite(AllergyTests, 'test')
	vacc_tests = unittest.makeSuite(VaccinationTests, 'test')
	lab_tests = unittest.makeSuite(LabAPITests, 'test')

	test_suite = unittest.TestSuite((
		emr_struct_tests
		, vacc_tests
		, lab_tests
		, allg_tests
	))

	return test_suite
#------------------------------------------------------------
# Make this test module runnable from the command prompt
def main():
	gmPG.set_default_client_encoding('latin1')

	runner = unittest.TextTestRunner()
	runner.run(suite())

	backend = gmPG.ConnectionPool()
	backend.StopListeners()
#------------------------------------------------------------
if __name__ == "__main__":
	_ = lambda x:x
	# this is Captain Kirk
	# Modify its PK to adapt to your backend to run the tests
	# FIXME: get Kirk's ID from backend via query ?
	patient_id = 13
	main()
#============================================================
# $Log: gmClinicalRecordTest.py,v $
# Revision 1.6  2004-06-26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.5  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.4  2004/06/17 22:49:22  ncq
# - testGetAllergies() needs to [0] the return of get_allergies
#
# Revision 1.3  2004/06/17 21:28:35  ncq
# - indication_list -> indications
#
# Revision 1.2  2004/06/14 07:51:59  ncq
# - activate all the unit tests
#
# Revision 1.1  2004/06/14 07:37:43  ncq
# - first check in
#
