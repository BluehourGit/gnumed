"""gmResizingWidgets - Resizing widgets for use in GnuMed.

Design by Richard Terry and Ian Haywood.
"""
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmResizingWidgets.py,v $
# $Id: gmResizingWidgets.py,v 1.19 2005-03-03 21:14:24 ncq Exp $
__version__ = "$Revision: 1.19 $"
__author__ = "Ian Haywood, Karsten Hilbert, Richard Terry"
__license__ = 'GPL  (details at http://www.gnu.org)'

import sys

from wxPython import wx
from wxPython import stc

from Gnumed.pycommon import gmI18N, gmLog
from Gnumed.wxpython import gmGuiHelpers, gmTimer

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

STYLE_ERROR=1
STYLE_TEXT=2
STYLE_EMBED=4

#====================================================================
class cPickList(wx.wxListBox):
	def __init__ (self, parent, pos, size, callback):
		wx.wxListBox.__init__(self, parent, -1, pos, size, style=wx.wxLB_SINGLE | wx.wxLB_NEEDED_SB)
		self.callback = callback
		self.alive = 1 # 0=dead, 1=alive, 2=must die
		wx.EVT_LISTBOX (self, self.GetId(), self.OnList)
	#------------------------------------------------
	def SetItems (self, items):
		"""
		Sets the items, Items is a dict with label, data, weight items
		"""
		items.sort (lambda a,b: cmp(b['weight'], a['weight']))
		self.Clear()
		self.Set([item['label'] for item in items])
		n = 0
		for item in items:
			self.SetClientData(n, item['data'])
			# n += 1  ??
		self.SetSelection(0)
	#------------------------------------------------
	def Up(self):
		line = self.GetSelection()
		if line > 0:
			self.SetSelection(line-1)
	#------------------------------------------------
	def Down(self):
		line = self.GetSelection()
		if line < self.GetCount()-1:
			self.SetSelection(line+1)
	#------------------------------------------------
	def Enter (self):
		line = self.GetSelection()
		if line >= 0:
			text = self.GetString(line)
			data = self.GetClientData(line)
			self.callback(text, data)
		self.alive = 2
		self.Destroy() # this is only safe when in the event handler of another widget
	#------------------------------------------------
	def OnList(self, event):
		event.Skip()
		if self.alive != 2:
			line = self.GetSelection()
			if line >= 0:
				text = self.GetString(line)
				data = self.GetClientData(line)
				self.callback (text, data)
			self.alive = 2
		else:
			wx.wxCallAfter (self.Destroy) # in theory we shouldn't have to do this,
									   # but when we don't, wx segfaults.
	#------------------------------------------------
	def Destroy (self):
		self.alive = 0
		wx.wxListBox.Destroy (self)
#====================================================================
# according to Ian there isn't really a particular reason
# why we do not use wxMiniFrame instead of wxFrame or even a wxWindow
class cPopupFrame(wx.wxFrame):
#	def __init__ (self, embed_header, widget_class, originator=None, pos=wxDefaultPosition):
#		wxFrame.__init__(self, None, wxNewId(), widget_class.__name__, pos=pos, style=wxSIMPLE_BORDER)
#		self.win = widget_class(self, -1, pos = pos, size = wxSize(300, 150), complete = self.OnOK)
	def __init__ (self, embed_header, widget, originator=None, pos=wx.wxDefaultPosition):
		wx.wxFrame.__init__(self, None, wx.wxNewId(), widget.__class__.__name__, pos=pos, style=wx.wxSIMPLE_BORDER)
		widget.set_completion_callback(self.OnOK)
		self.win = widget
		self.embed_header = embed_header
		self.originator = originator

		self.__do_layout()

		EVT_BUTTON(self.__BTN_OK, self.__BTN_OK.GetId(), self.OnOK)
		EVT_BUTTON(self.__BTN_Cancel, self.__BTN_Cancel.GetId(), self._on_close)
		self.win.SetFocus ()
	#------------------------------------------------
	def __do_layout(self):
		self.__BTN_OK = wx.wxButton (self, -1, _("OK"), style=wx.wxBU_EXACTFIT)
		self.__BTN_Cancel = wx.wxButton (self, -1, _("Cancel"), style=wx.wxBU_EXACTFIT)
		szr_btns = wx.wxBoxSizer (wx.wxHORIZONTAL)
		szr_btns.Add(self.__BTN_OK, 0, 0)
		szr_btns.Add(self.__BTN_Cancel, 0, 0)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.win, 1, wx.wxEXPAND, 0)
		szr_main.Add(szr_btns, 0, wx.wxEXPAND)

		self.SetAutoLayout(1)
		self.SetSizer(szr_main)
		szr_main.Fit(self)
		szr_main.SetSizeHints(self)
		self.Layout()
	#------------------------------------------------
	def _on_close (self, event):
		self.Close()
	#------------------------------------------------
	def OnOK (self, event=None):
		if self.originator:
			self.originator.Embed ("%s: %s" % (self.embed_header, self.win.GetSummary()))
		self.Close ()
#====================================================================
class cPopupFrameNew(wx.wxFrame):
	"""This serves as a generic container around whatever is popped up.

	It has no functionality in itself. Given that should it
	be either a wxMiniFrame or a wxWindow ?
	"""
	def __init__ (self, widget=None, pos=wx.wxPyDefaultPosition):
		self.__ID = wx.wxNewId()
		wx.wxFrame.__init__(
			self,
			parent = None,
			id = self.__ID,
			title = widget.__class__.__name__,
			pos = pos,
			style = wx.wxSIMPLE_BORDER
		)
#		widget.set_completion_callback(self.OnOK)
#		self.embed_header = embed_header
#		self.originator = originator

		self.__widget = widget

		self.__do_layout()
#		self.__register_events()
		self.__widget.SetFocus()
	#------------------------------------------------
