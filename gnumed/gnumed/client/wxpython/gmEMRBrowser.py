"""GnuMed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.21 2005-04-02 20:45:14 cfmoro Exp $
__version__ = "$Revision: 1.21 $"
__author__ = "cfmoro1976@yahoo.es, sjtan@swiftdsl.com.au, Karsten.Hilbert@gmx.net"
__license__ = "GPL"

import sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmEMRStructWidgets, gmSOAPWidgets
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cEMRBrowserPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):

    def __init__(self, parent, id):
        """
        Contructs a new instance of EMR browser panel

        parent - Wx parent widget
        id - Wx widget id
        """
        # Call parents constructors
        wx.wxPanel.__init__ (
            self,
            parent,
            id,
            wx.wxPyDefaultPosition,
            wx.wxPyDefaultSize,
            wx.wxNO_BORDER
        )
        gmRegetMixin.cRegetOnPaintMixin.__init__(self)

        self.__pat = gmPerson.gmCurrentPatient()
        self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)
        
        self.__custom_right_widget = None
        self.__selected_node = None

        self.__do_layout()
        self.__register_interests()
        self.__reset_ui_content()

#        self.popup.SetPopupContext(self.__emr_tree.GetSelection())
    #--------------------------------------------------------
    def __do_layout(self):
        """
        Arranges EMR browser layout
        """
        
        # splitter window
        self.__tree_narr_splitter = wx.wxSplitterWindow(self, -1)
        # emr tree
        self.__emr_tree = wx.wxTreeCtrl (
            self.__tree_narr_splitter,
            -1,
            style=wx.wxTR_HAS_BUTTONS | wx.wxNO_BORDER
        )
        # popup menu
        self.popup = gmPopupMenuEMRBrowser(self)
        
        # right hand side
        PNL_emr_dump = wx.wxPanel(self.__tree_narr_splitter, -1)        
        # emr dump text control
        self.__narr_TextCtrl = wx.wxTextCtrl (
            PNL_emr_dump,
            -1,
            style = wx.wxTE_MULTILINE | wx.wxTE_READONLY | wx.wxTE_DONTWRAP
        )
        # - dump button
        self.__BTN_dump_emr = wx.wxButton(PNL_emr_dump, -1, _('&Export EMR to file'))
        # - arrange widgets
        szr_emr_dump = wx.wxBoxSizer(wx.wxVERTICAL)
        szr_emr_dump.Add(self.__narr_TextCtrl,1 , wx.wxEXPAND)
        szr_btns_emr_dump = wx.wxBoxSizer(wx.wxHORIZONTAL)
        szr_btns_emr_dump.Add(self.__BTN_dump_emr, 0)
        szr_emr_dump.Add(szr_btns_emr_dump, 0, wx.wxALIGN_CENTER)
        PNL_emr_dump.SetSizerAndFit(szr_emr_dump)
        
        # set up splitter
        # FIXME: read/save value from/into backend
        self.__tree_narr_splitter.SetMinimumPaneSize(20)
        self.__tree_narr_splitter.SplitVertically(self.__emr_tree, PNL_emr_dump)

        self.__szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
        self.__szr_main.Add(self.__tree_narr_splitter, 1, wx.wxEXPAND, 0)

        self.SetAutoLayout(1)
        self.SetSizer(self.__szr_main)
        self.__szr_main.Fit(self)
        self.__szr_main.SetSizeHints(self)

        # make popup menus for later use
        self.__epi_context_popup = wx.wxMenu()
        menu_id = wx.wxNewId()
        self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('rename episode')))
        wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__rename_episode)
        menu_id = wx.wxNewId()
        self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('close episode')))
        wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__close_episode)
        menu_id = wx.wxNewId()
        self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('delete episode')))
        wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__delete_episode)
        menu_id = wx.wxNewId()
        self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('attach episode to another health issue')))
        wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__relink_episode)
        menu_id = wx.wxNewId()
        self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('attach all encounters to another episode')))
        wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__relink_episode_encounters)
    #--------------------------------------------------------
    # event handling
    #--------------------------------------------------------
    def __register_interests(self):
        """
        Configures enabled event signals
        """
        # wx.wxPython events
        wx.EVT_TREE_SEL_CHANGED(self.__emr_tree, self.__emr_tree.GetId(), self._on_tree_item_selected)
        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.__emr_tree, self.__emr_tree.GetId(), self.__on_tree_item_right_clicked)
        wx.EVT_BUTTON(self.__BTN_dump_emr, self.__BTN_dump_emr.GetId(), self.__on_dump_emr)
        # client internal signals
        gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
        gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self.__on_episodes_modified)
    #--------------------------------------------------------
    def __on_dump_emr(self, event):
        """Dump EMR to file."""        
        self.__exporter.dump_emr_gui(parent = self)
    #--------------------------------------------------------
    def _on_patient_selected(self):
        """Patient changed."""
        self._schedule_data_reget()
    #--------------------------------------------------------
    def __on_episodes_modified(self):
        """Episode changed."""
        # FIXME: should *actually* be self._schedule_data_reget() but does not work properly yet
        self.refresh_tree()
    #--------------------------------------------------------
    def _on_tree_item_selected(self, event):
        """
        Displays information for a selected tree node
        """
        # retrieve the selected EMR element
        sel_item = event.GetItem()
        sel_item_obj = self.__emr_tree.GetPyData(sel_item)
        self.__selected_node = sel_item

        self.__display_narrative_on_right_pane()

        # update displayed text
        if isinstance(sel_item_obj, gmEMRStructItems.cHealthIssue):
            label = _('Health Issue')
            txt = self.__exporter.get_issue_info(issue=sel_item_obj)

        elif isinstance(sel_item_obj, gmEMRStructItems.cEpisode):
            label = _('Episode')
            txt = self.__exporter.get_episode_info(episode=sel_item_obj)

        elif isinstance(sel_item_obj, gmEMRStructItems.cEncounter):
            label = _('Encounter')
            epi = self.__emr_tree.GetPyData(self.__emr_tree.GetItemParent(sel_item))
            txt = self.__exporter.get_encounter_info(episode=epi, encounter=sel_item_obj)

        else:
            label = _('Summary')
            txt = self.__exporter.get_summary_info(0)

        header = header = '%s\n%s\n\n' % (label, ('=' * len(label)))
        self.__narr_TextCtrl.Clear()
        self.__narr_TextCtrl.WriteText(header)
        self.__narr_TextCtrl.WriteText(txt)
    #--------------------------------------------------------
    def __on_tree_item_right_clicked(self, event):
        """
        Right button clicked: display the popup for the tree
        """
        # FIXME: should get the list item at the current position
        # FIXME: should then update the context
#        sel_item = event.GetItem()
#        self.PopupMenu(self.popup, (event.GetX(), event.GetY()))

        node = event.GetItem()
        node_data = self.__emr_tree.GetPyData(node)

        self.__emr_tree.SelectItem(node)

        # FIXME: get position from tree item
#        pos = (event.GetX(), event.GetY())
        pos = wx.wxPyDefaultPosition
        if isinstance(node_data, gmEMRStructItems.cHealthIssue):
            self.__handle_issue_context(issue=node_data, pos=pos)
        elif isinstance(node_data, gmEMRStructItems.cEpisode):
            self.__handle_episode_context(episode=node_data, pos=pos)
        elif isinstance(node_data, gmEMRStructItems.cEncounter):
            self.__handle_encounter_context(encounter=node_data, pos=pos)
        else:
            print "error: unknown node type, no popup menu"
        event.Skip()
    #--------------------------------------------------------
    # reget mixin API
    #--------------------------------------------------------
    def _populate_with_data(self):
        """
        Fills UI with data.
        """
        self.__reset_ui_content()
        if self.refresh_tree():
            return True
        return False
    #--------------------------------------------------------
    # public API
    #--------------------------------------------------------        
    def refresh_tree(self):
        """
        Updates EMR browser data
        """
        
        # clear previous contents
        self.__emr_tree.DeleteAllItems()
        
        # FIXME: auto select the previously self.__selected_node if not None

        # EMR tree root item
        ident = self.__pat.get_identity()
        root_item = self.__emr_tree.AddRoot(_('%s EMR') % ident['description'])

        # Obtain all the tree from exporter
        self.__exporter.get_historical_tree(self.__emr_tree)

        # Expand root node and display patient summary info
        self.__emr_tree.Expand(root_item)
        label = _('Summary')
        underline = '=' * len(label)
        self.__narr_TextCtrl.WriteText('%s\n%s\n\n' % (label, underline))
        self.__narr_TextCtrl.WriteText(self.__exporter.get_summary_info(0))

        # Set sash position
        self.__tree_narr_splitter.SetSashPosition(self.__tree_narr_splitter.GetSizeTuple()[0]/3, True)

        # FIXME: error handling
        return True
    #--------------------------------------------------------
#    def get_EMR_item(self, selected_tree_item):
#        """
#        Retrieved the EMR struct item associated with the given
#        tree node.
#        
#        @param selected_tree_item The tree node to retrieve its data model for.
#        @type selected_tree_item A wxTreeItemId instance
#        """
#        return self.__emr_tree.GetPyData(selected_tree_item)
    #--------------------------------------------------------
    def get_selection(self):
        """
        """
        return self.__selected_node
    #--------------------------------------------------------
    def get_item_parent(self, tree_item):
        """
        """        
        return self.__emr_tree.GetItemParent(tree_item)
    #--------------------------------------------------------
    def SetCustomRightWidget(self, widget):
        """
        @param widget: 
        @type widget: 
        """
        widget.Reparent(self.__tree_narr_splitter)
        self.__custom_right_widget = widget
        self.__tree_narr_splitter.ReplaceWindow(self.__narr_TextCtrl, self.__custom_right_widget)
    #--------------------------------------------------------
    # internal API
    #--------------------------------------------------------
    def __reset_ui_content(self):
        """
        Clear all information displayed in browser (tree and details area)
        """
        self.__emr_tree.DeleteAllItems()
        self.__narr_TextCtrl.Clear()
    #--------------------------------------------------------
    def __display_narrative_on_right_pane(self):
        """
        """
        # FIXME: confirmation dialog to avoid loosing edits

        # FIXME: really needed ?
        if id(self.__tree_narr_splitter.GetWindow2()) == id(self.__narr_TextCtrl):
            return True
        self.__tree_narr_splitter.ReplaceWindow(self.__custom_right_widget, self.__narr_TextCtrl)
