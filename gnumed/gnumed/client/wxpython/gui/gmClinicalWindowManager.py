"""Patient window manager class for the main notebook.

Allows plugins to register, and swap in an out of view.

A plugin may elect to be in three modes:

wholescreen
 - the plugin seizes the whole panel
 - should this exist ? IMHO no (kh)

lefthalf
 - the plugin gets the left column onscreen
 - the right column becomes visible.

right column
 - the plugin is added to a vertical sizer on the right-hand
   column (note all of these plugins are visible at once)
"""
#==================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmClinicalWindowManager.py,v $
# $Id: gmClinicalWindowManager.py,v 1.11 2004-02-18 14:04:25 ncq Exp $
# license: GPL
__version__ = "$Revision: 1.11 $"
__author__ =	"I.Haywood"

from wxPython.wx import *
import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

import gmGuiBroker, gmDispatcher, gmShadow, gmPlugin
#==================================================
class gmClinicalPanel (wxPanel):

	def __init__ (self, parent):
		wxPanel.__init__ (self, parent, -1)
		EVT_SIZE (self, self.OnSize)
		self.__gb = gmGuiBroker.GuiBroker ()
		self.wholescreen = {}
		self.lefthalf = {}
		self.visible_plugin = '' # plugin currently visible in left or whole screen
		self.default = '' # set by one plugin!
		self.righthalf = {}
		self.sizer = wxBoxSizer (wxHORIZONTAL)
		self.SetSizer (self.sizer)
		if gmGuiBroker.config['main.shadow']:
			self.righthalfshadow = gmShadow.Shadow (self, -1)
			self.righthalfpanel = wxPanel (self.righthalfshadow, -1)
			self.righthalfshadow.SetContents (self.righthalfpanel)
		else:
			self.righthalfpanel = wxPanel (self, -1)
			self.righthalfshadow = self.righthalfpanel
	#----------------------------------------------
	def OnSize (self, event):
		w,h = self.GetClientSizeTuple ()
		self.sizer.SetDimension (0,0, w, h)
	#----------------------------------------------
	def SetDefault (self, d):
		self.default = d
	#----------------------------------------------
	def DisplayDefault (self):
		self.Display (self.default)
	#----------------------------------------------
	def RegisterWholeScreen (self, name, panel):
		"""Receives a wxPanel which is to fill the whole screen.

		Client must NOT do Show () on the panel!
		"""
		self.wholescreen[name] = panel
		panel.Show (0)
		_log.Log(gmLog.lData, "registering whole screen [%s]" % name)
	#----------------------------------------------
	def RegisterLeftSide (self, name, panel):
		"""Register for left side.
		"""
		panel.Show (0)
		self.lefthalf[name] = panel
		_log.Log(gmLog.lData, "registering left side [%s]" % name)
	#----------------------------------------------
	def RegisterRightSide (self, name, panel, position = 1):
		"""Register for right column.

		Panel must be self.righthalfpanel
		Note there is no display function for these: they are
		automatically displayed when a left-column plugin is displayed
		"""
		self.righthalf[name] = (panel, position)
		panel.Show(0)
		_log.Log(gmLog.lData, "registering right side [%s]" % name)
	#----------------------------------------------
	# FIXME: Someone please document what is happening here !!!
	def Unregister (self, name):
		if name == self.default:
			_log.Log(gmLog.lErr, 'cannot unregister default plugin [%s]' % name)
		else:
			if self.visible_plugin == name:
				self.Display (self.default)
			_log.Log(gmLog.lInfo, 'Unregistering plugin [%s]' % name)
			if self.righthalf.has_key (name):
				# self.visible_plugin is the name of the whole screen widget if any
				if self.lefthalf.has_key (self.visible_plugin):
					self.vbox.Remove (self.righthalf[name][0])
					self.vbox.Layout ()
				del self.righthalf[name]
			elif self.lefthalf.has_key (name):
				del self.lefthalf[name]
			elif self.wholescreen.has_key (name):
				del self.wholescreen[name]
			else:
				_log.Log(gmLog.lErr, 'tried to delete non-existant plugin [%s]' % name)
	#----------------------------------------------
	def Display (self, name):
		"""Displays the named widget.
		"""
		if self.wholescreen.has_key (name):
			self.DisplayWhole (name)
		elif self.lefthalf.has_key (name):
			self.DisplayLeft (name)
		else:
			_log.Log(gmLog.lErr, 'no plugin [%s] registered' % name)
	#----------------------------------------------
	def DisplayWhole (self, name):
		_log.Log(gmLog.lData, 'displaying whole screen plugin [%s]' % name)
		if self.wholescreen.has_key (self.visible_plugin):
			# already in full-screen mode
			self.wholescreen[self.visible_plugin].Show (0)
			self.sizer.Remove (0)
			self.sizer.Add (self.wholescreen[name])
			self.wholescreen[name].Show (1)
			self.sizer.Layout ()
			self.visible_plugin = name
		else:
			if self.lefthalf.has_key (self.visible_plugin):
				# remove left half and right column
				self.sizer.Remove (0)
				self.lefthalf[self.visible_plugin].Show (0)
				self.righthalfshadow.Show (0)
				self.sizer.Remove (self.righthalfshadow)
			# now put whole screen in
			self.wholescreen[name].Show (1)
			self.sizer.Add (self.wholescreen[name], 1, wxEXPAND, 0)
			self.visible_plugin = name
			self.sizer.Layout ()
	#----------------------------------------------
	def DisplayLeft (self, name):
		_log.Log(gmLog.lData, 'displaying left screen plugin [%s]' % name)
		if self.lefthalf.has_key (self.visible_plugin):
			self.sizer.Remove (self.lefthalf[self.visible_plugin])
			self.lefthalf[self.visible_plugin].Show (0)
			self.lefthalf[name].Show (1)
			self.sizer.Prepend (self.lefthalf[name], 2, wxEXPAND, 0)
			self.sizer.Layout ()
			self.visible_plugin = name
		else:
			if self.wholescreen.has_key (self.visible_plugin):
				self.sizer.Remove (self.wholescreen[self.visible_plugin])
				self.wholescreen[self.visible_plugin].Show (0)
			self.lefthalf[name].Show (1)
			self.sizer.Add (self.lefthalf[name], 2, wxEXPAND, 0)
			self.vbox = wxBoxSizer (wxVERTICAL)
			pos = 1
			done = 0
			while done < len (self.righthalf.values ()):
				for w, p in self.righthalf.values ():
					if p == pos:
						w.Show (1)
						self.vbox.Add (w, 1, wxEXPAND, 0)
						done += 1
				pos += 1
			self.righthalfpanel.SetSizer (self.vbox)
			self.righthalfpanel.SetAutoLayout (1)
			self.righthalfshadow.Show (1)
			self.sizer.Add (self.righthalfshadow, 1, wxEXPAND, 0) 
			self.sizer.Layout ()
			self.visible_plugin = name
	#----------------------------------------------
	def GetVisiblePlugin(self):
		if not self.__dict__.has_key('visible_plugin'):
			return ""
		return self.visible_plugin
