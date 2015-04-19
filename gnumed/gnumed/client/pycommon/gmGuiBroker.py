"""GNUMed GUI element brokerage

This module provides wrappers for the equivalent of global
variables needed for a gnumed GUI client interface

@author: Dr. Horst Herb
@version: 0.2
@copyright: GPL v2 or later
"""
#-----------------------------------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmGuiBroker.py,v $
# $Id: gmGuiBroker.py,v 1.4 2004-06-20 15:44:28 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "H.Herb <hherb@gnumed.net>, H.Berger <Hilmar.Berger@gmx.de>"
#===========================================================
if __name__ == '__main__':
	_ = lambda x:x

# FIXME !!! hack moved here from gmConf. This definitely must be replaced by some 
# structure getting data from the backend
# FIXME: hardcoded color/width !?! move to DB (?)
config = {'main.use_notebook':1, 'main.shadow.colour':(131, 129, 131), 'main.shadow.width':10}

#===========================================================
class GuiBroker:
	"Wrapper for global objects needed by GNUMmed GUI clients"

	#This class wraps all global gui objects (variables)for a gnumed
	#application. The static (at application level)dictionary
	#__objects can be accessed through the method addobject
	#and getobject.
	#So, if you need to access the main window frame, you would
	#query an instance of GuiBroker for it.

	__objects = {}
	__keycounter=0


	def __init__(self):
		pass


	def addobject(self, widget, key=None):
		"Add an object to the gnumed gui object dictionary"

		#An object can be anything (class, variable, widget)
		#The "key" is a key expression (number, text) that
		#allows you to retrieve the object.
		#Convention for keys is the widget or variable name
		#as a text string
		#If key is not passed as parameter, a unique serial
		#number is allocated as key and returned

		if not key:
		# create a new sequential key that doesn't exist yet
			key = GuiBroker.__keycounter + 1
			while key in GuiBroker.__objects:
				key +=1
		GuiBroker.__keycounter = key
		GuiBroker.__objects[key]=widget
		return key



	def getobject(self, key):
		"allows to retrieve a gnumed gui element; see addobject() regarding the key parameter"
		return GuiBroker.__objects[key]

	def has_key( self, key):
		return key in GuiBroker.__objects



	def keylist(self):
		" returns a list of all keys; see documentation for the dictionary data type"
		return GuiBroker.__objects.keys()



	def valuelist(self):
		"returns a list of all values; see documentation for the dictionary data type"
		return GuiBroker.__objects.values()



	def itemlist(self):
		"returns a list of all key:value pairs; see documentation for the dictionary data type"
		return GuiBroker.__objects.items()



	def __getitem__(self, key):
		"Allows retrieving the value via value = instance[key]"
		return self.getobject(key)



	def __setitem__(self, key, object):
		"Allows access in the style of instance[key]=value"
		return self.addobject(object, key)

#===========================================================
# you can test this module by invoking it as main program
if __name__ == "__main__":
    print '>>> gmGuiBroker.GuiBroker test'
    test = GuiBroker()

    print '>>> test.addobject("something", 3)'
    var = test.addobject("something", 3)
    print var, "\n"

    print '>>> test.addobject("something else without a specified key")'
    var = test.addobject("something else without a specified key")
    print var, "\n"

    print '>>> test.addobject(test)'
    testreference = test.addobject(test)
    print testreference, "\n"

    print '>>> test.addobject(100, "hundred)'
    var = test.addobject(100, "hundred")
    print var, "\n"

    print ">>> test.keylist()"
    var = test.keylist()
    print var, "\n"

    print ">>> test.valuelist()"
    var = test.valuelist()
    print var, "\n"

    print ">>> test.itemlist()"
    var = test.itemlist()
    print var, "\n"

    print ">>> test[3]"
    var = test[3]
    print var, "\n"

    print ">>> test[testreference].getobject('hundred')"
    var = test[testreference].getobject('hundred')
    print var, "\n"

    print ">>> var = test[testreference]"
    var = test[testreference]
    print var, "\n"

    print ">>> var = var['hundred']"
    var = var['hundred']
    print var, "\n"

    print '>>> try: test.addobject["duplicate key", 3]'
    print '>>> except KeyError: print "Duplicate keys not allowed!"'
    try: test["duplicate key", 3]
    except KeyError: print "Duplicate keys not allowed!"

    print ">>> test['key']='value'"
    test['key']='value'
    print test['key']

#===========================================================
# $Log: gmGuiBroker.py,v $
# Revision 1.4  2004-06-20 15:44:28  ncq
# - we need to be more careful in pleasing epydoc
#
# Revision 1.3  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.2  2004/03/10 00:14:04  ncq
# - fix imports
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.8  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.7  2003/02/09 11:48:59  ncq
# - just some silly cvs keyword
#
# Revision 1.6  2003/02/09 09:41:57  sjtan
#
# clean up new code, make it less intrusive.
#
# Revision 1.5  2003/01/16 14:45:03  ncq
# - debianized
#
# Revision 1.4  2003/01/12 00:20:04  ncq
# - fixed __author__
#
# Revision 1.3  2003/01/12 00:17:44  ncq
# - fixed typo, added CVS keywords
#