#        self.__custom_right_widget.Destroy()
        self.__custom_right_widget = None
    #--------------------------------------------------------
    def __handle_issue_context(self, issue=None, pos=wx.wxPyDefaultPosition):
        print "handling issue context menu"
        print issue
        print "actions:"
        print " rename issue"
        print " add new episode to issue"
        print " attach issue to another patient"
        print " move all episodes to another issue"
    #--------------------------------------------------------
    def __handle_episode_context(self, episode=None, pos=wx.wxPyDefaultPosition):
        print "handling episode context"
        self.__selected_episode = episode
        self.__epi_context_popup.SetTitle(_('Episode %s') % episode['description'])
        self.PopupMenu(self.__epi_context_popup, pos)
    #--------------------------------------------------------
    def __rename_episode(self, event):
        print "renaming episode"
        print self.__selected_episode
    #--------------------------------------------------------
    def __close_episode(self, event):
        print "closing episode"
        print self.__selected_episode
    #--------------------------------------------------------
    def __delete_episode(self, event):
        print "deleting episode"
        print self.__selected_episode
    #--------------------------------------------------------
    def __relink_episode(self, event):
        print "relinking episode"
        print self.__selected_episode
    #--------------------------------------------------------
    def __relink_episode_encounters(self, event):
        print "relinking encounters of episode"
        print self.__selected_episode
    #--------------------------------------------------------
    def __handle_encounter_context(self, encounter = None):
        print "handling encounter context menu"
        print encounter
        print "actions:"
        print " delete encounter"
        print " attach encounter to another patient"
        print " attach all progress notes to another encounter"
    #--------------------------------------------------------
