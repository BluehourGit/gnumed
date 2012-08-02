"""GNUmed medical document handling widgets.
"""
#================================================================
__version__ = "$Revision: 1.187 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import os.path
import os
import sys
import re as regex
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmCfg, gmPG2, gmMimeLib, gmExceptions, gmMatchProvider, gmDispatcher, gmDateTime, gmTools, gmShellAPI, gmHooks
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDocuments
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmSurgery

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)


default_chunksize = 1 * 1024 * 1024		# 1 MB
#============================================================
def manage_document_descriptions(parent=None, document=None):

	#-----------------------------------
	def delete_item(item):
		doit = gmGuiHelpers.gm_show_question (
			_(	'Are you sure you want to delete this\n'
				'description from the document ?\n'
			),
			_('Deleting document description')
		)
		if not doit:
			return True

		document.delete_description(pk = item[0])
		return True
	#-----------------------------------
	def add_item():
		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			parent,
			-1,
			title = _('Adding document description'),
			msg = _('Below you can add a document description.\n')
		)
		result = dlg.ShowModal()
		if result == wx.ID_SAVE:
			document.add_description(dlg.value)

		dlg.Destroy()
		return True
	#-----------------------------------
	def edit_item(item):
		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			parent,
			-1,
			title = _('Editing document description'),
			msg = _('Below you can edit the document description.\n'),
			text = item[1]
		)
		result = dlg.ShowModal()
		if result == wx.ID_SAVE:
			document.update_description(pk = item[0], description = dlg.value)

		dlg.Destroy()
		return True
	#-----------------------------------
	def refresh_list(lctrl):
		descriptions = document.get_descriptions()

		lctrl.set_string_items(items = [
			u'%s%s' % ( (u' '.join(regex.split('\r\n+|\r+|\n+|\t+', desc[1])))[:30], gmTools.u_ellipsis )
			for desc in descriptions
		])
		lctrl.set_data(data = descriptions)
	#-----------------------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Select the description you are interested in.\n'),
		caption = _('Managing document descriptions'),
		columns = [_('Description')],
		edit_callback = edit_item,
		new_callback = add_item,
		delete_callback = delete_item,
		refresh_callback = refresh_list,
		single_selection = True,
		can_return_empty = True
	)

	return True
#============================================================
def _save_file_as_new_document(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(save_file_as_new_document, **kwargs)

def _save_files_as_new_document(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(save_files_as_new_document, **kwargs)
#----------------------
def save_file_as_new_document(parent=None, filename=None, document_type=None, unlock_patient=False, episode=None, review_as_normal=False):
	return save_files_as_new_document (
		parent = parent,
		filenames = [filename],
		document_type = document_type,
		unlock_patient = unlock_patient,
		episode = episode,
		review_as_normal = review_as_normal
	)
#----------------------
def save_files_as_new_document(parent=None, filenames=None, document_type=None, unlock_patient=False, episode=None, review_as_normal=False, reference=None):

	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		return None

	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if episode is None:
		all_epis = emr.get_episodes()
		# FIXME: what to do here ? probably create dummy episode
		if len(all_epis) == 0:
			episode = emr.add_episode(episode_name = _('Documents'), is_open = False)
		else:
			dlg = gmEMRStructWidgets.cEpisodeListSelectorDlg(parent = parent, id = -1, episodes = all_epis)
			dlg.SetTitle(_('Select the episode under which to file the document ...'))
			btn_pressed = dlg.ShowModal()
			episode = dlg.get_selected_item_data(only_one = True)
			dlg.Destroy()

			if (btn_pressed == wx.ID_CANCEL) or (episode is None):
				if unlock_patient:
					pat.locked = False
				return None

	doc_type = gmDocuments.create_document_type(document_type = document_type)

	docs_folder = pat.get_document_folder()
	doc = docs_folder.add_document (
		document_type = doc_type['pk_doc_type'],
		encounter = emr.active_encounter['pk_encounter'],
		episode = episode['pk_episode']
	)
	if reference is not None:
		doc['ext_ref'] = reference
		doc.save()
	doc.add_parts_from_files(files = filenames)

	if review_as_normal:
		doc.set_reviewed(technically_abnormal = False, clinically_relevant = False)

	if unlock_patient:
		pat.locked = False

	gmDispatcher.send(signal = 'statustext', msg = _('Imported new document from %s.') % filenames, beep = True)

	return doc
#----------------------
gmDispatcher.connect(signal = u'import_document_from_file', receiver = _save_file_as_new_document)
gmDispatcher.connect(signal = u'import_document_from_files', receiver = _save_files_as_new_document)
#============================================================
class cDocumentCommentPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document comment from all existing comments."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			u'ctxt_doc_type': {
				u'where_part': u'and fk_type = %(pk_doc_type)s',
				u'placeholder': u'pk_doc_type'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (field_label) *
	FROM (
		-- constrained by doc type
		SELECT
			comment AS data,
			comment AS field_label,
			comment AS list_label,
			1 AS rank
		FROM blobs.doc_med
		WHERE
			comment %(fragment_condition)s
			%(ctxt_doc_type)s

		UNION ALL

		SELECT
			comment AS data,
			comment AS field_label,
			comment AS list_label,
			2 AS rank
		FROM blobs.doc_med
		WHERE
			comment %(fragment_condition)s
	) AS q_union
) AS q_distinct
ORDER BY rank, list_label
LIMIT 25"""],
			context = context
		)
		mp.setThresholds(3, 5, 7)
		mp.unset_context(u'pk_doc_type')

		self.matcher = mp
		self.picklist_delay = 50

		self.SetToolTipString(_('Enter a comment on the document.'))
#============================================================
# document type widgets
#============================================================
def manage_document_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = cEditDocumentTypesDlg(parent = parent)
	dlg.ShowModal()
#============================================================
from Gnumed.wxGladeWidgets import wxgEditDocumentTypesDlg

class cEditDocumentTypesDlg(wxgEditDocumentTypesDlg.wxgEditDocumentTypesDlg):
	"""A dialog showing a cEditDocumentTypesPnl."""

	def __init__(self, *args, **kwargs):
		wxgEditDocumentTypesDlg.wxgEditDocumentTypesDlg.__init__(self, *args, **kwargs)

#============================================================
from Gnumed.wxGladeWidgets import wxgEditDocumentTypesPnl

class cEditDocumentTypesPnl(wxgEditDocumentTypesPnl.wxgEditDocumentTypesPnl):
	"""A panel grouping together fields to edit the list of document types."""

	def __init__(self, *args, **kwargs):
		wxgEditDocumentTypesPnl.wxgEditDocumentTypesPnl.__init__(self, *args, **kwargs)
		self.__init_ui()
		self.__register_interests()
		self.repopulate_ui()
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_doc_type.set_columns([_('Type'), _('Translation'), _('User defined'), _('In use')])
		self._LCTRL_doc_type.set_column_widths()
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'doc_type_mod_db', receiver = self._on_doc_type_mod_db)
	#--------------------------------------------------------
	def _on_doc_type_mod_db(self):
		wx.CallAfter(self.repopulate_ui)
	#--------------------------------------------------------
	def repopulate_ui(self):

		self._LCTRL_doc_type.DeleteAllItems()

		doc_types = gmDocuments.get_document_types()
		pos = len(doc_types) + 1

		for doc_type in doc_types:
			row_num = self._LCTRL_doc_type.InsertStringItem(pos, label = doc_type['type'])
			self._LCTRL_doc_type.SetStringItem(index = row_num, col = 1, label = doc_type['l10n_type'])
			if doc_type['is_user_defined']:
				self._LCTRL_doc_type.SetStringItem(index = row_num, col = 2, label = ' X ')
			if doc_type['is_in_use']:
				self._LCTRL_doc_type.SetStringItem(index = row_num, col = 3, label = ' X ')

		if len(doc_types) > 0:
			self._LCTRL_doc_type.set_data(data = doc_types)
			self._LCTRL_doc_type.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_doc_type.SetColumnWidth(col=3, width=wx.LIST_AUTOSIZE_USEHEADER)

		self._TCTRL_type.SetValue('')
		self._TCTRL_l10n_type.SetValue('')

		self._BTN_set_translation.Enable(False)
		self._BTN_delete.Enable(False)
		self._BTN_add.Enable(False)
		self._BTN_reassign.Enable(False)

		self._LCTRL_doc_type.SetFocus()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()

		self._TCTRL_type.SetValue(doc_type['type'])
		self._TCTRL_l10n_type.SetValue(doc_type['l10n_type'])

		self._BTN_set_translation.Enable(True)
		self._BTN_delete.Enable(not bool(doc_type['is_in_use']))
		self._BTN_add.Enable(False)
		self._BTN_reassign.Enable(True)

		return
	#--------------------------------------------------------
	def _on_type_modified(self, event):
		self._BTN_set_translation.Enable(False)
		self._BTN_delete.Enable(False)
		self._BTN_reassign.Enable(False)

		self._BTN_add.Enable(True)
#		self._LCTRL_doc_type.deselect_selected_item()
		return
	#--------------------------------------------------------
	def _on_set_translation_button_pressed(self, event):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()
		if doc_type.set_translation(translation = self._TCTRL_l10n_type.GetValue().strip()):
			wx.CallAfter(self.repopulate_ui)

		return
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()
		if doc_type['is_in_use']:
			gmGuiHelpers.gm_show_info (
				_(
					'Cannot delete document type\n'
					' [%s]\n'
					'because it is currently in use.'
				) % doc_type['l10n_type'],
				_('deleting document type')
			)
			return

		gmDocuments.delete_document_type(document_type = doc_type)

		return
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		desc = self._TCTRL_type.GetValue().strip()
		if desc != '':
			doc_type = gmDocuments.create_document_type(document_type = desc)		# does not create dupes
			l10n_desc = self._TCTRL_l10n_type.GetValue().strip()
			if (l10n_desc != '') and (l10n_desc != doc_type['l10n_type']):
				doc_type.set_translation(translation = l10n_desc)

		return
	#--------------------------------------------------------
	def _on_reassign_button_pressed(self, event):

		orig_type = self._LCTRL_doc_type.get_selected_item_data()
		doc_types = gmDocuments.get_document_types()

		new_type = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'From the list below select the document type you want\n'
				'all documents currently classified as:\n\n'
				' "%s"\n\n'
				'to be changed to.\n\n'
				'Be aware that this change will be applied to ALL such documents. If there\n'
				'are many documents to change it can take quite a while.\n\n'
				'Make sure this is what you want to happen !\n'
			) % orig_type['l10n_type'],
			caption = _('Reassigning document type'),
			choices = [ [gmTools.bool2subst(dt['is_user_defined'], u'X', u''), dt['type'], dt['l10n_type']] for dt in doc_types ],
			columns = [_('User defined'), _('Type'), _('Translation')],
			data = doc_types,
			single_selection = True
		)

		if new_type is None:
			return

		wx.BeginBusyCursor()
		gmDocuments.reclassify_documents_by_type(original_type = orig_type, target_type = new_type)
		wx.EndBusyCursor()

		return
#============================================================
class cDocumentTypeSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document type."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""SELECT
	data,
	field_label,
	list_label
FROM ((
	SELECT
		pk_doc_type AS data,
		l10n_type AS field_label,
		l10n_type AS list_label,
		1 AS rank
	FROM blobs.v_doc_type
	WHERE
		is_user_defined IS True
			AND
		l10n_type %(fragment_condition)s
) UNION (
	SELECT
		pk_doc_type AS data,
		l10n_type AS field_label,
		l10n_type AS list_label,
		2 AS rank
	FROM blobs.v_doc_type
	WHERE
		is_user_defined IS False
			AND
		l10n_type %(fragment_condition)s
)) AS q1
ORDER BY q1.rank, q1.list_label"""]
			)
		mp.setThresholds(2, 4, 6)

		self.matcher = mp
		self.picklist_delay = 50

		self.SetToolTipString(_('Select the document type.'))
	#--------------------------------------------------------
	def _create_data(self):

		doc_type = self.GetValue().strip()
		if doc_type == u'':
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot create document type without name.'), beep = True)
			_log.debug('cannot create document type without name')
			return

		pk = gmDocuments.create_document_type(doc_type)['pk_doc_type']
		if pk is None:
			self.data = {}
		else:
			self.SetText (
				value = doc_type,
				data = pk
			)
