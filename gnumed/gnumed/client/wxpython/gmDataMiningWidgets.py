"""GNUmed data mining related widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmDataMiningWidgets.py,v $
# $Id: gmDataMiningWidgets.py,v 1.14 2009-07-30 12:03:34 ncq Exp $
__version__ = '$Revision: 1.14 $'
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'


# stdlib
import sys, os, fileinput, webbrowser, logging


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmMimeLib, gmTools, gmPG2, gmMatchProvider, gmI18N
from Gnumed.business import gmPerson, gmDataMining, gmPersonSearch
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets
from Gnumed.wxGladeWidgets import wxgPatientListingPnl, wxgDataMiningPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class cPatientListingCtrl(gmListWidgets.cReportListCtrl):

	def __init__(self, *args, **kwargs):
		"""<patient_key> must index or name a column in self.__data"""
		try:
			self.patient_key = kwargs['patient_key']
			del kwargs['patient_key']
		except KeyError:
			self.patient_key = None

		gmListWidgets.cReportListCtrl.__init__(self, *args, **kwargs)

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated, self)
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def _on_list_item_activated(self, evt):
		if self.patient_key is None:
			gmDispatcher.send(signal = 'statustext', msg = _('List not known to be patient-related.'))
			return
		data = self.get_selected_item_data(only_one=True)
		try:
			pat_data = data[self.patient_key]
		except (KeyError, IndexError, TypeError):
			gmGuiHelpers.gm_show_info (
				_(
				'Cannot activate patient.\n\n'
				'The row does not contain a column\n'
				'named or indexed "%s".\n\n'
				) % self.patient_key,
				_('activating patient from list')
			)
			return
		try:
			pat_pk = int(pat_data)
			pat = gmPerson.cIdentity(aPK_obj = pat_pk)
		except (ValueError, TypeError):
			searcher = gmPersonSearch.cPatientSearcher_SQL()
			idents = searcher.get_identities(pat_data)
			if len(idents) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No matching patient found.'))
				return
			if len(idents) == 1:
				pat = idents[0]
			else:
				from Gnumed.wxpython import gmPatSearchWidgets
				dlg = gmPatSearchWidgets.cSelectPersonFromListDlg(parent=wx.GetTopLevelParent(self), id=-1)
				dlg.set_persons(persons=idents)
				result = dlg.ShowModal()
				if result == wx.ID_CANCEL:
					dlg.Destroy()
					return
				pat = dlg.get_selected_person()
				dlg.Destroy()

		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient = pat)
#================================================================
class cPatientListingPnl(wxgPatientListingPnl.wxgPatientListingPnl):

	def __init__(self, *args, **kwargs):

		try:
			button_defs = kwargs['button_defs'][:5]
			del kwargs['button_defs']
		except KeyError:
			button_defs = []

		try:
			msg = kwargs['message']
			del kwargs['message']
		except KeyError:
			msg = None

		wxgPatientListingPnl.wxgPatientListingPnl.__init__(self, *args, **kwargs)

		if msg is not None:
			self._lbl_msg.SetLabel(msg)

		buttons = [self._BTN_1, self._BTN_2, self._BTN_3, self._BTN_4, self._BTN_5]
		for idx in range(len(button_defs)):
			button_def = button_defs[idx]
			if button_def['label'].strip() == u'':
				continue
			buttons[idx].SetLabel(button_def['label'])
			buttons[idx].SetToolTipString(button_def['tooltip'])
			buttons[idx].Enable(True)

		self.Fit()
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def _on_BTN_1_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_2_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_3_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_4_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_5_pressed(self, event):
		event.Skip()
#================================================================
class cDataMiningPnl(wxgDataMiningPnl.wxgDataMiningPnl):

	def __init__(self, *args, **kwargs):
		wxgDataMiningPnl.wxgDataMiningPnl.__init__(self, *args, **kwargs)

		self.__init_ui()

		# make me a file drop target
		dt = gmGuiHelpers.cFileDropTarget(self)
		self.SetDropTarget(dt)
	#--------------------------------------------------------
	def __init_ui(self):
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
				SELECT DISTINCT ON (label)
					cmd,
					label
				FROM cfg.report_query
				WHERE
					label %(fragment_condition)s
						OR
					cmd %(fragment_condition)s
			"""]
		)
		mp.setThresholds(2,3,5)
		self._PRW_report_name.matcher = mp
		self._PRW_report_name.add_callback_on_selection(callback = self._on_report_selected)
		self._PRW_report_name.add_callback_on_lose_focus(callback = self._auto_load_report)
	#--------------------------------------------------------
	def _auto_load_report(self, *args, **kwargs):
		if self._TCTRL_query.GetValue() == u'':
			if self._PRW_report_name.GetData() is not None:
				self._TCTRL_query.SetValue(self._PRW_report_name.GetData())
				self._BTN_run.SetFocus()
	#--------------------------------------------------------
	def _on_report_selected(self, *args, **kwargs):
		self._TCTRL_query.SetValue(self._PRW_report_name.GetData())
		self._BTN_run.SetFocus()
	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def add_filenames(self, filenames):
		# act on first file only
		fname = filenames[0]
		# act on text files only
		mime_type = gmMimeLib.guess_mimetype(fname)
		if not mime_type.startswith('text/'):
			gmDispatcher.send(signal='statustext', msg = _('Cannot read SQL from [%s]. Not a text file.') % fname, beep = True)
			return False
		# act on "small" files only
		stat_val = os.stat(fname)
		if stat_val.st_size > 2000:
			gmDispatcher.send(signal='statustext', msg = _('Cannot read SQL from [%s]. File too big (> 2000 bytes).') % fname, beep = True)
			return False
		# all checks passed
		for line in fileinput.input(fname):
			self._TCTRL_query.AppendText(line)
	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		pass
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_activated(self, evt):
		data = self._LCTRL_result.get_selected_item_data()

		try:
			pk_pat = data['pk_patient']
		except KeyError:
			gmGuiHelpers.gm_show_warning (
				_(
				'Cannot activate patient.\n\n'
				'The report result list does not contain\n'
				'a column named "pk_patient".\n\n'
				'You may want to use the SQL "AS" column alias\n'
				'syntax to make your query return such a column.\n'
				),
				_('Activating patient from report result')
			)
			return

		try:
			pat = gmPerson.cPatient(aPK_obj = pk_pat)
		except StandardError:
			gmGuiHelpers.gm_show_warning (
				_(
				'Cannot activate patient.\n'
				'\n'
				'There does not seem to exist a patient\n'
				'with an internal ID of [%s].\n'
				) % pk_pat,
				_('Activating patient from report result')
			)
			return

		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient = pat)
	#--------------------------------------------------------
	def _on_contribute_button_pressed(self, evt):
		report = self._PRW_report_name.GetValue().strip()
		if report == u'':
			gmDispatcher.send(signal = 'statustext', msg = _('Report must have a name for contribution.'), beep = False)
			return

		query = self._TCTRL_query.GetValue().strip()
		if query == u'':
			gmDispatcher.send(signal = 'statustext', msg = _('Report must have a query for contribution.'), beep = False)
			return

		do_it = gmGuiHelpers.gm_show_question (
			_(	'Be careful that your contribution (the query itself) does\n'
				'not contain any person-identifiable search parameters.\n'
				'\n'
				'Note, however, that no query result data whatsoever\n'
				'is included in the contribution that will be sent.\n'
				'\n'
				'Are you sure you wish to send this query to\n'
				'the gnumed community mailing list?\n'
			),
			_('Contributing custom report')
		)
		if not do_it:
			return

		auth = {'user': gmNetworkTools.default_mail_sender, 'password': u'gnumed-at-gmx-net'}
		msg = u"""--- This is a report definition contributed by a GNUmed user:

----------------------------------------

--- %s

%s

----------------------------------------

--- The GNUmed client.
""" % (report, query)

		if not gmNetworkTools.send_mail (
			sender = u'GNUmed Report Generator <gnumed@gmx.net>',
			receiver = [u'gnumed-devel@gnu.org'],
			subject = u'user contributed report',
			message = msg,
			encoding = gmI18N.get_encoding(),
			server = gmNetworkTools.default_mail_server,
			auth = auth
		):
			gmDispatcher.send(signal = 'statustext', msg = _('Unable to send mail. Cannot contribute report [%s] to GNUmed community.') % report, beep = True)
			return False

		gmDispatcher.send(signal = 'statustext', msg = _('Thank you for your contribution to the GNUmed community!'), beep = False)
		return True
	#--------------------------------------------------------
	def _on_schema_button_pressed(self, evt):
		# new=2: Python 2.5: open new tab
		# will block when called in text mode (that is, from a terminal, too !)
		webbrowser.open(u'http://wiki.gnumed.de/bin/view/Gnumed/DatabaseSchema', new=2, autoraise=1)
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, evt):
		report = self._PRW_report_name.GetValue().strip()
		if report == u'':
			return True
		if gmDataMining.delete_report_definition(name=report):
			self._PRW_report_name.SetText()
			self._TCTRL_query.SetValue(u'')
			gmDispatcher.send(signal='statustext', msg = _('Deleted report definition [%s].') % report, beep=False)
			return True
		gmDispatcher.send(signal='statustext', msg = _('Error deleting report definition [%s].') % report, beep=True)
		return False
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PRW_report_name.SetText()
		self._TCTRL_query.SetValue(u'')
		self._LCTRL_result.set_columns()
		self._LCTRL_result.patient_key = None
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		report = self._PRW_report_name.GetValue().strip()
		if report == u'':
			gmDispatcher.send(signal='statustext', msg = _('Cannot save report definition without name.'), beep=True)
			return False
		query = self._TCTRL_query.GetValue().strip()
		if query == u'':
			gmDispatcher.send(signal='statustext', msg = _('Cannot save report definition without query.'), beep=True)
			return False
		# FIXME: check for exists and ask for permission
		if gmDataMining.save_report_definition(name=report, query=query, overwrite=True):
			gmDispatcher.send(signal='statustext', msg = _('Saved report definition [%s].') % report, beep=False)
			return True
		gmDispatcher.send(signal='statustext', msg = _('Error saving report definition [%s].') % report, beep=True)
		return False
	#--------------------------------------------------------
	def _on_visualize_button_pressed(self, evt):

		try:
			# better fail early
			import Gnuplot
		except ImportError:
			gmGuiHelpers.gm_show_info (
				aMessage = _('Cannot import "Gnuplot" python module.'),
				aTitle = _('Query result visualizer')
			)
			return

		x_col = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _('Choose a column to be used as the X-Axis:'),
			caption = _('Choose column from query results ...'),
			choices = self.query_results[0].keys(),
			columns = [_('column name')],
			single_selection = True
		)
		if x_col is None:
			return

		y_col = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _('Choose a column to be used as the Y-Axis:'),
			caption = _('Choose column from query results ...'),
			choices = self.query_results[0].keys(),
			columns = [_('column name')],
			single_selection = True
		)
		if y_col is None:
			return

		# FIXME: support debugging (debug=1) depending on --debug
		gp = Gnuplot.Gnuplot(persist=1)
		if self._PRW_report_name.GetValue().strip() != u'':
			gp.title(_('GNUmed report: %s') % self._PRW_report_name.GetValue().strip()[:40])
		else:
			gp.title(_('GNUmed report results'))
		gp.xlabel(x_col)
		gp.ylabel(y_col)
		try:
			gp.plot([ [r[x_col], r[y_col]] for r in self.query_results ])
		except StandardError:
			_log.exception('unable to plot results from [%s:%s]' % (x_col, y_col))
			gmDispatcher.send(signal = 'statustext', msg = _('Error plotting data.'), beep = True)

		return
	#--------------------------------------------------------
	def _on_run_button_pressed(self, evt):

		self._BTN_visualize.Enable(False)

		query = self._TCTRL_query.GetValue().strip().strip(';')
		if query == u'':
			return True

		self._LCTRL_result.set_columns()
		self._LCTRL_result.patient_key = None

		# FIXME: make configurable
		query = u'select * from (' + query + u'\n) as real_query limit 1024'
		try:
			# read-only for safety reasons
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': query}], get_col_idx = True)
		except StandardError:
			_log.exception('report query failed')
			self._LCTRL_result.set_columns([_('Error')])
			t, v = sys.exc_info()[:2]
			rows = [
				[_('The query failed.')],
				[u''],
				[unicode(t)]
			]
			for line in str(v).decode(gmI18N.get_encoding()).split('\n'):
				rows.append([line])
			rows.append([u''])
			for line in query.split('\n'):
				rows.append([line])
			self._LCTRL_result.set_string_items(rows)
			self._LCTRL_result.set_column_widths()
			gmDispatcher.send('statustext', msg = _('The query failed.'), beep = True)
			return False

		if len(rows) == 0:
			self._LCTRL_result.set_columns([_('Results')])
			self._LCTRL_result.set_string_items([[_('Report returned no data.')]])
			self._LCTRL_result.set_column_widths()
			gmDispatcher.send('statustext', msg = _('No data returned for this report.'), beep = True)
			return True

		gmDispatcher.send(signal = 'statustext', msg = _('Found %s results.') % len(rows))

		# swap (col_name, col_idx) to (col_idx, col_name) as needed by
		# set_columns() and sort them according to position-in-query
		cols = [ (value, key) for key, value in idx.items() ]
		cols.sort()
		cols = [ pair[1] for pair in cols ]
		self._LCTRL_result.set_columns(cols)
		for row in rows:
			try:
				label = unicode(gmTools.coalesce(row[0], u'')).replace('\n', '<LF>').replace('\r', '<CR>')
			except UnicodeDecodeError:
				label = _('not unicode()able')
			if len(label) > 150:
				label = label[:150] + gmTools.u_ellipsis
			row_num = self._LCTRL_result.InsertStringItem(sys.maxint, label = label)
			for col_idx in range(1, len(row)):
				try:
					label = unicode(gmTools.coalesce(row[col_idx], u'')).replace('\n', '<LF>').replace('\r', '<CR>')[:250]
				except UnicodeDecodeError:
					label = _('not unicode()able')
				if len(label) > 150:
					label = label[:150] + gmTools.u_ellipsis
				self._LCTRL_result.SetStringItem (
					index = row_num,
					col = col_idx,
					label = label
				)
		self._LCTRL_result.set_column_widths()
		self._LCTRL_result.set_data(data = rows)
		try:
			self._LCTRL_result.patient_key = idx['pk_patient']
		except KeyError:
			pass

		self.query_results = rows
		self._BTN_visualize.Enable(True)

		return True
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmI18N, gmDateTime

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#------------------------------------------------------------
	def test_pat_list_ctrl():
		app = wx.PyWidgetTester(size = (400, 500))
		lst = cPatientListingCtrl(app.frame, patient_key = 0)
		lst.set_columns(['name', 'comment'])
		lst.set_string_items([
			['Kirk', 'Kirk by name'],
			['#12', 'Kirk by ID'],
			['unknown', 'unknown patient']
		])
#		app.SetWidget(cPatientListingCtrl, patient_key = 0)
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------

	test_pat_list_ctrl()

#================================================================