#	def __register_events(self):
#		EVT_BUTTON(self.__BTN_OK, self.__BTN_OK.GetId(), self.OnOK)
#		EVT_BUTTON(self.__BTN_Cancel, self.__BTN_Cancel.GetId(), self._on_cancel)
	#------------------------------------------------
	def __do_layout(self):
#		self.__BTN_OK = wx.wxButton (self, -1, _("OK"), style=wx.wxBU_EXACTFIT)
#		self.__BTN_Cancel = wx.wxButton (self, -1, _("Cancel"), style=wx.wxBU_EXACTFIT)
#		szr_btns = wx.wxBoxSizer(wx.wxHORIZONTAL)
#		szr_btns.Add(self.__BTN_OK, 0, 0)
#		szr_btns.Add(self.__BTN_Cancel, 0, 0)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.__widget, 1, wx.wxEXPAND, 0)
		szr_main.Add(szr_btns, 0, wx.wxEXPAND)

		self.SetAutoLayout(1)
		self.SetSizer(szr_main)
		szr_main.Fit(self)
		szr_main.SetSizeHints(self)
		self.Layout()
	#------------------------------------------------
#	def _on_cancel(self, event):
#		self.Close()
	#------------------------------------------------
#	def OnOK(self, event=None):
		# FIXME: deal with self.__widget here
#		if self.originator:
#			self.originator.Embed ("%s: %s" % (self.embed_header, self.__widget.GetSummary()))
#		self.Close()
#====================================================================
class cSTCval:
	def __init__(self):
		self.value = None
		self.data = None
#====================================================================
class cResizingWindow(wx.wxScrolledWindow):
	"""A vertically-scrolled window which allows subwindows
	   to change their size, and adjusts accordingly.
	"""
#	def __init__ (self, parent, id, pos = wx.wxDefaultPosition, size = wx.wxDefaultSize, complete = None):
	def __init__ (self, parent, id, pos = wx.wxPyDefaultPosition, size = wx.wxPyDefaultSize):

		wx.wxScrolledWindow.__init__(self, parent, id, pos = pos, size = size, style=wx.wxVSCROLL)
		self.SetScrollRate(0, 20) # suppresses X scrolling by setting X rate to zero

		self.__input_lines = [[]]
#		self.__list = None

#		self.complete = complete	# ??

		self.__szr_main = None
		self.DoLayout()
		self.__szr_main = wx.wxFlexGridSizer(len(self.__input_lines), 2)
		for line in self.__input_lines:
			if len(line) != 0:
				# first label goes into column 1
				if line[0]['label'] is not None:
					self.__szr_main.Add(line[0]['label'], 1)
				else:
					self.__szr_main.Add((1, 1))
				# the rest gets crammed into column 2
				h_szr = wx.wxBoxSizer (wx.wxHORIZONTAL)
				h_szr.Add(line[0]['instance'], 1, wx.wxGROW)
				for widget in line[1:]:
					if widget['label'] is not None:
						h_szr.Add(widget['label'], 0)
					h_szr.Add(widget['instance'], 1, wx.wxGROW)
				self.__szr_main.Add(h_szr, 1, wx.wxGROW)
		self.__szr_main.AddGrowableCol(1)
		self.__szr_main.Add((1, 1))

		self.SetSizer(self.__szr_main)
		self.FitInside()
	#------------------------------------------------
	def AddWidget(self, widget, label=None):
		"""
		Adds a widget, optionally with label
		
		@type label: string
		@param label: text of the label
		@type widgets: wx.wxWindow descendant
		"""
		if label is None:
			textbox = None
		else:
			textbox = wx.wxStaticText(self, -1, label, style=wx.wxALIGN_RIGHT)
		# append to last line
		self.__input_lines[-1].append({'ID': label, 'label': textbox, 'instance': widget})
	#------------------------------------------------
	def Newline (self):
		"""
		Starts a newline on the widget
		"""
		self.__input_lines.append([])
	#------------------------------------------------
	def DoLayout (self):
		"""
		Overridden by descendants, this function uses AddWidget and Newline to form
		the outline of the widget
		"""
		_log.Log(gmLog.lPanic, '[%s] forgot to override DoLayout()' % self.__class__.__name__)
	#------------------------------------------------
	def ReSize (self, widget, new_height):
		"""Called when a child widget has a new height, redoes the layout.
		"""
		if self.__szr_main:
			self.__szr_main.SetItemMinSize (widget, -1, new_height)
			self.__szr_main.FitInside (self)
	#------------------------------------------------
	def EnsureVisible (self, widget, cur_x = 0, cur_y = 0):
		"""
		Ensures widget is visible
		
		@param widget: a child widget
		@type cur_x: integer
		@param cur_x: the X co-ordinate of the cursor inside widget, if applicable
		@type cur_y: integer
		@param cur_y: the Y co-ordinate of the cursor inside widget
		"""
		# get widget position
		x, y = widget.GetPositionTuple()
		# adjust for cursor offset
		x += cur_x
		y += cur_y
		# convert to virtual coordinates
		x, y = self.CalcUnscrolledPosition(x, y)
		x_dimension, y_dimension = self.GetScrollPixelsPerUnit()
		y = y / y_dimension
		# currently, don't bother with X direction
		self.Scroll (-1, y)
	#------------------------------------------------
	def SetValue(self, values):
		"""
		Runs SetValue() on all the fields

		@type values: dictionary
		@param values: keys are the labels, values are passed to SetValue()
		"""
		# FIXME: adapt to cSTCval
		for line in self.__input_lines:
			for widget in line:
				if values.has_key(widget['ID']):
					if isinstance(widget['instance'], stc.wxStyledTextCtrl):
						widget['instance'].SetText(values[widget['ID']])
					elif isinstance(widget['instance'], (wx.wxChoice, wx.wxRadioBox)):
						widget['instance'].SetSelection(values[widget['ID']])
					else:
						widget['instance'].SetValue(values[widget['ID']])
	#------------------------------------------------
	def GetValue(self):
		"""
		Returns a dictionary of the results of GetValue()
		called on all widgets, keyed by label
		Unlabelled widgets don't get called
		"""
		# FIXME: this does not detect ID collisions between lines
		vals = {}
		for line in self.__input_lines:
			for widget in line:
				if widget['ID'] is None:
					continue
				result = cSTCval()
				if isinstance(widget['instance'], cResizingSTC):
					result.value = widget['instance'].GetText()
					result.data = widget['instance'].GetData()
				elif isinstance(widget['instance'], stc.wxStyledTextCtrl):
					result.value = widget['instance'].GetText()
				elif isinstance(widget['instance'], (wx.wxChoice, wx.wxRadioBox)):
					result.selection = widget['instance'].GetSelection()
				else:
					result.value = widget['instance'].GetValue()
				vals[widget['ID']] = result
		return vals
	#------------------------------------------------
	def Clear (self):
		"""
		Clears all widgets where this makes sense
		"""
		for line in self.__input_lines:
			for widget in line:
				if isinstance (widget['instance'], stc.wxStyledTextCtrl):
					widget['instance'].ClearAll()
				elif isinstance (widget['instance'], wx.wxTextCtrl):
					widget['instance'].Clear()
				elif isinstance (widget['instance'], (wx.wxToggleButton, wx.wxCheckBox, wx.wxRadioButton, wx.wxGauge)):
					widget['instance'].SetValue(0)
				elif isinstance (widget['instance'], (wx.wxChoice, wx.wxComboBox, wx.wxRadioBox)):
					widget['instance'].SetSelection(0)
				elif isinstance (widget['instance'], wx.wxSpinCtrl):
					widget['instance'].SetValue(widget['instance'].GetMin())
	#------------------------------------------------
	def SetFocus (self):
		# try to focus on the first line if we can.
		try:
			self.lines[0][0]['instance'].SetFocus()
		except IndexError:
			pass
		except AttributeError:
			pass
	#------------------------------------------------
	def GetPickList (self, callback, x_intended, y_intended):
		"""
		Returns a pick list, destroying a pre-existing pick list for this widget

		the alive member is true until the object is Destroy ()'ed

		@param callback: called when a item is selected,
		@type callback: callable
		@param x_intended: the X-position where the list should appear
		@type x_intended: int
		@param x: the Y-position where the list should appear
		@type y_intended: int

		@return: PickList
		"""