#============================================================
# document review widgets
#============================================================
def review_document_part(parent=None, part=None):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	dlg = cReviewDocPartDlg (
		parent = parent,
		id = -1,
		part = part
	)
	dlg.ShowModal()
	dlg.Destroy()
#------------------------------------------------------------
def review_document(parent=None, document=None):
	return review_document_part(parent = parent, part = document)
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgReviewDocPartDlg

class cReviewDocPartDlg(wxgReviewDocPartDlg.wxgReviewDocPartDlg):
	def __init__(self, *args, **kwds):
		"""Support parts and docs now.
		"""
		part = kwds['part']
		del kwds['part']
		wxgReviewDocPartDlg.wxgReviewDocPartDlg.__init__(self, *args, **kwds)

		if isinstance(part, gmDocuments.cDocumentPart):
			self.__part = part
			self.__doc = self.__part.get_containing_document()
			self.__reviewing_doc = False
		elif isinstance(part, gmDocuments.cDocument):
			self.__doc = part
			if len(self.__doc.parts) == 0:
				self.__part = None
			else:
				self.__part = self.__doc.parts[0]
			self.__reviewing_doc = True
		else:
			raise ValueError('<part> must be gmDocuments.cDocument or gmDocuments.cDocumentPart instance, got <%s>' % type(part))

		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		# FIXME: fix this
		# associated episode (add " " to avoid popping up pick list)
		self._PhWheel_episode.SetText('%s ' % self.__doc['episode'], self.__doc['pk_episode'])
		self._PhWheel_doc_type.SetText(value = self.__doc['l10n_type'], data = self.__doc['pk_type'])
		self._PhWheel_doc_type.add_callback_on_set_focus(self._on_doc_type_gets_focus)
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)

		if self.__reviewing_doc:
			self._PRW_doc_comment.SetText(gmTools.coalesce(self.__doc['comment'], ''))
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = self.__doc['pk_type'])
		else:
			self._PRW_doc_comment.SetText(gmTools.coalesce(self.__part['obj_comment'], ''))

		fts = gmDateTime.cFuzzyTimestamp(timestamp = self.__doc['clin_when'])
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._TCTRL_reference.SetValue(gmTools.coalesce(self.__doc['ext_ref'], ''))
		if self.__reviewing_doc:
			self._TCTRL_filename.Enable(False)
			self._SPINCTRL_seq_idx.Enable(False)
		else:
			self._TCTRL_filename.SetValue(gmTools.coalesce(self.__part['filename'], ''))
			self._SPINCTRL_seq_idx.SetValue(gmTools.coalesce(self.__part['seq_idx'], 0))

		self._LCTRL_existing_reviews.InsertColumn(0, _('who'))
		self._LCTRL_existing_reviews.InsertColumn(1, _('when'))
		self._LCTRL_existing_reviews.InsertColumn(2, _('+/-'))
		self._LCTRL_existing_reviews.InsertColumn(3, _('!'))
		self._LCTRL_existing_reviews.InsertColumn(4, _('comment'))

		self.__reload_existing_reviews()

		if self._LCTRL_existing_reviews.GetItemCount() > 0:
			self._LCTRL_existing_reviews.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_existing_reviews.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)
			self._LCTRL_existing_reviews.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_existing_reviews.SetColumnWidth(col=3, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_existing_reviews.SetColumnWidth(col=4, width=wx.LIST_AUTOSIZE)

		if self.__part is None:
			self._ChBOX_review.SetValue(False)
			self._ChBOX_review.Enable(False)
			self._ChBOX_abnormal.Enable(False)
			self._ChBOX_relevant.Enable(False)
			self._ChBOX_sign_all_pages.Enable(False)
		else:
			me = gmStaff.gmCurrentProvider()
			if self.__part['pk_intended_reviewer'] == me['pk_staff']:
				msg = _('(you are the primary reviewer)')
			else:
				other = gmStaff.cStaff(aPK_obj = self.__part['pk_intended_reviewer'])
				msg = _('(someone else is the intended reviewer: %s)') % other['short_alias']
			self._TCTRL_responsible.SetValue(msg)
			# init my review if any
			if self.__part['reviewed_by_you']:
				revs = self.__part.get_reviews()
				for rev in revs:
					if rev['is_your_review']:
						self._ChBOX_abnormal.SetValue(bool(rev[2]))
						self._ChBOX_relevant.SetValue(bool(rev[3]))
						break

			self._ChBOX_sign_all_pages.SetValue(self.__reviewing_doc)

		return True
	#--------------------------------------------------------
	def __reload_existing_reviews(self):
		self._LCTRL_existing_reviews.DeleteAllItems()
		if self.__part is None:
			return True
		revs = self.__part.get_reviews()		# FIXME: this is ugly as sin, it should be dicts, not lists
		if len(revs) == 0:
			return True
		# find special reviews
		review_by_responsible_doc = None
		reviews_by_others = []
		for rev in revs:
			if rev['is_review_by_responsible_reviewer'] and not rev['is_your_review']:
				review_by_responsible_doc = rev
			if not (rev['is_review_by_responsible_reviewer'] or rev['is_your_review']):
				reviews_by_others.append(rev)
		# display them
		if review_by_responsible_doc is not None:
			row_num = self._LCTRL_existing_reviews.InsertStringItem(sys.maxint, label=review_by_responsible_doc[0])
			self._LCTRL_existing_reviews.SetItemTextColour(row_num, col=wx.BLUE)
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=0, label=review_by_responsible_doc[0])
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=1, label=review_by_responsible_doc[1].strftime('%x %H:%M'))
			if review_by_responsible_doc['is_technically_abnormal']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=2, label=u'X')
			if review_by_responsible_doc['clinically_relevant']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=3, label=u'X')
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=4, label=review_by_responsible_doc[6])
			row_num += 1
		for rev in reviews_by_others:
			row_num = self._LCTRL_existing_reviews.InsertStringItem(sys.maxint, label=rev[0])
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=0, label=rev[0])
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=1, label=rev[1].strftime('%x %H:%M'))
			if rev['is_technically_abnormal']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=2, label=u'X')
			if rev['clinically_relevant']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=3, label=u'X')
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=4, label=rev[6])
		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		"""Save the metadata to the backend."""

		evt.Skip()

		# 1) handle associated episode
		pk_episode = self._PhWheel_episode.GetData(can_create=True, is_open=True)
		if pk_episode is None:
			gmGuiHelpers.gm_show_error (
				_('Cannot create episode\n [%s]'),
				_('Editing document properties')
			)
			return False

		doc_type = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type is None:
			gmDispatcher.send(signal='statustext', msg=_('Cannot change document type to [%s].') % self._PhWheel_doc_type.GetValue().strip())
			return False

		# since the phrasewheel operates on the active
		# patient all episodes really should belong
		# to it so we don't check patient change
		self.__doc['pk_episode'] = pk_episode
		self.__doc['pk_type'] = doc_type
		if self.__reviewing_doc:
			self.__doc['comment'] = self._PRW_doc_comment.GetValue().strip()
		# FIXME: a rather crude way of error checking:
		if self._PhWheel_doc_date.GetData() is not None:
			self.__doc['clin_when'] = self._PhWheel_doc_date.GetData().get_pydt()
		self.__doc['ext_ref'] = self._TCTRL_reference.GetValue().strip()

		success, data = self.__doc.save_payload()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Cannot link the document to episode\n\n [%s]') % epi_name,
				_('Editing document properties')
			)
			return False

		# 2) handle review
		if self._ChBOX_review.GetValue():
			provider = gmStaff.gmCurrentProvider()
			abnormal = self._ChBOX_abnormal.GetValue()
			relevant = self._ChBOX_relevant.GetValue()
			msg = None
			if self.__reviewing_doc:		# - on all pages
				if not self.__doc.set_reviewed(technically_abnormal = abnormal, clinically_relevant = relevant):
					msg = _('Error setting "reviewed" status of this document.')
				if self._ChBOX_responsible.GetValue():
					if not self.__doc.set_primary_reviewer(reviewer = provider['pk_staff']):
						msg = _('Error setting responsible clinician for this document.')
			else:								# - just on this page
				if not self.__part.set_reviewed(technically_abnormal = abnormal, clinically_relevant = relevant):
					msg = _('Error setting "reviewed" status of this part.')
				if self._ChBOX_responsible.GetValue():
					self.__part['pk_intended_reviewer'] = provider['pk_staff']
			if msg is not None:
				gmGuiHelpers.gm_show_error(msg, _('Editing document properties'))
				return False

		# 3) handle "page" specific parts
		if not self.__reviewing_doc:
			self.__part['filename'] = gmTools.none_if(self._TCTRL_filename.GetValue().strip(), u'')
			new_idx = gmTools.none_if(self._SPINCTRL_seq_idx.GetValue(), 0)
			if self.__part['seq_idx'] != new_idx:
				if new_idx in self.__doc['seq_idx_list']:
					msg = _(
						'Cannot set page number to [%s] because\n'
						'another page with this number exists.\n'
						'\n'
						'Page numbers in use:\n'
						'\n'
						' %s'
					) % (
						new_idx,
						self.__doc['seq_idx_list']
					)
					gmGuiHelpers.gm_show_error(msg, _('Editing document part properties'))
				else:
					self.__part['seq_idx'] = new_idx
			self.__part['obj_comment'] = self._PRW_doc_comment.GetValue().strip()
			success, data = self.__part.save_payload()
			if not success:
				gmGuiHelpers.gm_show_error (
					_('Error saving part properties.'),
					_('Editing document part properties')
				)
				return False

		return True
	#--------------------------------------------------------
	def _on_reviewed_box_checked(self, evt):
		state = self._ChBOX_review.GetValue()
		self._ChBOX_abnormal.Enable(enable = state)
		self._ChBOX_relevant.Enable(enable = state)
		self._ChBOX_responsible.Enable(enable = state)
	#--------------------------------------------------------
	def _on_doc_type_gets_focus(self):
		"""Per Jim: Changing the doc type happens a lot more often
		   then correcting spelling, hence select-all on getting focus.
		"""
		self._PhWheel_doc_type.SetSelection(-1, -1)
	#--------------------------------------------------------
	def _on_doc_type_loses_focus(self):
		pk_doc_type = self._PhWheel_doc_type.GetData()
		if pk_doc_type is None:
			self._PRW_doc_comment.unset_context(context = 'pk_doc_type')
		else:
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = pk_doc_type)
		return True