#    def set_patient(self, patient):
#        """
#        Configures EMR browser patient and instantiates exporter.
#        Appropiate for standalaone use.
#        patient - The patient to display EMR for
#        """
#        self.__patient = patient
#        self.__exporter.set_patient(patient)

#================================================================
class gmPopupMenuEMRBrowser(wx.wxMenu):
    """
    Popup menu for the EMR tree
    """
    
    #--------------------------------------------------------
    def __init__(self , browser):
        
        wx.wxMenu.__init__(self)
        
        # menu items ids
        self.ID_NEW_ENCOUNTER=1    
        self.ID_EDIT_ENCOUNTER_NOTES=2
        self.ID_NEW_HEALTH_ISSUE=3
        self.ID_EPISODE_EDITOR=4
        
        # target widget
        self.__browser = browser
        self.__sel_item_obj = None
        
        # configure event handling
        self.__register_interests()

    #--------------------------------------------------------
    # event handling
    #--------------------------------------------------------
    def __register_interests(self):
        """
        Configures enabled event signals
        """
        # wx.wxPython events
        wx.EVT_MENU(self.__browser, self.ID_NEW_HEALTH_ISSUE , self.__on_new_health_issue)
#        wx.EVT_MENU(self.__browser, self.ID_EPISODE_EDITOR, self.__on_episode_editor)
#        wx.EVT_MENU(self.__browser, self.ID_EPISODE_EDITOR, self.__browser.edit_episode)
        wx.EVT_MENU(self.__browser, self.ID_NEW_ENCOUNTER , self.__on_new_encounter)
        wx.EVT_MENU(self.__browser, self.ID_EDIT_ENCOUNTER_NOTES , self.__on_edit_encounter_notes)

    #--------------------------------------------------------
    def __on_new_health_issue(self, event):
        """
        On new health issue menu item selection: create a new health issue
        """
        msg = _('We are lacking code to create a new health issue yet.')
        gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening health issue editor'))
    
    #--------------------------------------------------------
    def __on_episode_editor(self, event):
        """
        On new episode menu item selection: create a new episode
        """
        # obtain pk for the target health issue
        pk_issue = None
        if (isinstance(self.__sel_item_obj, gmEMRStructItems.cEpisode)):
            pk_issue = self.__sel_item_obj['pk_health_issue']

        elif (isinstance(self.__sel_item_obj, gmEMRStructItems.cHealthIssue)):
            pk_issue = self.__sel_item_obj['id']

        self.__browser.SetCustomRightWidget(gmEMRStructWidgets.cEpisodeEditor(self.__browser, -1, pk_issue))
        
        #episode_selector = gmEMRStructWidgets.cEpisodeEditorDlg (
        #    None,
        #    -1,
        #    _('Create/Edit episode'),
        #    pk_health_issue = pk_issue
        #)
        #retval = episode_selector.ShowModal()
        # FIXME refresg only if an episode was created/updated
        #self.__browser.refresh_tree()
        #if retval == gmEMRStructWidgets.dialog_OK:
        #    # FIXME refresh only if episode selector action button was performed
        #    print "would be refreshing emr tree now"
        #    self.__browser.refresh_tree()
        #elif retval == gmEMRStructWidgets.dialog_CANCELLED:
        #    print 'User canceled'
        #    return False
        #else:
        #    raise Exception('Invalid dialog return code [%s]' % retval)
        #episode_selector.Destroy() # finally destroy it when finished.
        # FIXME: ensure visible the problem's episodes
        
    #--------------------------------------------------------
    def __on_new_encounter(self, event):
        """
        On new encounter menu item selection: create a new encounter
        """        
        msg = _('We are lacking code to create a new encounter yet.')
        gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening encounter editor'))
        
    #--------------------------------------------------------
    def __on_edit_encounter_notes(self, event):
        """
        On new edit encounter notes menu item selection: edit encounter's soap notes
        """
        emr = gmPerson.gmCurrentPatient().get_clinical_record()
        encounter = self.__sel_item_obj
        item = self.__browser.get_item_parent(self.__browser.get_selection())
        episode = self.__emr_tree.GetPyData(item)
        narrative = self.__get_narrative(pk_encounter = encounter['pk_encounter'], pk_health_issue = episode['pk_health_issue'])
        problem = emr.get_problems(issues = [episode['pk_health_issue']], episodes=[episode['pk_episode']])[0]
        self.__browser.SetCustomRightWidget(gmSOAPWidgets.cResizingSoapPanel(self.__browser, problem = problem,
        input_defs = narrative))
                
    #--------------------------------------------------------
    # internal API
    #--------------------------------------------------------
    def __get_narrative(self, pk_encounter=None, pk_health_issue = None, default_labels=None):
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
            # retrieve narrative for given problem/encounter
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
                line = gmSOAPWidgets.cSOAPLineDef()
                line.label = label_txt
                line.text = narrative['narrative']
                line.data['narrative instance'] = narrative
                soap_lines.append(line)
        return soap_lines
        
    #--------------------------------------------------------    
    def __append_new_encounter_menuitem(self, episode):
        """
        Adds a menu item to create a new encounter for the given episode.
        
        @param episode The episode to create a new encounter for.
        @type episode A gmEMRStructItems.cEpisode instance.
        """        
        self.Append(self.ID_NEW_ENCOUNTER, "Encounter editor (of episode '%s')" % episode['description'] )
        
    #--------------------------------------------------------        
    def __append_new_episode_menuitem(self, health_issue):
        """
        Adds a menu item to create a new episode for the given health issue.
        
        @param health_issue The health issue to create a new encounter for.
        @type health_issue A gmEMRStructItems.cHealthIssue instance.
        """
        self.Append(self.ID_EPISODE_EDITOR, "Episode editor (of health issue '%s')" % health_issue['description'] )

    #--------------------------------------------------------
    # public API
    #--------------------------------------------------------        
    def Clear(self):
        """
        Clears all items from the menu
        """
        for item in self.GetMenuItems():
            self.Remove(item.GetId())
            
    #--------------------------------------------------------
    def SetPopupContext(self, sel_item):
        """
        Fills the menu with its items, according the selected EMR element.
        
        @param sel_item The selected tree item
        @type sel_item A wxTreeItemId instance
        """
        
        # clear the menu
        self.Clear()
        # retrieve the EMR object associated with the selected tree item and
        # keep cache of it        
        self.__sel_item_obj = self.__browser.get_EMR_item(sel_item)
        print self.__sel_item_obj
        
        # append menu items according the EMR struct element selection
        if(isinstance(self.__sel_item_obj, gmEMRStructItems.cEncounter)):
            episode = self.__browser.get_EMR_item(self.__browser.get_item_parent(self.__browser.get_selection()))
            self.__append_new_encounter_menuitem(episode=episode)
            self.Append(self.ID_EDIT_ENCOUNTER_NOTES, "Progress notes editor (of encounter '%s:%s')" % 
            (self.__sel_item_obj['l10n_type'], self.__sel_item_obj['started'].Format('%Y-%m-%d')))
            
        elif (isinstance(self.__sel_item_obj, gmEMRStructItems.cEpisode)):
            health_issue = self.__browser.get_EMR_item(self.__browser.get_item_parent(self.__browser.get_selection()))
            self.__append_new_episode_menuitem(health_issue=health_issue)
            self.__append_new_encounter_menuitem(episode=self.__browser.get_EMR_item(sel_item) )
            
        elif (isinstance(self.__sel_item_obj, gmEMRStructItems.cHealthIssue)):
            self.Append(self.ID_NEW_HEALTH_ISSUE, "Health Issue editor")
            self.__append_new_episode_menuitem(health_issue=self.__browser.get_EMR_item(sel_item))            
                        
        else:
            self.Append(self.ID_NEW_HEALTH_ISSUE, "New Health Issue")


