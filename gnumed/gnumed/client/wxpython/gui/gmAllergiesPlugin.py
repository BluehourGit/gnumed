#======================================================================
# GnuMed allergies notebook plugin
# --------------------------------
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmAllergiesPlugin.py,v $
# $Id: gmAllergiesPlugin.py,v 1.1 2004-07-17 21:16:39 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"

from wxPython.wx import *

from Gnumed.wxpython import gmPlugin, gmAllergyWidgets
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmAllergiesPlugin(gmPlugin.wxNotebookPlugin):
	"""Plugin to encapsulate the allergies window."""

	__icons = {
"""icon_letter_A""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}

	tab_name = _('Allergies')

	def name (self):
		return gmAllergiesPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmAllergyWidgets.cAllergyPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('view', '&Allergies')

	def populate_with_data(self):
		# no use reloading if invisible
		if self.gb['main.notebook.raised_plugin'] != self.__class__.__name__:
			return 1
		self._widget.populate()
		return 1

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(gmAllergyWidgets.cAllergyPanel, -1)
	app.MainLoop()
#======================================================================
# $Log: gmAllergiesPlugin.py,v $
# Revision 1.1  2004-07-17 21:16:39  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