#============================================================
def acquire_images_from_capture_device(device=None, calling_window=None):

	_log.debug('acquiring images from [%s]', device)

	# do not import globally since we might want to use
	# this module without requiring any scanner to be available
	from Gnumed.pycommon import gmScanBackend
	try:
		fnames = gmScanBackend.acquire_pages_into_files (
			device = device,
			delay = 5,
			calling_window = calling_window
		)
	except OSError:
		_log.exception('problem acquiring image from source')
		gmGuiHelpers.gm_show_error (
			aMessage = _(
				'No images could be acquired from the source.\n\n'
				'This may mean the scanner driver is not properly installed.\n\n'
				'On Windows you must install the TWAIN Python module\n'
				'while on Linux and MacOSX it is recommended to install\n'
				'the XSane package.'
			),
			aTitle = _('Acquiring images')
		)
		return None

	_log.debug('acquired %s images', len(fnames))

	return fnames
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgScanIdxPnl

class cScanIdxDocsPnl(wxgScanIdxPnl.wxgScanIdxPnl, gmPlugin.cPatientChange_PluginMixin):
	def __init__(self, *args, **kwds):
		wxgScanIdxPnl.wxgScanIdxPnl.__init__(self, *args, **kwds)
		gmPlugin.cPatientChange_PluginMixin.__init__(self)

		self._PhWheel_reviewer.matcher = gmPerson.cMatchProvider_Provider()

		self.__init_ui_data()
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)

		# make me and listctrl a file drop target
		dt = gmGuiHelpers.cFileDropTarget(self)
		self.SetDropTarget(dt)
		dt = gmGuiHelpers.cFileDropTarget(self._LBOX_doc_pages)
		self._LBOX_doc_pages.SetDropTarget(dt)
		self._LBOX_doc_pages.add_filenames = self.add_filenames_to_listbox

		# do not import globally since we might want to use
		# this module without requiring any scanner to be available
		from Gnumed.pycommon import gmScanBackend
		self.scan_module = gmScanBackend
	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def add_filenames_to_listbox(self, filenames):
		self.add_filenames(filenames=filenames)
	#--------------------------------------------------------
	def add_filenames(self, filenames):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal='statustext', msg=_('Cannot accept new documents. No active patient.'))
			return

		# dive into folders dropped onto us and extract files (one level deep only)
		real_filenames = []
		for pathname in filenames:
			try:
				files = os.listdir(pathname)
				gmDispatcher.send(signal='statustext', msg=_('Extracting files from folder [%s] ...') % pathname)
				for file in files:
					fullname = os.path.join(pathname, file)
					if not os.path.isfile(fullname):
						continue
					real_filenames.append(fullname)
			except OSError:
				real_filenames.append(pathname)

		self.acquired_pages.extend(real_filenames)
		self.__reload_LBOX_doc_pages()
	#--------------------------------------------------------
	def repopulate_ui(self):
		pass
	#--------------------------------------------------------
	# patient change plugin API
	#--------------------------------------------------------
	def _pre_patient_selection(self, **kwds):
		# FIXME: persist pending data from here
		pass
	#--------------------------------------------------------
	def _post_patient_selection(self, **kwds):
		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		# -----------------------------
		self._PhWheel_episode.SetText(value = _('other documents'), suppress_smarts = True)
		self._PhWheel_doc_type.SetText('')
		# -----------------------------
		# FIXME: make this configurable: either now() or last_date()
		fts = gmDateTime.cFuzzyTimestamp()
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._PRW_doc_comment.SetText('')
		# FIXME: should be set to patient's primary doc
		self._PhWheel_reviewer.selection_only = True
		me = gmStaff.gmCurrentProvider()
		self._PhWheel_reviewer.SetText (
			value = u'%s (%s%s %s)' % (me['short_alias'], me['title'], me['firstnames'], me['lastnames']),
			data = me['pk_staff']
		)
		# -----------------------------
		# FIXME: set from config item
		self._ChBOX_reviewed.SetValue(False)
		self._ChBOX_abnormal.Disable()
		self._ChBOX_abnormal.SetValue(False)
		self._ChBOX_relevant.Disable()
		self._ChBOX_relevant.SetValue(False)
		# -----------------------------
		self._TBOX_description.SetValue('')
		# -----------------------------
		# the list holding our page files
		self._LBOX_doc_pages.Clear()
		self.acquired_pages = []

		self._PhWheel_doc_type.SetFocus()
	#--------------------------------------------------------
	def __reload_LBOX_doc_pages(self):
		self._LBOX_doc_pages.Clear()
		if len(self.acquired_pages) > 0:
			for i in range(len(self.acquired_pages)):
				fname = self.acquired_pages[i]
				self._LBOX_doc_pages.Append(_('part %s: %s') % (i+1, fname), fname)
	#--------------------------------------------------------
	def __valid_for_save(self):
		title = _('saving document')

		if self.acquired_pages is None or len(self.acquired_pages) == 0:
			dbcfg = gmCfg.cCfgSQL()
			allow_empty = bool(dbcfg.get2 (
				option =  u'horstspace.scan_index.allow_partless_documents',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user',
				default = False
			))
			if allow_empty:
				save_empty = gmGuiHelpers.gm_show_question (
					aMessage = _('No parts to save. Really save an empty document as a reference ?'),
					aTitle = title
				)
				if not save_empty:
					return False
			else:
				gmGuiHelpers.gm_show_error (
					aMessage = _('No parts to save. Aquire some parts first.'),
					aTitle = title
				)
				return False

		doc_type_pk = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type_pk is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('No document type applied. Choose a document type'),
				aTitle = title
			)
			return False

		# this should be optional, actually