#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

    from Gnumed.pycommon import gmCfg

    _log.SetAllLogLevels(gmLog.lData)
    _log.Log (gmLog.lInfo, "starting emr browser...")

    _cfg = gmCfg.gmDefCfgFile     
    if _cfg is None:
        _log.Log(gmLog.lErr, "Cannot run without config file.")
        sys.exit("Cannot run without config file.")

    try:
        # make sure we have a db connection
        gmPG.set_default_client_encoding('latin1')
        pool = gmPG.ConnectionPool()
        
        # obtain patient
        patient = gmPerson.ask_for_patient()
        if patient is None:
            print "No patient. Exiting gracefully..."
            sys.exit(0)

        # display standalone browser
        application = wx.wxPyWidgetTester(size=(800,600))
        emr_browser = cEMRBrowserPanel(application.frame, -1)
#        emr_browser.set_patient(patient)        
        emr_browser.refresh_tree()
        
        application.frame.Show(True)
        application.MainLoop()
        
        # clean up
        if patient is not None:
            try:
                patient.cleanup()
            except:
                print "error cleaning up patient"
    except StandardError:
        _log.LogException("unhandled exception caught !", sys.exc_info(), 1)
        # but re-raise them
        raise
    try:
        pool.StopListeners()
    except:
        _log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
        raise

    _log.Log (gmLog.lInfo, "closing emr browser...")