#		# retire previous pick list
#		if self.__list and self.__list.alive:
#			self.__list.Destroy()
		our_width, our_height = self.GetSizeTuple()
		char_height = self.GetCharHeight()
		# make list 9 lines of height char_height high
		list_height = char_height * 9
		# and find best placement
		# - height
		if (list_height + char_height) > our_height:
			list_height = our_height
			y_final = 0
		elif (y_intended + list_height + char_height) > our_height:
			y_final = our_height - list_height
		else:
			y_final = y_intended + char_height
		# - width
		list_width = int(list_height / 1.4)
		if list_width > our_width:
			list_width = our_width
			x_final = 0
		elif (x_intended + list_width) > our_width:
			x_final = our_width - list_width
		else:
			x_final = x_intended
#		self.__list = cPickList(self, wx.wxPoint(x_final, y_final), wx.wxSize(list_width, list_height), callback=callback)
#		return self.__list
		list = cPickList(self, wx.wxPoint(x_final, y_final), wx.wxSize(list_width, list_height), callback=callback)
		return list
	#------------------------------------------------
#	def set_completion_callback(self, callback):
#		self.complete = callback
	#------------------------------------------------
	def GetSummary (self):
		"""Gets a terse summary string for the data in the widget"""
		return ""
#====================================================================
class cResizingSTC(stc.wxStyledTextCtrl):
	"""
	A StyledTextCrl that monitors the size of its internal text and
	resizes the parent accordingly.
	
	MUST ONLY be used inside ResizingWindow !

	FIXME: override standard STC popup menu
	"""
	def __init__ (self, parent, id, pos=wx.wxDefaultPosition, size=wx.wxDefaultSize, style=0, data=None):
		if not isinstance(parent, cResizingWindow):
			 raise ValueError, 'parent of %s MUST be a ResizingWindow' % self.__class__.__name__
		stc.wxStyledTextCtrl.__init__ (self, parent, id, pos, size, style)
		self.SetWrapMode (stc.wxSTC_WRAP_WORD)
		# FIXME: configure
		self.StyleSetSpec (STYLE_ERROR, "fore:#7F11010,bold")
		self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
		self.StyleSetChangeable (STYLE_EMBED, 0)
