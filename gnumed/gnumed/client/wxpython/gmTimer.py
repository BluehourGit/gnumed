"""GnuMed wxTimer proxy object.

@copyright: author(s)
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmTimer.py,v $
# $Id: gmTimer.py,v 1.1 2004-12-23 15:07:36 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

# 3rd party
from wxPython.wx import wxTimer

# GnuMed
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#===========================================================================
class cTimer(wxTimer):
	"""wxTimer proxy.

	It would be quite useful to tune the delay
	according to current network speed either at
	application startup or even during runtime.
	"""
	def __init__(self, callback = None, delay = 300, cookie = None):
		"""Set up our timer with reasonable defaults.

		- delay default is 300ms as per Richard Terry's experience
		- delay should be tailored to network speed/user speed
		- <cookie> is passed to <callback> when <delay> is up
		"""
		# sanity check
		if callback is None:
			_log.Log(gmLog.lErr, "no use setting up a timer without a callback function")
			raise ValueError, "No use setting up a timer without a callback function."

		if cookie is None:
			self.__cookie = id(self)
		else:
			self.__cookie = cookie
		self.__callback = callback
		self.__delay = delay

		wxTimer.__init__(self)
	#-----------------------------------------------------------------------
	def Notify(self):
		self.__callback(self.__cookie)
	#-----------------------------------------------------------------------
	def set_cookie(self, cookie=None):
		if cookie is None:
			self.__cookie = id(self)
		else:
			self.__cookie = cookie
#===========================================================================
if __name__ == '__main__':
	import time
	#-----------------------------------------------------------------------
	def cb_timer(cookie):
		print "timer <%s> fired" % cookie
		return 1
	#-----------------------------------------------------------------------
	print "setting up timer"
	timer = cTimer(callback = cb_timer)
	print "starting timer"
	timer.Start(oneShot = True)
	print "waiting for timer to trigger"
	time.sleep(2)
#===========================================================================
# $Log: gmTimer.py,v $
# Revision 1.1  2004-12-23 15:07:36  ncq
# - provide a convenient wxTimer proxy object
#
#
