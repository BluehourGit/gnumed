"""GnuMed SOAP related widgets.

The code in here is independant of gmPG.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmSOAPWidgets.py,v $
# $Id: gmSOAPWidgets.py,v 1.26 2005-03-17 16:41:30 ncq Exp $
__version__ = "$Revision: 1.26 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std library
import types

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmDispatcher, gmSignals, gmI18N, gmLog, gmExceptions, gmMatchProvider, gmWhoAmI
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.wxpython import gmResizingWidgets, gmPhraseWheel, gmEMRStructWidgets, gmGuiHelpers, gmRegetMixin, gmMultiSash
from Gnumed.business import gmPerson, gmEMRStructItems, gmSOAPimporter

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

NOTE_SAVED = -2

# FIXME attribute encapsulation and private methods
# FIXME i18n
#============================================================
class cMultiSashedProgressNoteInputPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):
	"""
	Basic multi-sash based note input panel.

	Health problems are selected in a list.
	The user can split new soap windows, which are disposed in stack.
	Usability is provided by:
		-Logically enabling/disabling action buttons
		-Controlling user actions and rising informative
		 message boxes when needed.

	Post-0.1? :
		-Add context information widgets

	Currently displays a dynamic stack of note input widgets on the left
	and the health problems list on the right.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""
		Contructs a new instance of SOAP input panel

		@param parent: Wx parent widget
		@param id: Wx widget id
		"""
		print "creating", self.__class__.__name__
		wx.wxPanel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize,
			style = wx.wxNO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__selected_episode = None

		# ui contruction and event handling set up
		self.__do_layout()
		self.__register_interests()
		self._populate_with_data()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.

		left: soap editors
		right: problem list (mix of issues and episodes)
		"""
		# SOAP input panel main splitter window
		self.__splitter = wx.wxSplitterWindow(self, -1)

		# left hand side
		# - soap inputs panel
		PNL_soap_editors = wx.wxPanel(self.__splitter, -1)
		self.__soap_multisash = gmMultiSash.cMultiSash(PNL_soap_editors, -1)				
		#self.__soap_multisash.SetController(self)		# what does this do ?
		# - buttons
		self.__BTN_save = wx.wxButton(PNL_soap_editors, -1, _('&Save'))
		self.__BTN_save.Disable()
		self.__BTN_save.SetToolTipString(_('save focussed progress note into medical record'))

		self.__BTN_clear = wx.wxButton(PNL_soap_editors, -1, _('&Clear'))
		self.__BTN_clear.Disable()
		self.__BTN_clear.SetToolTipString(_('clear focussed progress note'))

		self.__BTN_remove = wx.wxButton(PNL_soap_editors, -1, _('&Remove'))
		self.__BTN_remove.Disable()
		self.__BTN_remove.SetToolTipString(_('close focussed progress note'))
		
		self.__BTN_add_unassociated = wx.wxButton(PNL_soap_editors, -1, _('&Unassociated new progress note'))
		self.__BTN_add_unassociated.SetToolTipString(_('create a progress note that is not at first associated with any episode'))

		# FIXME comment out that button for now until we fully
		# understand how we want it to work.
		#self.__BTN_new = wx.wxButton(PNL_soap_editors, -1, _('&New'))
		#self.__BTN_new.Disable()
		#self.__BTN_new.SetToolTipString(_('create empty progress note for new problem'))

		# - arrange widgets
		szr_btns_left = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns_left.Add(self.__BTN_save, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_clear, 0, wx.wxSHAPED)		
		szr_btns_left.Add(self.__BTN_remove, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_add_unassociated, 0, wx.wxSHAPED)
		szr_left = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_left.Add(self.__soap_multisash, 1, wx.wxEXPAND)
		szr_left.Add(szr_btns_left)
		PNL_soap_editors.SetSizerAndFit(szr_left)

		# right hand side
		# - problem list
		self.__LST_problems = wx.wxListBox (
			self.__splitter,
			-1,
			style= wx.wxNO_BORDER
		)

		# arrange widgets
		self.__splitter.SetMinimumPaneSize(20)
		self.__splitter.SplitVertically(PNL_soap_editors, self.__LST_problems)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.__splitter, 1, wx.wxEXPAND, 0)
		self.SetSizerAndFit(szr_main)
		
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""
		Updates health problems list
		"""
		self.__LST_problems.Clear()
		emr = self.__pat.get_clinical_record()
		problems = emr.get_problems()
		for problem in problems:
			item = '%s (%s)' % (problem['problem'], problem['type'])
			self.__LST_problems.Append(item, problem)
		splitter_width = self.__splitter.GetSizeTuple()[0]
		self.__splitter.SetSashPosition((splitter_width / 2), True)
		return True
		
	#--------------------------------------------------------
	def __update_button_state(self):
		"""
		Check and configure adecuate buttons enabling state
		"""						
		selected_soap = self.__soap_multisash.get_focussed_leaf().get_content()
		# if soap stack is empty, disable save, clear and remove buttons		
		if isinstance(selected_soap, gmMultiSash.cEmptyChild) or selected_soap.IsSaved():
			self.__BTN_save.Enable(False)
			self.__BTN_clear.Enable(False)
			self.__BTN_remove.Enable(False)
		else:
			self.__BTN_save.Enable(True)
			self.__BTN_clear.Enable(True)
			self.__BTN_remove.Enable(True)

		# disabled save button when soap was dumped to backend
		if isinstance(selected_soap, cResizingSoapPanel) and selected_soap.IsSaved():
			self.__BTN_remove.Enable(True)
					
	#--------------------------------------------------------
	#def __get_problem_by_struct_element_REMOVE(self, emr_struct_element):
	#	"""
	#	Retrieve the problem in the list that corresponds with a
	#	issue, episode (both typically selected via dialog) or
	#	problem name (typically in an unassociated note).
	#	"""
	#	result_problem = None
	#
	#	emr = self.__pat.get_clinical_record()
	#
	#	if isinstance(emr_struct_element, gmEMRStructItems.cHealthIssue):
	#		for problem in emr.get_problems():
	#			if problem['pk_health_issue'] == emr_struct_element['id']:
	#				result_problem = problem
	#	elif isinstance(emr_struct_element, gmEMRStructItems.cEpisode):
	#		for problem in emr.get_problems():
	#			if problem['pk_episode'] == emr_struct_element['pk_episode']:
	#				result_problem = problem
	#	elif isinstance(emr_struct_element, types.StringType):
	#		for problem in emr.get_problems():
	#			if problem['problem'] == emr_struct_element:
	#				result_problem = problem					
	#	return result_problem

	#--------------------------------------------------------
	def __make_soap_editor(self):
		"""
		Instantiates a new soap editor. The widget itself (cMultiSashedProgressNoteInputPanel)
		is the temporary parent, as the final one will be the multisash bottom
		leaf (by reparenting).
		"""
		soap_editor = cResizingSoapPanel(self, self.__selected_episode)
		return soap_editor
	#--------------------------------------------------------
	def __get_displayed_episodes(self):
		"""
		Retrieves the list of episodes that are currently displayed in the
		multisash widget.
		"""
		displayed_episodes = []
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:
			content = a_leaf.get_content()
			if isinstance(content, cResizingSoapPanel):
				if content.GetEpisode() == NOTE_SAVED:
					displayed_episodes.append(NOTE_SAVED)
				elif content.GetEpisode() is not None:
					displayed_episodes.append(content.GetEpisode()['description'])
				elif content.GetEpisode() is None:
					displayed_episodes.append(content.GetHeadingTxt())
		return displayed_episodes
		
	#--------------------------------------------------------
	def __get_leaf_for_episode(self, episode):
		"""
		Retrieves the displayed leaf for the given episode (or the first
		is they are multiple, eg. after saving various soap notes).
		@param episode The episode to retrieve the displayed note for.
		@type episode gmEMRStructItems.cEpisode
		"""
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:
			content = a_leaf.get_content()
			if isinstance(content, cResizingSoapPanel) \
			and content.GetEpisode() == episode:
				return a_leaf
		return None
	#--------------------------------------------------------
	def __focus_episode(self, episode_name):
		"""
		Focus in multisash widget the progress note for the given
		episode name.
		
		@param episode_name: The name of the episode to focus
		@type episode_name: string
		"""
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:			
			content = a_leaf.get_content()
			target_name = ''
			
			if content is not None \
				and isinstance(content, cResizingSoapPanel) \
				and content.GetEpisode() != NOTE_SAVED \
				and content.GetEpisode() is not None:
					target_name = content.GetEpisode()['description']
			elif content.GetEpisode() is None:
				target_name = content.GetHeadingTxt()

			if target_name == episode_name:
				a_leaf.Select()
				return
	#--------------------------------------------------------