#		self.StyleSetHotSpot (STYLE_EMBED, 1)
		self.SetEOLMode (stc.wxSTC_EOL_LF)
		self.SetModEventMask (stc.wxSTC_MOD_INSERTTEXT | stc.wxSTC_MOD_DELETETEXT | stc.wxSTC_PERFORMED_USER)

		stc.EVT_STC_MODIFIED (self, self.GetId(), self.__on_STC_modified)
		wx.EVT_KEY_DOWN (self, self.__on_key_down)
		wx.EVT_KEY_UP (self, self.__OnKeyUp)

		self.next_in_tab_order = None
		self.prev_in_tab_order = None

		self.__parent = parent

		self.__popup_keywords = {}
		self.__popup = None
		self.__popup_visible = False
		# FIXME: delay configurable
		self.__timer = gmTimer.cTimer (
			callback = self._on_timer_fired,
			delay = 300
		)
		self.__matcher = None

		self.__show_list = 1
		self.__embed = {}
		self.list = None
		self.no_list = 0			# ??

		self.__data = data			# this is just a placeholder for data to be attached to this STC, will be returned from get_data()
	#------------------------------------------------
	# public API
	#------------------------------------------------
	def set_keywords(self, popup_keywords=None):
		if popup_keywords is None:
			return
		self.__popup_keywords = popup_keywords
	#------------------------------------------------
	def SetText(self, text):
		self.__show_list = 0
		stc.wxStyledTextCtrl.SetText(self, text)
		self.__show_list = 1
	#------------------------------------------------
	def ReplaceText (self, start, end, text, style=-1, space=0):
		"""
		Oddly, the otherwise very rich wxSTC API does not provide an
		easy way to replace text, so we provide it here.

		@param start: the position in the text to start from
		@param length: the length of the string to replace
		@param text: the new string
		@param style: the style for the replaced string
		"""
		self.SetTargetStart(start)
		self.SetTargetEnd(end)
		self.ReplaceTarget(text)
		if style > -1:
			self.StartStyling(start, 0xFF)
			self.SetStyling(len(text), style)
	#------------------------------------------------
	def Embed (self, text, data=None):
		self.no_list = 1
		self.ReplaceText (self.fragment_start, self.fragment_end, text+';', STYLE_EMBED, 1)
		self.GotoPos (self.fragment_start+len (text)+1)
		self.SetFocus()
		if data:
			self.__embed[text] = data
		self.no_list = 0
	#------------------------------------------------
	def DelPhrase (self, pos):
		# FIXME: optimize
		end = pos+1
		while (end < self.GetLength()) and (self.GetCharAt(end) != ord(';')):
			end += 1
		start = pos
		while (start > 0) and (self.GetCharAt(start and start-1) != ord(';')):
			start -= 1
		self.SetTargetStart(start)
		self.SetTargetEnd(end)
		self.ReplaceTarget('')
	#------------------------------------------------
	def SetFocus(self, x=None, line=None):
		"""Set focus to current position in STC.

		- make sure that's visible, too
		"""
		stc.wxStyledTextCtrl.SetFocus(self)
		# goto first line ?
		if line == 1:
			if x is None:
				x = 0
			self.GotoPos(self.PositionFromPoint(wx.wxPoint(x,0)))
			return
		# goto last line ?
		if line == -1:
			_log.Log(gmLog.lData, 'going to last line in STC')
			last_char_pos = self.GetLength()
			if x is None:
				self.GotoPos(last_char_pos)
				_log.Log(gmLog.lData, 'no X given, use X=%s' % last_char_pos.x)
				return
			y = self.PointFromPosition(last_char_pos).y
			_log.Log(gmLog.lData, 'going to given X=%s' % x)
			self.GotoPos(self.PositionFromPoint(wx.wxPoint(x,y)))
			return
		# goto last current position
		cur = self.PointFromPosition(self.GetCurrentPos())
		self.__parent.EnsureVisible (self, cur.x, cur.y)
	#------------------------------------------------
	def AttachMatcher (self, matcher):
		"""
		Attaches a gmMatchProvider to the STC,this will be used to drive auto-completion
		"""
		self.__matcher = matcher
	#------------------------------------------------
	def SetData(self, data):
		"""
		Configures the data associated with this STC
		@param data The associated data
		@type data Any object
		"""
		self.__data = data
	#------------------------------------------------
	def GetData(self):
		"""
		Retrieves the data associated with this STC
		"""
		return self.__data
	#------------------------------------------------
	# event handlers
	#------------------------------------------------
	def __on_STC_modified(self, event):
		# did the user do anything of note to us ?
		if not (event.GetModificationType() & (stc.wxSTC_MOD_INSERTTEXT | stc.wxSTC_MOD_DELETETEXT)):
			event.Skip()
			return
		last_char_pos = self.GetLength()
		# do we need to restart timer ?
		if last_char_pos == 0:
			self.__timer.Stop()
		else:
			self.__timer.Start(oneShot = True)
		# do we need to resize ?
		true_txt_height = (self.PointFromPosition(last_char_pos).y - self.PointFromPosition(0).y) + self.TextHeight(0)
		x, visible_height = self.GetSizeTuple()
		if visible_height != true_txt_height:
			self.__parent.ReSize(self, true_txt_height)
		# is currently relevant term a keyword for popping up an edit area or something ?
		fragment = self.__get_focussed_fragment()
		if fragment in self.__popup_keywords.keys():
			self.__timer.Stop()
			self.__handle_keyword(fragment)
#			# keep this so the parent class handler inserts the character for us
#			event.Skip()
			return
		return
	#------------------------------------------------
	def __on_key_down(self, event):
		"""Act on some key presses we want to process ourselves."""

		if self.__popup is not None:
			print "proxying keypress to popup"
			try:
				self.__popup.on_key_down(event)
				if not event.GetSkipped():
					return
			except AttributeError:
				pass

#		if (self.list is not None) and not self.list.alive:
#			self.list = None # someone else has destroyed our list!

		curs_pos = self.GetCurrentPos()

		# <DOWN>
		# - if in list: scroll list
		# - if in last line: goto first line, same character, in next_in_tab_order
		# - else standard behaviour
		if event.KeyCode() == wx.WXK_DOWN:
#			if (self.list is not None) and self.list.alive:
#				self.list.Down()
#				return
#			print "arrow down @ %s (line %s of %s)" % (curs_pos, self.LineFromPosition(curs_pos), self.GetLineCount())
			if self.LineFromPosition(curs_pos)+1 == self.GetLineCount():
				if self.next_in_tab_order is not None:
					curs_coords = self.PointFromPosition(curs_pos)
					self.next_in_tab_order.SetFocus(x=curs_coords.x, line=1)
					return

		# <UP>
		# - if in list: scroll list
		# - if in first line: goto last line, same character, in prev_in_tab_order
		# - else standard behaviour
		if event.KeyCode() == wx.WXK_UP:
			_log.Log(gmLog.lData, '<UP-ARROW> key press detected')