#		if self._PRW_doc_comment.GetValue().strip() == '':
#			gmGuiHelpers.gm_show_error (
#				aMessage = _('No document comment supplied. Add a comment for this document.'),
#				aTitle = title
#			)
#			return False

		if self._PhWheel_episode.GetValue().strip() == '':
			gmGuiHelpers.gm_show_error (
				aMessage = _('You must select an episode to save this document under.'),
				aTitle = title
			)
			return False

		if self._PhWheel_reviewer.GetData() is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('You need to select from the list of staff members the doctor who is intended to sign the document.'),
				aTitle = title
			)
			return False

		return True
	#--------------------------------------------------------
	def get_device_to_use(self, reconfigure=False):

		if not reconfigure:
			dbcfg = gmCfg.cCfgSQL()
			device = dbcfg.get2 (
				option =  'external.xsane.default_device',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'workplace',
				default = ''
			)
			if device.strip() == u'':
				device = None
			if device is not None:
				return device

		try:
			devices = self.scan_module.get_devices()
		except:
			_log.exception('cannot retrieve list of image sources')
			gmDispatcher.send(signal = 'statustext', msg = _('There is no scanner support installed on this machine.'))
			return None

		if devices is None:
			# get_devices() not implemented for TWAIN yet
			# XSane has its own chooser (so does TWAIN)
			return None

		if len(devices) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot find an active scanner.'))
			return None

#		device_names = []
#		for device in devices:
#			device_names.append('%s (%s)' % (device[2], device[0]))

		device = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _('Select an image capture device'),
			caption = _('device selection'),
			choices = [ '%s (%s)' % (d[2], d[0]) for d in devices ],
			columns = [_('Device')],
			data = devices,
			single_selection = True
		)
		if device is None:
			return None

		# FIXME: add support for actually reconfiguring
		return device[0]
	#--------------------------------------------------------
	# event handling API
	#--------------------------------------------------------
	def _scan_btn_pressed(self, evt):

		chosen_device = self.get_device_to_use()

		tmpdir = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp'))
		try:
			gmTools.mkdir(tmpdir)
		except:
			tmpdir = None

		# FIXME: configure whether to use XSane or sane directly
		# FIXME: add support for xsane_device_settings argument
		try:
			fnames = self.scan_module.acquire_pages_into_files (
				device = chosen_device,
				delay = 5,
				tmpdir = tmpdir,
				calling_window = self
			)
		except OSError:
			_log.exception('problem acquiring image from source')
			gmGuiHelpers.gm_show_error (
				aMessage = _(
					'No pages could be acquired from the source.\n\n'
					'This may mean the scanner driver is not properly installed.\n\n'
					'On Windows you must install the TWAIN Python module\n'
					'while on Linux and MacOSX it is recommended to install\n'
					'the XSane package.'
				),
				aTitle = _('acquiring page')
			)
			return None

		if len(fnames) == 0:		# no pages scanned
			return True

		self.acquired_pages.extend(fnames)
		self.__reload_LBOX_doc_pages()

		return True
	#--------------------------------------------------------
	def _load_btn_pressed(self, evt):
		# patient file chooser
		dlg = wx.FileDialog (
			parent = None,
			message = _('Choose a file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "%s (*)|*|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST | wx.MULTIPLE
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			files = dlg.GetPaths()
			for file in files:
				self.acquired_pages.append(file)
			self.__reload_LBOX_doc_pages()
		dlg.Destroy()
	#--------------------------------------------------------
	def _show_btn_pressed(self, evt):
		# did user select a page ?
		page_idx = self._LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			gmGuiHelpers.gm_show_info (
				aMessage = _('You must select a part before you can view it.'),
				aTitle = _('displaying part')
			)
			return None
		# now, which file was that again ?
		page_fname = self._LBOX_doc_pages.GetClientData(page_idx)

		(result, msg) = gmMimeLib.call_viewer_on_file(page_fname)
		if not result:
			gmGuiHelpers.gm_show_warning (
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('displaying part')
			)
			return None
		return 1
	#--------------------------------------------------------
	def _del_btn_pressed(self, event):
		page_idx = self._LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			gmGuiHelpers.gm_show_info (
				aMessage = _('You must select a part before you can delete it.'),
				aTitle = _('deleting part')
			)
			return None
		page_fname = self._LBOX_doc_pages.GetClientData(page_idx)

		# 1) del item from self.acquired_pages
		self.acquired_pages[page_idx:(page_idx+1)] = []

		# 2) reload list box
		self.__reload_LBOX_doc_pages()

		# 3) optionally kill file in the file system
		do_delete = gmGuiHelpers.gm_show_question (
			_('The part has successfully been removed from the document.\n'
			  '\n'
			  'Do you also want to permanently delete the file\n'
			  '\n'
			  ' [%s]\n'
			  '\n'
			  'from which this document part was loaded ?\n'
			  '\n'
			  'If it is a temporary file for a page you just scanned\n'
			  'this makes a lot of sense. In other cases you may not\n'
			  'want to lose the file.\n'
			  '\n'
			  'Pressing [YES] will permanently remove the file\n'
			  'from your computer.\n'
			) % page_fname,
			_('Removing document part')
		)
		if do_delete:
			try:
				os.remove(page_fname)
			except:
				_log.exception('Error deleting file.')
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot delete part in file [%s].\n\nYou may not have write access to it.') % page_fname,
					aTitle = _('deleting part')
				)

		return 1
	#--------------------------------------------------------
	def _save_btn_pressed(self, evt):

		if not self.__valid_for_save():
			return False

		wx.BeginBusyCursor()

		pat = gmPerson.gmCurrentPatient()
		doc_folder = pat.get_document_folder()
		emr = pat.get_emr()

		# create new document
		pk_episode = self._PhWheel_episode.GetData()
		if pk_episode is None:
			episode = emr.add_episode (
				episode_name = self._PhWheel_episode.GetValue().strip(),
				is_open = True
			)
			if episode is None:
				wx.EndBusyCursor()
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot start episode [%s].') % self._PhWheel_episode.GetValue().strip(),
					aTitle = _('saving document')
				)
				return False
			pk_episode = episode['pk_episode']

		encounter = emr.active_encounter['pk_encounter']
		document_type = self._PhWheel_doc_type.GetData()
		new_doc = doc_folder.add_document(document_type, encounter, pk_episode)
		if new_doc is None:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot create new document.'),
				aTitle = _('saving document')
			)
			return False

		# update business object with metadata
		# - date of generation
		new_doc['clin_when'] = self._PhWheel_doc_date.GetData().get_pydt()
		# - external reference
		cfg = gmCfg.cCfgSQL()
		generate_uuid = bool (
			cfg.get2 (
				option = 'horstspace.scan_index.generate_doc_uuid',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user',
				default = False
			)
		)
		ref = None
		if generate_uuid:
			ref = gmDocuments.get_ext_ref()
		if ref is not None:
			new_doc['ext_ref'] = ref
		# - comment
		comment = self._PRW_doc_comment.GetLineText(0).strip()
		if comment != u'':
			new_doc['comment'] = comment
		# - save it
		if not new_doc.save_payload():
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot update document metadata.'),
				aTitle = _('saving document')
			)
			return False
		# - long description
		description = self._TBOX_description.GetValue().strip()
		if description != '':
			if not new_doc.add_description(description):
				wx.EndBusyCursor()
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot add document description.'),
					aTitle = _('saving document')
				)
				return False

		# add document parts from files
		success, msg, filename = new_doc.add_parts_from_files (
			files = self.acquired_pages,
			reviewer = self._PhWheel_reviewer.GetData()
		)
		if not success:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				aMessage = msg,
				aTitle = _('saving document')
			)
			return False

		# set reviewed status
		if self._ChBOX_reviewed.GetValue():
			if not new_doc.set_reviewed (
				technically_abnormal = self._ChBOX_abnormal.GetValue(),
				clinically_relevant = self._ChBOX_relevant.GetValue()
			):
				msg = _('Error setting "reviewed" status of new document.')

		gmHooks.run_hook_script(hook = u'after_new_doc_created')

		# inform user
		show_id = bool (
			cfg.get2 (
				option = 'horstspace.scan_index.show_doc_id',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user'
			)
		)
		wx.EndBusyCursor()
		if show_id:
			if ref is None:
				msg = _('Successfully saved the new document.')
			else:
				msg = _(
"""The reference ID for the new document is:

 <%s>

You probably want to write it down on the
original documents.

If you don't care about the ID you can switch
off this message in the GNUmed configuration.""") % ref
			gmGuiHelpers.gm_show_info (
				aMessage = msg,
				aTitle = _('Saving document')
			)
		else:
			gmDispatcher.send(signal='statustext', msg=_('Successfully saved new document.'))

		self.__init_ui_data()
		return True
	#--------------------------------------------------------
	def _startover_btn_pressed(self, evt):
		self.__init_ui_data()
	#--------------------------------------------------------
	def _reviewed_box_checked(self, evt):
		self._ChBOX_abnormal.Enable(enable = self._ChBOX_reviewed.GetValue())
		self._ChBOX_relevant.Enable(enable = self._ChBOX_reviewed.GetValue())
	#--------------------------------------------------------
	def _on_doc_type_loses_focus(self):
		pk_doc_type = self._PhWheel_doc_type.GetData()
		if pk_doc_type is None:
			self._PRW_doc_comment.unset_context(context = 'pk_doc_type')
		else:
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = pk_doc_type)
		return True