#	def __check_problem(self, problem_name):
#		"""
#		Check whether the supplied problem (usually, from an unassociated
#		progress note, is an existing episode or we must create a new
#		episode (unattached to any problem).
#
#		@param problem_name: The progress note's problem name to check
#		@type problem: StringType
#		"""
#		emr = self.__pat.get_clinical_record()
#		target_episode = self.__get_problem_by_struct_element(problem_name)
#		if not target_episode is None and isinstance(target_episode, gmEMRStructItems.cEpisode):
#			# the text is not an existing episode, let's create it
#			target_episode = emr.add_episode (episode_name = problem_name)
#		if not target_episode is None:
#			return (True, target_episode)
#		else:
#			return (False, target_episode)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events
		wx.EVT_LISTBOX_DCLICK(self.__LST_problems, self.__LST_problems.GetId(), self.__on_problem_activated)
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self.__on_save)
		wx.EVT_BUTTON(self.__BTN_clear, self.__BTN_clear.GetId(), self.__on_clear)		
		wx.EVT_BUTTON(self.__BTN_remove, self.__BTN_remove.GetId(), self.__on_remove)
		wx.EVT_BUTTON(self.__BTN_add_unassociated, self.__BTN_add_unassociated.GetId(), self.__on_add_unassociated)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self.__on_patient_selected)
		gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self.__on_episodes_modified)
	#--------------------------------------------------------
	def __on_problem_activated(self, event):
		"""
		When the user changes health issue selection, update selected issue
		reference and update buttons according its input status.

		when the user selects a problem in the problem list:
			- check whether selection is issue or episode
			- if issue: create episode
			- if editor for episode exists: focus it
			- if no editor for episode exists: create one and focus it
			- update button status
			- if currently selected editor is an unassociated one and its episode name is empty,
			  set its episode name in phrasewheel
		"""
		print self.__class__.__name__, "-> __on_problem_activated()"
		problem_idx = self.__LST_problems.GetSelection()
		problem = self.__LST_problems.GetClientData(problem_idx)		

		# FIXME: constant in gmEMRStructIssues 
		if problem['type'] == 'issue':
			print "... is issue"
			# health issue selected, show episode selector dialog
			pk_issue = problem['pk_health_issue']
			episode_selector = gmEMRStructWidgets.cEpisodeSelectorDlg (
				None,
				-1,
				_('Create or select episode'),
				_('Add episode and start progress note'),
				pk_health_issue = pk_issue
			)
			retval = episode_selector.ShowModal()
			if retval == gmEMRStructWidgets.dialog_OK:
				# FIXME refresh only if episode selector action button was performed
				print "would be refreshing problem list now"