#==================================================
class gmClinicalWindowManager (gmPlugin.wxNotebookPlugin):

	tab_name = _("Clinical")

	def name (self):
		return gmClinicalWindowManager.tab_name
	#----------------------------------------------
	def MenuInfo (self):
		return None # we add our own submenu
	#----------------------------------------------
	def GetWidget (self, parent):
		self.panel = gmClinicalPanel (parent)
		self.gb['clinical.manager'] = self.panel
		return self.panel
	#----------------------------------------------
	def register (self):
		gmPlugin.wxNotebookPlugin.register(self)
		# add own submenu, patient plugins add to this
		ourmenu = wxMenu()
		self.gb['clinical.submenu'] = ourmenu
		menu = self.gb['main.viewmenu']
		self.menu_id = wxNewId ()
		menu.AppendMenu (self.menu_id, _('&Clinical'), ourmenu, self.name ())
		# "patient" needs fixing
		plugin_list = gmPlugin.GetPluginLoadList('patient')
		# "patient" needs fixing
		for plugin in plugin_list:
			p = gmPlugin.InstPlugin(
				'patient',
				plugin,
				guibroker = self.gb
			)
			try:
				p.register()
			except:
				_log.LogException("file [%s] doesn't seem to be a plugin" % (plugin), sys.exc_info(), verbose = 1)
		#self.panel.Show (0)
		self.panel.DisplayDefault()
		self.gb['toolbar.%s' % self.internal_name()].Realize()
	#----------------------------------------------
	def unregister (self):
		# tidy up after ourselves
		gmPlugin.wxNotebookPlugin.unregister (self)
		menu = self.gb['main.viewmenu']
		menu.Destroy (self.menu_id)
		# FIXME: should we unregister () each of our sub-modules?
	#----------------------------------------------
	def ReceiveFocus(self):
		try:
			self.gb['modules.patient'][self.panel.GetVisiblePlugin()].Shown()
		except:
			self.gb['modules.patient'][self.gb['modules.patient'].keys()[0]].Shown()
	#----------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#==================================================
# $Log: gmClinicalWindowManager.py,v $
# Revision 1.11  2004-02-18 14:04:25  ncq
# - whitespace fix
#
# Revision 1.10  2003/11/06 01:38:05  sjtan
#
# allows a default subclinical window to be selected, if none already selected; this allows the main tabs to switch
# to clinical if a patient is selected whilst in any non- cliniclManager tab window.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.9  2003/06/29 15:21:22  ncq
# - add can_receive_focus() on patient not selected
#
# Revision 1.8  2003/06/01 12:52:26  ncq
# - "verbose" != "verbosity"
#
# Revision 1.7  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.6  2003/05/27 13:00:41  sjtan
#
# removed redundant property support, read directly from __dict__
#
# Revision 1.5  2003/05/26 12:07:12  ncq
# - fatal=1 gives full tracebacks, no need for explicity
#
# Revision 1.4  2003/05/25 04:43:15  sjtan
#
# PropertySupport misuse for notifying Configurator objects during gui construction,
# more debugging info
#
# Revision 1.3  2003/04/28 12:08:35  ncq
# - more intuitive internal variable names
# - use plugin.internal_name()
# - leaner logging
#
# Revision 1.2  2003/04/05 00:39:23  ncq
# - "patient" is now "clinical", changed all the references
#
# Revision 1.1  2003/04/04 23:15:46  ncq
# - renamed to clinical* as per Richard's request
# - updated plugins.conf.sample
#
# Revision 1.15  2003/02/09 20:03:43  ncq
# - Shown -> ReceiveFocus
#
# Revision 1.14  2003/02/09 10:30:49  ncq
# - cleanup
#
# Revision 1.13  2003/02/09 01:08:03  sjtan
#
# a patient handler class for the classes in patient directory. Not all controls seem exposed.
#
# Revision 1.12  2003/01/12 16:46:42  ncq
# - catch failing plugins better
#
# Revision 1.11  2003/01/12 01:48:47  ncq
# - massive cleanup, CVS keywords
#