#============================================================
def display_document_part(parent=None, part=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# sanity check
	if part['size'] == 0:
		_log.debug('cannot display part [%s] - 0 bytes', part['pk_obj'])
		gmGuiHelpers.gm_show_error (
			aMessage = _('Document part does not seem to exist in database !'),
			aTitle = _('showing document')
		)
		return None

	wx.BeginBusyCursor()
	cfg = gmCfg.cCfgSQL()

	# determine database export chunk size
	chunksize = int(
	cfg.get2 (
		option = "horstspace.blob_export_chunk_size",
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = 2048
	))

	# shall we force blocking during view ?
	block_during_view = bool( cfg.get2 (
		option = 'horstspace.document_viewer.block_during_view',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'user',
		default = None
	))

	wx.EndBusyCursor()

	# display it
	successful, msg = part.display_via_mime (
		chunksize = chunksize,
		block = block_during_view
	)
	if not successful:
		gmGuiHelpers.gm_show_error (
			aMessage = _('Cannot display document part:\n%s') % msg,
			aTitle = _('showing document')
		)
		return None

	# handle review after display
	# 0: never
	# 1: always
	# 2: if no review by myself exists yet
	# 3: if no review at all exists yet
	# 4: if no review by responsible reviewer
	review_after_display = int(cfg.get2 (
		option = 'horstspace.document_viewer.review_after_display',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'user',
		default = 3
	))
	if review_after_display == 1:			# always review
		review_document_part(parent = parent, part = part)
	elif review_after_display == 2:			# review if no review by me exists
		review_by_me = filter(lambda rev: rev['is_your_review'], part.get_reviews())
		if len(review_by_me) == 0:
			review_document_part(parent = parent, part = part)
	elif review_after_display == 3:
		if len(part.get_reviews()) == 0:
			review_document_part(parent = parent, part = part)
	elif review_after_display == 4:
		reviewed_by_responsible = filter(lambda rev: rev['is_review_by_responsible_reviewer'], part.get_reviews())
		if len(reviewed_by_responsible) == 0:
			review_document_part(parent = parent, part = part)

	return True
#============================================================
def manage_documents(parent=None, msg=None):

	pat = gmPerson.gmCurrentPatient()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#--------------------------------------------------------
	def edit(document=None):
		return
		#return edit_consumable_substance(parent = parent, substance = substance, single_entry = (substance is not None))
	#--------------------------------------------------------
	def delete(document):
		return
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		return gmMedication.delete_consumable_substance(substance = substance['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
		docs = pat.document_folder.get_documents()
		items = [ [
			gmDateTime.pydt_strftime(d['clin_when'], u'%Y-%m-%d', accuracy = gmDateTime.acc_days),
			d['l10n_type'],
			gmTools.coalesce(d['comment'], u''),
			gmTools.coalesce(d['ext_ref'], u''),
			d['pk_doc']
		] for d in docs ]
		lctrl.set_string_items(items)
		lctrl.set_data(docs)
	#------------------------------------------------------------
	if msg is None:
		msg = _('Document list for this patient.')
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing documents.'),
		columns = [_('Generated'), _('Type'), _('Comment'), _('Ref #'), u'#'],
		single_selection = True,
		#new_callback = edit,
		#edit_callback = edit,
		#delete_callback = delete,
		refresh_callback = refresh
		#,left_extra_button = (_('Import'), _('Import consumable substances from a drug database.'), add_from_db)
	)
#============================================================
from Gnumed.wxGladeWidgets import wxgSelectablySortedDocTreePnl

class cSelectablySortedDocTreePnl(wxgSelectablySortedDocTreePnl.wxgSelectablySortedDocTreePnl):
	"""A panel with a document tree which can be sorted."""
	#--------------------------------------------------------
	# inherited event handlers
	#--------------------------------------------------------
	def _on_sort_by_age_selected(self, evt):
		self._doc_tree.sort_mode = 'age'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_age.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_review_selected(self, evt):
		self._doc_tree.sort_mode = 'review'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_review.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_episode_selected(self, evt):
		self._doc_tree.sort_mode = 'episode'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_episode.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_issue_selected(self, event):
		self._doc_tree.sort_mode = 'issue'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_issue.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_type_selected(self, evt):
		self._doc_tree.sort_mode = 'type'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_type.SetValue(True)
#============================================================
class cDocTree(wx.TreeCtrl, gmRegetMixin.cRegetOnPaintMixin):
	# FIXME: handle expansion state
	"""This wx.TreeCtrl derivative displays a tree view of stored medical documents.

	It listens to document and patient changes and updated itself accordingly.

	This acts on the current patient.
	"""
	_sort_modes = ['age', 'review', 'episode', 'type', 'issue']
	_root_node_labels = None
	#--------------------------------------------------------
	def __init__(self, parent, id, *args, **kwds):
		"""Set up our specialised tree.
		"""
		kwds['style'] = wx.TR_NO_BUTTONS | wx.NO_BORDER | wx.TR_SINGLE
		wx.TreeCtrl.__init__(self, parent, id, *args, **kwds)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		tmp = _('available documents (%s)')
		unsigned = _('unsigned (%s) on top') % u'\u270D'
		cDocTree._root_node_labels = {
			'age': tmp % _('most recent on top'),
			'review': tmp % unsigned,
			'episode': tmp % _('sorted by episode'),
			'issue': tmp % _('sorted by health issue'),
			'type': tmp % _('sorted by type')
		}

		self.root = None
		self.__sort_mode = 'age'

		self.__build_context_menus()
		self.__register_interests()
		self._schedule_data_reget()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def display_selected_part(self, *args, **kwargs):

		node = self.GetSelection()
		node_data = self.GetPyData(node)

		if not isinstance(node_data, gmDocuments.cDocumentPart):
			return True

		self.__display_part(part = node_data)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_sort_mode(self):
		return self.__sort_mode
	#-----
	def _set_sort_mode(self, mode):
		if mode is None:
			mode = 'age'

		if mode == self.__sort_mode:
			return

		if mode not in cDocTree._sort_modes:
			raise ValueError('invalid document tree sort mode [%s], valid modes: %s' % (mode, cDocTree._sort_modes))

		self.__sort_mode = mode

		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			return

		self._schedule_data_reget()
	#-----
	sort_mode = property(_get_sort_mode, _set_sort_mode)
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot load documents. No active patient.'))
			return False

		if not self.__populate_tree():
			return False

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		# connect handlers
		wx.EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self._on_activate)
		wx.EVT_TREE_ITEM_RIGHT_CLICK (self, self.GetId(), self.__on_right_click)

#		 wx.EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)

		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_doc_mod_db)
		gmDispatcher.connect(signal = u'doc_page_mod_db', receiver = self._on_doc_page_mod_db)
	#--------------------------------------------------------
	def __build_context_menus(self):

		# --- part context menu ---
		self.__part_context_menu = wx.Menu(title = _('Part Actions:'))

		ID = wx.NewId()
		self.__part_context_menu.Append(ID, _('Display part'))
		wx.EVT_MENU(self.__part_context_menu, ID, self.__display_curr_part)

		ID = wx.NewId()
		self.__part_context_menu.Append(ID, _('%s Sign/Edit properties') % u'\u270D')
		wx.EVT_MENU(self.__part_context_menu, ID, self.__review_curr_part)

		self.__part_context_menu.AppendSeparator()

		item = self.__part_context_menu.Append(-1, _('Delete part'))
		self.Bind(wx.EVT_MENU, self.__delete_part, item)

		item = self.__part_context_menu.Append(-1, _('Move part'))
		self.Bind(wx.EVT_MENU, self.__move_part, item)

		ID = wx.NewId()
		self.__part_context_menu.Append(ID, _('Print part'))
		wx.EVT_MENU(self.__part_context_menu, ID, self.__print_part)

		ID = wx.NewId()
		self.__part_context_menu.Append(ID, _('Fax part'))
		wx.EVT_MENU(self.__part_context_menu, ID, self.__fax_part)

		ID = wx.NewId()
		self.__part_context_menu.Append(ID, _('Mail part'))
		wx.EVT_MENU(self.__part_context_menu, ID, self.__mail_part)

		self.__part_context_menu.AppendSeparator()			# so we can append some items

		# --- doc context menu ---
		self.__doc_context_menu = wx.Menu(title = _('Document Actions:'))

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('%s Sign/Edit properties') % u'\u270D')
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__review_curr_part)

		self.__doc_context_menu.AppendSeparator()

		item = self.__doc_context_menu.Append(-1, _('Add parts'))
		self.Bind(wx.EVT_MENU, self.__add_part, item)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Print all parts'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__print_doc)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Fax all parts'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__fax_doc)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Mail all parts'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__mail_doc)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Export all parts'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__export_doc_to_disk)

		self.__doc_context_menu.AppendSeparator()

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Delete document'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__delete_document)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Access external original'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__access_external_original)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Edit corresponding encounter'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__edit_encounter_details)

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Select corresponding encounter'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__select_encounter)