#================================================================
# $Log: gmEMRBrowser.py,v $
# Revision 1.21  2005-04-02 20:45:14  cfmoro
# Implementated  exporting emr from gui client
#
# Revision 1.20  2005/03/30 22:10:07  ncq
# - just cleanup
#
# Revision 1.19  2005/03/30 18:59:03  cfmoro
# Added file selector dialog to emr dump callback function
#
# Revision 1.18  2005/03/30 18:14:56  cfmoro
# Added emr export button
#
# Revision 1.17  2005/03/29 07:27:14  ncq
# - add missing argument
#
# Revision 1.16  2005/03/11 22:52:54  ncq
# - simplify popup menu use
#
# Revision 1.15  2005/03/10 19:51:29  cfmoro
# Obtained problem from cClinicalRecord on progress notes edition
#
# Revision 1.14  2005/03/09 20:00:13  cfmoro
# Added fixme comment in problem retrieval
#
# Revision 1.13  2005/03/09 19:43:21  cfmoro
# EMR browser edit problem-episodes notes responsible for providing the narrative definitions to cSoapResizingPanel
#
# Revision 1.12  2005/03/09 18:31:57  cfmoro
# As proof of concept: episode editor and notes editor are displayed in the right panel. Just an initial draft, needs feeback a lot of coding yet ;)
#
# Revision 1.11  2005/03/09 16:58:09  cfmoro
# Thanks to Syan code, added contextual menu to emr tree. Linked episode edition action with the responsible dialog
#
# Revision 1.10  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.9  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.8  2005/01/31 13:02:18  ncq
# - use ask_for_patient() in gmPerson.py
#
# Revision 1.7  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.6  2004/10/31 00:37:13  cfmoro
# Fixed some method names. Refresh function made public for easy reload, eg. standalone. Refresh browser at startup in standalone mode
#
# Revision 1.5  2004/09/06 18:57:27  ncq
# - Carlos pluginized the lot ! :-)
# - plus some fixes/tabified it
#
# Revision 1.4    2004/09/01 22:01:45     ncq
# - actually use Carlos' issue/episode summary code
#
# Revision 1.3    2004/08/11 09:46:24     ncq
# - now that EMR exporter supports SOAP notes - display them
#
# Revision 1.2    2004/07/26 00:09:27     ncq
# - Carlos brings us data display for the encounters - can REALLY browse EMR now !
#
# Revision 1.1    2004/07/21 12:30:25     ncq
# - initial checkin
#