#			if (self.list is not None) and self.list.alive:
#				self.list.Up()
#				return
			_log.Log(gmLog.lData, 'pos %s = line %s' % (curs_pos, self.LineFromPosition(curs_pos)))
			if self.LineFromPosition(curs_pos) == 0:
				_log.Log(gmLog.lData, 'first line of STC - special handling')
				if self.prev_in_tab_order is not None:
					_log.Log(gmLog.lData, 'prev_in_tab_order = %s' % str(self.prev_in_tab_order))
					curs_coords = self.PointFromPosition(curs_pos)
					_log.Log(gmLog.lData, 'cursor coordinates in current STC: %s:%s' % (curs_coords.x, curs_coords.y))
					self.prev_in_tab_order.SetFocus(x=curs_coords.x, line=-1)
					return
			else:
				_log.Log(gmLog.lData, 'not first line of STC - standard handling')

		# <TAB> key
		# - move to next/prev_in_tab_order
		# FIXME: what about inside a list ?
		if event.KeyCode() == wx.WXK_TAB:
			if event.m_shiftDown:
				if self.prev_in_tab_order is not None:
					self.prev_in_tab_order.SetFocus()
			else:
				if self.next_in_tab_order is not None:
					self.next_in_tab_order.SetFocus()
			return
				# FIXME: why ?
#				elif self.__parent.complete:
#					self.__parent.complete()

		# <;>
		# - do not put into empty field
		# - do not allow consecutive ';'s
		if event.KeyCode() == ord(';'):
			if self.GetLength() == 0:
				return
			# FIXME: smartup for whitespace after trailing ';'
			if self.GetCharAt(curs_pos-1) == ord(';'):
				return

		# <DEL>
		# - if inside embedded string
		#	- delete entire string and data dict
		# - else standard behaviour
		if event.KeyCode() == wx.WXK_DELETE:
			# FIXME: perhaps add check for regex, too ?
			if self.GetStyleAt(curs_pos) == STYLE_EMBED:
				self.DelPhrase(curs_pos)
				# FIXME: also delete corresponding "additional data" dict ...
				return

		# <BACKSPACE>
		# - if inside embedded string
		#	- delete entire string and data dict
		# - else standard behaviour
		if event.KeyCode() == wx.WXK_BACK:
			# FIXME: perhaps add check for regex, too ?
			if self.GetStyleAt(curs_pos-1) == STYLE_EMBED:
				self.DelPhrase (curs_pos-1)
				# FIXME: also delete corresponding "additional data" dict ...
				return

		# <ENTER>
		# - if in list: proxy to list
		# - in empty widget: go to next in tab order
		# - after last character in widget:
		#	- if after ';': go to next in tab order
		#	- f no ';' there: add one
		if event.KeyCode() == wx.WXK_RETURN and not event.m_shiftDown:
#			if (self.list is not None) and self.list.alive:
#				self.list.Enter()
#				return
			if self.GetLength() == 0:
				if self.next_in_tab_order is not None:
					self.next_in_tab_order.SetFocus()
				return
			if curs_pos == self.GetLength():
				# FIXME: make this smarter to deal with whitespace after ';'
				if self.GetCharAt(curs_pos-1) == ord(';'):
					if self.next_in_tab_order:
						self.next_in_tab_order.SetFocus()
					# FIXME: why ?
#					elif self.__parent.complete:
#						self.__parent.complete()
				else:
					self.AddText (';')
				return

		# FIXME: why ?
