"""GnuMed simple ASCII EMR export tool.

TODO:
- GUI mode:
  - post-0.1 !
  - allow user to select patient
  - allow user to pick episodes/encounters/etc from list
- output modes:
  - HTML - post-0.1 !
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/gmPatientExporter.py,v $
# $Id: gmPatientExporter.py,v 1.40 2005-02-20 08:32:51 sjtan Exp $
__version__ = "$Revision: 1.40 $"
__author__ = "Carlos Moro"
__license__ = 'GPL'

import sys, traceback, string, types

import mx.DateTime.Parser as mxParser
import mx.DateTime as mxDT

from Gnumed.pycommon import gmLog, gmPG, gmI18N, gmCLI, gmCfg, gmExceptions, gmNull
from Gnumed.business import gmClinicalRecord, gmPerson, gmAllergy, gmVaccination, gmPathLab, gmMedDoc
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_cfg = gmCfg.gmDefCfgFile
#============================================================
class cEmrExport:

    #--------------------------------------------------------                
    def __init__(self, constraints = None, fileout = None, patient = None):
        """
        Constructs a new instance of exporter
        
        constraints - Exporter constraints for filtering clinical items
        fileout - File-like object as target for dumping operations
        """
        if constraints is None:
            # default constraints to None for complete emr dump
            self.__constraints = {
                'since': None,
                'until': None,
                'encounters': None,
                'episodes': None,
                'issues': None
            }
        else:
            self.__constraints = constraints
        self.__target = fileout
        self.__patient = patient
        self.lab_new_encounter = True
        
    #--------------------------------------------------------
    def set_constraints(self, constraints = None):
        """Sets exporter constraints.

        constraints - Exporter constraints for filtering clinical items
        """
        if constraints is None:
            # default constraints to None for complete emr dump
            self.__constraints = {
                'since': None,
                'until': None,
                'encounters': None,
                'episodes': None,
                'issues': None
            }
        else:
            self.__constraints = constraints
        return True
        
    #--------------------------------------------------------
    def get_constraints(self):
        """
        Retrieve exporter constraints
        """
        return self.__constraints
        
    #--------------------------------------------------------
    def set_patient(self, patient=None):
        """
            Sets exporter patient
            
            patient - Patient whose data are to be dumped
        """
        if patient is None:
            _log.Log(gmLog.lErr, "can't set None patient for exporter")
            return
        self.__patient = patient
        
    #--------------------------------------------------------
    def get_patient(self):
        """
            Retrieves patient whose data are to be dumped
        """
        return self.__patient
        
    #--------------------------------------------------------
    def cleanup(self):
        """
            Exporter class cleanup code
        """
        pass
        
    #--------------------------------------------------------
    def __dump_vacc_table(self, vacc_regimes):
        """
        Retrieves string containg ASCII vaccination table
        """                
        
        emr = self.__patient.get_clinical_record()
        
        # patient dob
        patient_dob = mxParser.DateFromString(self.__patient.get_identity().getDOB(aFormat = 'YYYY-MM-DD'), formats= ['iso']) 
        date_length = len(patient_dob.Format('%Y-%m-%d')) + 2 # (YYYY-mm-dd)

        # dictionary of pairs indication : scheduled vaccination
        vaccinations4regimes = {}
        for a_vacc_regime in vacc_regimes:
            indication = a_vacc_regime['indication']
            vaccinations4regimes[indication] = emr.get_scheduled_vaccinations(indications=[indication])
        # vaccination regimes count
        chart_columns = len(vacc_regimes)
        # foot headers
        foot_headers = ['last booster', 'next booster']        
        # string for both: ending of vaccinations; non boosters needed
        ending_str = '='
        
        # chart row count, columns width and vaccination dictionary of pairs indication : given shot
        column_widths = []
        chart_rows = -1
        vaccinations = {}        
        temp = -1
        for foot_header in foot_headers: # first column width
            if len(foot_header) > temp:
                temp = len(foot_header)
        column_widths.append(temp)        
        for a_vacc_regime in vacc_regimes:
            if a_vacc_regime['shots'] > chart_rows: # max_seq  -> row count 
                chart_rows = a_vacc_regime['shots']
            if (len(a_vacc_regime['l10n_indication'])) > date_length: # l10n indication -> column width
                column_widths.append(len(a_vacc_regime['l10n_indication'])) 
            else:
                column_widths.append(date_length)  # date -> column width at least
            vaccinations[a_vacc_regime['indication']] = emr.get_vaccinations(indications=[a_vacc_regime['indication']]) # given shots 4 indication
                
        # patient dob in top of vaccination chart 
        txt = '\nDOB: %s' %(patient_dob.Format('%Y-%m-%d')) + '\n'       
        
        # vacc chart table headers
        # top ---- header line
        for column_width in column_widths: 
            txt += column_width * '-' + '-'
        txt += '\n'                
        # indication names header line
        txt += column_widths[0] * ' ' + '|'
        col_index = 1
        for a_vacc_regime in vacc_regimes:
            txt +=  a_vacc_regime['l10n_indication'] + (column_widths[col_index] - len(a_vacc_regime['l10n_indication'])) * ' ' + '|'
            col_index += 1
        txt +=  '\n'
        # bottom ---- header line
        for column_width in column_widths:
            txt += column_width * '-' + '-'
        txt += '\n'        
        
        # vacc chart data
        due_date = None        
        # previously displayed date list
        prev_displayed_date = [patient_dob]
        for a_regime in vacc_regimes:
            prev_displayed_date.append(patient_dob) # initialice with patient dob (useful for due first shot date calculation)
        # iterate data rows
        for row_index in range(0, chart_rows):            
            row_header = '#%s' %(row_index+1)
            txt += row_header + (column_widths[0] - len(row_header)) * ' ' + '|'
                        
            for col_index in range(1, chart_columns+1):
                indication =vacc_regimes[col_index-1]['indication']
                seq_no = vacc_regimes[col_index-1]['shots']
                if row_index == seq_no: # had just ended scheduled vaccinations
                     txt += ending_str * column_widths[col_index] + '|'
                elif row_index < seq_no: # vaccination scheduled
                    try:
                        vacc_date = vaccinations[indication][row_index]['date'] # vaccination given                        
                        vacc_date_str = vacc_date.Format('%Y-%m-%d')                        
                        txt +=  vacc_date_str + (column_widths[col_index] - len(vacc_date_str)) * ' ' + '|'                        
                        prev_displayed_date[col_index] = vacc_date                                                
                    except:
                        if row_index == 0: # due first shot
                            due_date = prev_displayed_date[col_index] + vaccinations4regimes[indication][row_index]['age_due_min'] # FIXME 'age_due_min' not properly retrieved
                        else: # due any other than first shot
                            due_date = prev_displayed_date[col_index] + vaccinations4regimes[indication][row_index]['min_interval']
                        txt += '('+ due_date.Format('%Y-%m-%d') + ')' + (column_widths[col_index] - date_length) * ' ' + '|'
                        prev_displayed_date[col_index] = due_date
                else: # not scheduled vaccination at that position
                    txt += column_widths[col_index] * ' ' + '|'
            txt += '\n' # end of scheduled vaccination dates display
            for column_width in column_widths: # ------ separator line
                txt += column_width * '-' + '-'
            txt += '\n'
                                    
        # scheduled vaccination boosters (date retrieving)
        all_vreg_boosters = []                
        for a_vacc_regime in vacc_regimes:
            vaccs4indication = vaccinations[a_vacc_regime['indication']] # iterate over vaccinations by indication
            given_boosters = [] # will contain given boosters for current indication
            for a_vacc in vaccs4indication:
                try:
                     if a_vacc['is_booster']:
                         given_boosters.append(a_vacc)
                except:
                    # not a booster
                    pass
            if len(given_boosters) > 0:
                all_vreg_boosters.append(given_boosters[len(given_boosters)-1]) # last of given boosters
            else:
                all_vreg_boosters.append(None)

        # next booster in schedule
        all_next_boosters = []
        for a_booster in all_vreg_boosters:
            all_next_boosters.append(None)
        # scheduled vaccination boosters (displaying string)
        cont = 0
        for a_vacc_regime in vacc_regimes:
            vaccs = vaccinations4regimes[a_vacc_regime['indication']]        
            if vaccs[len(vaccs)-1]['is_booster'] == False: # booster is not scheduled/needed
                all_vreg_boosters[cont] = ending_str * column_widths[cont+1]
                all_next_boosters[cont] = ending_str * column_widths[cont+1]
            else:
                indication = vacc_regimes[cont]['indication']
                if len(vaccinations[indication]) > vacc_regimes[cont]['shots']: # boosters given
                    all_vreg_boosters[cont] = vaccinations[indication][len(vaccinations[indication])-1]['date'].Format('%Y-%m-%d') # show last given booster date
                    scheduled_booster = vaccinations4regimes[indication][len(vaccinations4regimes[indication])-1]
                    booster_date = vaccinations[indication][len(vaccinations[indication])-1]['date'] + scheduled_booster['min_interval']                                        
                    if booster_date < mxDT.today():
                        all_next_boosters[cont] = '<(' + booster_date.Format('%Y-%m-%d') + ')>' # next booster is due
                    else:
                        all_next_boosters[cont] = booster_date.Format('%Y-%m-%d')
                elif len(vaccinations[indication]) == vacc_regimes[cont]['shots']: # just finished vaccinations, begin boosters
                    all_vreg_boosters[cont] = column_widths[cont+1] * ' '
                    scheduled_booster = vaccinations4regimes[indication][len(vaccinations4regimes[indication])-1]
                    booster_date = vaccinations[indication][len(vaccinations[indication])-1]['date'] + scheduled_booster['min_interval']                    
                    if booster_date < mxDT.today():
                        all_next_boosters[cont] = '<(' + booster_date.Format('%Y-%m-%d') + ')>' # next booster is due
                    else:
                        all_next_boosters[cont] = booster_date.Format('%Y-%m-%d')
                else:
                    all_vreg_boosters[cont] = column_widths[cont+1] * ' '  # unfinished schedule
                    all_next_boosters[cont] = column_widths[cont+1] * ' '
            cont += 1
                             
        # given boosters
        foot_header = foot_headers[0]
        col_index = 0
        txt += foot_header + (column_widths[0] - len(foot_header)) * ' ' + '|'
        col_index += 1
        for a_vacc_regime in vacc_regimes:
            txt +=  str(all_vreg_boosters[col_index-1]) + (column_widths[col_index] - len(str(all_vreg_boosters[col_index-1]))) * ' ' + '|'
            col_index += 1
        txt +=  '\n'
        for column_width in column_widths:            
            txt += column_width * '-' + '-'
        txt += '\n' 
        
        # next booster
        foot_header = foot_headers[1]
        col_index = 0
        txt += foot_header + (column_widths[0] - len(foot_header)) * ' ' + '|'
        col_index += 1
        for a_vacc_regime in vacc_regimes:
            txt +=  str(all_next_boosters[col_index-1]) + (column_widths[col_index] - len(str(all_next_boosters[col_index-1]))) * ' ' + '|'
            col_index += 1
        txt +=  '\n'
        for column_width in column_widths:
            txt += column_width * '-' + '-'
        txt += '\n'                

        self.__target.write(txt)        
        
    #--------------------------------------------------------
    def get_vacc_table(self):
        """
        Iterate over patient scheduled regimes preparing vacc tables dump
        """        
        
        emr = self.__patient.get_clinical_record()
        
        # vaccination regimes
        all_vacc_regimes = emr.get_scheduled_vaccination_regimes()
        # Configurable: vacc regimes per displayed table
        # FIXME: option, post 0.1 ?
        max_regs_per_table = 4

        # Iterate over patient scheduled regimes dumping in tables of 
        # max_regs_per_table regimes per table
        reg_count = 0
        vacc_regimes = []
        for total_reg_count in range(0,len(all_vacc_regimes)):
            if reg_count%max_regs_per_table == 0:
                if len(vacc_regimes) > 0:
                    self.__dump_vacc_table(vacc_regimes)
                vacc_regimes = []
                reg_count = 0
            vacc_regimes.append(all_vacc_regimes[total_reg_count])
            reg_count += 1
        if len(vacc_regimes) > 0:
            self.__dump_vacc_table(vacc_regimes)        
                            
    #--------------------------------------------------------
    def dump_item_fields(self, offset, item, field_list):
        """
            Dump information related to the fields of a clinical item
            offset - Number of left blank spaces
            item - Item of the field to dump
            fields - Fields to dump
        """
        txt = ''
        for a_field in field_list:
            txt += offset*' ' + a_field + ': ' + str(item[a_field]) + '\n'
        return txt
        
    #--------------------------------------------------------
    def get_allergy_output(self, allergy, left_margin = 0):
        """
            Dumps allergy item data
            allergy - Allergy item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = ''
        txt += left_margin*' ' + _('Allergy')  + ': \n'
        txt += self.dump_item_fields((left_margin+3), allergy, ['allergene', 'substance', 'generic_specific','l10n_type', 'definite', 'reaction'])
        return txt
        
    #--------------------------------------------------------
    def get_vaccination_output(self, vaccination, left_margin = 0):
        """
            Dumps vaccination item data
            vaccination - Vaccination item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = ''
        txt += left_margin*' ' + _('Vaccination') + ': \n'
        txt += self.dump_item_fields((left_margin+3), vaccination, ['l10n_indication', 'vaccine', 'batch_no', 'site', 'narrative'])        
        return txt
        
    #--------------------------------------------------------
    def get_lab_result_output(self, lab_result, left_margin = 0):
        """
            Dumps lab result item data
            lab_request - Lab request item to dump
            left_margin - Number of spaces on the left margin            
        """
        txt = ''
        if self.lab_new_encounter:
            txt += (left_margin)*' ' + _('Lab result') + ': \n'
        txt += (left_margin+3) * ' ' + lab_result['unified_name']  + ': ' + lab_result['unified_val']+ ' ' + lab_result['val_unit'] + ' (' + lab_result['material'] + ')' + '\n'
        return txt
        
    #--------------------------------------------------------
    def get_item_output(self, item, left_margin = 0):
        """
            Obtains formatted clinical item output dump
            item - The clinical item to dump
            left_margin - Number of spaces on the left margin            
        """
        txt = ''
        if isinstance(item, gmAllergy.cAllergy):
            txt += self.get_allergy_output(item, left_margin)
        elif isinstance(item, gmVaccination.cVaccination):
            txt += self.get_vaccination_output(item, left_margin)
        elif isinstance(item, gmPathLab.cLabResult):
            txt += self.get_lab_result_output(item, left_margin)
            self.lab_new_encounter = False
        return txt
        
    #--------------------------------------------------------
    def __fetch_filtered_items(self):
        """
            Retrieve patient clinical items filtered by multiple constraints
        """
        emr = self.__patient.get_clinical_record()
        filtered_items = []
        filtered_items.extend(emr.get_allergies(
            since=self.__constraints['since'],
            until=self.__constraints['until'],
            encounters=self.__constraints['encounters'],
            episodes=self.__constraints['episodes'],
            issues=self.__constraints['issues']))
	try:
		filtered_items.extend(emr.get_vaccinations(
		    since=self.__constraints['since'],
		    until=self.__constraints['until'],
		    encounters=self.__constraints['encounters'],
		    episodes=self.__constraints['episodes'],
		    issues=self.__constraints['issues']))
	except:
		_log.Error("vaccination error? outside regime")

        filtered_items.extend(emr.get_lab_results(
            since=self.__constraints['since'],
            until=self.__constraints['until'],
            encounters=self.__constraints['encounters'],
            episodes=self.__constraints['episodes'],
            issues=self.__constraints['issues']))
        self.__filtered_items = filtered_items
        
    #--------------------------------------------------------
    def get_allergy_summary(self, allergy, left_margin = 0):
        """
            Dumps allergy item data summary
            allergy - Allergy item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = left_margin*' ' + _('Allergy') + ': ' + allergy['descriptor'] + ', ' + \
            allergy['reaction'] + '\n'
        return txt
        
    #--------------------------------------------------------
    def get_vaccination_summary(self, vaccination, left_margin = 0):
        """
            Dumps vaccination item data summary
            vaccination - Vaccination item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = left_margin*' ' + _('Vaccination') + ': ' + vaccination['l10n_indication'] + ', ' + \
            vaccination['narrative'] + '\n'
        return txt
        
    #--------------------------------------------------------
    def get_lab_result_summary(self, lab_result, left_margin = 0):
        """
            Dumps lab result item data summary
            lab_request - Lab request item to dump
            left_margin - Number of spaces on the left margin            
        """
        txt = ''
        if self.lab_new_encounter:
            txt += (left_margin+3)*' ' + _('Lab') + ': '  + \
                lab_result['unified_name'] + '-> ' + lab_result['unified_val'] + \
                ' ' + lab_result['val_unit']+ '\n' + '(' + lab_result['req_when'].Format('%Y-%m-%d') + ')'
        return txt
        
    #--------------------------------------------------------
    def get_item_summary(self, item, left_margin = 0):
        """
            Obtains formatted clinical item summary dump
            item - The clinical item to dump
            left_margin - Number of spaces on the left margin            
        """
        txt = ''
        if isinstance(item, gmAllergy.cAllergy):
            txt += self.get_allergy_summary(item, left_margin)
        elif isinstance(item, gmVaccination.cVaccination):
            txt += self.get_vaccination_summary(item, left_margin)
        elif isinstance(item, gmPathLab.cLabResult) and \
            (item['relevant'] == True or item['abnormal'] == True):
            txt += self.get_lab_result_summary(item, left_margin)
            self.lab_new_encounter = False
        return txt
                                    
    #--------------------------------------------------------            
    def get_historical_tree(self, emr_tree):
        """
        Retrieves patient's historical in form of a wx tree of health issues
                                                                                        -> episodes
                                                                                           -> encounters
        Encounter object is associated with item to allow displaying its information
        """
        # variable initialization
        self.__fetch_filtered_items()
        emr = self.__patient.get_clinical_record()
        h_issues = emr.get_health_issues(id_list = self.__constraints['issues'])
        root_node = emr_tree.GetRootItem()
        # build the tree
        for a_health_issue in h_issues:
            issue_node =  emr_tree.AppendItem(root_node, a_health_issue['description'])
            emr_tree.SetPyData(issue_node, a_health_issue)
            episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['id']])
            for an_episode in episodes:    
               episode_node =  emr_tree.AppendItem(issue_node, an_episode['description'])
               emr_tree.SetPyData(episode_node, an_episode)
               encounters = emr.get_encounters(since=self.__constraints['since'],
                until=self.__constraints['until'], id_list=self.__constraints['encounters'],
                episodes=[an_episode['pk_episode']], issues=[a_health_issue['id']])
               for an_encounter in encounters:
                    label = '%s:%s' % (an_encounter['l10n_type'], an_encounter['started'].Format('%Y-%m-%d'))
                    encounter_node = emr_tree.AppendItem(episode_node, label)
                    emr_tree.SetPyData(encounter_node, an_encounter)
                    
    #--------------------------------------------------------  
    def dump_summary_info(self, left_margin = 0):
        """
        Dumps patient EMR summary
                                                              
        """
        txt = ''
        for an_item in self.__filtered_items:
            txt += self.get_item_summary(an_item, left_margin)
        return txt                    
        
    #--------------------------------------------------------  
    def dump_issue_info(self, issue=None, left_margin=0):
        """
        Dumps health specific data
                                                              
        """
        # fetch first and last encounters for the issue
        emr = self.__patient.get_clinical_record()
        first_encounter = emr.get_first_encounter(issue_id = issue['id'])

        last_encounter = emr.get_last_encounter(issue_id = issue['id'])
        # dump info
        txt = ''
        txt += left_margin *' ' + 'Started: ' + first_encounter['started'].Format('%Y-%m-%d %H:%M') + '\n'
        txt += left_margin *' ' + 'Last treated: ' + last_encounter['last_affirmed'].Format('%Y-%m-%d %H:%M') + '\n' 
        if issue['description'] is not None and len(issue['description']) > 0:
            txt += left_margin *' ' + 'Description: ' + issue['description'] + '\n'
        return txt                    
        
    #--------------------------------------------------------  
    def dump_episode_info(self, episode, left_margin = 0):
        """
        Dumps episode specific data
                                                              
        """
        # fetch first and last encounters for the issue
        emr = self.__patient.get_clinical_record()
        first_encounter = emr.get_first_encounter(episode_id = episode['pk_episode'])
        last_encounter = emr.get_last_encounter(episode_id = episode['pk_episode'])
        # dump info
        txt = ''
        txt += left_margin *' ' + 'Started: ' + first_encounter['started'].Format('%Y-%m-%d %H:%M') + '\n'
        txt += left_margin *' ' + 'Last treated: ' + last_encounter['last_affirmed'].Format('%Y-%m-%d %H:%M') + '\n' 
        if episode['description'] is not None and len(episode['description']) > 0:
            txt += left_margin *' ' + 'Description: ' + episode['description'] + '\n'
        return txt                                
                
    #--------------------------------------------------------  
    def dump_encounter_info(self, episode, encounter, left_margin = 0):
        """
        Dumps encounter specific data (title, rfe, aoe and soap)
                                                              
        """
        emr = self.__patient.get_clinical_record()
        txt = ''
        # general
        txt += left_margin *' ' + 'Type: ' + encounter['l10n_type'] + '\n'        
        txt += left_margin *' ' + 'Date: ' + encounter['started'].Format('%Y-%m-%d %H:%M') + \
            ' - ' + encounter['last_affirmed'].Format('%Y-%m-%d %H:%M') + '\n'
        if encounter['description'] is not None and len(encounter['description']) > 0:
            txt += left_margin *' ' + 'Description: ' + encounter['description'] + '\n'        
        # rfe
        rfes = encounter.get_rfes()
        for rfe in rfes:
            txt += left_margin *' ' + 'RFE: ' + rfe['clin_when'].Format('%Y-%m-%d %H:%M') + ', ' +  rfe['rfe'] + '\n'
        
        # soap
        soap_cats = ['s', 'o', 'a', 'p']
        soap_cat_narratives = []
        for soap_cat in soap_cats:
            soap_cat_narratives = emr.get_clin_narrative(
                episodes = [episode['pk_episode']],
                encounters = [encounter['pk_encounter']],
                soap_cats = [soap_cat],
                exclude_rfe_aoe = True
            )
            txt += left_margin *' ' +  string.upper(soap_cat) +':\n'
            if soap_cat_narratives is None or len(soap_cat_narratives) == 0:
                txt +=''
            else:
                for soap_entry in soap_cat_narratives:
                    narrative_txt = string.replace(soap_entry['narrative'], '\n',
                        '\n' + (left_margin+3)*' ')
                    txt += (left_margin+3)*' ' + narrative_txt + '\n'
        # aoe
        aoes = encounter.get_aoes()            
        for aoe in aoes:
            txt += left_margin*' ' + 'AOE: ' + aoe['clin_when'].Format('%Y-%m-%d %H:%M') + ', ' +  aoe['aoe'] + '\n'
            if aoe.is_diagnosis():
                diagnosis = aoe.get_diagnosis()
                for a_code in diagnosis.get_codes():
                    txt += (left_margin+3)*' ' + a_code[0] +'(' + a_code[1] + ')\n' 
        # items
        for an_item  in self.__filtered_items:
            if an_item['pk_encounter'] == encounter['pk_encounter']:
                txt += self.get_item_output(an_item, left_margin)
        return txt    
        
    #--------------------------------------------------------  
    def dump_historical_tree(self):
        """Dumps patient's historical in form of a tree of health issues
                                                        -> episodes
                                                           -> encounters
                                                              -> clinical items
                                                              
        """

        # fecth all values
        self.__fetch_filtered_items()
        emr = self.__patient.get_clinical_record()

        # dump clinically relevant items summary
        for an_item in self.__filtered_items:
            self.__target.write(self.get_item_summary(an_item, 3))
                
        # begin with the tree
        h_issues = emr.get_health_issues(id_list = self.__constraints['issues'])
        for a_health_issue in h_issues:
            self.__target.write('\n' + 3*' ' + 'Health Issue: ' + a_health_issue['description'] + '\n')
            episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['id']])
            for an_episode in episodes:
               self.__target.write('\n' + 6*' ' + 'Episode: ' + an_episode['description'] + '\n')
               encounters = emr.get_encounters(since=self.__constraints['since'],
                until=self.__constraints['until'], id_list=self.__constraints['encounters'],
                episodes=[an_episode['pk_episode']], issues=[a_health_issue['id']])
               for an_encounter in encounters:
                    # title
                    self.lab_new_encounter = True
                    self.__target.write(
                        '\n         %s %s: %s - %s (%s)\n' % (
                            _('Encounter'),
                            an_encounter['l10n_type'],
                            an_encounter['started'].Format('%A, %Y-%m-%d %H:%M'),
                            an_encounter['last_affirmed'].Format('%m-%d %H:%M'),
                            an_encounter['description']
                        )
                    )
                    self.__target.write(self.dump_encounter_info(an_episode, an_encounter, 12))
                    
    #--------------------------------------------------------
    def dump_clinical_record(self):
        """
        Dumps in ASCII format patient's clinical record
        
        """
        
        emr = self.__patient.get_clinical_record()
        if emr is None:
            _log.Log(gmLog.lErr, 'cannot get EMR text dump')
            print(_(
                'An error occurred while retrieving a text\n'
                'dump of the EMR for the active patient.\n\n'
                'Please check the log file for details.'
            ))
            return None
        self.__target.write('\nOverview\n')
        self.__target.write('--------\n')
        
        self.__target.write("1) Allergy status (for details, see below):\n\n")
        for allergy in     emr.get_allergies():
            self.__target.write("   " + allergy['descriptor'] + "\n\n")
        
        self.__target.write("2) Vaccination status (* indicates booster):\n")
        self.get_vacc_table()
        
        self.__target.write("\n3) Historical:\n\n")
        self.dump_historical_tree()

        try:
            emr.cleanup()
        except:
            print "error cleaning up EMR"
            
    #--------------------------------------------------------
    def dump_med_docs(self):
        """
            Dumps patient stored medical documents

        """
        doc_folder = self.__patient.get_document_folder()

        self.__target.write('\n4) Medical documents: (date) reference - type "comment"\n')
        self.__target.write('                         object - comment')

        docs = doc_folder.get_documents()
        for doc in docs:
            self.__target.write('\n\n   (%s) %s - %s "%s"' % (
                doc['date'].Format('%Y-%m-%d'),
                doc['ext_ref'],
                doc['l10n_type'],
                doc['comment'])
            )
            parts = doc.get_parts()
            for part in parts:
                self.__target.write('\n      %s - %s' % (
                    part['seq_idx'],
                    part['obj_comment'])
                )
        self.__target.write('\n\n')
        
    #--------------------------------------------------------    
    def dump_demographic_record(self, all = False):
        """
            Dumps in ASCII format some basic patient's demographic data
            
        """
        ident = self.__patient.get_identity()
        dump = ident.export_demographics(all)
        if demo is None:
            _log.Log(gmLog.lErr, 'cannot get Demographic export')
            print(_(
                'An error occurred while Demographic record export\n'
                'Please check the log file for details.'
            ))
            return None

        self.__target.write('\n\n\nDemographics')
        self.__target.write('\n------------\n')
        self.__target.write('   Id: ' + str(dump['id']) + '\n')
        for name in dump['names']:
            if dump['names'].index(name) == 0:
                self.__target.write('   Name (Active): ' + name['first'] + ', ' + name['last'] + '\n')
            else:
                self.__target.write('   Name ' + dump['names'].index(name) + ': ' + name['first'] + ', ' +  name['last'] + '\n')
        self.__target.write('   Gender: ' + dump['gender'] + '\n')
        self.__target.write('   Title: ' + dump['title'] + '\n')
        self.__target.write('   Dob: ' + dump['dob'] + '\n')
        self.__target.write('   Medical age: ' + dump['mage'] + '\n')
        addr_types = dump['addresses'].keys()
        for addr_t in addr_types:
            addr_lst = dump['addresses'][addr_t]
            for address in addr_lst:
                self.__target.write('   Address (' + addr_t + '): ' + address + '\n')
                
    #--------------------------------------------------------    
    def dump_constraints(self):
        """
            Dumps exporter filtering constraints
        """
        self.__first_constraint = True
        
        if not self.__constraints['since'] is None:
            self.dump_constraints_header()
            self.__target.write('\nSince: %s' % self.__constraints['since'].Format('%Y-%m-%d'))
        
        if not self.__constraints['until'] is None:
            self.dump_constraints_header()
            self.__target.write('\nUntil: %s' % self.__constraints['until'].Format('%Y-%m-%d'))
        
        if not self.__constraints['encounters'] is None:
            self.dump_constraints_header()
            self.__target.write('\nEncounters: ')
            for enc in self.__constraints['encounters']:
                self.__target.write(str(enc) + ' ')
        
        if not self.__constraints['episodes'] is None:
            self.dump_constraints_header()
            self.__target.write('\nEpisodes: ')
            for epi in self.__constraints['episodes']:
                self.__target.write(str(epi) + ' ')
        
        if not self.__constraints['issues'] is None:
            self.dump_constraints_header()
            self.__target.write('\nIssues: ')
            for iss in self.__constraints['issues']:
                self.__target.write(str(iss) + ' ')
        
    #--------------------------------------------------------    
    def dump_constraints_header(self):
        """
            Dumps constraints header
        """
        if self.__first_constraint == True:
            self.__target.write('\nClinical items dump constraints\n')
            self.__target.write('-'*(len(head_txt)-2))
            self.__first_constraint = False
            
#============================================================
# main
#------------------------------------------------------------
def usage():
    """
        Prints application usage options to stdout.
    """
    print 'usage: python gmPatientExporter [--fileout=<outputfilename>] [--conf-file=<file>] [--text-domain=<textdomain>]'
    sys.exit(0)
    
#------------------------------------------------------------
def parse_constraints():
    """
        Obtains, parses and normalizes config file options
    """
    if isinstance(_cfg, gmNull.cNull):
        usage()

    # Retrieve options
    cfg_group = 'constraints'
    constraints = {
        'since': _cfg.get(cfg_group, 'since'),
        'until': _cfg.get(cfg_group, 'until'),
        'encounters': _cfg.get(cfg_group, 'encounters'),
        'episodes': _cfg.get(cfg_group, 'episodes'),
        'issues': _cfg.get(cfg_group, 'issues')
    }

    # Normalize null constraints (None is interpreted as non existing constraint along all methods)
    for a_constraint in constraints.keys():
        if len(constraints[a_constraint]) == 0:
            constraints[a_constraint] = None
    
    # Cast existing constraints to correct type
    if not constraints['since'] is None:
        constraints['since'] = mxParser.DateFromString(constraints['since'], formats= ['iso'])
    if not constraints['until'] is None:
        constraints['until'] = mxParser.DateFromString(constraints['until'], formats= ['iso'])
    if not constraints['encounters'] is None:
        constraints['encounters'] = map(lambda encounter: int(encounter), constraints['encounters'])
    if not constraints['episodes'] is None:
        constraints['episodes'] = map(lambda episode: int(episode), constraints['episodes'])
    if not constraints['issues'] is None:
        constraints['issues'] = map(lambda issue: int(issue), constraints['issues'])
    
    return constraints
    
#------------------------------------------------------------                
def run():
    """
        Main module application execution loop.
    """
    # Check that output file name is defined and create an instance of exporter
    if gmCLI.has_arg('--fileout'):
        outFile = open(gmCLI.arg['--fileout'], 'wb')
    else:
        usage()
    export_tool = cEmrExport(parse_constraints(), outFile)
    
    # More variable initializations
    patient = None
    patient_id = None
    patient_term = None
    pat_searcher = gmPerson.cPatientSearcher_SQL()

    # App execution loop
    while patient_term != 'bye':
        patient = gmPerson.ask_for_patient()
	if patient is None:
			break
        export_tool.set_patient(patient)
        # Dump patient EMR sections
        export_tool.dump_constraints()
        export_tool.dump_demographic_record(True)
        export_tool.dump_clinical_record()
        export_tool.dump_med_docs()
        
    # Clean ups
    outFile.close()
    export_tool.cleanup()
    if patient is not None:
        try:
            patient.cleanup()
        except:
            print "error cleaning up patient"
            
#------------------------------------------------------------
if __name__ == "__main__":
    gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)

    print "\n\nGnumed Simple EMR ASCII Export Tool"
    print     "==================================="

    if gmCLI.has_arg('--help'):
        usage()

    gmPG.set_default_client_encoding('latin1')
    # make sure we have a connection
    pool = gmPG.ConnectionPool()
    # run main loop
    try:
        run()
    except StandardError:
        traceback.print_exc(file=sys.stdout)
        _log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
    try:
        pool.StopListeners()
    except:
        traceback.print_exc(file=sys.stdout)
        _log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
        
#============================================================
# $Log: gmPatientExporter.py,v $
# Revision 1.40  2005-02-20 08:32:51  sjtan
#
# indentation syntax error.
#
# Revision 1.39  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.38  2005/01/31 13:01:23  ncq
# - use ask_for_patient() in gmPerson
#
# Revision 1.37  2005/01/31 10:19:11  ncq
# - gmPatient -> gmPerson
#
# Revision 1.36  2004/10/26 12:52:56  ncq
# - Carlos: fix conceptual bug by building top-down (eg. issue -> episode
#   -> item) instead of bottom-up
#
# Revision 1.35  2004/10/20 21:43:45  ncq
# - cleanup
# - use allergy['descriptor']
# - Format() dates
#
# Revision 1.34  2004/10/20 11:14:55  sjtan
# restored import for unix. get_historical_tree may of changed, but mainly should
# be guards in gmClinicalRecord for changing [] to None when functions expecting None, and client
# functions passing [].
#
# Revision 1.33  2004/10/12 10:52:40  ncq
# - improve vaccinations handling
#
# Revision 1.32  2004/10/11 19:53:41  ncq
# - document classes are now VOs
#
# Revision 1.31  2004/09/29 19:13:37  ncq
# - cosmetical fixes as discussed with our office staff
#
# Revision 1.30  2004/09/29 10:12:50  ncq
# - Carlos added intuitive vaccination table - muchos improvos !
#
# Revision 1.29  2004/09/10 10:39:01  ncq
# - fixed assignment that needs to be comparison == in lambda form
#
# Revision 1.28  2004/09/06 18:55:09  ncq
# - a bunch of cleanups re get_historical_tree()
#
# Revision 1.27  2004/09/01 21:59:01  ncq
# - python classes can only have one single __init__
# - add in Carlos' code for displaying episode/issue summaries
#
# Revision 1.26  2004/08/23 09:08:53  ncq
# - improve output
#
# Revision 1.25  2004/08/11 09:45:28  ncq
# - format SOAP notes, too
#
# Revision 1.24  2004/08/09 18:41:08  ncq
# - improved ASCII dump
#
# Revision 1.23  2004/07/26 00:02:30  ncq
# - Carlos introduces export of RFE/AOE and dynamic layouting (left margin)
#
# Revision 1.22  2004/07/18 10:46:30  ncq
# - lots of cleanup by Carlos
#
# Revision 1.21  2004/07/09 22:39:40  ncq
# - write to file like object passed to __init__
#
# Revision 1.20  2004/07/06 00:26:06  ncq
# - fail on _cfg is_instance of cNull(), not on missing conf-file option
#
# Revision 1.19  2004/07/03 17:15:59  ncq
# - decouple contraint/patient/outfile handling
#
# Revision 1.18  2004/07/02 00:54:04  ncq
# - constraints passing cleanup by Carlos
#
# Revision 1.17  2004/06/30 12:52:36  ncq
# - cleanup
#
# Revision 1.16  2004/06/30 12:43:10  ncq
# - read opts from config file, cleanup
#
# Revision 1.15  2004/06/29 08:16:35  ncq
# - take output file from command line
# - *search* for patients, don't require knowledge of their ID
#
# Revision 1.14  2004/06/28 16:15:56  ncq
# - still more faulty id_ found
#
# Revision 1.13  2004/06/28 15:52:00  ncq
# - some comments
#
# Revision 1.12  2004/06/28 12:18:52  ncq
# - more id_* -> fk_*
#
# Revision 1.11  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.10  2004/06/26 06:53:25  ncq
# - id_episode -> pk_episode
# - constrained by date range from Carlos
# - dump documents folder, too, by Carlos
#
# Revision 1.9  2004/06/23 22:06:48  ncq
# - cleaner error handling
# - fit for further work by Carlos on UI interface/dumping to file
# - nice stuff !
#
# Revision 1.8  2004/06/20 18:50:53  ncq
# - some exception catching, needs more cleanup
#
# Revision 1.7  2004/06/20 18:35:07  ncq
# - more work from Carlos
#
# Revision 1.6  2004/05/12 14:34:41  ncq
# - now displays nice vaccination tables
# - work by Carlos Moro
#
# Revision 1.5  2004/04/27 18:54:54  ncq
# - adapt to gmClinicalRecord
#
# Revision 1.4  2004/04/24 13:35:33  ncq
# - vacc table update
#
# Revision 1.3  2004/04/24 12:57:30  ncq
# - stop db listeners on exit
#
# Revision 1.2  2004/04/20 13:00:22  ncq
# - recent changes by Carlos to use VO API
#
# Revision 1.1  2004/03/25 23:10:02  ncq
# - gmEmrExport -> gmPatientExporter by Carlos' suggestion
#
# Revision 1.2  2004/03/25 09:53:30  ncq
# - added log keyword
#
