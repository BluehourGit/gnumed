"""GnuMed date input widget

All GnuMed date input should happen via classes in
this module. Initially this is just a plain text box
but using this throughout GnuMed will allow us to
transparently add features.
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/Attic/gmDateTimeInput.py,v $
# $Id: gmDateTimeInput.py,v 1.1 2003-10-06 09:16:21 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"

import sys, re, string
if __name__ == "__main__":
	sys.path.append ("../python-common/")

def no_interpret(s):
	return s

interpret = no_interpret

def _(s):
	return interpret(s)



import gmLog
_log = gmLog.gmDefLog

import gmExceptions, gmPhraseWheel

import mx.DateTime as mxDT

from wxPython.wx import *

_true = (1==1)
_false = not true
#============================================================
class cMatchProvider_Date(gmPhraseWheel.cMatchProvider):
	def __init__(self):
		self.__allow_past = None
		self.__shifting_base = None
		self.__expanders = []
		self.__expanders.append(self.__single_number)
		self.__expanders.append(self.__explicit_offset)
		gmPhraseWheel.cMatchProvider.__init__(self)
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""
		self.__now = mxDT.now()
		matches = []
		for expander in self.__expanders:
			items = expander(aFragment)
			if items is not None:
				matches.extend(items)
		if len(matches) > 0:
			return (_true, matches)
		else:
			return (_false, [])
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return None
	#--------------------------------------------------------
	# date fragment expanders
	#--------------------------------------------------------
	def __single_number(self, aFragment):
		if not re.match("^(\s|\t)*\d+(\s|\t)*$", aFragment):
			return None
		val = aFragment.replace(' ', '')
		val = int(val.replace('\t', ''))

		matches = []
		# nth day of this month (if larger than today or past explicitely allowed)
		if (self.__now.day <= val) or (self.__allow_past):
			target_date = self.__now + mxDT.RelativeDateTime(day = val)
			tmp = {
				'data': target_date,
				'label': _('day %d of this month (a %s)') % (val, target_date.strftime('%A'))
			}
			matches.append(tmp)
		# day of next month
		target_date = self.__now + mxDT.RelativeDateTime(months = 1, day = val)
		tmp = {
			'data': target_date,
			'label': _('day %d of next month (a %s)') % (val, target_date.strftime('%A'))
		}
		matches.append(tmp)
		# X days from now (if <32)
		if val < 32:
			target_date = self.__now + mxDT.RelativeDateTime(days = val)
			tmp = {
				'data': target_date,
				'label': _('in %d days (a %s)') % (val, target_date.strftime('%A'))
			}
			matches.append(tmp)
		# X weeks from now (if <5)
		if val < 7:
			target_date = self.__now + mxDT.RelativeDateTime(weeks = val)
			tmp = {
				'data': target_date,
				'label': _('in %d weeks (a %s)') % (val, target_date.strftime('%A'))
			}
			matches.append(tmp)
		# day of this week
		# day of next week
		return matches
	#--------------------------------------------------------
	def __explicit_offset(self, aFragment):
		# "+/-XXd/w/m/t"
		if not re.match("^(\s|\t)*(\+|-)?(\s|\t)*\d{1,2}(\s|\t)*[mdtw](\s|\t)*$", aFragment):
			return None
		# allow past ?
		is_future = 1
		if string.find(aFragment, '-') > -1:
			is_future = None
			if not self.__allow_past:
				return None

		val = int(re.search('\d{1,2}', aFragment).group())
		target_date = None
		if re.search('[dt]', aFragment):
			if is_future:
				target_date = self.__now + mxDT.RelativeDateTime(days = val)
				label = _('in %d days (a %s)') % (val, target_date.strftime('%A'))
			else:
				target_date = self.__now - mxDT.RelativeDateTime(days = val)
				label = _('%d days ago (a %s)') % (val, target_date.strftime('%A'))
		elif re.search('[w]', aFragment):
			if is_future:
				target_date = self.__now + mxDT.RelativeDateTime(weeks = val)
				label = _('in %d weeks (a %s)') % (val, target_date.strftime('%A'))
			else:
				target_date = self.__now - mxDT.RelativeDateTime(weeks = val)
				label = _('%d weeks ago (a %s)') % (val, target_date.strftime('%A'))
		elif re.search('[m]', aFragment):
			if is_future:
				target_date = self.__now + mxDT.RelativeDateTime(months = val)
				label = _('in %d months (a %s)') % (val, target_date.strftime('%A'))
			else:
				target_date = self.__now - mxDT.RelativeDateTime(months = val)
				label = _('%d months (a %s)') % (val, target_date.strftime('%A'))
		if target_date is None:
			return None
		tmp = {
			'data': target_date,
			'label': label
		}
		return [tmp]
#==================================================
class gmDateInput(gmPhraseWheel.cPhraseWheel):
	def __init__(self, *args, **kwargs):
		matcher = cMatchProvider_Date()
		matcher.setWordSeparators('xxx_do_not_separate_words_xxx')
#		matcher.setIgnoredChars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
		matcher.setThresholds(aWord = 998, aSubstring = 999)

#		if not kwargs.has_key('id_callback'):
#			kwargs['id_callback'] =  self.__selected
		kwargs['aMatchProvider'] = matcher
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.allow_multiple_phrases(None)
		
		self.__display_format = _('%Y-%m-%d')
		self.__default_text = _('enter date here')

		self.SetValue(self.__default_text)
		self.SetSelection (-1,-1)

		EVT_CHAR(self, self.__on_char)
		#EVT_KEY_DOWN (self, self.__on_key_pressed)

		self.__tooltip = _(
"""------------------------------------------------------------------------------
Date input field

 <ALT-v/g/h/m/�>: vorgestern/gestern/heute/morgen/�bermorgen
 <ALT-K>:         Kalender
 +/- X d/w/m:     X days/weeks/months ago/from now
