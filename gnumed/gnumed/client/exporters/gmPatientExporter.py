"""GNUmed simple ASCII EMR export tool.

TODO:
- GUI mode:
  - post-0.1 !
  - allow user to select patient
  - allow user to pick episodes/encounters/etc from list
- output modes:
  - HTML - post-0.1 !
"""
#============================================================
__version__ = "$Revision: 1.138 $"
__author__ = "Carlos Moro"
__license__ = 'GPL'

import os.path, sys, types, time, codecs, datetime as pyDT, logging, shutil


import mx.DateTime.Parser as mxParser
import mx.DateTime as mxDT


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmExceptions, gmNull, gmPG2, gmTools
from Gnumed.business import gmClinicalRecord, gmPerson, gmAllergy, gmDemographicRecord, gmClinNarrative, gmPersonSearch


_log = logging.getLogger('gm.export')
_log.info(__version__)
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
        self.__filtered_items = []
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
            _log.error("can't set None patient for exporter")
            return
        self.__patient = patient
    #--------------------------------------------------------
    def set_output_file(self, target=None):
        """
            Sets exporter output file
            
            @param file_name - The file to dump the EMR to
            @type file_name - FileType
        """
        self.__target = target
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
        emr = self.__patient.get_emr()
        # patient dob
        patient_dob = self.__patient['dob']
        date_length = len(patient_dob.strftime('%x')) + 2

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
        txt = '\nDOB: %s' %(patient_dob.strftime('%x')) + '\n'

        # vacc chart table headers
        # top ---- header line
        for column_width in column_widths: 
            txt += column_width * '-' + '-'
        txt += '\n'                   
        # indication names header line
        txt += column_widths[0] * ' ' + '|'
        col_index = 1
        for a_vacc_regime in vacc_regimes:
            txt +=    a_vacc_regime['l10n_indication'] + (column_widths[col_index] - len(a_vacc_regime['l10n_indication'])) * ' ' + '|'
            col_index += 1
        txt +=    '\n'
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
                        vacc_date_str = vacc_date.strftime('%x')
                        txt +=    vacc_date_str + (column_widths[col_index] - len(vacc_date_str)) * ' ' + '|'
                        prev_displayed_date[col_index] = vacc_date
                    except:
                        if row_index == 0: # due first shot
                            due_date = prev_displayed_date[col_index] + vaccinations4regimes[indication][row_index]['age_due_min'] # FIXME 'age_due_min' not properly retrieved
                        else: # due any other than first shot
                            due_date = prev_displayed_date[col_index] + vaccinations4regimes[indication][row_index]['min_interval']
                        txt += '('+ due_date.strftime('%Y-%m-%d') + ')' + (column_widths[col_index] - date_length) * ' ' + '|'
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
                    all_vreg_boosters[cont] = vaccinations[indication][len(vaccinations[indication])-1]['date'].strftime('%Y-%m-%d') # show last given booster date
                    scheduled_booster = vaccinations4regimes[indication][len(vaccinations4regimes[indication])-1]
                    booster_date = vaccinations[indication][len(vaccinations[indication])-1]['date'] + scheduled_booster['min_interval']                                        
                    if booster_date < mxDT.today():
                        all_next_boosters[cont] = '<(' + booster_date.strftime('%Y-%m-%d') + ')>' # next booster is due
                    else:
                        all_next_boosters[cont] = booster_date.strftime('%Y-%m-%d')
                elif len(vaccinations[indication]) == vacc_regimes[cont]['shots']: # just finished vaccinations, begin boosters
                    all_vreg_boosters[cont] = column_widths[cont+1] * ' '
                    scheduled_booster = vaccinations4regimes[indication][len(vaccinations4regimes[indication])-1]
                    booster_date = vaccinations[indication][len(vaccinations[indication])-1]['date'] + scheduled_booster['min_interval']                    
                    if booster_date < mxDT.today():
                        all_next_boosters[cont] = '<(' + booster_date.strftime('%Y-%m-%d') + ')>' # next booster is due
                    else:
                        all_next_boosters[cont] = booster_date.strftime('%Y-%m-%d')
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
            txt +=    str(all_vreg_boosters[col_index-1]) + (column_widths[col_index] - len(str(all_vreg_boosters[col_index-1]))) * ' ' + '|'
            col_index += 1
        txt +=    '\n'
        for column_width in column_widths:              
            txt += column_width * '-' + '-'
        txt += '\n' 

        # next booster
        foot_header = foot_headers[1]
        col_index = 0
        txt += foot_header + (column_widths[0] - len(foot_header)) * ' ' + '|'
        col_index += 1
        for a_vacc_regime in vacc_regimes:
            txt +=    str(all_next_boosters[col_index-1]) + (column_widths[col_index] - len(str(all_next_boosters[col_index-1]))) * ' ' + '|'
            col_index += 1
        txt +=    '\n'
        for column_width in column_widths:
            txt += column_width * '-' + '-'
        txt += '\n'                   

        self.__target.write(txt)        
    #--------------------------------------------------------
    def get_vacc_table(self):
        """
        Iterate over patient scheduled regimes preparing vacc tables dump
        """           
        
        emr = self.__patient.get_emr()
        
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
            if type(a_field) is not types.UnicodeType:
                a_field = unicode(a_field, encoding='latin1', errors='replace')
            txt += u'%s%s%s' % ((offset * u' '), a_field, gmTools.coalesce(item[a_field], u'\n', template_initial = u': %s\n'))
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
#        elif isinstance(item, gmVaccination.cVaccination):
 #           txt += self.get_vaccination_output(item, left_margin)