#				self.__refresh_problem_list()
				self.__selected_episode = episode_selector.get_selected_episode()
				print 'Creating progress note for episode: %s' % self.__selected_episode
			elif retval == gmEMRStructWidgets.dialog_CANCELLED:
				print 'User canceled'
				return False
			else:
				raise Exception('Invalid dialog return code [%s]' % retval)
			episode_selector.Destroy() # finally destroy it when finished.
		elif problem['type'] == 'episode':
			print "... is episode"
			# FIXME: check use of self.__selected_episode whether we can leave it as problem
			self.__selected_episode = self.__pat.get_clinical_record().get_episodes(id_list=[problem['pk_episode']])[0]
		else:
			msg = _('Cannot open progress note editor for problem:\n%s') % problem
			gmGuiHelpers.gm_show_error(msg, _('progress note editor'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid problem type [%s]' % type(problem))
			return False
				
		episode_name = self.__selected_episode['description']
		if episode_name not in self.__get_displayed_episodes():
			focused_widget = self.__soap_multisash.get_focussed_leaf().get_content()
			if isinstance(focused_widget, cResizingSoapPanel) and (focused_widget.GetEpisode() is None or focused_widget.GetEpisode() == NOTE_SAVED) and focused_widget.GetHeadingTxt().strip() == '':
				# configure episode name in unassociated progress note
				focused_widget = self.__soap_multisash.get_focussed_leaf().get_content()		
				focused_widget.SetHeadingTxt(self.__selected_episode['description'])
				return
			# let's create new note for the selected episode
			if NOTE_SAVED in self.__get_displayed_episodes():
				# there are some displayed empty notes (after saving)
				# set the selected problem in first of them
				leaf = self.__get_leaf_for_episode(episode = NOTE_SAVED)
				leaf.get_content().SetEpisode(self.__selected_episode)
			else:
				# create note in new leaf, always on bottom
				successful, errno = self.__soap_multisash.add_content(content = self.__make_soap_editor())
				# FIXME: actually, one would have to check errno but there is only one error number so far
				if not successful:
					msg = _('Cannot open progress note editor for\n\n'
							'[%s]\n\n'
							'The GnuMed window is too small. Please enlarge\n'
							'the lowermost editor and try again.') % problem['problem']
					gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening progress note editor'))
		else:
			# let's find and focus the displayed note for the selected episode
			self.__focus_episode(episode_name)
		self.__update_button_state()

	#--------------------------------------------------------
	def __on_patient_selected(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def __on_episodes_modified(self):
		print "episodes modified ..."
		self._schedule_data_reget()
	#--------------------------------------------------------
	def __on_save(self, event):
		"""
		Obtain SOAP data from selected editor and dump to backend
		"""
		emr = self.__pat.get_clinical_record()
		focussed_leaf = self.__soap_multisash.get_focussed_leaf()
		soap_widget = focussed_leaf.get_content()
		soap_editor = soap_widget.get_editor()
		episode = soap_widget.GetEpisode()
		# do we need to create a new episode ?
		if episode is None:
			episode_name = soap_widget.GetHeadingTxt()
			if episode_name is None or episode_name.strip() == '':
				msg = _('Need a name for the new episode to save new progress note under.\n'
						'Please type a new episode name or select an existing one from the list.')
				gmGuiHelpers.gm_show_error(msg, _('saving progress note'), gmLog.lErr)
				return False
			emr = self.__pat.get_clinical_record()
			episode = emr.add_episode(episode_name = episode_name)
#			stat, problem = self.__check_problem(episode_name)
#			if not stat:
			if episode is None:
				msg = _('Cannot create episode [%s] to save progress note under.' % episode_name)
				gmGuiHelpers.gm_show_error(msg, _('saving progress note'), gmLog.lErr)
				return False
			print "SAVING UNASSOCIATED note for episode: %s " % episode
		# set up clinical context in soap bundle
		encounter = emr.get_active_encounter()
		staff_id = gmWhoAmI.cWhoAmI().get_staff_ID()
		clin_ctx = {
			gmSOAPimporter.soap_bundle_EPISODE_ID_KEY: episode['pk_episode'],
			gmSOAPimporter.soap_bundle_ENCOUNTER_ID_KEY: encounter['pk_encounter'],
			gmSOAPimporter.soap_bundle_STAFF_ID_KEY: staff_id
		}
		# fill bundle for import
		bundle = []
		editor_content = soap_editor.GetValue()
		print editor_content
#		for input_label in editor_content.keys():
		for input_label in editor_content.values():
			print "Data: %s" % input_label.data
			print "Value: %s" % input_label.value
#			narr = editor_content[input_label].value
#			if isinstance(narr, gmClinNarrative.cNarrative):
#				# double-check staff_id vs. narr['who owns it']
#				print "updating existing narrative"
#				narr['narrative'] = editor_content['text']
#				narr['soap_cat'] = editor_content['soap_cat']
#				successful, data = narr.save_payload()
#				if not successful:
					# FIXME: pop up error dialog etc.
#					print "cannot update narrative"
#					print data
#					continue
				# FIXME: update associated types list
 				# FIXME: handle embedded structural data list
#				continue
			bundle.append ({
				gmSOAPimporter.soap_bundle_SOAP_CAT_KEY: input_label.data['soap_cat'],
				gmSOAPimporter.soap_bundle_TYPES_KEY: [],		# these types need to come from the editor
				gmSOAPimporter.soap_bundle_TEXT_KEY: input_label.value,
				gmSOAPimporter.soap_bundle_CLIN_CTX_KEY: clin_ctx,
				gmSOAPimporter.soap_bundle_STRUCT_DATA_KEY: {}	# this data needs to come from the editor
			})

		# let's dump soap contents		   
		print 'Saving: %s' % bundle
		#importer = gmSOAPimporter.cSOAPImporter()
		#importer.import_soap(bundle)
				
		# update buttons
		soap_widget.SetSaved(True)
		self.__update_button_state()
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""
		Clear currently selected SOAP input widget
		"""
			
		selected_soap = self.__soap_multisash.get_focussed_leaf().get_content()
		selected_soap.Clear()

	#--------------------------------------------------------
	def __on_add_unassociated(self, evt):
		"""
		Create and display a new SOAP input widget on the stack for an unassociated
		progress note.
		"""
		successful, errno = self.__soap_multisash.add_content(content = cResizingSoapPanel(self))
		# FIXME: actually, one would have to check errno but there is only one error number so far
		if not successful:
			msg = _('Cannot open progress note editor for\n\n'
					'[%s]\n\n'
					'The GnuMed window is too small. Please enlarge\n'
					'the lowermost editor and try again.') % problem['problem']
			gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening progress note editor'))
		self.__update_button_state()
				
	#--------------------------------------------------------
	def __on_remove(self, event):
		"""
		Removes currently selected SOAP input widget
		"""

		print "remove SOAP input widget"
		selected_leaf = self.__soap_multisash.get_focussed_leaf()
		selected_leaf.DestroyLeaf()

		#print "problems with soap: %s" % (self.__managed_episodes)
		# there's no leaf selected after deletion, so disable all buttons
		self.__BTN_save.Disable()
		self.__BTN_clear.Disable()
		self.__BTN_remove.Disable()
		# enable new button is soap stack is empty
		#selected_leaf = self.__soap_multisash.GetSelectedLeaf()
		#if self.__selected_soap.GetHealthIssue() is None:
		#	self.__BTN_new.Enable(True)
		
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
		#self.reset_ui_content()
		if self.__refresh_problem_list():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	#def activate_selected_problem(self):
	#	"""
	#	Activate the currently selected problem, simulating double clicking
	#	over the problem in the list and therefore, firing the actions
	#	to create a new soap for the problem.
	#	"""
	#	self.__on_problem_activated(None)
	#	
	#--------------------------------------------------------
	#def get_selected_episode(self):
	#	"""
	#	Retrieves selected episode in list
	#	"""
	#	return self.__selected_episode

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self.__selected_episode = None
		#self.__managed_episodes = []
		self.__LST_problems.Clear()
		self.__soap_multisash.Clear()
#============================================================
# Old Log for: gmSoapPlugins.py,v in test_area:
#
# Revision 1.29  2005/03/14 20:55:25  cfmoro
# Let saved unassociated note be reused on new problem activation. Minot clean ups
#
# Revision 1.28  2005/03/14 18:22:22  cfmoro
# Passing episodes instead of problems to soap editor. Clean ups
#
# Revision 1.27  2005/03/14 14:49:05  ncq
# - ongoing work/cleanup
# - self.__emr is dangerous, use self.__pat.get_clinical_record()
#
# Revision 1.26  2005/03/13 09:04:34  cfmoro
# Added intial support for unassociated progress notes
#
# Revision 1.25  2005/03/03 21:34:23  ncq
# - cleanup
# - start implementing saving existing narratives
#
# Revision 1.24  2005/02/24 20:03:02  cfmoro
# Fixed bug when focusing and any of the content is None
#
# Revision 1.23  2005/02/23 19:41:26  ncq
# - listen to episodes_modified() signal instead of manual refresh
# - cleanup, renaming, pretty close to being moved to main trunk
#
# Revision 1.22  2005/02/23 03:19:02  cfmoro
# Fixed bug while refreshing leafs, using recursivity. On save, clear the editor and reutilize on future notes. Clean ups
#
# Revision 1.21  2005/02/22 18:22:31  ncq
# - cleanup
#
# Revision 1.20  2005/02/21 23:44:59  cfmoro
# Commented out New button. Focus editor when trying to add and existing one. Clean ups
#
# Revision 1.19  2005/02/21 11:52:37  cfmoro
# Ported action of buttons to recent changes. Begin made them functional
#
# Revision 1.18  2005/02/21 10:20:46  cfmoro
# Class renaming
#
# Revision 1.17  2005/02/17 16:46:20  cfmoro
# Adding and removing soap editors. Simplified multisash interface.
#
# Revision 1.16  2005/02/16 11:19:12  ncq
# - better error handling
# - tabified
# - get_bottom_leaf() verified
#
# Revision 1.15  2005/02/14 00:58:37  cfmoro
# Restarted the adaptation of multisash widget to make it completely usable for GnuMed while keeping it generic and not SOAP dependent. Advance step by step. Step 1: Disabled leaf creators, create new widgets on bottom and keep consistency while deleting leafs
#
# Revision 1.14  2005/02/09 20:19:58  cfmoro
# Making soap editor made factory function outside SOAPMultiSash
#
# Revision 1.13  2005/02/08 11:36:11  ncq
# - lessen reliance on implicit callbacks
# - make things more explicit, eg Pythonic
#
# Revision 1.12  2005/02/02 21:43:13  cfmoro
# Adapted to recent gmEMRStructWidgets changes. Multiple editors can be created
#
# Revision 1.11  2005/01/31 13:06:02  ncq
# - use gmPerson.ask_for_patient()
#
# Revision 1.10  2005/01/31 09:50:59  ncq
# - gmPatient -> gmPerson
#
# Revision 1.9  2005/01/29 18:04:58  ncq
# - cleanup/added "$ Log" CVS keyword
#
#============================================================
class cSOAPLineDef:
	def __init__(self):
		self.label = _('label missing')
		self.text = ''
		self.data = {
			'soap_cat': _('soap cat missing'),
			'narrative instance': None
		}
#============================================================
class cResizingSoapWin (gmResizingWidgets.cResizingWindow):

	def __init__(self, parent, size, input_defs=None):
		"""Resizing SOAP note input editor.

		Labels and categories are customizable.

		@param input_defs: note's labels and categories
		@type input_defs: list of cSOAPLineDef instances
		"""
		if input_defs is None or len(input_defs) == 0:
			raise gmExceptions.ConstructorError, 'cannot generate note with field defs [%s]' % (input_defs)
		self.__input_defs = input_defs
		gmResizingWidgets.cResizingWindow.__init__(self, parent, id= -1, size=size)
	#--------------------------------------------------------
	def DoLayout(self):
		"""Visually display input note according to user defined labels.
		"""
		input_fields = []
		# add fields to edit widget
		# note: this may produce identically labelled lines
		for line_def in self.__input_defs:
			input_field = gmResizingWidgets.cResizingSTC(self, -1, data = line_def.data)
			input_field.SetText(line_def.text)
			self.AddWidget(widget=input_field, label=line_def.label)
			self.Newline()
			input_fields.append(input_field)
		# setup tab navigation between input fields
		for field_idx in range(len(input_fields)):
			# previous
			try:
				input_fields[field_idx].prev_in_tab_order = input_fields[field_idx-1]
			except IndexError:
				input_fields[field_idx].prev_in_tab_order = None
			# next
			try:
				input_fields[field_idx].next_in_tab_order = input_fields[field_idx+1]
			except IndexError:
				input_fields[field_idx].next_in_tab_order = None
		# FIXME: PENDING keywords set up
		#kwds = {}
		#kwds['$test_keyword'] = {'widget_factory': create_widget_on_test_kwd2}
		#self.input2.set_keywords(popup_keywords=kwds)
		# FIXME: pending matcher setup

#============================================================
class cResizingSoapPanel(wx.wxPanel):
	"""Basic progress note panel.

	It provides a gmResizingWindow based progress note editor
	with a header line. The header either displays the episode
	this progress note is associated with or it allows for
	entering an episode name. The episode name either names
	an existing episode or is the name for a new episode.

	Can work as:
		a) Progress note creation: displays an empty set of soap entries to
		create a new soap note for the given episode (or unassociated)
		b) Progress note editor: displays the narrative entries (format and
		narrative text) encapsulated in each element of input_defs.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, episode=None, input_defs=None):
		"""
		Construct a new SOAP input widget.

		@param parent: the parent widget

		@param episode: the episode to create the SOAP editor for.
		@type episode gmEMRStructItems.cEpisode instance or None (to create an
		unassociated progress note). A gmEMRStructItems.cProblem instance is 
		also allowed to be passed, as the widget will obtain the related cEpisode.

		@param input_defs: the display and associated data for each displayed narrative
		@type input_defs: a list of cSOAPLineDef instances

		"""
		# problem -> episode conversion
		if isinstance(episode, gmEMRStructItems.cProblem):
			old_epi = episode
			episode = episode.get_as_episode()
			if episode is None:
				raise gmExceptions.ConstructorError, 'cannot make progress note editor for [%s]' % str(old_epi)
		# sanity check
		if not isinstance(episode, gmEMRStructItems.cEpisode):
			raise gmExceptions.ConstructorError, 'cannot make progress note editor for [%s]' % str(episode)
		self.__episode = episode
		# do layout
		wx.wxPanel.__init__ (self,
			parent,
			-1,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		# - heading
		if episode is None:
			mp = gmMatchProvider.cMatchProvider_Func (
				get_candidates = self.get_episode_list
			)
			self.__soap_heading = gmPhraseWheel.cPhraseWheel (
				self,
				-1,
				aMatchProvider = mp
			)
		else:
			self.__soap_heading = wx.wxStaticText (
				self,
				-1,
				_('episode: %s') % self.__episode['description']
			)
		# - editor
		if input_defs is None:
			soap_lines = []
			# make Richard the default ;-)
			line = cSOAPLineDef()
			line.label = _('Patient Request')
			line.data['soap_cat'] = 's'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('History Taken')
			line.data['soap_cat'] = 's'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Findings')
			line.data['soap_cat'] = 'o'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Assessment')
			line.data['soap_cat'] = 'a'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Plan')
			line.data['soap_cat'] = 'p'
			soap_lines.append(line)
		else:
			soap_lines = input_defs
		self.__soap_text_editor = cResizingSoapWin (
			self,
			size = wx.wxSize(300, 150),
			input_defs = soap_lines
		)
		# - arrange
		self.__szr_main = wx.wxFlexGridSizer(cols = 1, rows = 3, vgap = 4, hgap = 4)
		self.__szr_main.Add(self.__soap_heading, 1, wx.wxEXPAND)
		self.__szr_main.Add(self.__soap_text_editor, 0, wx.wxSHAPED)
		self.SetSizerAndFit(self.__szr_main)

		self.__is_saved = False
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def SetEpisode(self, episode):
		"""
		Set the related episode for this SOAP input widget.
		Update heading label with episode descriptive text.
		
		@param episode: SOAP input widget's related episode
		@type episode: gmEMRStructItems.cEpisode		
		"""
		if episode is None:
			# FIXME: need handling when unsetting episode
			return False
		self.__episode = episode
		# display episode
		txt = _('episode: %s') % self.__episode['description']
		self.__set_heading(txt)
		# flag indicating saved state
		self.__is_saved = False
	#--------------------------------------------------------
	def GetEpisode(self):
		"""
		Retrieve the related episode for this SOAP input widget.
		"""
		return self.__episode
	#--------------------------------------------------------
	def get_episode_list(self):
		# match provider helper
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_clinical_record()
		episodes = emr.get_episodes()
		epi_list = []
		for epi in episodes:
			epi_list.append({'label': epi['description'], 'data': epi['description']})
		print epi_list
		return epi_list
	#--------------------------------------------------------
	def GetHeadingTxt(self):
		"""
		Retrieve the header displayed text. Typically useful to obtain
		the entered episode text in an unassociated progress note.
		"""
		txt = ''
		if self.__episode is None:
			txt = self.__soap_heading.GetValue()
		else:
			txt = self.__soap_heading.GetLabel()
		return txt
	#--------------------------------------------------------
	def SetHeadingTxt(self, txt):
		"""
		Set the header displayed text (only for an unassociated
		progress note).

		@param txt: The heading text to set (episode name)
		@param txt: StringType
		"""
		if isinstance(self.__soap_heading, gmPhraseWheel.cPhraseWheel):
			self.__set_heading(txt)
		else:
			msg = _('Cannot change the episode description for current note.')
			gmGuiHelpers.gm_show_error(msg, _('changing episode description'), gmLog.lErr)
	#--------------------------------------------------------
	def get_editor(self):
		"""
		Retrieves widget's SOAP text editor
		"""
		return self.__soap_text_editor
	#--------------------------------------------------------
	def Clear(self):
		"""Clear any entries in widget's SOAP text editor
		"""
		self.__soap_text_editor.Clear()
	#--------------------------------------------------------
	def SetSaved(self, is_saved):
		"""
		Set SOAP input widget saved (dumped to backend) state

		@param is_saved: Flag indicating wether the SOAP has been dumped to
						 persistent backend
		@type is_saved: boolean
		"""
		self.__is_saved = is_saved
		self.__set_heading('')
		self.Clear()
		self.__episode = NOTE_SAVED
	#--------------------------------------------------------
	def IsSaved(self):
		"""
		Check  SOAP input widget saved (dumped to backend) state
		"""
		return self.__is_saved
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __set_heading(self, txt):
		"""
		Configure SOAP widget's heading title (both for associated
		and unassociated progress note).

		@param txt: New widget's heading title to set
		@type txt: string
		"""
		if isinstance(self.__soap_heading, gmPhraseWheel.cPhraseWheel):
			self.__soap_heading.SetValue(txt)
		else:
			self.__soap_heading.SetLabel(txt)
			size = self.__soap_heading.GetBestSize()
			self.__szr_main.SetItemMinSize(self.__soap_heading, size.width, size.height)
			self.Layout()
		
#============================================================
class cSingleBoxSOAP(wx.wxTextCtrl):
	"""if we separate it out like this it can transparently gain features"""
	def __init__(self, *args, **kwargs):
		wx.wxTextCtrl.__init__(self, *args, **kwargs)
#============================================================
class cSingleBoxSOAPPanel(wx.wxPanel):
	"""Single Box free text SOAP input.

	This widget was suggested by David Guest on the mailing
	list. All it does is provide a single multi-line textbox
	for typing free-text clinical notes which are stored as
	Subjective.
	"""
	def __init__(self, *args, **kwargs):
		wx.wxPanel.__init__(self, *args, **kwargs)
		self.__do_layout()
		self.__pat = gmPerson.gmCurrentPatient()
		if not self.__register_events():
			raise gmExceptions.ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		# large box for free-text clinical notes
		self.__soap_box = cSingleBoxSOAP (
			self,
			-1,
			'',
			style = wx.wxTE_MULTILINE
		)
		# buttons below that
		self.__BTN_save = wx.wxButton(self, wx.wxNewId(), _("save"))
		self.__BTN_save.SetToolTipString(_('save clinical note in EMR'))
		self.__BTN_discard = wx.wxButton(self, wx.wxNewId(), _("discard"))
		self.__BTN_discard.SetToolTipString(_('discard clinical note'))
		szr_btns = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns.Add(self.__BTN_save, 1, wx.wxALIGN_CENTER_HORIZONTAL, 0)
		szr_btns.Add(self.__BTN_discard, 1, wx.wxALIGN_CENTER_HORIZONTAL, 0)
		# arrange widgets
		szr_outer = wx.wxStaticBoxSizer(wx.wxStaticBox(self, -1, _("clinical progress note")), wx.wxVERTICAL)
		szr_outer.Add(self.__soap_box, 1, wx.wxEXPAND, 0)
		szr_outer.Add(szr_btns, 0, wx.wxEXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self._on_save_note)
		wx.EVT_BUTTON(self.__BTN_discard, self.__BTN_discard.GetId(), self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._save_note)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._save_note)

		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_note(self, event):
		self.__save_note()
		#event.Skip()
	#--------------------------------------------------------
	def _on_discard_note(self, event):
		# FIXME: maybe ask for confirmation ?
		self.__soap_box.SetValue('')
		#event.Skip()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _save_note(self):
		wx.wxCallAfter(self.__save_note)
	#--------------------------------------------------------
	def __save_note(self):
		# sanity checks
		if self.__pat is None:
			return True
		if not self.__pat.is_connected():
			return True
		if not self.__soap_box.IsModified():
			return True
		note = self.__soap_box.GetValue()
		if note.strip() == '':
			return True
		# now save note
		emr = self.__pat.get_clinical_record()
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot access clinical record of patient')
			return False
		if not emr.add_clin_narrative(note, soap_cat='s'):
			_log.Log(gmLog.lErr, 'error saving clinical note')
			return False
		self.__soap_box.SetValue('')
		return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	def get_narrative(pk_encounter=None, pk_health_issue = None, default_labels=None):
		"""
		Retrieve the soap editor input lines definitions built from
		all the narratives for the given issue along a specific
		encounter.
		
		@param pk_health_issue The id of the health issue to obtain the narratives for.
		@param pk_health_issue An integer instance

		@param pk_encounter The id of the encounter to obtain the narratives for.
		@type A gmEMRStructItems.cEncounter instance.

		@param default_labels: The user customized labels for each
		soap category.
		@type default_labels: A dictionary instance which keys are
		soap categories.
		"""
		
		# custom labels
		if default_labels is None:
			default_labels = {
				's': _('History Taken'),
				'o': _('Findings'),
				'a': _('Assessment'),
				'p': _('Plan')
		}		
		
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_clinical_record()
		soap_lines = []
		# for each soap cat
		for soap_cat in gmSOAPimporter.soap_bundle_SOAP_CATS:
			# retrieve narrative for given encounter
			narr_items =  emr.get_clin_narrative (
				encounters = [pk_encounter],
				issues = [pk_health_issue],
				soap_cats = [soap_cat]
			)
			for narrative in narr_items:
				try:
					# FIXME: add more data such as doctor sig
					label_txt = default_labels[narrative['soap_cat']]
				except:
					label_txt = narrative['soap_cat']				
				line = cSOAPLineDef()
				line.label = label_txt
				line.text = narrative['narrative']
				line.data['narrative instance'] = narrative
				soap_lines.append(line)
		return soap_lines


	def create_widget_on_test_kwd1(*args, **kwargs):
		print "test keyword must have been typed..."
		print "actually this would have to return a suitable wxWindow subclass instance"
		print "args:", args
		print "kwd args:"
		for key in kwargs.keys():
			print key, "->", kwargs[key]

	def create_widget_on_test_kwd2(*args, **kwargs):
		msg = (
			"test keyword must have been typed...\n"
			"actually this would have to return a suitable wxWindow subclass instance\n"
		)
		for arg in args:
			msg = msg + "\narg ==> %s" % arg
		for key in kwargs.keys():
			msg = msg + "\n%s ==> %s" % (key, kwargs[key])
		gmGuiHelpers.gm_show_info (
			aMessage = msg,
			aTitle = 'msg box on create_widget from test_keyword'
		)

	_log.SetAllLogLevels(gmLog.lData)

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
	
		# multisash soap
		print 'testing multisashed soap input...'
		application = wx.wxPyWidgetTester(size=(800,500))
		soap_input = cMultiSashedProgressNoteInputPanel(application.frame, -1)
		application.frame.Show(True)
		application.MainLoop()
				
		# soap widget displaying all narratives for an issue along an encounter
		print 'testing soap editor for encounter narratives...'
		episode = gmEMRStructItems.cEpisode(aPK_obj=1)
		encounter = gmEMRStructItems.cEncounter(aPK_obj=1)
		narrative = get_narrative(pk_encounter = encounter['pk_encounter'], pk_health_issue = episode['pk_health_issue'])
		default_labels = {'s':'Subjective', 'o':'Objective', 'a':'Assesment', 'p':'Plan'}
		app = wx.wxPyWidgetTester(size=(300,500))		
		app.SetWidget(cResizingSoapPanel, episode, narrative)
		app.MainLoop()
		del app				
		
		# soap progress note for episode
		print 'testing soap editor for episode...'
		app = wx.wxPyWidgetTester(size=(300,300))
		app.SetWidget(cResizingSoapPanel, episode)
		app.MainLoop()
		del app
		
		# soap progress note for problem
		print 'testing soap editor for problem...'
		problem = gmEMRStructItems.cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': 1})		
		app = wx.wxPyWidgetTester(size=(300,300))
		app.SetWidget(cResizingSoapPanel, problem)
		app.MainLoop()
		del app		
		
		# unassociated soap progress note
		print 'testing unassociated soap editor...'
		app = wx.wxPyWidgetTester(size=(300,300))
		app.SetWidget(cResizingSoapPanel, None)
		app.MainLoop()
		del app		
		
		# unstructured progress note
		print 'testing unstructured progress note...'
		app = wx.wxPyWidgetTester(size=(600,600))
		app.SetWidget(cSingleBoxSOAPPanel, -1)
		app.MainLoop()
		
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

#============================================================
# $Log: gmSOAPWidgets.py,v $
# Revision 1.26  2005-03-17 16:41:30  ncq
# - properly allow explicit None episodes to indicate "unassociated"
#
# Revision 1.25  2005/03/17 13:35:23  ncq
# - some cleanup
#
# Revision 1.24  2005/03/16 19:29:22  cfmoro
# cResizingSoapPanel accepting cProblem instance of type episode
#
# Revision 1.23  2005/03/16 17:47:30  cfmoro
# Minor fixes after moving the file. Restored test harness
#
# Revision 1.22  2005/03/15 08:07:52  ncq
# - incorporated cMultiSashedProgressNoteInputPanel from Carlos' test area
# - needs fixing/cleanup
# - test harness needs to be ported
#
# Revision 1.21  2005/03/14 21:02:41  cfmoro
# Handle changing text in unassociated notes
#
# Revision 1.20  2005/03/14 18:41:53  cfmoro
# Indent fix
#
# Revision 1.19  2005/03/14 18:39:49  cfmoro
# Clear phrasewheel on saving unassociated note
#
# Revision 1.18  2005/03/14 17:36:51  cfmoro
# Added unit test for unassociated progress note
#
# Revision 1.17  2005/03/14 14:39:18  ncq
# - somewhat improve Carlos' support for unassociated progress notes
#
# Revision 1.16  2005/03/13 09:05:06  cfmoro
# Added intial support for unassociated progress notes
#
# Revision 1.15  2005/03/09 19:41:18  cfmoro
# Decoupled cResizingSoapPanel from editing problem-encounter soap notes use case
#
# Revision 1.14  2005/03/04 19:44:28  cfmoro
# Minor fixes from unit test
#
# Revision 1.13  2005/03/03 21:12:49  ncq
# - some cleanups, switch to using data transfer classes
#   instead of complex and unwieldy dictionaries
#
# Revision 1.12  2005/02/23 03:20:44  cfmoro
# Restores SetProblem function. Clean ups
#
# Revision 1.11  2005/02/21 19:07:42  ncq
# - some cleanup
#
# Revision 1.10  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.9  2005/01/28 18:35:42  cfmoro
# Removed problem idx number
#
# Revision 1.8  2005/01/18 13:38:24  ncq
# - cleanup
# - input_defs needs to be list as dict does not guarantee order
# - make Richard-SOAP the default
#
# Revision 1.7  2005/01/17 19:55:28  cfmoro
# Adapted to receive cProblem instances for SOAP edition
#
# Revision 1.6  2005/01/13 14:28:07  ncq
# - cleanup
#
# Revision 1.5  2005/01/11 08:12:39  ncq
# - fix a whole bunch of bugs from moving to main trunk
#
# Revision 1.4  2005/01/10 20:14:02  cfmoro
# Import sys
#
# Revision 1.3  2005/01/10 17:50:36  ncq
# - carry over last bits and pieces from test-area
#
# Revision 1.2  2005/01/10 17:48:03  ncq
# - all of test_area/cfmoro/soap_input/gmSoapWidgets.py moved here
#
# Revision 1.1  2005/01/10 16:14:35  ncq
# - soap widgets independant of the backend (gmPG) live in here
#
# Revision 1.13	 2004/06/30 20:33:41  ncq
# - add_clinical_note() -> add_clin_narrative()
#
# Revision 1.12	 2004/03/09 07:54:32  ncq
# - can call __save_note() from button press handler directly
#
# Revision 1.11	 2004/03/08 23:35:10  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.10	 2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.9	2004/02/05 23:49:52	 ncq
# - use wxCallAfter()
#
# Revision 1.8	2003/11/09 14:29:11	 ncq
# - new API style in clinical record
#
# Revision 1.7	2003/10/26 01:36:13	 ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.6	2003/07/05 12:57:23	 ncq
# - catch one more error on saving note
#
# Revision 1.5	2003/06/26 22:26:04	 ncq
# - streamlined _save_note()
#
# Revision 1.4	2003/06/25 22:51:24	 ncq
# - now also handle signale application_closing()
#
# Revision 1.3	2003/06/24 12:57:05	 ncq
# - actually connect to backend
# - save note on patient change and on explicit save request
#
# Revision 1.2	2003/06/22 16:20:33	 ncq
# - start backend connection
#
# Revision 1.1	2003/06/19 16:50:32	 ncq
# - let's make something simple but functional first
#
#
