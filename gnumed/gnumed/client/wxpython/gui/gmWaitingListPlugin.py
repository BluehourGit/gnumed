#=====================================================
# GNUmed provider inbox plugin
# later to evolve into a more complete "provider-centric hub"
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmWaitingListPlugin.py,v $
# $Id: gmWaitingListPlugin.py,v 1.2 2009-06-29 15:13:25 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmPatSearchWidgets

#======================================================================
class gmWaitingListPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the waiting list."""

	tab_name = _('Waiting list')
	#--------------------------------------------------------
	def __init__(self):
		gmPlugin.cNotebookPlugin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmWaitingListPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmPatSearchWidgets.cWaitingListPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('office', _('&Waiting list'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
#======================================================================
# $Log: gmWaitingListPlugin.py,v $
# Revision 1.2  2009-06-29 15:13:25  ncq
# - improved placement in menu hierarchy
# - add active letters
#
# Revision 1.1  2009/01/17 23:00:00  ncq
# - a new plugin
#
# Revision 1.8  2007/10/12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.7  2006/12/17 22:21:05  ncq
# - cleanup
#
# Revision 1.6  2006/12/17 20:45:38  ncq
# - cleanup
#
# Revision 1.5  2006/05/28 16:15:27  ncq
# - populate already handled by plugin base class now
#
# Revision 1.4  2006/05/20 18:56:03  ncq
# - use receive_focus() interface
#
# Revision 1.3  2006/05/15 13:41:05  ncq
# - use patient change signal mixin
# - raise ourselves when patient has changed
#
# Revision 1.2  2006/05/15 11:07:26  ncq
# - cleanup
#
# Revision 1.1  2006/01/15 14:30:56  ncq
# - first crude cut at this
#
#