#		if event.KeyCode() == wx.WXK_F12 and self.__parent.complete:
#			self.__parent.complete()

		event.Skip()	# skip to next event handler to keep processing
	#------------------------------------------------
	def __OnKeyUp (self, event):
		if not self.list:
			curs_pos = self.PointFromPosition(self.GetCurrentPos())
			self.__parent.EnsureVisible (self, curs_pos.x, curs_pos.y)
	#------------------------------------------------
	def _cb_on_popup_completion(self, was_cancelled=False):
		"""Callback for popup completion.

		- this is called when the user has signalled
		  being done interacting with the popup
		- if was_cancelled is True the popup content should
		  be ignored and no further action taken on it
		"""
		print "popup interaction completed"
		self.__popup_visible = False
		if self.__popup is None:
			_log.Log(gmLog.lErr, 'got called from non-existing popup')
			return
		if was_cancelled:
			print "popup cancelled, ignoring data"
			self.__popup.Destroy()
			self.__popup = None
			return
		print "getting data from popup and acting on it"
		print self.__popup.GetData()
		# FIXME: wxCallAfter(embed) and store
		# maybe be a little smarter here
		self.__popup.Destroy()
		self.__popup = None
	#------------------------------------------------
	def _on_timer_fired(self, cookie):
		print 'timer <%s> fired' % cookie
		fragment = self.__get_focussed_fragment()
		print 'should popup context pick list on <%s> now' % fragment

		return 1

		# - get matches and popup select list
		if self.no_list:
			return
		if self.__matcher is None:
			return
		if not self.__show_list:
			return

		# do indeed show list
		if len(fragment) == 0:
			if (self.list is not None) and self.list.alive:
				self.list.Destroy()
			return
		matches_found, matches = self.__matcher.getMatches(fragment)
		if not matches_found:
			if (self.list is not None) and self.list.alive:
				self.list.Destroy()
			return
		if not ((self.list is not None) and self.list.alive):
			x, y = self.GetPositionTuple()
			p = self.PointFromPosition(curs_pos)
			self.list = self.__parent.GetPickList(self.__userlist, x+p.x, y+p.y)
		self.list.SetItems(matches)
	#------------------------------------------------
	# internal API
	#------------------------------------------------
	def __get_focussed_fragment(self):
		curs_pos = self.GetCurrentPos()
		text = self.GetText()
		self.fragment_start = text.rfind(';', 0, curs_pos)				# FIXME: ';' hardcoded as separator
		if self.fragment_start == -1:
			self.fragment_start = 0
		else:
			self.fragment_start += 1
		last_char_pos = self.GetLength()
		self.fragment_end = text.find(';', curs_pos, last_char_pos)		# FIXME: ';' hardcoded as separator
		if self.fragment_end == -1:
			self.fragment_end = last_char_pos
		return text[self.fragment_start:self.fragment_end].strip()
	#------------------------------------------------
	def __get_best_popup_geom(self):
		print "calculating optimal popup geometry"
		parent_width, parent_height = self.__parent.GetSizeTuple()
		print "parent size is %sx%s pixel" % (parent_width, parent_height)
		# FIXME: this should be gotten from ourselves, not the parent, but how ?
		parent_char_height = self.__parent.GetCharHeight()
		print "char height in parent is", parent_char_height, "pixel"
		# make popup 9 lines of height parent_char_height high
		# FIXME: better detect this, but how ?
		popup_height = parent_char_height * 9
		print "hence intended popup height is", popup_height, "pixel"
		# get STC displacement inside parent
		stc_origin_x, stc_origin_y = self.GetPositionTuple()
		print "inside parent STC is @ %s:%s" % (stc_origin_x, stc_origin_y)
		# get current cursor position inside STC in pixels
		curs_pos = self.PointFromPosition(self.GetCurrentPos())
		print "inside STC cursor is @ %s:%s" % (curs_pos.x, curs_pos.y)
		# find best placement
		# - height
		if (popup_height + parent_char_height) > parent_height:
			# don't let popup get bigger than parent window
			popup_height = parent_height
			popup_y_pos = 0
		elif ((popup_height + parent_char_height) + (curs_pos.y + stc_origin_y)) > parent_height:
			# if would fit inside but forced (partially) outside
			# by cursor position then move inside
			popup_y_pos = parent_height - popup_height
		else:
			popup_y_pos = (curs_pos.y + stc_origin_y) + parent_char_height
		# - width
		popup_width = int(popup_height / 1.4)		# Golden Cut
		if popup_width > parent_width:
			# don't let popup get bigger than parent window
			popup_width = parent_width
			popup_x_pos = 0
		elif (popup_width + (curs_pos.x + stc_origin_x)) > parent_width:
			# if would fit inside but forced (partially) outside
			# by cursor position then move inside
			popup_x_pos = parent_width - popup_width
		else:
			popup_x_pos = curs_pos.x + stc_origin_x
		print "optimal geometry = %sx%s @ %s:%s" % (popup_width, popup_height, popup_x_pos, popup_y_pos)
		return (wx.wxPoint(popup_x_pos, popup_y_pos), wx.wxSize(popup_width, popup_height))
	#------------------------------------------------
	def __handle_keyword(self, kwd=None):
		print "detected popup keyword:", kwd

		try:
			create_widget = self.__popup_keywords[kwd]['widget_factory']
		except KeyError:
			gmGuiHelpers.gm_beep_statustext (
				aMessage = _('No action configured for keyword [%s].') % kwd,
				aLogLevel = gmLog.lWarn
			)
			return False

		best_pos, best_size = self.__get_best_popup_geom()
		try:
			self.__popup = create_widget (
				parent = self.__parent,
				pos = best_pos,
				size = best_size,
				style = wx.wxSIMPLE_BORDER,
				completion_callback = self._cb_on_popup_completion
			)
		except StandardError:
			_log.LogException('cannot call [%s] on keyword [%s] to create widget' % (create_widget, kwd), sys.exc_info(), verbose=1)
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot invoke action [%s] for keyword [%s].') % (create_widget, kwd),
				aTitle = _('showing keyword popup')
			)
			return False

		print "popup is:", type(self.__popup), str(self.__popup)

		# FIXME: issubclass() ?
#		if not isinstance(self.__popup, wx.wxWindow):
		if not isinstance(self.__popup, wx.wxPanel):
			gmGuiHelpers.gm_beep_statustext (
				aMessage = _('Action [%s] on keyword [%s] is invalid.') % (create_widget, kwd)
			)
			_log.Log(gmLog.lErr, 'keyword [%s] triggered action [%s]' % (kwd, create_widget))
			_log.Log(gmLog.lErr, 'the result (%s) is not a wxWindow subclass instance, however' % str(self.__popup))
			return False

		# make new popup window to put widget inside
#		self.__popup_win = wx.wxWindow (
#			parent = self.__parent,
#			id = -1,
#			pos = self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos())),
#			size = ,
#			style = wx.wxSIMPLE_BORDER,
#			name = self.__class__.__name__
#		)

		# display widget
		# FIXME: the embed_header business needs to go away, eg. be dealt
		# FIXME: with later by calling widget_to_show.get_embed_string()
		# FIXME: same with originator

		self.__popup_visible = True
		self.__popup.Show()
		print "after popup.Show()"
	#------------------------------------------------
	def __userlist (self, text, data=None):
		# this is a callback
#		--- old --------------
#		# FIXME: need explanation on instance/callable business, it seems complicated
#		if issubclass(data, cResizingWindow):
#			win = data (
#				self,
#				-1,
#				pos = self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos())),
#				size = wxSize(300, 150)
#			)
#			cPopupFrame (
#				embed_header = text,
#				widget = win,
#				originator = self,
#				pos = self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos()))
#			).Show()
#		elif callable(data):
#			data (text, self.__parent, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ())))
#		--- old --------------
		if self.MakePopup (text, data, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ()))):
			pass
		else:
			self.Embed (text, data)
	#--------------------------------------------------
	def MakePopup (self, text, data, parent, cursor_position):
		"""
		An overrideable method, called whenever a match is made in this STC
		Designed for producing popups, but the overrider can in fact, do
		whatever they please.

		@return True if a poup-up or similar actually happened (which suppresses inserting the match string in the text
		@rtype boolean
		"""
		#cPopupFrame(text, win, self, cursor_position)).Show()
		return False
#====================================================================
#====================================================================
if __name__ == '__main__':

	_log.SetAllLogLevels(gmLog.lData)