#		self.__doc_context_menu.AppendSeparator()

		ID = wx.NewId()
		self.__doc_context_menu.Append(ID, _('Manage descriptions'))
		wx.EVT_MENU(self.__doc_context_menu, ID, self.__manage_document_descriptions)

		# document / description
#		self.__desc_menu = wx.Menu()
#		ID = wx.NewId()
#		self.__doc_context_menu.AppendMenu(ID, _('Descriptions ...'), self.__desc_menu)

#		ID = wx.NewId()
#		self.__desc_menu.Append(ID, _('Add new description'))
#		wx.EVT_MENU(self.__desc_menu, ID, self.__add_doc_desc)

#		ID = wx.NewId()
#		self.__desc_menu.Append(ID, _('Delete description'))
#		wx.EVT_MENU(self.__desc_menu, ID, self.__del_doc_desc)

#		self.__desc_menu.AppendSeparator()
	#--------------------------------------------------------
	def __populate_tree(self):

		wx.BeginBusyCursor()

		# clean old tree
		if self.root is not None:
			self.DeleteAllItems()

		# init new tree
		self.root = self.AddRoot(cDocTree._root_node_labels[self.__sort_mode], -1, -1)
		self.SetItemPyData(self.root, None)
		self.SetItemHasChildren(self.root, False)

		# read documents from database
		curr_pat = gmPerson.gmCurrentPatient()
		docs_folder = curr_pat.get_document_folder()
		docs = docs_folder.get_documents()

		if docs is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error searching documents.'),
				aTitle = _('loading document list')
			)
			# avoid recursion of GUI updating
			wx.EndBusyCursor()
			return True

		if len(docs) == 0:
			wx.EndBusyCursor()
			return True

		# fill new tree from document list
		self.SetItemHasChildren(self.root, True)

		# add our documents as first level nodes
		intermediate_nodes = {}
		for doc in docs:

			parts = doc.parts

			label = _('%s%7s %s:%s (%s part(s)%s)') % (
				gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, u'', u'?'),
				doc['clin_when'].strftime('%m/%Y'),
				doc['l10n_type'][:26],
				gmTools.coalesce(initial = doc['comment'], instead = u'', template_initial = u' %s'),
				len(parts),
				gmTools.coalesce(initial = doc['ext_ref'], instead = u'', template_initial = u', \u00BB%s\u00AB')
			)

			# need intermediate branch level ?
			if self.__sort_mode == 'episode':
				lbl = u'%s%s' % (doc['episode'], gmTools.coalesce(doc['health_issue'], u'', u' (%s)'))
				if not intermediate_nodes.has_key(lbl):
					intermediate_nodes[lbl] = self.AppendItem(parent = self.root, text = lbl)
					self.SetItemBold(intermediate_nodes[lbl], bold = True)
					self.SetItemPyData(intermediate_nodes[lbl], None)
					self.SetItemHasChildren(intermediate_nodes[lbl], True)
				parent = intermediate_nodes[lbl]
			elif self.__sort_mode == 'type':
				lbl = doc['l10n_type']
				if not intermediate_nodes.has_key(lbl):
					intermediate_nodes[lbl] = self.AppendItem(parent = self.root, text = lbl)
					self.SetItemBold(intermediate_nodes[lbl], bold = True)
					self.SetItemPyData(intermediate_nodes[lbl], None)
					self.SetItemHasChildren(intermediate_nodes[lbl], True)
				parent = intermediate_nodes[lbl]
			elif self.__sort_mode == 'issue':
				if doc['health_issue'] is None:
					lbl = _('Unattributed episode: %s') % doc['episode']
				else:
					lbl = doc['health_issue']
				if not intermediate_nodes.has_key(lbl):
					intermediate_nodes[lbl] = self.AppendItem(parent = self.root, text = lbl)
					self.SetItemBold(intermediate_nodes[lbl], bold = True)
					self.SetItemPyData(intermediate_nodes[lbl], None)
					self.SetItemHasChildren(intermediate_nodes[lbl], True)
				parent = intermediate_nodes[lbl]
			else:
				parent = self.root

			doc_node = self.AppendItem(parent = parent, text = label)
			#self.SetItemBold(doc_node, bold = True)
			self.SetItemPyData(doc_node, doc)
			if len(parts) == 0:
				self.SetItemHasChildren(doc_node, False)
			else:
				self.SetItemHasChildren(doc_node, True)

			# now add parts as child nodes
			for part in parts:
