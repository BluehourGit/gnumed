#===================================================
# Thanks to Python Patterns !
# ---------------------------
# $Id: gmBorg.py,v 1.1 2004-02-25 09:30:13 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

#===================================================
class cBorg:
	"""A generic Borg mixin.

	- mixin this class with your class' ancestors to borg it
	- call cBorg.__init__(self) right away in your own __init__()

	- there may be many instances of this but they all share state
	"""
	_shared_state = {}

	def __init__(self):
		# share state among all instances ...
		self.__dict__ = self._shared_state

#===================================================
# $Log: gmBorg.py,v $
# Revision 1.1  2004-02-25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.3  2003/12/29 16:21:51  uid66147
# - spelling fix
#
# Revision 1.2  2003/11/17 10:56:35  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.1  2003/04/02 16:07:55  ncq
# - first version
#
