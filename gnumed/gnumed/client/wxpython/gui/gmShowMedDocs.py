#!/usr/bin/env python
#----------------------------------------------------------------
"""
This is a no-frills document display handler for the
GNUmed medical document database.

It knows nothing about the documents itself. All it does
is to let the user select a page to display and tries to
hand it over to an appropriate viewer.

For that it relies on proper mime type handling at the OS level.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmShowMedDocs.py,v $
__version__ = "$Revision: 1.53 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys

from wxPython.wx import *

from Gnumed.pycommon import gmLog, gmI18N
from Gnumed.business import gmPatient, gmMedDoc
from Gnumed.wxpython import gmGuiHelpers, gmMedDocWidgets

_log = gmLog.gmDefLog

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lInfo, __version__)
#== classes for standalone use ==================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmLoginInfo, gmPG, gmExceptions, gmCfg
	from Gnumed.business import gmXdtObjects, gmXdtMappings, gmDemographicRecord

	wxID_btn_quit = wxNewId()
	_cfg = gmCfg.gmDefCfgFile

	class cStandalonePanel(wxPanel):

		def __init__(self, parent, id):
			# get patient from file
			if self.__get_pat_data() is None:
				raise gmExceptions.ConstructorError, "Cannot load patient data."

			# set up database connectivity
			auth_data = gmLoginInfo.LoginInfo(
				user = _cfg.get('database', 'user'),
				passwd = _cfg.get('database', 'password'),
				host = _cfg.get('database', 'host'),
				port = _cfg.get('database', 'port'),
				database = _cfg.get('database', 'database')
			)
			backend = gmPG.ConnectionPool(login = auth_data)

			# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
			cooked_search_terms = {
				'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
				'lastnames': self.__xdt_pat['last name'],
				'gender': self.__xdt_pat['gender'],
				'firstnames': self.__xdt_pat['first name']
			}

			# find matching patient IDs
			searcher = gmPatient.cPatientSearcher_SQL()
			patient_ids = searcher.get_patient_ids(search_dict = cooked_search_terms)
			if patient_ids is None or len(patient_ids)== 0:
				gmGuiHelpers.gm_show_error(
					aMessage = _('This patient does not exist in the document database.\n"%s %s"') % (self.__xdt_pat['first name'], self.__xdt_pat['last name']),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise gmExceptions.ConstructorError, "Patient from XDT file does not exist in database."

			# ambigous ?
			if len(patient_ids) != 1:
				gmGuiHelpers.gm_show_error(
					aMessage = _('Data in xDT file matches more than one patient in database !'),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise gmExceptions.ConstructorError, "Problem getting patient ID from database. Aborting."

			try:
				gm_pat = gmPatient.gmCurrentPatient(aPKey = patient_ids[0])
			except:
				# this is an emergency
				gmGuiHelpers.gm_show_error(
					aMessage = _('Cannot load patient from database !\nAborting.'),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, 'Cannot access patient [%s] in database.' % patient_ids[0])
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise

			# make main panel
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			self.SetTitle(_("stored medical documents"))

			# make patient panel
			gender = gmDemographicRecord.map_gender_gm2long[gmXdtMappings.map_gender_xdt2gm[self.__xdt_pat['gender']]]
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
				style = wxALIGN_CENTER
			)
			self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

			# make document tree
			self.tree = gmMedDocWidgets.cDocTree(self, -1)
			self.tree.update()
			self.tree.SelectItem(self.tree.root)

			# buttons
			btn_quit = wxButton(
				parent = self,
				id = wxID_btn_quit,
				label = _('Quit')
			)
			EVT_BUTTON (btn_quit, wxID_btn_quit, self.__on_quit)
			szr_buttons = wxBoxSizer(wxHORIZONTAL)
			szr_buttons.Add(btn_quit, 0, wxALIGN_CENTER_VERTICAL, 1)

			szr_main = wxBoxSizer(wxVERTICAL)
			szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
			szr_main.Add(self.tree, 1, wxEXPAND, 9)
			szr_main.Add(szr_buttons, 0, wxEXPAND, 1)

			self.SetAutoLayout(1)
			self.SetSizer(szr_main)
			szr_main.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __get_pat_data(self):
			"""Get data of patient for which to retrieve documents.

			"""
			# FIXME: error checking
			pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
			# FIXME: actually handle pat_format, too
			pat_format = _cfg.get("viewer", "patient file format")

			# get patient data from BDT file
			try:
				self.__xdt_pat = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
			except:
				_log.LogException('Cannot read patient from xDT file [%s].' % pat_file, sys.exc_info())
				gmGuiHelpers.gm_show_error(
					aMessage = _('Cannot load patient from xDT file\n[%s].') % pat_file,
					aTitle = _('loading patient from xDT file')
				)
				return None

			return 1
		#--------------------------------------------------------
		def __on_quit(self, evt):
			app = wxGetApp()
			app.ExitMainLoop()
#== classes for plugin use ======================================
else:
	wxID_TB_BTN_show_page = wxNewId()

	class cPluginTreePanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make document tree
			self.tree = gmMedDocWidgets.cDocTree(self, -1)

			# just one vertical sizer
			sizer = wxBoxSizer(wxVERTICAL)
			sizer.Add(self.tree, 1, wxEXPAND, 0)
			self.SetAutoLayout(1)
			self.SetSizer(sizer)
			sizer.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __del__(self):
			# FIXME: return service handle
			#self.DB.disconnect()
			pass

	#------------------------------------------------------------
	from Gnumed.wxpython import gmPlugin, images_Archive_plugin, images_Archive_plugin1

	class gmShowMedDocs(gmPlugin.cNotebookPluginOld):
		tab_name = _("Documents")

		def name (self):
			return gmShowMedDocs.tab_name

		def GetWidget (self, parent):
			self._widget = cPluginTreePanel(parent, -1)
			return self._widget

		def MenuInfo (self):
			return ('tools', _('Show &archived documents'))

		def populate_with_data(self):
			# no use reloading if invisible
			if self.gb['main.notebook.raised_plugin'] != self.__class__.__name__:
				return 1
			if self._widget.tree.update() is None:
				_log.Log(gmLog.lErr, "cannot update document tree")
				return None
			self._widget.tree.SelectItem(self._widget.tree.root)
			return 1

		def can_receive_focus(self):
			# need patient
			if not self._verify_patient_avail():
				return None
			return 1

		def populate_toolbar (self, tb, widget):
			#tool1 = tb.AddTool(
			#	wxID_PNL_BTN_load_pages,
			#	images_Archive_plugin.getcontentsBitmap(),
			#	shortHelpString=_("load pages"),
			#	isToggle=False
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_load_pages, widget.on_load_pages)

			#tool1 = tb.AddTool(
			#	wxID_PNL_BTN_save_data,
			#	images_Archive_plugin.getsaveBitmap(),
			#	shortHelpString=_("save document"),
			#	isToggle=False
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_save_data, widget.on_save_data)
			
			#tool1 = tb.AddTool(
			#	wxID_PNL_BTN_del_page,
			#	images_Archive_plugin.getcontentsBitmap(),
			#	shortHelpString=_("delete page"),
			#	isToggle=False
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_del_page, widget.on_del_page)
			
			tool1 = tb.AddTool(
				wxID_TB_BTN_show_page,
				images_Archive_plugin.getreportsBitmap(),
				shortHelpString=_("show document"),
				isToggle=False
			)
			EVT_TOOL (tb, wxID_TB_BTN_show_page, gmMedDocWidgets.cDocTree.OnActivate)
	
			#tool1 = tb.AddTool(
			#	wxID_PNL_BTN_select_files,
			#	images_Archive_plugin1.getfoldersearchBitmap(),
			#	shortHelpString=_("select files"),
			#	isToggle=False
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_select_files, widget.on_select_files)
		
			tb.AddControl(wxStaticBitmap(
				tb,
				-1,
				images_Archive_plugin.getvertical_separator_thinBitmap(),
				wxDefaultPosition,
				wxDefaultSize
			))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting display handler")

	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(size=(640,480))
		application.SetWidget(cStandalonePanel,-1)
		application.MainLoop()
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing display handler")
#================================================================
# $Log: gmShowMedDocs.py,v $
# Revision 1.53  2004-08-04 17:16:02  ncq
# - wxNotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.52  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.51  2004/07/15 20:42:18  ncq
# - support if-needed updates again
#
# Revision 1.50  2004/07/15 07:57:21  ihaywood
# This adds function-key bindings to select notebook tabs
# (Okay, it's a bit more than that, I've changed the interaction
# between gmGuiMain and gmPlugin to be event-based.)
#
# Oh, and SOAPTextCtrl allows Ctrl-Enter
#
# Revision 1.49  2004/06/29 22:58:43  ncq
# - add missing gmMedDocWidgets. qualifiers
#
# Revision 1.48  2004/06/26 23:39:34  ncq
# - factored out widgets for re-use
#
# Revision 1.47	 2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.46	 2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.45	 2004/06/17 11:43:18  ihaywood
# Some minor bugfixes.
# My first experiments with wxGlade
# changed gmPhraseWheel so the match provider can be added after instantiation
# (as wxGlade can't do this itself)
#
# Revision 1.44	 2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.43	 2004/06/01 07:55:46  ncq
# - use cDocumentFolder
#
# Revision 1.42	 2004/04/16 00:36:23  ncq
# - cleanup, constraints
#
# Revision 1.41	 2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.40	 2004/03/20 19:48:07  ncq
# - adapt to flat id list from get_patient_ids
#
# Revision 1.39	 2004/03/20 18:30:54  shilbert
# - runs standalone again
#
# Revision 1.38	 2004/03/19 21:26:15  shilbert
# - more module import fixes
#
# Revision 1.37	 2004/03/19 08:29:21  ncq
# - fix spurious whitespace
#
# Revision 1.36	 2004/03/19 08:08:41  ncq
# - fix import of gmLoginInfo
# - remove dead code
#
# Revision 1.35	 2004/03/07 22:19:26  ncq
# - proper import
# - re-fix gmTmpPatient -> gmPatient (fallout from "Syan's commit")
#
# Revision 1.34	 2004/03/06 21:52:02  shilbert
# - adapted code to new API since __set/getitem is gone
#
# Revision 1.33	 2004/02/25 09:46:23  ncq
# - import from pycommon now, not python-common
#
# Revision 1.32	 2004/01/06 23:19:52  ncq
# - use whoami
#
# Revision 1.31	 2003/11/17 10:56:40  sjtan
#
# synced and commiting.
#
# Revision 1.30	 2003/11/16 11:53:32  shilbert
# - fixed stanalone mode
# - makes use of toolbar
#
# Revision 1.29	 2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.28	 2003/08/27 12:31:41  ncq
# - some cleanup
#
# Revision 1.27	 2003/08/24 12:50:20  shilbert
# - converted from __show_error() to gmGUIHelpers.gm_show_error()
#
# Revision 1.26	 2003/06/29 15:21:22  ncq
# - add can_receive_focus() on patient not selected
#
# Revision 1.25	 2003/06/26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.24	 2003/06/19 15:31:37  ncq
# - cleanup, page change vetoing
#
# Revision 1.23	 2003/04/28 12:11:30  ncq
# - refactor name() to not directly return _(<name>)
#
# Revision 1.22	 2003/04/20 15:39:36  ncq
# - call_viewer was moved to gmMimeLib
#
# Revision 1.21	 2003/04/19 15:01:33  ncq
# - we need import re both standalone and plugin
#
# Revision 1.20	 2003/04/18 22:34:44  ncq
# - document context menu, mainly for descriptions, currently
#
# Revision 1.19	 2003/04/18 17:45:05  ncq
# - add quit button
#
# Revision 1.18	 2003/04/18 16:40:04  ncq
# - works again as standalone
#
# Revision 1.17	 2003/04/04 20:49:22  ncq
# - make plugin work with gmCurrentPatient
#
# Revision 1.16	 2003/04/01 12:31:53  ncq
# - we can't use constant reference self.patient if we don't register interest
#	in gmSignals.patient_changed, hence, acquire patient when needed
#
# Revision 1.15	 2003/03/25 19:57:09  ncq
# - add helper __show_error()
#
# Revision 1.14	 2003/03/23 02:38:46  ncq
# - updated Hilmar's fix
#
# Revision 1.13	 2003/03/02 17:03:19  ncq
# - make sure metadata is retrieved
#
# Revision 1.12	 2003/03/02 11:13:01  hinnef
# preliminary fix for crash on ReceiveFocus()
#
# Revision 1.11	 2003/02/25 23:30:31  ncq
# - need sys.exc_info() in LogException
#
# Revision 1.10	 2003/02/24 23:14:53  ncq
# - adapt to get_patient_ids actually returning a flat list of IDs now
#
# Revision 1.9	2003/02/21 13:54:17	 ncq
# - added even more likely and unlikely user warnings
#
# Revision 1.8	2003/02/20 01:25:18	 ncq
# - read login data from config file again
#
# Revision 1.7	2003/02/19 15:19:43	 ncq
# - remove extra print()
#
# Revision 1.6	2003/02/18 02:45:21	 ncq
# - almost fixed standalone mode again
#
# Revision 1.5	2003/02/17 16:10:50	 ncq
# - plugin mode seems to be fully working, actually calls viewers on files
#
# Revision 1.4	2003/02/15 14:21:49	 ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.3	2003/02/11 18:26:16	 ncq
# - fix exp_base buglet in OnActivate
#
# Revision 1.2	2003/02/09 23:41:09	 ncq
# - reget doc list on receiving focus thus being able to react to selection of a different patient
#
# Revision 1.1	2003/02/09 20:07:31	 ncq
# - works as a plugin, patient hardcoded, though
#
# Revision 1.8	2003/01/26 17:00:18	 ncq
# - support chunked object retrieval
#
# Revision 1.7	2003/01/25 00:21:42	 ncq
# - show nr of bytes on object in metadata :-)
#