#				if part['clinically_relevant']:
#					rel = ' [%s]' % _('Cave')
#				else:
#					rel = ''
				f_ext = u''
				if part['filename'] is not None:
					f_ext = os.path.splitext(part['filename'])[1].strip('.').strip()
				if f_ext != u'':
					f_ext = u' .' + f_ext.upper()
				label = '%s%s (%s%s)%s' % (
					gmTools.bool2str (
						boolean = part['reviewed'] or part['reviewed_by_you'] or part['reviewed_by_intended_reviewer'],
						true_str = u'',
						false_str = gmTools.u_writing_hand
					),
					_('part %2s') % part['seq_idx'],
					gmTools.size2str(part['size']),
					f_ext,
					gmTools.coalesce (
						part['obj_comment'],
						u'',
						u': %s%%s%s' % (gmTools.u_left_double_angle_quote, gmTools.u_right_double_angle_quote)
					)
				)

				part_node = self.AppendItem(parent = doc_node, text = label)
				self.SetItemPyData(part_node, part)
				self.SetItemHasChildren(part_node, False)

		self.__sort_nodes()
		self.SelectItem(self.root)

		# FIXME: apply expansion state if available or else ...
		# FIXME: ... uncollapse to default state
		self.Expand(self.root)
		if self.__sort_mode in ['episode', 'type', 'issue']:
			for key in intermediate_nodes.keys():
				self.Expand(intermediate_nodes[key])

		wx.EndBusyCursor()

		return True
	#------------------------------------------------------------------------
	def OnCompareItems (self, node1=None, node2=None):
		"""Used in sorting items.

		-1: 1 < 2
		 0: 1 = 2
		 1: 1 > 2
		"""
		# Windows can send bogus events so ignore that
		if not node1:
			_log.debug('invalid node 1')
			return 0
		if not node2:
			_log.debug('invalid node 2')
			return 0
		if not node1.IsOk():
			_log.debug('no data on node 1')
			return 0
		if not node2.IsOk():
			_log.debug('no data on node 2')
			return 0

		data1 = self.GetPyData(node1)
		data2 = self.GetPyData(node2)

		# doc node
		if isinstance(data1, gmDocuments.cDocument):

			date_field = 'clin_when'
			#date_field = 'modified_when'

			if self.__sort_mode == 'age':
				# reverse sort by date
				if data1[date_field] > data2[date_field]:
					return -1
				if data1[date_field] == data2[date_field]:
					return 0
				return 1

			elif self.__sort_mode == 'episode':
				if data1['episode'] < data2['episode']:
					return -1
				if data1['episode'] == data2['episode']:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				return 1

			elif self.__sort_mode == 'issue':
				if data1['health_issue'] < data2['health_issue']:
					return -1
				if data1['health_issue'] == data2['health_issue']:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				return 1

			elif self.__sort_mode == 'review':
				# equality
				if data1.has_unreviewed_parts == data2.has_unreviewed_parts:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				if data1.has_unreviewed_parts:
					return -1
				return 1

			elif self.__sort_mode == 'type':
				if data1['l10n_type'] < data2['l10n_type']:
					return -1
				if data1['l10n_type'] == data2['l10n_type']:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				return 1

			else:
				_log.error('unknown document sort mode [%s], reverse-sorting by age', self.__sort_mode)
				# reverse sort by date
				if data1[date_field] > data2[date_field]:
					return -1
				if data1[date_field] == data2[date_field]:
					return 0
				return 1

		# part node
		if isinstance(data1, gmDocuments.cDocumentPart):
			# compare sequence IDs (= "page" numbers)
			# FIXME: wrong order ?
			if data1['seq_idx'] < data2['seq_idx']:
				return -1
			if data1['seq_idx'] == data2['seq_idx']:
				return 0
			return 1

		# else sort alphabetically
		if None in [data1, data2]:
			l1 = self.GetItemText(node1)
			l2 = self.GetItemText(node2)
			if l1 < l2:
				return -1
			if l1 == l2:
				return 0
		else:
			if data1 < data2:
				return -1
			if data1 == data2:
				return 0
		return 1
	#------------------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------------------
	def _on_doc_mod_db(self, *args, **kwargs):
		# FIXME: remember current expansion state
		wx.CallAfter(self._schedule_data_reget)
	#------------------------------------------------------------------------
	def _on_doc_page_mod_db(self, *args, **kwargs):
		# FIXME: remember current expansion state
		wx.CallAfter(self._schedule_data_reget)
	#------------------------------------------------------------------------
	def _on_pre_patient_selection(self, *args, **kwargs):
		# FIXME: self.__store_expansion_history_in_db

		# empty out tree
		if self.root is not None:
			self.DeleteAllItems()
		self.root = None
	#------------------------------------------------------------------------
	def _on_post_patient_selection(self, *args, **kwargs):
		# FIXME: self.__load_expansion_history_from_db (but not apply it !)
		self._schedule_data_reget()
	#------------------------------------------------------------------------
	def _on_activate(self, event):
		node = event.GetItem()
		node_data = self.GetPyData(node)

		# exclude pseudo root node
		if node_data is None:
			return None

		# expand/collapse documents on activation
		if isinstance(node_data, gmDocuments.cDocument):
			self.Toggle(node)
			return True

		# string nodes are labels such as episodes which may or may not have children
		if type(node_data) == type('string'):
			self.Toggle(node)
			return True

		self.__display_part(part = node_data)
		return True
	#--------------------------------------------------------
	def __on_right_click(self, evt):

		node = evt.GetItem()
		self.__curr_node_data = self.GetPyData(node)

		# exclude pseudo root node
		if self.__curr_node_data is None:
			return None

		# documents
		if isinstance(self.__curr_node_data, gmDocuments.cDocument):
			self.__handle_doc_context()

		# parts
		if isinstance(self.__curr_node_data, gmDocuments.cDocumentPart):
			self.__handle_part_context()

		del self.__curr_node_data
		evt.Skip()
	#--------------------------------------------------------
	def __activate_as_current_photo(self, evt):
		self.__curr_node_data.set_as_active_photograph()
	#--------------------------------------------------------
	def __display_curr_part(self, evt):
		self.__display_part(part = self.__curr_node_data)
	#--------------------------------------------------------
	def __review_curr_part(self, evt):
		self.__review_part(part = self.__curr_node_data)
	#--------------------------------------------------------
	def __manage_document_descriptions(self, evt):
		manage_document_descriptions(parent = self, document = self.__curr_node_data)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __sort_nodes(self, start_node=None):

		if start_node is None:
			start_node = self.GetRootItem()

		# protect against empty tree where not even
		# a root node exists
		if not start_node.IsOk():
			return True

		self.SortChildren(start_node)

		child_node, cookie = self.GetFirstChild(start_node)
		while child_node.IsOk():
			self.__sort_nodes(start_node = child_node)
			child_node, cookie = self.GetNextChild(start_node, cookie)

		return
	#--------------------------------------------------------
	def __handle_doc_context(self):
		self.PopupMenu(self.__doc_context_menu, wx.DefaultPosition)
	#--------------------------------------------------------
	def __handle_part_context(self):
		# make active patient photograph
		if self.__curr_node_data['type'] == 'patient photograph':
			ID = wx.NewId()
			self.__part_context_menu.Append(ID, _('Activate as current photo'))
			wx.EVT_MENU(self.__part_context_menu, ID, self.__activate_as_current_photo)
		else:
			ID = None

		self.PopupMenu(self.__part_context_menu, wx.DefaultPosition)

		if ID is not None:
			self.__part_context_menu.Delete(ID)
	#--------------------------------------------------------
	# part level context menu handlers
	#--------------------------------------------------------
	def __display_part(self, part):
		"""Display document part."""

		# sanity check
		if part['size'] == 0:
			_log.debug('cannot display part [%s] - 0 bytes', part['pk_obj'])
			gmGuiHelpers.gm_show_error (
				aMessage = _('Document part does not seem to exist in database !'),
				aTitle = _('showing document')
			)
			return None

		wx.BeginBusyCursor()

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(
		cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		# shall we force blocking during view ?
		block_during_view = bool( cfg.get2 (
			option = 'horstspace.document_viewer.block_during_view',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = None
		))

		# display it
		successful, msg = part.display_via_mime (
			chunksize = chunksize,
			block = block_during_view
		)

		wx.EndBusyCursor()

		if not successful:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('showing document')
			)
			return None

		# handle review after display
		# 0: never
		# 1: always
		# 2: if no review by myself exists yet
		# 3: if no review at all exists yet
		# 4: if no review by responsible reviewer
		review_after_display = int(cfg.get2 (
			option = 'horstspace.document_viewer.review_after_display',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = 3
		))
		if review_after_display == 1:			# always review
			self.__review_part(part=part)
		elif review_after_display == 2:			# review if no review by me exists
			review_by_me = filter(lambda rev: rev['is_your_review'], part.get_reviews())
			if len(review_by_me) == 0:
				self.__review_part(part = part)
		elif review_after_display == 3:
			if len(part.get_reviews()) == 0:
				self.__review_part(part = part)
		elif review_after_display == 4:
			reviewed_by_responsible = filter(lambda rev: rev['is_review_by_responsible_reviewer'], part.get_reviews())
			if len(reviewed_by_responsible) == 0:
				self.__review_part(part = part)

		return True
	#--------------------------------------------------------
	def __review_part(self, part=None):
		dlg = cReviewDocPartDlg (
			parent = self,
			id = -1,
			part = part
		)
		dlg.ShowModal()
		dlg.Destroy()
	#--------------------------------------------------------
	def __move_part(self, evt):
		target_doc = manage_documents (
			parent = self,
			msg = _('\nSelect the document into which to move the selected part !\n')
		)
		if target_doc is None:
			return
		self.__curr_node_data['pk_doc'] = target_doc['pk_doc']
		self.__curr_node_data.save()
	#--------------------------------------------------------
	def __delete_part(self, evt):
		delete_it = gmGuiHelpers.gm_show_question (
			cancel_button = True,
			title = _('Deleting document part'),
			question = _(
				'Are you sure you want to delete the %s part #%s\n'
				'\n'
				'%s'
				'from the following document\n'
				'\n'
				' %s (%s)\n'
				'%s'
				'\n'
				'Really delete ?\n'
				'\n'
				'(this action cannot be reversed)'
			) % (
				gmTools.size2str(self.__curr_node_data['size']),
				self.__curr_node_data['seq_idx'],
				gmTools.coalesce(self.__curr_node_data['obj_comment'], u'', u' "%s"\n\n'),
				self.__curr_node_data['l10n_type'],
				gmDateTime.pydt_strftime(self.__curr_node_data['date_generated'], format = '%Y-%m-%d', accuracy = gmDateTime.acc_days),
				gmTools.coalesce(self.__curr_node_data['doc_comment'], u'', u' "%s"\n')
			)
		)
		if not delete_it:
			return

		gmDocuments.delete_document_part (
			part_pk = self.__curr_node_data['pk_obj'],
			encounter_pk = gmPerson.gmCurrentPatient().emr.active_encounter['pk_encounter']
		)
	#--------------------------------------------------------
	def __process_part(self, action=None, l10n_action=None):

		gmHooks.run_hook_script(hook = u'before_%s_doc_part' % action)

		wx.BeginBusyCursor()

		# detect wrapper
		found, external_cmd = gmShellAPI.detect_external_binary(u'gm-%s_doc' % action)
		if not found:
			found, external_cmd = gmShellAPI.detect_external_binary(u'gm-%s_doc.bat' % action)
		if not found:
			_log.error('neither of gm-%s_doc or gm-%s_doc.bat found', action, action)
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document part - %(l10n_action)s command not found.\n'
				  '\n'
				  'Either of gm_%(action)s_doc.sh or gm_%(action)s_doc.bat\n'
				  'must be in the execution path. The command will\n'
				  'be passed the filename to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document part: %s') % l10n_action
			)
			return

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		part_file = self.__curr_node_data.export_to_file(aChunkSize = chunksize)

		cmd = u'%s %s' % (external_cmd, part_file)
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)

		wx.EndBusyCursor()

		if not success:
			_log.error('%s command failed: [%s]', action, cmd)
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document part - %(l10n_action)s command failed.\n'
				  '\n'
				  'You may need to check and fix either of\n'
				  ' gm_%(action)s_doc.sh (Unix/Mac) or\n'
				  ' gm_%(action)s_doc.bat (Windows)\n'
				  '\n'
				  'The command is passed the filename to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document part: %s') % l10n_action
			)
	#--------------------------------------------------------
	def __print_part(self, evt):
		self.__process_part(action = u'print', l10n_action = _('print'))
	#--------------------------------------------------------
	def __fax_part(self, evt):
		self.__process_part(action = u'fax', l10n_action = _('fax'))
	#--------------------------------------------------------
	def __mail_part(self, evt):
		self.__process_part(action = u'mail', l10n_action = _('mail'))
	#--------------------------------------------------------
	# document level context menu handlers
	#--------------------------------------------------------
	def __select_encounter(self, evt):
		enc = gmEMRStructWidgets.select_encounters (
			parent = self,
			patient = gmPerson.gmCurrentPatient()
		)
		if not enc:
			return
		self.__curr_node_data['pk_encounter'] = enc['pk_encounter']
		self.__curr_node_data.save()
	#--------------------------------------------------------
	def __edit_encounter_details(self, evt):
		enc = gmEMRStructItems.cEncounter(aPK_obj = self.__curr_node_data['pk_encounter'])
		gmEMRStructWidgets.edit_encounter(parent = self, encounter = enc)
	#--------------------------------------------------------
	def __process_doc(self, action=None, l10n_action=None):

		gmHooks.run_hook_script(hook = u'before_%s_doc' % action)

		wx.BeginBusyCursor()

		# detect wrapper
		found, external_cmd = gmShellAPI.detect_external_binary(u'gm-%s_doc' % action)
		if not found:
			found, external_cmd = gmShellAPI.detect_external_binary(u'gm-%s_doc.bat' % action)
		if not found:
			_log.error('neither of gm-%s_doc or gm-%s_doc.bat found', action, action)
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document - %(l10n_action)s command not found.\n'
				  '\n'
				  'Either of gm_%(action)s_doc.sh or gm_%(action)s_doc.bat\n'
				  'must be in the execution path. The command will\n'
				  'be passed a list of filenames to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document: %s') % l10n_action
			)
			return

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		part_files = self.__curr_node_data.export_parts_to_files(chunksize = chunksize)

		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		cmd = external_cmd + u' ' + u' '.join(part_files)
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)

		wx.EndBusyCursor()

		if not success:
			_log.error('%s command failed: [%s]', action, cmd)
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document - %(l10n_action)s command failed.\n'
				  '\n'
				  'You may need to check and fix either of\n'
				  ' gm_%(action)s_doc.sh (Unix/Mac) or\n'
				  ' gm_%(action)s_doc.bat (Windows)\n'
				  '\n'
				  'The command is passed a list of filenames to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document: %s') % l10n_action
			)
	#--------------------------------------------------------
	# FIXME: icons in the plugin toolbar
	def __print_doc(self, evt):
		self.__process_doc(action = u'print', l10n_action = _('print'))
	#--------------------------------------------------------
	def __fax_doc(self, evt):
		self.__process_doc(action = u'fax', l10n_action = _('fax'))
	#--------------------------------------------------------
	def __mail_doc(self, evt):
		self.__process_doc(action = u'mail', l10n_action = _('mail'))
	#--------------------------------------------------------
	def __add_part(self, evt):
		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose a file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "%s (*)|*|PNGs (*.png)|*.png|PDFs (*.pdf)|*.pdf|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.OPEN | wx.FILE_MUST_EXIST | wx.MULTIPLE
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			self.__curr_node_data.add_parts_from_files(files = dlg.GetPaths(), reviewer = gmStaff.gmCurrentProvider()['pk_staff'])
		dlg.Destroy()
	#--------------------------------------------------------
	def __access_external_original(self, evt):

		gmHooks.run_hook_script(hook = u'before_external_doc_access')

		wx.BeginBusyCursor()

		# detect wrapper
		found, external_cmd = gmShellAPI.detect_external_binary(u'gm_access_external_doc.sh')
		if not found:
			found, external_cmd = gmShellAPI.detect_external_binary(u'gm_access_external_doc.bat')
		if not found:
			_log.error('neither of gm_access_external_doc.sh or .bat found')
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Cannot access external document - access command not found.\n'
				  '\n'
				  'Either of gm_access_external_doc.sh or *.bat must be\n'
				  'in the execution path. The command will be passed the\n'
				  'document type and the reference URL for processing.'
				),
				_('Accessing external document')
			)
			return

		cmd = u'%s "%s" "%s"' % (external_cmd, self.__curr_node_data['type'], self.__curr_node_data['ext_ref'])
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)

		wx.EndBusyCursor()

		if not success:
			_log.error('External access command failed: [%s]', cmd)
			gmGuiHelpers.gm_show_error (
				_('Cannot access external document - access command failed.\n'
				  '\n'
				  'You may need to check and fix either of\n'
				  ' gm_access_external_doc.sh (Unix/Mac) or\n'
				  ' gm_access_external_doc.bat (Windows)\n'
				  '\n'
				  'The command is passed the document type and the\n'
				  'external reference URL on the command line.'
				),
				_('Accessing external document')
			)
	#--------------------------------------------------------
	def __export_doc_to_disk(self, evt):
		"""Export document into directory.

		- one file per object
		- into subdirectory named after patient
		"""
		pat = gmPerson.gmCurrentPatient()
		dname = '%s-%s%s' % (
			self.__curr_node_data['l10n_type'],
			self.__curr_node_data['clin_when'].strftime('%Y-%m-%d'),
			gmTools.coalesce(self.__curr_node_data['ext_ref'], '', '-%s').replace(' ', '_')
		)
		def_dir = os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'docs', pat['dirname'], dname))
		gmTools.mkdir(def_dir)

		dlg = wx.DirDialog (
			parent = self,
			message = _('Save document into directory ...'),
			defaultPath = def_dir,
			style = wx.DD_DEFAULT_STYLE
		)
		result = dlg.ShowModal()
		dirname = dlg.GetPath()
		dlg.Destroy()

		if result != wx.ID_OK:
			return True

		wx.BeginBusyCursor()

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		fnames = self.__curr_node_data.export_parts_to_files(export_dir = dirname, chunksize = chunksize)

		wx.EndBusyCursor()

		gmDispatcher.send(signal='statustext', msg=_('Successfully exported %s parts into the directory [%s].') % (len(fnames), dirname))

		return True
	#--------------------------------------------------------
	def __delete_document(self, evt):
		result = gmGuiHelpers.gm_show_question (
			aMessage = _('Are you sure you want to delete the document ?'),
			aTitle = _('Deleting document')
		)
		if result is True:
			curr_pat = gmPerson.gmCurrentPatient()
			emr = curr_pat.get_emr()
			enc = emr.active_encounter
			gmDocuments.delete_document(document_id = self.__curr_node_data['pk_doc'], encounter_id = enc['pk_encounter'])
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	#----------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
#		test_*()
		pass

#============================================================