------------------------------------------------------------------------------
""")
		self.SetToolTip(wxToolTip(self.__tooltip))
	#----------------------------------------------
	def on_list_item_selected (self):
		"""Gets called when user selected a list item."""
		self._hide_picklist()

		selection_idx = self._picklist.GetSelection()
		data = self._picklist.GetClientData(selection_idx)

		self.SetValue(data.strftime(self.__display_format))

		if self.notify_caller is not None:
			self.notify_caller (data)
	#----------------------------------------------
	# event handlers
	#----------------------------------------------
	def __on_char(self, evt):
		keycode = evt.GetKeyCode()

		if evt.AltDown():
			if keycode in [ord('h'), ord('H')]:
				date = mxDT.now()
				self.SetValue(date.strftime(self.__display_format))
				return true
			if keycode in [ord('m'), ord('M')]:
				date = mxDT.now() + mxDT.RelativeDateTime(days = 1)
				self.SetValue(date.strftime(self.__display_format))
				return true
			if keycode in [ord('g'), ord('G')]:
				date = mxDT.now() - mxDT.RelativeDateTime(days = 1)
				self.SetValue(date.strftime(self.__display_format))
				return true
			if keycode in [ord('�'), ord('�')]:
				date = mxDT.now() + mxDT.RelativeDateTime(days = 2)
				self.SetValue(date.strftime(self.__display_format))
				return true
			if keycode in [ord('v'), ord('V')]:
				date = mxDT.now() - mxDT.RelativeDateTime(days = 2)
				self.SetValue(date.strftime(self.__display_format))
				return true
			if keycode in [ord('k'), ord('K')]:
				print "Kalender noch nicht implementiert"
				return true

		evt.Skip()
	#----------------------------------------------
	def __on_key_pressed (self, key):
		"""Is called when a key is pressed."""
		print "on key pressed"
		if key.GetKeyCode in (ord('h'), ord('H')):
			date = mxDT.now()
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('m'), ord('M')):
			date = mxDT.now() + mxDT.RelativeDateTime(days = 1)
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('g'), ord('G')):
			date = mxDT.now() - mxDT.RelativeDateTime(days = 1)
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('�'), ord('�')):
			date = mxDT.now() + mxDT.RelativeDateTime(days = 2)
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('v'), ord('V')):
			date = mxDT.now() - mxDT.RelativeDateTime(days = 2)
			self.SetValue(date.strftime(self.__display_format))
			return

		key.Skip()
	#----------------------------------------------
	def __selected(self, data):
		pass
	#----------------------------------------------
	def set_value(self, aValue = None):
		"""Only set value if it's a valid one."""
		pass
	#----------------------------------------------	
	def set_range(self, list_of_ranges):
	#----------------------------------------------
		pass
#==================================================
class gmTimeInput(wxTextCtrl):
	def __init__(self, parent, *args, **kwargs):
		if len(args) < 2:
			if not kwargs.has_key('value'):
				kwargs['value'] = _('enter time here')
		wxTextCtrl.__init__(
			self,
			parent,
			*args,
			**kwargs
		)
	#----------------------------------------------
#==================================================
# main
#--------------------------------------------------
if __name__ == '__main__':
	import gmI18N
	#----------------------------------------------------
	def clicked (data):
		print "Selected :%s" % data
	#----------------------------------------------------
	class TestApp (wxApp):
		def OnInit (self):

			frame = wxFrame (
				None,
				-4,
				"date input wheel test for GNUmed",
				size=wxSize(300, 350),
				style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE
			)

			date_wheel = gmDateInput(
				parent = frame,
				id = -1,
				pos = (50, 50),
				size = (180, 30)
			)
			date_wheel.on_resize (None)

			frame.Show (1)
			return 1
	#--------------------------------------------------------
	app = TestApp ()
	app.MainLoop ()

#	app = wxPyWidgetTester(size = (200, 80))
#	app.SetWidget(gmTimeInput, -1)
#	app.MainLoop()
#==================================================
# - free text input: start string with "
#==================================================
# $Log: gmDateTimeInput.py,v $
# Revision 1.1  2003-10-06 09:16:21  sjtan
#
# this version of editArea works with the modified phraseWheel and dateInput in
# the same directory.
#
# Revision 1.4  2003/10/02 20:51:12  ncq
# - add alt-XX shortcuts, move __* to _*
#
# Revision 1.3  2003/09/30 18:47:47  ncq
# - converted date time input field into phrase wheel descendant
#
# Revision 1.2  2003/08/10 00:57:15  ncq
# - add TODO item
#
# Revision 1.1  2003/05/23 14:05:01  ncq
# - first implementation
#