#        elif isinstance(item, gmPathLab.cLabResult):
 #           txt += self.get_lab_result_output(item, left_margin)
  #          self.lab_new_encounter = False
        return txt
    #--------------------------------------------------------
    def __fetch_filtered_items(self):
        """
            Retrieve patient clinical items filtered by multiple constraints
        """
        if not self.__patient.connected:
            return False
        emr = self.__patient.get_emr()
        filtered_items = []
        filtered_items.extend(emr.get_allergies(
            since=self.__constraints['since'],
            until=self.__constraints['until'],
            encounters=self.__constraints['encounters'],
            episodes=self.__constraints['episodes'],
            issues=self.__constraints['issues']))
#        try:
 #               filtered_items.extend(emr.get_vaccinations(
  #                  since=self.__constraints['since'],
   #                 until=self.__constraints['until'],
    #                encounters=self.__constraints['encounters'],
     #               episodes=self.__constraints['episodes'],
      #              issues=self.__constraints['issues']))
       # except:
        #        _log.error("vaccination error? outside regime")

#        filtered_items.extend(emr.get_lab_results(
 #           since=self.__constraints['since'],
  #          until=self.__constraints['until'],
   #         encounters=self.__constraints['encounters'],
    #        episodes=self.__constraints['episodes'],
     #       issues=self.__constraints['issues']))
        self.__filtered_items = filtered_items
        return True
    #--------------------------------------------------------
    def get_allergy_summary(self, allergy, left_margin = 0):
        """
            Dumps allergy item data summary
            allergy - Allergy item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = _('%sAllergy: %s, %s (noted %s)\n') % (
            left_margin * u' ',
            allergy['descriptor'],
            gmTools.coalesce(allergy['reaction'], _('unknown reaction')),
            allergy['date'].strftime('%x')
        )
#        txt = left_margin * ' ' \
#           + _('Allergy') + ': ' \
#            + allergy['descriptor'] + u', ' \
#            + gmTools.coalesce(allergy['reaction'], _('unknown reaction')) ' ' \
#            + _('(noted %s)') % allergy['date'].strftime('%x') \
#            + '\n'
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
                ' ' + lab_result['val_unit']+ '\n' + '(' + lab_result['req_when'].strftime('%Y-%m-%d') + ')'
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
#        elif isinstance(item, gmVaccination.cVaccination):
 #           txt += self.get_vaccination_summary(item, left_margin)
#        elif isinstance(item, gmPathLab.cLabResult) and \
#	    True: 
 #           #(item['relevant'] == True or item['abnormal'] == True):
  #          txt += self.get_lab_result_summary(item, left_margin)
   #         self.lab_new_encounter = False
        return txt
    #--------------------------------------------------------             
    def refresh_historical_tree(self, emr_tree):
        """
        checks a emr_tree constructed with this.get_historical_tree() 
        and sees if any new items need to be inserted.
        """
        #TODO , caching eliminates tree update time, so don't really need this
        self._traverse_health_issues( emr_tree, self._update_health_issue_branch)
    #--------------------------------------------------------             
    def get_historical_tree( self, emr_tree):
        self._traverse_health_issues( emr_tree, self._add_health_issue_branch)
    #--------------------------------------------------------             
    def _traverse_health_issues(self, emr_tree, health_issue_action):
        """
        Retrieves patient's historical in form of a wx tree of health issues
                                                                                        -> episodes
                                                                                           -> encounters
        Encounter object is associated with item to allow displaying its information
        """
        # variable initialization
        # this protects the emrBrowser from locking up in a paint event, e.g. in
        # some configurations which want to use emrBrowser, but don't stop tabbing
        # to emr browser when no patient selected. the effect is to displace a cNull instance
        # which is a sane representation when no patient is selected.
        if not self.__fetch_filtered_items():
            return
        emr = self.__patient.get_emr()
        unlinked_episodes = emr.get_episodes(issues = [None])
        h_issues = []
        h_issues.extend(emr.get_health_issues(id_list = self.__constraints['issues']))
        # build the tree
        # unlinked episodes
        if len(unlinked_episodes) > 0:
            h_issues.insert(0, {
                'description': _('Unattributed episodes'),
                'pk_health_issue': None
            })
        # existing issues
        for a_health_issue in h_issues:
            health_issue_action( emr_tree, a_health_issue)

        root_item = emr_tree.GetRootItem()
        if len(h_issues) == 0:
            emr_tree.SetItemHasChildren(root_item, False)
        else:
            emr_tree.SetItemHasChildren(root_item, True)
        emr_tree.SortChildren(root_item)
    #--------------------------------------------------------
    def _add_health_issue_branch( self, emr_tree, a_health_issue):
            """appends to a wx emr_tree  , building wx treenodes from the health_issue  make this reusable for non-collapsing tree updates"""
            emr = self.__patient.get_emr()
            root_node = emr_tree.GetRootItem()
            issue_node =  emr_tree.AppendItem(root_node, a_health_issue['description'])
            emr_tree.SetItemPyData(issue_node, a_health_issue)
            episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['pk_health_issue']])
            if len(episodes) == 0:
                emr_tree.SetItemHasChildren(issue_node, False)
            else:
                emr_tree.SetItemHasChildren(issue_node, True)
            for an_episode in episodes:
                self._add_episode_to_tree( emr, emr_tree, issue_node,a_health_issue,  an_episode)
            emr_tree.SortChildren(issue_node)
    #--------------------------------------------------------
    def _add_episode_to_tree( self, emr , emr_tree, issue_node, a_health_issue, an_episode):
        episode_node =  emr_tree.AppendItem(issue_node, an_episode['description'])
        emr_tree.SetItemPyData(episode_node, an_episode)
        if an_episode['episode_open']:
            emr_tree.SetItemBold(issue_node, True)

        encounters = self._get_encounters( an_episode, emr )
        if len(encounters) == 0:
            emr_tree.SetItemHasChildren(episode_node, False)
        else:
            emr_tree.SetItemHasChildren(episode_node, True)
        self._add_encounters_to_tree( encounters,  emr_tree, episode_node )
        emr_tree.SortChildren(episode_node)
        return episode_node
    #--------------------------------------------------------
    def _add_encounters_to_tree( self, encounters, emr_tree, episode_node):
        for an_encounter in encounters:
#            label = u'%s: %s' % (an_encounter['started'].strftime('%Y-%m-%d'), an_encounter['l10n_type'])
            label = u'%s: %s' % (
                an_encounter['started'].strftime('%Y-%m-%d'),
				gmTools.unwrap (
                	gmTools.coalesce (
                    	gmTools.coalesce (
                    	    gmTools.coalesce (
                    	        an_encounter.get_latest_soap (						# soAp
                    	            soap_cat = 'a',
                    	            episode = emr_tree.GetPyData(episode_node)['pk_episode']
                    	        ),
                    	        an_encounter['assessment_of_encounter']				# or AOE
                    	    ),
                    	    an_encounter['reason_for_encounter']					# or RFE
                    	),
                    	an_encounter['l10n_type']									# or type
                	),
                	max_length = 40
                )
            )
            encounter_node_id = emr_tree.AppendItem(episode_node, label)
            emr_tree.SetItemPyData(encounter_node_id, an_encounter)
            emr_tree.SetItemHasChildren(encounter_node_id, False)
    #--------------------------------------------------------
    def _get_encounters ( self, an_episode, emr ):
               encounters = emr.get_encounters (
                   episodes = [an_episode['pk_episode']]
               )
               return encounters
    #--------------------------------------------------------             
    def  _update_health_issue_branch(self, emr_tree, a_health_issue):
		emr = self.__patient.get_emr()
		root_node = emr_tree.GetRootItem()
		id, cookie = emr_tree.GetFirstChild(root_node)
		found = False
		while id.IsOk():
			if emr_tree.GetItemText(id)  ==  a_health_issue['description']:
				found = True
				break
			id,cookie = emr_tree.GetNextChild( root_node, cookie)

		if not found:
			_log.error("health issue %s should exist in tree already", a_health_issue['description'] )
			return
		issue_node = id
		episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['pk_health_issue']])

		#check for removed episode and update tree
		tree_episodes = {} 
		id_episode, cookie = emr_tree.GetFirstChild(issue_node)
		while id_episode.IsOk():
			tree_episodes[ emr_tree.GetPyData(id_episode)['pk_episode'] ]= id_episode
			id_episode,cookie = emr_tree.GetNextChild( issue_node, cookie)

		existing_episode_pk = [ e['pk_episode'] for e in episodes]
		missing_tree_pk = [ pk for pk in tree_episodes.keys() if pk not in existing_episode_pk]
		for pk in missing_tree_pk:
			emr_tree.Remove( tree_episodes[pk] )

		added_episode_pk = [pk for pk in existing_episode_pk if pk not in tree_episodes.keys()]
		add_episodes = [ e for e in episodes if e['pk_episode'] in added_episode_pk]

		#check for added episodes and update tree
		for an_episode in add_episodes:
			node = self._add_episode_to_tree( emr, emr_tree, issue_node, a_health_issue, an_episode)
			tree_episodes[an_episode['pk_episode']] = node

		for an_episode in episodes:
			# found episode, check for encounter change
			try:
				#print "getting id_episode of ", an_episode['pk_episode']
				id_episode = tree_episodes[an_episode['pk_episode']]	
			except:
				import pdb
				pdb.set_trace()
			# get a map of encounters in the tree by pk_encounter as key
			tree_enc = {}
			id_encounter, cookie = emr_tree.GetFirstChild(id_episode)
			while id_encounter.IsOk():
				tree_enc[ emr_tree.GetPyData(id_encounter)['pk_encounter'] ] = id_encounter
				id_encounter,cookie = emr_tree.GetNextChild(id_episode, cookie)

			# remove encounters in tree not in existing encounters in episode
#			encounters = self._get_encounters( a_health_issue, an_episode, emr )
			encounters = self._get_encounters( an_episode, emr )
			existing_enc_pk = [ enc['pk_encounter'] for enc in encounters]
			missing_enc_pk = [ pk  for pk in tree_enc.keys() if pk not in existing_enc_pk]
			for pk in missing_enc_pk:
				emr_tree.Remove( tree_enc[pk] )

			# check for added encounter
			added_enc_pk = [ pk for pk in existing_enc_pk if pk not in tree_enc.keys() ]
			add_encounters = [ enc for enc in encounters if enc['pk_encounter'] in added_enc_pk]
			if add_encounters != []:
				#print "DEBUG found encounters to add"
				self._add_encounters_to_tree( add_encounters, emr_tree, id_episode)
    #--------------------------------------------------------
    def get_summary_info(self, left_margin = 0):
        """
        Dumps patient EMR summary
        """
        txt = ''
        for an_item in self.__filtered_items:
            txt += self.get_item_summary(an_item, left_margin)
        return txt
    #--------------------------------------------------------
    def get_episode_summary (self, episode, left_margin = 0):
        """Dumps episode specific data"""
        emr = self.__patient.get_emr()
        encs = emr.get_encounters(episodes = [episode['pk_episode']])
        if encs is None:
            txt = left_margin * ' ' + _('Error retrieving encounters for episode\n%s') % str(episode)
            return txt
        no_encs = len(encs)
        if no_encs == 0:
            txt = left_margin * ' ' + _('There are no encounters for this episode.')
            return txt
        if episode['episode_open']:
            status = _('active')
        else:
            status = _('finished')
        first_encounter = emr.get_first_encounter(episode_id = episode['pk_episode'])
        last_encounter = emr.get_last_encounter(episode_id = episode['pk_episode'])
        txt = _(
            '%sEpisode "%s" [%s]\n'
            '%sEncounters: %s (%s - %s)\n'
            '%sLast worked on: %s\n'
        ) % (
            left_margin * ' ', episode['description'], status,
            left_margin * ' ', no_encs, first_encounter['started'].strftime('%m/%Y'), last_encounter['last_affirmed'].strftime('%m/%Y'),
            left_margin * ' ', last_encounter['last_affirmed'].strftime('%Y-%m-%d %H:%M')
        )
        return txt
    #--------------------------------------------------------
    def get_encounter_info(self, episode, encounter, left_margin = 0):
        """
        Dumps encounter specific data (rfe, aoe and soap)
        """
        emr = self.__patient.get_emr()
        # general
        txt = (' ' * left_margin) + '#%s: %s - %s   %s' % (
            encounter['pk_encounter'],
            encounter['started'].strftime('%Y-%m-%d %H:%M'),
            encounter['last_affirmed'].strftime('%H:%M (%Z)'),
            encounter['l10n_type']
        )
        if (encounter['assessment_of_encounter'] is not None) and (len(encounter['assessment_of_encounter']) > 0):
            txt += ' "%s"' % encounter['assessment_of_encounter']
        txt += '\n\n'

        # rfe/aoe
        txt += (' ' * left_margin) + '%s: %s\n' % (_('RFE'), encounter['reason_for_encounter'])
        txt += (' ' * left_margin) + '%s: %s\n' % (_('AOE'), encounter['assessment_of_encounter'])

        # soap
        soap_cat_labels = {
            's': _('Subjective'),
            'o': _('Objective'),
            'a': _('Assessment'),
            'p': _('Plan'),
            None: _('Administrative')
        }
        eol_w_margin = '\n' + (' ' * (left_margin+3))
        for soap_cat in 'soapu':
            soap_cat_narratives = emr.get_clin_narrative (
                episodes = [episode['pk_episode']],
                encounters = [encounter['pk_encounter']],
                soap_cats = [soap_cat]
            )
            if soap_cat_narratives is None:
                continue
            if len(soap_cat_narratives) == 0:
                continue
            txt += (' ' * left_margin) + soap_cat_labels[soap_cat] + ':\n'
            for soap_entry in soap_cat_narratives:
                txt += gmTools.wrap (
                    '%s %.8s: %s\n' % (
                        soap_entry['date'].strftime('%d.%m. %H:%M'),
                        soap_entry['provider'],
                        soap_entry['narrative']
                    ), 75
                )

#                txt += (
 #                   (' ' * (left_margin+3)) +
  #                  soap_entry['date'].strftime('%H:%M %.8s: ') % soap_entry['provider'] +
   #                 soap_entry['narrative'].replace('\n', eol_w_margin) +
    #                '\n'
     #           )
		#FIXME: add diagnoses

        # items
        for an_item in self.__filtered_items:
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
        emr = self.__patient.get_emr()

        # dump clinically relevant items summary
        for an_item in self.__filtered_items:
            self.__target.write(self.get_item_summary(an_item, 3))
                
        # begin with the tree
        h_issues = []
        h_issues.extend(emr.get_health_issues(id_list = self.__constraints['issues']))
        # unlinked episodes
        unlinked_episodes = emr.get_episodes(issues = [None])
        if len(unlinked_episodes) > 0:
            h_issues.insert(0, {'description':_('Unattributed episodes'), 'pk_health_issue':None})        
        for a_health_issue in h_issues:
            self.__target.write('\n' + 3*' ' + 'Health Issue: ' + a_health_issue['description'] + '\n')
            episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['pk_health_issue']])
            for an_episode in episodes:
               self.__target.write('\n' + 6*' ' + 'Episode: ' + an_episode['description'] + '\n')
               if a_health_issue['pk_health_issue'] is None:
                  issues = None
               else:
                  issues = [a_health_issue['pk_health_issue']]
               encounters = emr.get_encounters (
                  since = self.__constraints['since'],
                  until = self.__constraints['until'],
                  id_list = self.__constraints['encounters'],
                  episodes = [an_episode['pk_episode']],
                  issues = issues
               )
               for an_encounter in encounters:
                    # title
                    self.lab_new_encounter = True
                    self.__target.write(
                        '\n            %s %s: %s - %s (%s)\n' % (
                            _('Encounter'),
                            an_encounter['l10n_type'],
                            an_encounter['started'].strftime('%A, %Y-%m-%d %H:%M'),
                            an_encounter['last_affirmed'].strftime('%m-%d %H:%M'),
                            an_encounter['assessment_of_encounter']
                        )
                    )
                    self.__target.write(self.get_encounter_info(an_episode, an_encounter, 12))
    #--------------------------------------------------------
    def dump_clinical_record(self):
        """
        Dumps in ASCII format patient's clinical record
        """
        emr = self.__patient.get_emr()
        if emr is None:
            _log.error('cannot get EMR text dump')
            print(_(
                'An error occurred while retrieving a text\n'
                'dump of the EMR for the active patient.\n\n'
                'Please check the log file for details.'
            ))
            return None
        self.__target.write('\nOverview\n')
        self.__target.write('--------\n')
        self.__target.write("1) Allergy status (for details, see below):\n\n")
        for allergy in       emr.get_allergies():
            self.__target.write("    " + allergy['descriptor'] + "\n\n")
        self.__target.write("2) Vaccination status (* indicates booster):\n")
#        self.get_vacc_table()
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
        self.__target.write('                          object - comment')

        docs = doc_folder.get_documents()
        for doc in docs:
            self.__target.write('\n\n    (%s) %s - %s "%s"' % (
                doc['clin_when'].strftime('%Y-%m-%d'),
                doc['ext_ref'],
                doc['l10n_type'],
                doc['comment'])
            )
            for part in doc.parts:
                self.__target.write('\n         %s - %s' % (
                    part['seq_idx'],
                    part['obj_comment'])
                )
        self.__target.write('\n\n')
    #--------------------------------------------------------     
    def dump_demographic_record(self, all = False):
        """
            Dumps in ASCII format some basic patient's demographic data
        """
        if self.__patient is None:
            _log.error('cannot get Demographic export')
            print(_(
                'An error occurred while Demographic record export\n'
                'Please check the log file for details.'
            ))
            return None

        self.__target.write('\n\n\nDemographics')
        self.__target.write('\n------------\n')
        self.__target.write('    Id: %s \n' % self.__patient['pk_identity'])
        cont = 0
        for name in self.__patient.get_names():
            if cont == 0:
                self.__target.write('    Name (Active): %s, %s\n' % (name['firstnames'], name['lastnames']) )
            else:
                self.__target.write('    Name %s: %s, %s\n' % (cont, name['firstnames'], name['lastnames']))
            cont += 1
        self.__target.write('    Gender: %s\n' % self.__patient['gender'])
        self.__target.write('    Title: %s\n' % self.__patient['title'])
        self.__target.write('    Dob: %s\n' % self.__patient.get_formatted_dob(format = '%Y-%m-%d'))
        self.__target.write('    Medical age: %s\n' % self.__patient.get_medical_age())
    #--------------------------------------------------------
    def dump_constraints(self):
        """
            Dumps exporter filtering constraints
        """
        self.__first_constraint = True
        if not self.__constraints['since'] is None:
            self.dump_constraints_header()
            self.__target.write('\nSince: %s' % self.__constraints['since'].strftime('%Y-%m-%d'))

        if not self.__constraints['until'] is None:
            self.dump_constraints_header()
            self.__target.write('\nUntil: %s' % self.__constraints['until'].strftime('%Y-%m-%d'))

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
class cEMRJournalExporter:
	"""Exports patient EMR into a simple chronological journal.

	Note that this export will emit u'' strings only.
	"""
	def __init__(self):
		self.__part_len = 72
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def export_to_file(self, filename=None, patient=None):
		"""Export medical record into a file.

		@type filename: None (creates filename by itself) or string
		@type patient: None (use currently active patient) or <gmPerson.cIdentity> instance
		"""
		if patient is None:
			patient = gmPerson.gmCurrentPatient()
			if not patient.connected:
				raise ValueError('[%s].export_to_file(): no active patient' % self.__class__.__name__)

		if filename is None:
			filename = u'%s-%s-%s-%s.txt' % (
				_('emr-journal'),
				patient['lastnames'].replace(u' ', u'_'),
				patient['firstnames'].replace(u' ', u'_'),
				patient.get_formatted_dob(format = '%Y-%m-%d')
			)
			path = os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'EMR', patient['dirname'], filename))

		f = codecs.open(filename = filename, mode = 'w+b', encoding = 'utf8', errors = 'replace')
		self.export(target = f, patient = patient)
		f.close()
		return filename
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def export(self, target=None, patient=None):
		"""
		Export medical record into a Python object.

		@type target: a python object supporting the write() API
		@type patient: None (use currently active patient) or <gmPerson.cIdentity> instance
		"""
		if patient is None:
			patient = gmPerson.gmCurrentPatient()
			if not patient.connected:
				raise ValueError('[%s].export(): no active patient' % self.__class__.__name__)

		# write header
		txt = _('Chronological EMR Journal\n')
		target.write(txt)
		target.write(u'=' * (len(txt)-1))
		target.write('\n')
		target.write(_('Patient: %s (%s), No: %s\n') % (patient['description'], patient['gender'], patient['pk_identity']))
		target.write(_('Born   : %s, age: %s\n\n') % (
			patient.get_formatted_dob(format = '%x', encoding = gmI18N.get_encoding()),
			patient.get_medical_age()
		))
		target.write(u'.-%10.10s---%9.9s-------%72.72s\n' % (u'-' * 10, u'-' * 9, u'-' * self.__part_len))
		target.write(u'| %10.10s | %9.9s |     | %s\n' % (_('Happened'), _('Doc'), _('Narrative')))
		target.write(u'|-%10.10s---%9.9s-------%72.72s\n' % (u'-' * 10, u'-' * 9, u'-' * self.__part_len))

		# get data
		cmd = u"""