#	from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList
#	from Gnumed.pycommon import gmI18N

	def create_widget_on_test_kwd1(*args, **kwargs):
		print "test keyword must have been typed..."
		print "actually this would have to return a suitable wxWindow subclass instance"
		print "args:", args
		print "kwd args:"
		for key in kwargs.keys():
			print key, "->", kwargs[key]
	#================================================================
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
	#================================================================
	class cTestKwdPopupPanel(wx.wxPanel):
		def __init__(self, parent, pos, size, style, completion_callback):
			wx.wxPanel.__init__ (
				self,
				parent,
				-1,
				pos,
				size,
				style
			)
			self.__completion_callback = completion_callback
			self._wxID_BTN_OK = wx.wxNewId()
			self._wxID_BTN_Cancel = wx.wxNewId()
			self.__do_layout()
			self.__register_interests()
			self.Show()

		def __do_layout(self):
			# message
			msg = "test keyword popup"
			text = wx.wxStaticText (self, -1, msg)
			# buttons
			self.btn_OK = wx.wxButton(self, self._wxID_BTN_OK, _("OK"))
			self.btn_OK.SetToolTipString(_('dismiss popup and embed data'))
			self.btn_Cancel = wx.wxButton(self, self._wxID_BTN_Cancel, _("Cancel"))
			self.btn_Cancel.SetToolTipString(_('dismiss popup and throw away data'))
			szr_buttons = wx.wxBoxSizer(wx.wxHORIZONTAL)
			szr_buttons.Add(self.btn_OK, 1, wx.wxEXPAND | wx.wxALL, 1)
			szr_buttons.Add(5, 0, 0)
			szr_buttons.Add(self.btn_Cancel, 1, wx.wxEXPAND | wx.wxALL, 1)
			# arrange
			szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
			szr_main.Add(text, 1, wx.wxEXPAND | wx.wxALL, 1)
			szr_main.Add(szr_buttons, 0)
			# layout
			self.SetAutoLayout(True)
			self.SetSizer(szr_main)
			szr_main.Fit(self)

		def __register_interests(self):
			wx.EVT_BUTTON(self.btn_OK, self._wxID_BTN_OK, self._on_ok)
			wx.EVT_BUTTON(self.btn_Cancel, self._wxID_BTN_Cancel, self._on_cancel)

		def _on_ok(self, event):
			self.__completion_callback(was_cancelled = False)

		def _on_cancel(self, event):
			self.__completion_callback(was_cancelled = True)
	#================================================================
	def create_widget_on_test_kwd3(parent, pos, size, style, completion_callback):
		pnl = cTestKwdPopupPanel (
			parent = parent,
			pos = pos,
			size = size,
			style = style,
			completion_callback = completion_callback
		)
		return pnl
	#================================================================
	class cSoapWin (cResizingWindow):
		def DoLayout(self):
			self.input1 = cResizingSTC(self, -1)
			self.input2 = cResizingSTC(self, -1)
			self.input3 = cResizingSTC(self, -1)

			self.input1.prev_in_tab_order = None
			self.input1.next_in_tab_order = self.input2
			self.input2.prev_in_tab_order = self.input1
			self.input2.next_in_tab_order = self.input3
			self.input3.prev_in_tab_order = self.input2
			self.input3.next_in_tab_order = None

			self.AddWidget (widget=self.input1, label="S")
			self.Newline()
			self.AddWidget (widget=self.input2, label="O")
			self.Newline()
			self.AddWidget (widget=self.input3, label="A+P")

			kwds = {}
			kwds['$test_keyword'] = {'widget_factory': create_widget_on_test_kwd3}
			self.input2.set_keywords(popup_keywords=kwds)
	#================================================================
	class cSoapPanel(wx.wxPanel):
		def __init__ (self, parent, id):
			wx.wxPanel.__init__(self, parent, id)
			sizer = wx.wxBoxSizer(wx.wxVERTICAL)
			self.soap = cSoapWin(self, -1)
			self.save = wx.wxButton (self, -1, _(" Save "))
			self.delete = wx.wxButton (self, -1, _(" Delete "))
			self.new = wx.wxButton (self, -1, _(" New "))
#			self.list = wx.wxListBox (self, -1, style=wx.wxLB_SINGLE | wx.wxLB_NEEDED_SB)
			wx.EVT_BUTTON (self.save, self.save.GetId (), self.OnSave)
			wx.EVT_BUTTON (self.delete, self.delete.GetId (), self.OnDelete)
			wx.EVT_BUTTON (self.new, self.new.GetId (), self.OnNew)
#			wx.EVT_LISTBOX (self.list, self.list.GetId (), self.OnList)
			self.__do_layout()

		def __do_layout (self):
			sizer_1 = wx.wxBoxSizer(wx.wxVERTICAL)
			sizer_1.Add(self.soap, 3, wx.wxEXPAND, 0)
			sizer_2 = wx.wxBoxSizer (wx.wxHORIZONTAL)
			sizer_2.Add(self.save, 0, 0)
			sizer_2.Add(self.delete, 0, 0)
			sizer_2.Add(self.new, 0, 0)
			sizer_1.Add(sizer_2, 0, wx.wxEXPAND)
#			sizer_1.Add(self.list, 3, wx.wxEXPAND, 0)
			self.SetAutoLayout(1)
			self.SetSizer(sizer_1)
			sizer_1.Fit(self)
			sizer_1.SetSizeHints(self)
			self.Layout()

		def OnDelete (self, event):
			self.soap.Clear()
#			sel = self.list.GetSelection ()
#			if sel >= 0:
#				self.list.Delete (sel)

		def OnNew (self, event):
#			sel = self.list.GetSelection ()
#			if sel >= 0:
#				self.OnSave (None)
			self.soap.Clear()
#			self.list.SetSelection (sel, 0)

		def OnSave (self, event):
			data = self.soap.GetValue()
#			title = data['Assessment'] or data['Subjective'] or data['Plan'] or data['Objective']
			self.soap.Clear()
#			sel = self.list.GetSelection ()
#			if sel < 0:
#				self.list.Append (title, data)
#			else:
#				self.list.SetClientData (sel, data)
#				self.list.SetString (sel, title)

