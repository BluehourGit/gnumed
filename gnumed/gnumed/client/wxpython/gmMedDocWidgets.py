"""GnuMed medical document handling widgets.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedDocWidgets.py,v $
__version__ = "$Revision: 1.10 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, re

from wxPython.wx import *

from Gnumed.pycommon import gmLog, gmI18N, gmCfg, gmWhoAmI, gmPG, gmMimeLib, gmExceptions
from Gnumed.business import gmPerson, gmMedDoc
from Gnumed.wxpython import gmGuiHelpers

_log = gmLog.gmDefLog
_whoami = gmWhoAmI.cWhoAmI()

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lInfo, __version__)

wxID_PNL_main = wxNewId()
wxID_TB_BTN_show_page = wxNewId()


		# NOTE:	 For some reason tree items have to have a data object in
		#		 order to be sorted.  Since our compare just uses the labels
		#		 we don't need any real data, so we'll just use None.

#============================================================
class cDocTree(wxTreeCtrl):
	"""This wxTreeCtrl derivative displays a tree view of stored medical documents.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised tree.
		"""
		wxTreeCtrl.__init__(self, parent, id, style=wxTR_NO_BUTTONS)
		self.root = None
		self.__pat = gmPerson.gmCurrentPatient()

		self.__register_events()

#		self.tree = MyTreeCtrl(self, tID, wxDefaultPosition, wxDefaultSize,
#								wxTR_HAS_BUTTONS | wxTR_EDIT_LABELS# | wxTR_MULTIPLE
#								, self.log)

	#--------------------------------------------------------
	def __register_events(self):
		# connect handlers
		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self._on_activate)
		EVT_TREE_ITEM_RIGHT_CLICK (self, self.GetId(), self.__on_right_click)

#		 EVT_TREE_ITEM_EXPANDED	 (self, tID, self.OnItemExpanded)
#		 EVT_TREE_ITEM_COLLAPSED (self, tID, self.OnItemCollapsed)
#		 EVT_TREE_SEL_CHANGED	 (self, tID, self.OnSelChanged)
#		 EVT_TREE_BEGIN_LABEL_EDIT(self, tID, self.OnBeginEdit)
#		 EVT_TREE_END_LABEL_EDIT (self, tID, self.OnEndEdit)

#		 EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)
	#--------------------------------------------------------
	def refresh(self):
		if not self.__pat.is_connected():
			gmGuiHelpers.gm_beep_statustext(
				_('Cannot load documents. No active patient.'),
				gmLog.lErr
			)
			return False

		if not self.__populate_tree():
			return False

		return True
	#--------------------------------------------------------
	def __populate_tree(self):
		# FIXME: check if patient changed at all

		# clean old tree
		if not self.root is None:
			self.DeleteAllItems()

		# init new tree
		self.root = self.AddRoot(_("available documents (most recent on top)"), -1, -1)
		self.SetPyData(self.root, None)
		self.SetItemHasChildren(self.root, False)

		# read documents from database
		docs_folder = self.__pat.get_document_folder()
		docs = docs_folder.get_documents()
		if docs is None:
			name = self.__pat['demographic record'].get_names()
			gmGuiHelpers.gm_show_error(
				aMessage = _('Error searching documents for patient\n[%s %s].') % (name['first'], name['last']),
				aTitle = _('loading document list')
			)
			# avoid recursion of GUI updating
			return True

		if len(docs) == 0:
			return True

		# fill new tree from document list
		self.SetItemHasChildren(self.root, True)

		# add our documents as first level nodes
		for doc in docs:
			if doc['comment'] is not None:
				cmt = '"%s"' % doc['comment']
			else:
				cmt = _('no comment available')

			parts = doc.get_parts()
			page_num = len(parts)

			if doc['ext_ref'] is not None:
				ref = '>%s<' % doc['ext_ref']
			else:
				ref = _('no reference ID found')

			label = _('%10s %25s: %s (%s page(s), %s)') % (
				doc['date'].Format('%Y-%m-%d').ljust(10),
				doc['l10n_type'].ljust(25),
				cmt,
				page_num,
				ref
			)

			doc_node = self.AppendItem(self.root, label)
			self.SetItemBold(doc_node, bold=True)
			self.SetPyData(doc_node, doc)
			if len(parts) > 0:
				self.SetItemHasChildren(doc_node, True)

			# now add parts as child nodes
			for part in parts:
				p = _('page %2s') % part['seq_idx']

				if part['obj_comment'] is None:
					c = _("no comment available")
				else:
					c = part['obj_comment']

				if part['size'] == 0:
					s = _('0 bytes - data missing')
				else:
					s = _('%s bytes') % part['size']

				label = _('%s: "%s" (%s)') % (p, c, s)

				part_node = self.AppendItem(doc_node, label)
				self.SetPyData(part_node, part)

		# and uncollapse
		self.Expand(self.root)

		return True
	#------------------------------------------------------------------------
	def OnCompareItems (self, node1=None, node2=None):
		"""Used in sorting items.

		-1: 1 < 2
		 0: 1 = 2
		 1: 1 > 2
		"""
		item1 = self.GetPyData(node1)
		item2 = self.GetPyData(node2)

		# doc node
		if isinstance(item1, gmMedDoc.cMedDoc):
			# compare dates
			if item1['date'] > item2['date']:
				return -1
			if item1['date'] == item2['date']:
				return 0
			return 1
		# part node
		if isinstance(item1, gmMedDoc.cMedDocPart):
			# compare sequence IDs (= "page" numbers)
			if item1['seq_idx'] < item2['seq_idx']:
				return -1
			if item1['seq_idx'] == item2['seq_idx']:
				return 0
			return 1
		# error out
		_log.Log(gmLog.lErr, 'do not know how to compare [%s] with [%s]' % (type(item1), type(item2)))
		return None
	#------------------------------------------------------------------------
	def _on_activate (self, event):
		node = event.GetItem()
		node_data = self.GetPyData(node)

		# exclude pseudo root node
		if node_data is None:
			return None

		# do nothing with documents yet
		if isinstance(node_data, gmMedDoc.cMedDoc):
			return None

		# but do everything with parts
		if __name__ == "__main__":
			tmp = "unknown_workplace"
		else:
			tmp = _whoami.get_workplace()

		exp_base, set = gmCfg.getDBParam (
			workplace = tmp,
			option = "doc export dir"
		)
		if exp_base is None:
			exp_base = ''
		else:
			exp_base = os.path.abspath(os.path.expanduser(exp_base))
		if not os.path.exists(exp_base):
			_log.Log(gmLog.lErr, "The directory [%s] does not exist ! Falling back to default temporary directory." % exp_base) # which is tempfile.tempdir == None == use system defaults
		else:
			_log.Log(gmLog.lData, "working into directory [%s]" % exp_base)

		if node_data['size'] == 0:
			_log.Log(gmLog.lErr, 'cannot display part [%s] - 0 bytes' % node_data['pk_obj'])
			gmGuiHelpers.gm_show_error(
				aMessage = _('Document part does not seem to exist in database !'),
				aTitle = _('showing document')
			)
			return None

		if __name__ == "__main__":
			chunksize = None
		else:
			chunksize, set = gmCfg.getDBParam (
				workplace = _whoami.get_workplace(),
				option = "doc export chunk size"
			)
		if chunksize is None:
			# 1 MB
			chunksize = 1 * 1024 * 1024

		# retrieve doc part
		fname = node_data.export_to_file(aTempDir = exp_base, aChunkSize = chunksize)
		if fname is None:
			_log.Log(gmLog.lErr, "cannot export doc part [%s] data from database" % node_data['pk_obj'])
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot export document part from database to file.'),
				aTitle = _('showing document')
			)
			return None

		(result, msg) = gmMimeLib.call_viewer_on_file(fname)
		if not result:
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('displaying page')
			)
			return None
		return 1
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		node = evt.GetItem()
		node_data = self.GetPyData(node)

		# exclude pseudo root node
		if node_data is None:
			return None

		# documents
		if isinstance(node_data, gmMedDoc.cMedDoc):
			self.__handle_doc_context(doc=node_data)

		# parts
		if isinstance(node_data, gmMedDoc.cMedDocPart):
			self.__handle_part_context(node_data)
		evt.Skip()
	#--------------------------------------------------------
	def __handle_doc_context(self, doc=None):
		# build menu
		descriptions = doc.get_descriptions()
		wxIDs_desc = []
		desc_menu = wxMenu()
		for desc in descriptions:
			d_id = wxNewId()
			wxIDs_desc.append(d_id)
			# contract string
			tmp = re.split('\r\n+|\r+|\n+|\s+|\t+', desc)
			tmp = ' '.join(tmp)
			# but only use first 30 characters
			tmp = "%s ..." % tmp[:30]
			desc_menu.AppendItem(wxMenuItem(desc_menu, d_id, tmp))
			# connect handler
			EVT_MENU(desc_menu, d_id, self.__show_description)
		wxID_load_submenu = wxNewId()
		menu = wxMenu(title = _('document menu'))
		menu.AppendMenu(wxID_load_submenu, _('descriptions ...'), desc_menu)
		self.PopupMenu(menu, wxPyDefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def __show_description(self, evt):
		print "showing description"
	#--------------------------------------------------------
	def __handle_part_context(self, data):
		print "handling doc part context menu"
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	print "please write a unit test"

#============================================================
# $Log: gmMedDocWidgets.py,v $
# Revision 1.10  2005-01-31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.9  2004/10/17 15:57:36  ncq
# - after pat.get_documents():
#   1) separate len(docs) == 0 from docs is None
#   2) only the second really is an error
#   3) however, return True from it, too, as we
#      informed the user about the error already
#
# Revision 1.8  2004/10/17 00:05:36  sjtan
#
# fixup for paint event re-entry when notification dialog occurs over medDocTree graphics
# area, and triggers another paint event, and another notification dialog , in a loop.
# Fixup is set flag to stop _repopulate_tree, and to only unset this flag when
# patient activating signal gmMedShowDocs to schedule_reget, which is overridden
# to include resetting of flag, before calling mixin schedule_reget.
#
# Revision 1.7  2004/10/14 12:11:50  ncq
# - __on_activate -> _on_activate
#
# Revision 1.6  2004/10/11 19:56:03  ncq
# - cleanup, robustify, attach doc/part VO directly to node
#
# Revision 1.5  2004/10/01 13:34:26  ncq
# - don't fail to display just because some metadata is missing
#
# Revision 1.4  2004/09/19 15:10:44  ncq
# - lots of cleanup
# - use status message instead of error box on missing patient
#   so that we don't get an endless loop
#   -> paint_event -> update_gui -> no-patient message -> paint_event -> ...
#
# Revision 1.3  2004/07/19 11:50:43  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.2  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.1  2004/06/26 23:39:34  ncq
# - factored out widgets for re-use
#