select
	to_char(vemrj.clin_when, 'YYYY-MM-DD') as date,
	vemrj.*,
	(select rank from clin.soap_cat_ranks where soap_cat = vemrj.soap_cat) as scr,
	to_char(vemrj.modified_when, 'YYYY-MM-DD HH24:MI') as date_modified
from clin.v_emr_journal vemrj
where pk_patient = %s
order by date, pk_episode, scr, src_table"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [patient['pk_identity']]}], get_col_idx = True)

		# write data
		prev_date = u''
		prev_doc = u''
		prev_soap = u''
		for row in rows:
			# narrative
			if row['narrative'] is None:
				continue

			txt = gmTools.wrap (
				text = row['narrative'].replace(u'\r', u'') + (u' (%s)' % row['date_modified']),
				width = self.__part_len
			).split('\n')

			# same provider ?
			curr_doc = row['modified_by']
			if curr_doc != prev_doc:
				prev_doc = curr_doc
			else:
				curr_doc = u''

			# same soap category ?
			curr_soap = row['soap_cat']
			if curr_soap != prev_soap:
				prev_soap = curr_soap

			# same date ?
			curr_date = row['date']
			if curr_date != prev_date:
				prev_date = curr_date
				curr_doc = row['modified_by']
				prev_doc = curr_doc
				curr_soap = row['soap_cat']
				prev_soap = curr_soap
			else:
				curr_date = u''

			# display first part
			target.write(u'| %10.10s | %9.9s | %3.3s | %s\n' % (
				curr_date,
				curr_doc,
				gmClinNarrative.soap_cat2l10n[curr_soap],
				txt[0]
			))

			# only one part ?
			if len(txt) == 1:
				continue

			template = u'| %10.10s | %9.9s | %3.3s | %s\n'
			for part in txt[1:]:
				line = template % (u'', u'', u' ', part)
				target.write(line)

		# write footer
		target.write(u'`-%10.10s---%9.9s-------%72.72s\n\n' % (u'-' * 10, u'-' * 9, u'-' * self.__part_len))
		target.write(_('Exported: %s\n') % pyDT.datetime.now().strftime('%c').decode(gmI18N.get_encoding()))

		return