#		def OnList (self, event):
#			self.soap.SetValues (event.GetClientData ())
	#================================================================
	class testFrame(wx.wxFrame):
		def __init__ (self, title):
			wx.wxFrame.__init__ (self, None, wx.wxNewId(), "test SOAP", size = wx.wxSize (350, 500)) # this frame will have big fat borders
			wx.EVT_CLOSE (self, self.OnClose)
			panel = cSoapPanel(self, -1)
			sizer = wx.wxBoxSizer(wx.wxVERTICAL)
			sizer.Add (panel, 1, wx.wxGROW)
			self.SetSizer(sizer)
			self.SetAutoLayout(1)
			sizer.Fit (self)
			self.Layout ()

		def OnClose (self, event):
			self.Destroy()
	#================================================================
	class testApp(wx.wxApp):
		def OnInit (self):
			self.frame = testFrame ("testFrame")
			self.frame.Show()
			return 1
	#================================================================
	app = testApp(0)
	app.MainLoop()
#====================================================================
# $Log: gmResizingWidgets.py,v $
# Revision 1.19  2005-03-03 21:14:24  ncq
# - use cSTCval instead of complex dict
# - apply Carlos' patch for progress note *editing*
#
# Revision 1.18  2005/01/11 08:06:38  ncq
# - comment out self.completion for now
#
# Revision 1.17  2005/01/05 21:52:24  ncq
# - add logging on UP-ARROW for debugging
#
# Revision 1.16  2004/12/30 12:39:10  ncq
# - real popup sample added demonstrating the (yet unclean) API
#
# Revision 1.15  2004/12/25 18:52:44  cfmoro
# Fixed var name in loop
#
# Revision 1.14  2004/12/23 21:57:31  ncq
# - credit where credit is due, of course
#
# Revision 1.13  2004/12/23 16:22:52  ncq
# - factor out __get_focussed_fragment and us in keyword/list handling
# - move list popup handling to where it belongs
#
# Revision 1.12  2004/12/23 15:08:41  ncq
# - use timer from gmTimer to time list popup
# - callback simply prints a message to the console for now
#
# Revision 1.11  2004/12/23 14:11:55  ncq
# - scroll across STCs with Arrow-UP/DOWN as discussed with Richard
#
# Revision 1.10  2004/12/21 18:22:26  ncq
# - add test code and start handling a test keyword
#
# Revision 1.9  2004/12/21 17:20:24  ncq
# - we are slowly getting closer to the functionality of the original SOAP2
# - key handling according to discussion with Richard
#
# Revision 1.8  2004/12/15 21:49:47  ncq
# - just to let Ian know what I'm getting at re keyword/string
#   match separation
# - both occur after matches but "keywords"
# 	- don't have partial matches
# 	- occur immediately
# 	- execute arbitrary actions (usually popup some widget)
# 	- embed data keys into the narrative and add additional
# 	  data in the background
#   while "string matches"
#   	- produce partial matches (depending on configuration)
# 	- occur after a 300ms timeout (configurable)
# 	- always present a list to pick one entry from
# 	- return a simple string and do not add additional data
# - I think this warrants dedicated code
#
# Revision 1.7  2004/12/15 12:48:39  ihaywood
# replaced fancy GUI-widget handling match providers with a simpler solution that
# preserves the GUI/business layer divide.
#
# Revision 1.6  2004/12/14 11:58:15  ncq
# - various inline comments enhanced
# - in __OnKeyDown isn't the Skip() logic wrong ?
#
# Revision 1.5  2004/12/14 10:26:01  ihaywood
#
# minor fixes carried over from SOAP2.py
#
# Revision 1.4  2004/12/13 19:03:00  ncq
# - inching close to code that I actually understand
#
# Revision 1.3  2004/12/07 21:54:56  ncq
# - add some comments on proposed plan
#
# Revision 1.2  2004/12/06 20:46:49  ncq
# - a bit of cleanup
#
# Revision 1.1  2004/12/06 20:36:48  ncq
# - starting to integrate soap2
#
#
#====================================================
# Taken from:
# Source: /cvsroot/gnumed/gnumed/gnumed/test-area/ian/SOAP2.py,v
# Id: SOAP2.py,v 1.8 2004/11/09 13:13:18 ihaywood Exp
#
# Revision 1.8	2004/11/09 13:13:18	 ihaywood
# Licence added
#
# Segfaults fixed.
# Demonstration listbox for multiple SOAP entries, I had intended to drop
# this into the gnumed client, will check what Carlos is doing
#
# Still have vanishing cursor problem when returning  from a popup, can't
# seem to get it back even after explicit SetFocus ()
#
# Revision 1.7	2004/11/09 11:20:59	 ncq
# - just silly cleanup
#
# Revision 1.6	2004/11/09 11:19:47	 ncq
# - if we know that parent of ResizingSTC must be
#	ResizingWindow we can test for it
# - added some CVS keywords
# - this should not be a physical replacement for the edit
#	area, just a logical one where people want to use it !
#	IOW we will keep gmEditArea around as it IS a good design !
#
#----------------------------------------------------------------
# revision 1.5
# date: 2004/11/09 02:05:20;  author: ihaywood;	 state: Exp;  lines: +106 -100
# crashes less often now, the one stickler is clicking on the
# auto-completion list causes a segfault.
#
# This is becoming a candidate replacement for cEditArea
#
# revision 1.4
# date: 2004/11/08 09:36:28;  author: ihaywood;	 state: Exp;  lines: +86 -77
# fixed the crashing bu proper use of wxSize.SetItemMinSize (when all else
# fails, read the docs ;-)
#
# revision 1.3
# date: 2004/11/08 07:07:29;  author: ihaywood;	 state: Exp;  lines: +108 -22
# more fun with semicolons
# popups too: having a lot of trouble with this, many segfaults.
#
# revision 1.2
# date: 2004/11/02 11:55:59;  author: ihaywood;	 state: Exp;  lines: +198 -19
# more feaures, including completion box (unfortunately we can't use the
# one included with StyledTextCtrl)
#
# revision 1.1
# date: 2004/10/24 13:01:15;  author: ihaywood;	 state: Exp;
# prototypical SOAP editor, secondary to Sebastian's comments:
#	- Now shrinks as well as grows boxes
#	- TAB moves to next box, Shift-TAB goes back