#============================================================
class cMedistarSOAPExporter:
	"""Export SOAP data per encounter into Medistar import format."""
	def __init__(self, patient=None):
		if patient is None:
			self.__pat = gmPerson.gmCurrentPatient()
		else:
			if not isinstance(patient, gmPerson.cIdentity):
				raise gmExceptions.ConstructorError, '<patient> argument must be instance of <cIdentity>, but is: %s' % type(patient)
			self.__pat = patient
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def export_to_file(self, filename=None, encounter=None, soap_cats=u'soapu', export_to_import_file=False):
		if not self.__pat.connected:
			return (False, 'no active patient')

		if filename is None:
			path = os.path.abspath(os.path.expanduser('~/gnumed/export'))
			filename = '%s-%s-%s-%s-%s.txt' % (
				os.path.join(path, 'Medistar-MD'),
				time.strftime('%Y-%m-%d',time.localtime()),
				self.__pat['lastnames'].replace(' ', '-'),
				self.__pat['firstnames'].replace(' ', '_'),
				self.__pat.get_formatted_dob(format = '%Y-%m-%d')
			)

		f = codecs.open(filename = filename, mode = 'w+b', encoding = 'cp437', errors='replace')
		status = self.__export(target = f, encounter = encounter, soap_cats = soap_cats)
		f.close()

		if export_to_import_file:
			# detect "LW:\medistar\inst\soap.txt"
			medistar_found = False
			for drive in u'cdefghijklmnopqrstuvwxyz':
				path = drive + ':\\medistar\\inst'
				if not os.path.isdir(path):
					continue
				try:
					import_fname = path + '\\soap.txt'
					open(import_fname, mode = 'w+b').close()
					_log.debug('exporting narrative to [%s] for Medistar import', import_fname)
					shutil.copyfile(filename, import_fname)
					medistar_found = True
				except IOError:
					continue

			if not medistar_found:
				_log.debug('no Medistar installation found (no <LW>:\\medistar\\inst\\)')

		return (status, filename)
	#--------------------------------------------------------
	def export(self, target, encounter=None, soap_cats=u'soapu'):
		return self.__export(target, encounter = encounter, soap_cats = soap_cats)
	#--------------------------------------------------------
	# interal API
	#--------------------------------------------------------
	def __export(self, target=None, encounter=None, soap_cats=u'soapu'):
		# get data
		cmd = u"select narrative from clin.v_emr_journal where pk_patient=%s and pk_encounter=%s and soap_cat=%s"
		for soap_cat in soap_cats:
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': (self.__pat['pk_identity'], encounter['pk_encounter'], soap_cat)}])
			target.write('*MD%s*\r\n' % gmClinNarrative.soap_cat2l10n[soap_cat])
			for row in rows:
				text = row[0]
				if text is None:
					continue
				target.write('%s\r\n' % gmTools.wrap (
					text = text,
					width = 64,
					eol = u'\r\n'
				))
		return True
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
def run():
    """
        Main module application execution loop.
    """
    # More variable initializations
    patient = None
    patient_id = None
    patient_term = None
    pat_searcher = gmPersonSearch.cPatientSearcher_SQL()

    # App execution loop
    while patient_term != 'bye':
        patient = gmPersonSearch.ask_for_patient()
        if patient is None:
            break
        # FIXME: needed ?
#        gmPerson.set_active_patient(patient=patient)
        exporter = cEMRJournalExporter()
        exporter.export_to_file(patient=patient)
#        export_tool.set_patient(patient)
        # Dump patient EMR sections
#        export_tool.dump_constraints()
#        export_tool.dump_demographic_record(True)
#        export_tool.dump_clinical_record()
#        export_tool.dump_med_docs()

    # Clean ups
#    outFile.close()
#    export_tool.cleanup()
    if patient is not None:
        try:
            patient.cleanup()
        except:
            print "error cleaning up patient"
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
	def export_journal():

		print "Exporting EMR journal(s) ..."
		pat_searcher = gmPersonSearch.cPatientSearcher_SQL()
		while True:
			patient = gmPersonSearch.ask_for_patient()
			if patient is None:
				break

			exporter = cEMRJournalExporter()
			print "exported into file:", exporter.export_to_file(patient=patient)

			if patient is not None:
				try:
					patient.cleanup()
				except:
					print "error cleaning up patient"
		print "Done."
	#--------------------------------------------------------
	print "\n\nGNUmed ASCII EMR Export"
	print     "======================="

	# run main loop
	export_journal()

#============================================================
