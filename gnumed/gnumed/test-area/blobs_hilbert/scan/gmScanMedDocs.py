#!/usr/bin/env python
#==================================================
"""GnuMed/Archive document scanning.
"""
#==================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/scan/Attic/gmScanMedDocs.py,v $
__version__ = "$Revision: 1.7 $"
__license__ = "GPL"
__author__ =	"Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
				 Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#==================================================
import sys, os.path, os

# location of our modules
if __name__ == "__main__":
	# standalone from within GnuMed once integrated
	#sys.path.append(os.path.join('..', '..', 'python-common'))
	# standalone from test_area CVS tree
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N

from wxPython.wx import *
import string, time, shutil, os, tempfile

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import docDocument

_twain = None
_sane = None
#==================================================
[	wxID_SCANFRAME,
	wxID_LBOX_doc_pages,
	wxID_BTN_del_page,
	wxID_BTN_show_page,
	wxID_BTN_move_page,
	wxID_BTN_save_doc,
	wxID_BTN_acquire_page,
	wxID_PNL_main
] = map(lambda _init_ctrls: wxNewId(), range(8))
#==================================================
class scanFrame(wxPanel):
	# a list holding our objects
	acquired_pages = []
	#----------------------------------------------
	def __init__(self, parent, id):
		wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,)
        
		# FIXME: dict this !!
		(self.TwainSrcMngr, self.TwainScanner) = (None, None)
		(self.SaneSrcMngr, self.SaneScanner) = (None, None)

		self.scan_drv = "unknown"

		# get temp dir path from config file
		self.scan_tmp_dir = None
		tmp = _cfg.get("scanning", "tmp")
		if tmp == None:
			_log.Log(gmLog.lErr, 'Cannot get tmp dir from config file.')
		else:
			tmp = os.path.abspath(os.path.expanduser(tmp))
			if os.path.exists(tmp):
				self.scan_tmp_dir = tmp
		_log.Log(gmLog.lData, 'using tmp dir [%s]' % self.scan_tmp_dir)
		
		# -- main panel -----------------------
		self.PNL_main = wxPanel(
		    parent = self,
		    id = wxID_PNL_main
		)

		# -- "get next page" button -----------
		self.BTN_acquire_page = wxButton(
		    name = 'BTN_acquire_page',
		    parent = self.PNL_main,
		    id = wxID_BTN_acquire_page,
		    label = _("acquire image")
		)
		self.BTN_acquire_page.SetToolTipString(_('acquire the next image from the image source'))
		EVT_BUTTON(self.BTN_acquire_page, wxID_BTN_acquire_page, self.on_acquire_page)

		# -- list box with pages --------------
		self.LBOX_doc_pages = wxListBox(
		    size = wxSize(300,300),
		    choices = [],
		    parent = self.PNL_main,
		    id = wxID_LBOX_doc_pages,
		    style = wxLB_SORT,
		    validator = wxDefaultValidator
		)    
		self.LBOX_doc_pages.SetToolTipString(_('these pages make up the current document'))
		
		# -- show page button -----------------
		self.BTN_show_page = wxButton(
		    name = 'BTN_show_page',
		    parent = self.PNL_main,
		    id = wxID_BTN_show_page,
		    label = _("show page")
		)
		self.BTN_show_page.SetToolTipString(_('display selected part of the document'))
		EVT_BUTTON(self.BTN_show_page, wxID_BTN_show_page, self.on_show_page)
		
		# -- del page button ------------------
		self.BTN_del_page = wxButton(
		    name = 'BTN_del_page',
		    parent = self.PNL_main,
		    id = wxID_BTN_del_page,
		    label = _("delete page")
		)
		self.BTN_del_page.SetToolTipString(_('delete selected page from document'))
		EVT_BUTTON(self.BTN_del_page, wxID_BTN_del_page, self.on_del_page)
		
		# -- move page button -----------------		
		self.BTN_move_page = wxButton(
		    name = 'BTN_move_page',
		    parent = self.PNL_main,
		    id = wxID_BTN_move_page,
		    label = _("move page")
		)
		self.BTN_move_page.SetToolTipString(_('move selected page within document'))
		EVT_BUTTON(self.BTN_move_page, wxID_BTN_move_page, self.on_move_page)		
    		
		# -- save doc button ------------------
		self.BTN_save_doc = wxButton(
		    name = 'BTN_save_doc',
		    parent = self.PNL_main,
		    id = wxID_BTN_save_doc,
		    label = _("save document")
		)
		self.BTN_save_doc.SetToolTipString(_('save all currently acquired pages as one document'))
		EVT_BUTTON(self.BTN_save_doc, wxID_BTN_save_doc, self.on_save_doc)
    		
		self.staticText1 = wxStaticText(
		    name = 'staticText1',
		    parent = self.PNL_main,
		    id = -1,
		    label = _("document pages")
		)
		self.staticText2 = wxStaticText(
		    name = 'staticText2',
		    parent = self.PNL_main,
		    id = -1,
		    label = _("1) scan")
		)
    		self.staticText3 = wxStaticText(
		    name = 'staticText3',
		    parent = self.PNL_main,
		    id = -1,
		    label = _("2) save")
		)
		self.__set_properties()
		self.__do_layout()
	#-----------------------------------
	def __set_properties(self):
		self.SetTitle(_("scan documents"))
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))
		self.BTN_acquire_page.SetToolTipString(_("acquire the next image from the image source"))
		self.LBOX_doc_pages.SetToolTipString(_("these pages make up the current document"))
		self.LBOX_doc_pages.SetSelection(0)
		self.BTN_show_page.SetToolTipString(_("display selected part of the document"))
		self.BTN_del_page.SetToolTipString(_("delete selected page from document"))
		self.BTN_move_page.SetToolTipString(_("move selected page within document"))
		self.BTN_save_doc.SetToolTipString(_("save all currently acquired pages as one document"))
	#-----------------------------------
	def __do_layout(self):
		sizer_2 = wxBoxSizer(wxHORIZONTAL)
		grid_sizer_2 = wxGridSizer(2, 2, 0, 0)
		sizer_3 = wxBoxSizer(wxVERTICAL)
		sizer_4 = wxBoxSizer(wxHORIZONTAL)
		sizer_5 = wxBoxSizer(wxVERTICAL)
		sizer_6 = wxBoxSizer(wxVERTICAL)
		sizer_3.Add(self.staticText2, 0, wxBOTTOM, 10)
		sizer_3.Add(self.BTN_acquire_page, 0, wxEXPAND|wxRIGHT, 20)
		sizer_3.Add(self.staticText1, 0, wxTOP|wxBOTTOM, 5)
		sizer_3.Add(self.LBOX_doc_pages, 1, wxEXPAND|wxRIGHT|wxBOTTOM, 20)
		sizer_4.Add(self.BTN_show_page, 0, wxALL, 5)
		sizer_4.Add(self.BTN_del_page, 0, wxALL, 5)
		sizer_6.Add(sizer_4, 0, wxALIGN_CENTER_HORIZONTAL|wxRIGHT, 20) 
		sizer_6.Add(self.BTN_move_page, 0, wxALIGN_TOP|wxALIGN_CENTER_HORIZONTAL|wxTOP, 10)
		sizer_3.Add(sizer_6, 1, wxALIGN_CENTER_HORIZONTAL, 0)
		grid_sizer_2.Add(sizer_3, 1, wxEXPAND|wxLEFT, 20)
		#grid_sizer_2.Add(self.BTN_save_doc, 0, wxALIGN_CENTER_HORIZONTAL|wxLEFT|wxRIGHT|wxEXPAND, 20)
		sizer_5.Add(self.staticText3, 0, wxBOTTOM, 10)
		sizer_5.Add(self.BTN_save_doc, 1, wxEXPAND, 0)
		grid_sizer_2.Add(sizer_5, 1, wxEXPAND|wxLEFT|wxRIGHT|wxBOTTOM, 40)
		self.PNL_main.SetAutoLayout(1)
		self.PNL_main.SetSizer(grid_sizer_2)
		grid_sizer_2.Fit(self.PNL_main)
		sizer_2.Add(self.PNL_main, 1, wxEXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(sizer_2)
		sizer_2.Fit(self)
		self.Layout()
		
	#-----------------------------------
	# event handlers
	#-----------------------------------
	def on_acquire_page(self, event):
		global _twain
		global _sane

		# if we did not load the scanner driver yet
		if self.scan_drv == "unknown":
			try:
				import twain
				_twain = twain
				self.scan_drv = 'wintwain'
			except ImportError:
				exc = sys.exc_info()
				_log.LogException('Cannot import WinTWAIN.py.', exc, fatal=0)
				try:
					import sane
					_sane = sane
					self.scan_drv = 'linsane'
				except ImportError:
					exc = sys.exc_info()
					_log.LogException('Cannot import SANE.py.', exc, fatal=0)
					_log.Log(gmLog.lErr, "Can import neither TWAIN nor SANE scanner access library.")
					dlg = wxMessageDialog(
						self,
						_('Cannot load any scanner driver (SANE or TWAIN).'),
						_('acquiring page'),
						wxOK | wxICON_ERROR
					)
					dlg.ShowModal()
					dlg.Destroy()
					return None

			# like this:
			self.acquire_handler = {
				'wintwain': self.__acquire_from_twain,
				'linsane': self.__acquire_from_sane
			}
			if self.scan_drv == 'wintwain':
				self.twain_event_handler = {
					twain.MSG_XFERREADY: self.__twain_handle_transfer,
					twain.MSG_CLOSEDSREQ: self.__twain_close_datasource,
					twain.MSG_CLOSEDSOK: self.__twain_save_state,
					twain.MSG_DEVICEEVENT: self.__twain_handle_src_event
				}

		return self.acquire_handler[self.scan_drv]()
	#-----------------------------------
	def on_show_page(self, event):
		# did user select a page ?
		page_idx = self.LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can view it.'),
				_('displaying page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# now, which file was that again ?
		page_fname = self.LBOX_doc_pages.GetClientData(page_idx)

		(result, msg) = docDocument.call_viewer_on_file(page_fname)
		if not result:
			dlg = wxMessageDialog(
				self,
				_('Cannot display page %s.\n%s') % (page_idx+1, msg),
				_('displaying page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
	#-----------------------------------
	def on_del_page(self, event):
		page_idx = self.LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can delete it.'),
				_('deleting page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		else:
			page_fname = self.LBOX_doc_pages.GetClientData(page_idx)

			# 1) del item from self.acquired_pages
			self.acquired_pages[page_idx:(page_idx+1)] = []

			# 2) reload list box
			self.__reload_LBOX_doc_pages()

			# 3) kill file in the file system
			try:
				os.remove(page_fname)
			except:
				exc = sys.exc_info()
				_log.LogException("Cannot delete file.", exc, fatal=0)
				dlg = wxMessageDialog(
					self,
					_('Cannot delete page (file %s).\nSee log for details.') % page_fname,
					_('deleting page'),
					wxOK | wxICON_INFORMATION
				)
				dlg.ShowModal()
				dlg.Destroy()

			return 1
	#-----------------------------------
	def on_move_page(self, event):
		# 1) get page
		old_page_idx = self.LBOX_doc_pages.GetSelection()
		if old_page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can move it around.'),
				_('moving page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		page_fname = self.LBOX_doc_pages.GetClientData(old_page_idx)
		path, name = os.path.split(page_fname)

		# 2) ask for new position
		new_page_idx = -1
		while new_page_idx == -1:
			dlg = wxTextEntryDialog(
				parent = self,
				message = _('Moving original page %s.\n(file %s in %s)\n\nPlease enter the new position for the page !') % ((old_page_idx+1), name, path),
				caption = _('moving page'),
				defaultValue = str(old_page_idx+1)
			)
			btn = dlg.ShowModal()
			dlg.Destroy()
			# move ?
			if  btn == wxID_OK:
				tmp = dlg.GetValue()

				# numeric ?
				if not tmp.isdigit():
					new_page_idx = -1
					continue
				new_page_idx = int(tmp) - 1

				# in range ?
				if new_page_idx not in range(len(self.acquired_pages)):
					new_page_idx = -1
					continue

				# 3) move pages after the new position
				self.acquired_pages[old_page_idx:(old_page_idx+1)] = []
				self.acquired_pages[new_page_idx:new_page_idx] = [page_fname]

				# 5) update list box
				self.__reload_LBOX_doc_pages()

				return 1
			# or cancel moving ?
			elif btn == wxID_CANCEL:
				return 1
	#-----------------------------------
	def on_save_doc(self, event):
		# anything to do ?
		if self.acquired_pages == []:
			dlg = wxMessageDialog(
				self,
				_('You must acquire some images before\nyou can save them as a document !'),
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# get target directory
		target_repository = self.__get_target_repository()
		if not target_repository:
			return None

		# get document ID generation mode
		mode = self.__get_ID_mode()
		
		# get document ID
		if mode == "consecutive":
			doc_id = self.__get_next_consecutive_ID()
		else:
			doc_id = self.__get_random_ID(target_repository)

		# create barcode ?
		if self.__do_barcode():
			barcode = self.__generate_barcode(doc_id)
			if not barcode:
				return None
		else:
			barcode = None

		# create new directory in target repository
		doc_dir = self.__make_doc_dir(target_repository, doc_id)
		if not doc_dir:
			return None

		# write XML meta file
		if not self.__dump_metadata_to_xml(doc_dir):
			return None

		# copy data files there
		for i in range(len(self.acquired_pages)):
			old_name = self.acquired_pages[i]
			new_name = os.path.join(doc_dir, os.path.basename(old_name))
			try:
				shutil.copyfile(old_name, new_name)
			except:
				exc = sys.exc_info()
				_log.LogException("Can't move file [%s] into target repository [%s]." % (old_name, new_name), exc, fatal = 1)
				dlg = wxMessageDialog(
					self,
					_('Cannot copy page to target directory\n(%s -> %s).') % (old_name, new_name),
					_('saving document'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

		# unlock the directory for indexing
		if not self.__unlock_for_indexing(doc_dir):
			return None

		# remove old data files
		for i in range(len(self.acquired_pages)):
			old_name = self.acquired_pages[i]
			try:
				os.remove(old_name)
			except:
				exc = sys.exc_info()
				_log.LogException("Cannot remove source file [%s]." % old_name, exc, fatal = 0)

		# clean up gui/acquired_pages
		self.acquired_pages = []
		self.__reload_LBOX_doc_pages()

		# finally show doc ID for copying down on paper
		self.__show_doc_ID()

		return 1
	#-----------------------------------
	# internal methods
	#-----------------------------------
	def __reload_LBOX_doc_pages(self):
		self.LBOX_doc_pages.Clear()
		if len(self.acquired_pages) > 0:	
			for i in range(len(self.acquired_pages)):
				fname = self.acquired_pages[i]
				path, name = os.path.split(fname)
				self.LBOX_doc_pages.Append(_('page %s (%s in %s)' % (i+1, name, path)), fname)
	#-----------------------------------
	# TWAIN related scanning code
	#-----------------------------------
	def twain_event_callback(self, twain_event):
		_log.Log(gmLog.lData, 'notification of TWAIN event <%s>' % str(twain_event))
		return self.twain_event_handler[twain_event]()
	#-----------------------------------
	def __twain_handle_transfer(self):
		_log.Log(gmLog.lInfo, 'receiving image')
		_log.Log(gmLog.lData, 'image info: %s' % self.TwainScanner.GetImageInfo())

		# get from source
		try:
			(external_data_handle, more_images_pending) = self.TwainScanner.XferImageNatively()
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to get global heap image handle !', exc, fatal=1)
			# free external image memory
			_twain.GlobalHandleFree(external_data_handle)
			# hide the scanner user interface again
			self.TwainScanner.HideUI()
			return None

		_log.Log(gmLog.lData, '%s pending images' % more_images_pending)

		# make tmp file name
		# for now we know it's bitmap
		# FIXME: should be JPEG, perhaps ?
		tempfile.tempdir = self.scan_tmp_dir
		tempfile.template = 'obj-'
		fname = tempfile.mktemp('.bmp')
		try:
			# convert to bitmap file
			_twain.DIBToBMFile(external_data_handle, fname)
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to convert image in global heap handle into file [%s] !' % fname, exc, fatal=1)
			# free external image memory
			_twain.GlobalHandleFree(external_data_handle)
			# hide the scanner user interface again
			self.TwainScanner.HideUI()
			return None

		# free external image memory
		_twain.GlobalHandleFree(external_data_handle)
		# hide the scanner user interface again
		self.TwainScanner.HideUI()
		# and keep a reference
		self.acquired_pages.append(fname)
		#update list of pages in GUI
		self.__reload_LBOX_doc_pages()
		# FIXME: if more_images_pending:
		return 1
	#-----------------------------------
	def __twain_close_datasource(self):
		_log.Log(gmLog.lData, "being asked to close data source")
		return 1
	#-----------------------------------
	def __twain_save_state(self):
		_log.Log(gmLog.lData, "being asked to save application state")
		return 1
	#-----------------------------------
	def __twain_handle_src_event(self):
		_log.Log(gmLog.lInfo, "being asked to handle device specific event")
		return 1
	#-----------------------------------
	def __acquire_from_twain(self):
		_log.Log(gmLog.lInfo, "scanning with TWAIN source")
		# open scanner on demand
		if not self.TwainScanner:
			if not self.__open_twain_scanner():
				dlg = wxMessageDialog(
					self,
					_('Cannot connect to TWAIN source (scanner or camera).'),
					_('acquiring page'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

		self.TwainScanner.RequestAcquire()
		return 1
	#-----------------------------------
	def __open_twain_scanner(self):
		# did we open the scanner before ?
		if not self.TwainSrcMngr:
			#_log.Log(gmLog.lData, "TWAIN version: %s" % _twain.Version())
			# no, so we need to open it now
			# TWAIN talks to us via MS-Windows message queues so we
			# need to pass it a handle to ourselves
			self.TwainSrcMngr = _twain.SourceManager(self.GetHandle())
			if not self.TwainSrcMngr:
				_log.Log(gmLog.lData, "cannot get a handle for the TWAIN source manager")
				return None

			# TWAIN will notify us when the image is scanned
			self.TwainSrcMngr.SetCallback(self.twain_event_callback)

			_log.Log(gmLog.lData, "TWAIN source manager config: %s" % str(self.TwainSrcMngr.GetIdentity()))

		if not self.TwainScanner:
			self.TwainScanner = self.TwainSrcMngr.OpenSource()
			if not self.TwainScanner:
				_log.Log(gmLog.lData, "cannot open the scanner via the TWAIN source manager")
				return None

			_log.Log(gmLog.lData, "TWAIN data source: %s" % self.TwainScanner.GetSourceName())
			_log.Log(gmLog.lData, "TWAIN data source config: %s" % str(self.TwainScanner.GetIdentity()))
		return 1
	#-----------------------------------
	# SANE related scanning code
	#-----------------------------------
	def __acquire_from_sane(self):
		_log.Log(gmLog.lInfo, "scanning with SANE source")

		# open scanner on demand
		if not self.SaneScanner:
			if not self.__open_sane_scanner():
				dlg = wxMessageDialog(
					self,
					_('Cannot connect to SANE source (scanner or camera).'),
					_('acquiring page'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

		# Set scan parameters
		# FIXME: get those from config file
		#scanner.contrast=170 ; scanner.brightness=150 ; scanner.white_level=190
		#scanner.depth=6
		scanner.br_x = 412.0
		scanner.br_y = 583.0

		# make tmp file name
		# for now we know it's bitmap
		# FIXME: should be JPEG, perhaps ?
		# FIXME: get extension from config file
		tempfile.tempdir = self.scan_tmp_dir
		tempfile.template = 'obj-'
		fname = tempfile.mktemp('.jpg')
		try:
			# initiate the scan
			scanner.start()
			# get an Image object
			img = scanner.snap()
			#save image file to disk
			img.save(fname)
			# and keep a reference
			self.acquired_pages.appen(fname)

			# FIXME:
			#if more_images_pending:
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to get image from scanner into [%s] !' % fname, exc, fatal=1)
			return None

		# update list of pages in GUI
		self.__reload_LBOX_doc_pages()

		return 1
	#-----------------------------------
	def __open_sane_scanner(self):
		# did we open the scanner before ?
		if not self.SaneSrcMngr:
			# no, so we need to open it now
			try:
				init_result = _sane.init()
			except:
				exc = sys.exc_info()
				_log.LogException('cannot init SANE', exc, fatal=1)
				self.SaneSrcMngr = None
				return None

			_log.Log(gmLog.lData, "SANE version: %s" % str(init_result))

		if not self.SaneScanner:
			# FIXME: actually we should use this to remember which device we work with
			devices = []
			devices = _sane.get_devices()
			if devices == []:
				_log.Log (gmLog.lErr, "SANE did not find any devices")
				dlg = wxMessageDialog(
					self,
					_('Cannot find any SANE connected devices.'),
					_('opening scanner'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

			_log.Log(gmLog.lData, "available SANE devices: %s" % devices)

			try:
				# by default use the first device
				self.SaneScanner = _sane.open(_sane.get_devices()[0][0])
			except:
				exc = sys.exc_info()
				_log.LogException('cannot open SANE scanner', exc, fatal=1)
				return None

			_log.Log(gmLog.lData, 'opened SANE device: %s' % str(self.SaneScanner))
			_log.Log(gmLog.lData, 'SANE device config: %s' % self.SaneScanner.get_parameters())
			_log.Log(gmLog.lData, 'SANE device opts  : %s' % self.SaneScanner.optlist())

		return 1
	#-----------------------------------
	# internal helper methods
	#-----------------------------------
	def __do_barcode(self):
		tmp = _cfg.get("scanning", "generate barcode")
		_log.Log(gmLog.lData, 'document barcode generation mode: <%s>' % tmp)
		if tmp in ['on', 'yes']:
			return 1
		else:
			return None
	#-----------------------------------
	def __generate_barcode(self, doc_id):
		tmp = _cfg.get("scanning", "barcode generation command")
		if not tmp:
			_log.Log(gmLog.lErr, 'Cannot get barcode generation command from config file.')
			return None

		if tmp.count("%s") == 1:
			barcode_cmd = tmp % doc_id
		else:
			barcode_cmd = tmp

		aPipe = os.popen(barcode_cmd, "w")
		if aPipe == None:
			_log.Log(gmLog.lData, "Cannot open pipe to [%s]." % barcode_cmd)
			return None

		if tmp.count("%s") != 1:
			aPipe.write('"%s"\n' % doc_id)

		barcode = aPipe.readline()
		ret_code = aPipe.close()

		if ret_code == None and barcode != "":
			return barcode
		else:
			_log.Log(gmLog.lErr, "Something went awry while calling `%s`." % barcode_cmd)
			_log.Log(gmLog.lErr, '%s (%s): exit(%s) -> <%s>' % (os.name, sys.platform, ret_code, barcode), gmLog.lCooked)
			return None
	#-----------------------------------
	def __get_ID_mode(self):
		tmp = _cfg.get("scanning", "document ID mode")

		if not tmp in ['random', 'consecutive']:
			_log.Log(gmLog.lErr, '"%s" is not a valid document ID generation mode. Falling back to "random".' % tmp)
			return "random"

		_log.Log(gmLog.lData, 'document ID generation mode is "%s"' % tmp)
		return tmp
	#-----------------------------------
	def __get_next_consecutive_ID(self):
		fname = _cfg.get("scanning", "document ID file")
		if fname == None:
			_log.Log(gmLog.lErr, 'Cannot get name of file with most recently used document ID from config file')
			return None

		fname = os.path.abspath(os.path.expanduser(fname))

		try:
			ID_file = open(fname, "rb")
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot open file [%s] with most recently used document ID.' % fname, exc, fatal=0)
			return None

		last_ID = ID_file.readline()
		ID_file.close()

		# ask for confirmation of ID
		doc_id = -1
		new_ID = str(int(last_ID) + 1)
		while doc_id < 0:
			dlg = wxTextEntryDialog(
				parent = self,
				message = _('The most recently used document ID was <%s>.\nWe would use the ID <%s> for the current document.\nPlease confirm the ID or type in a new numeric ID.') % (last_ID, new_ID),
				caption = _('document ID'),
				defaultValue = new_ID,
				style = wxOK | wxCentre
			)
			dlg.ShowModal()
			dlg.Destroy()
			tmp = dlg.GetValue()
			# numeric ?
			if not new_ID.isdigit():
				doc_id = -1
			else:
				doc_id = int(new_ID)

		# store new document ID as most recently used one
		try:
			ID_file = open(fname, "wb")
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot open file [%s] storing the most recently used document ID for saving the new ID.' % fname, exc, fatal=0)
			return None
		ID_file.write("%s\n" % new_ID)
		ID_file.close()

		return new_ID
	#-----------------------------------
	def __get_random_ID(self, aTarget):
		# set up temp file environment for creating unique random directory
		tempfile.tempdir = aTarget
		tempfile.template = ""
		# create temp dir name
		dirname = tempfile.mktemp(suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()))
		# extract name for dir
		path, doc_ID = os.path.split(dirname)

		return doc_ID
	#-----------------------------------
	def __show_doc_ID(self, anID):
		show_ID = _cfg.get('scanning', 'show document ID')
		if show_ID == None:
			_log.Log(gmLog.lWarn, 'Cannot get option from config file.')
			show_ID = "yes"

		if show_ID != "no":
			dlg = wxMessageDialog(
				self,
				_("This is the reference ID for the current document:\n<%s>\nYou should write this down on the original documents.\n\nIf you don't care about the ID you can switch off this\nmessage in the config file.") % anID,
				_('document ID'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
	#-----------------------------------
	def __dump_metadata_to_xml(self, aDir):
		# FIMXE: error handling
		content = []

		tag = _cfg.get("metadata", "document_tag")
		content.append('<%s>\n' % tag)

		tag = _cfg.get("metadata", "obj_tag")
		for idx in range(len(self.acquired_pages)):
			dirname, fname = os.path.split(self.acquired_pages[idx])
			content.append('<%s>%s</%s>\n' % (tag, fname, tag))

		content.append('</%s>\n' % _cfg.get("metadata", "document_tag"))

		# overwrite old XML metadata file and write new one
		xml_fname = os.path.join(aDir, _cfg.get("metadata", "description"))
		#os.remove(xml_fname)
		xml_file = open(xml_fname, "w")
		map(xml_file.write, content)
		xml_file.close()
		return 1
	#-----------------------------------
	def __get_target_repository(self):
		"""Retrieve and validate target repository configuration."""
		tmp = _cfg.get("index", "repository")
		if tmp == None:
			_log.Log(gmLog.lErr, 'Cannot get target repository for scans from config file.')
			dlg = wxMessageDialog(
				self,
				_('Cannot get target repository from config file.'),
				_('invalid configuration'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# valid dir ?
		if not os.path.exists(tmp):
			_log.Log(gmLog.lErr, 'Target repository [%s] not accessible.' % tmp)
			dlg = wxMessageDialog(
				self,
				_('The configured target repository is not accessible.\n[%s]') % tmp,
				_('invalid configuration'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return tmp
	#-----------------------------------
	def __make_doc_dir(self, repository, doc_dir):
		"""Make new document directory in target repository."""
		dirname = os.path.join(repository, doc_dir)
		if os.path.exists(dirname):
			_log.Log(gmLog.lErr, 'The subdirectory [%s] already exists in the repository [%s]. Cannot save current document there.' % (doc_dir, repository))
			dlg = wxMessageDialog(
				self,
				_('The subdirectory [%s] already exists in the repository [%s].\nCannot save current document there.') % (doc_dir, repository),
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		try:
			os.mkdir(dirname)
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot create target repository subdirectory [%s]' % dirname, exc, fatal=1)
			dlg = wxMessageDialog(
				self,
				_("Cannot create the target repository subdirectory.\n(%s)") % dirname,
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return dirname
	#-----------------------------------
	def __unlock_for_indexing(self, aDir):
		"""Write checkpoint file so indexing can start."""
		can_index_file = _cfg.get('index', 'checkpoint file')
		if not can_index_file:
			dlg = wxMessageDialog(
				self,
				_('You must specify a checkpoint file for indexing in the config file.\nUse option <can index> in group [index].'),
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		fullname = os.path.join(aDir, can_index_file)
		try:
			f = open(fullname, "wb")
		except:
			exc = sys.exc_info()
			_log.LogException("Cannot lock target directory with checkpoint file [%s]." % fullname, exc, fatal = 1)
			dlg = wxMessageDialog(
				self,
				_('Cannot lock target directory !\ncheckpoint file: %s.') % fullname,
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		f.close()
		return 1
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	try:
		#application = ScanningApp(size = (800,600))
		application = wxPyWidgetTester(size=(-1,-1))
		application.SetWidget(scanFrame,-1)
		application.MainLoop()
	except:
		exc = sys.exc_info()
		_log.LogException('Unhandled exception.', exc, fatal=1)
		raise
else:
	import gmPlugin

	class gmScanMedDocs(gmPlugin.wxNotebookPlugin):
		def name (self):
			return _("Scan")

		def GetWidget (self, parent):
			return scanFrame (parent, -1)

		def MenuInfo (self):
			return (_('Tools'), _('&scan documents'))
#======================================================
# $Log: gmScanMedDocs.py,v $
# Revision 1.7  2002-11-17 17:07:03  ncq
# - various sane related fixes
#
# Revision 1.6  2002/11/17 16:24:13  ncq
# - sane.* -> _sane.*
#
# Revision 1.5  2002/10/11 10:20:37  ncq
# - on demand loading of scanner library so we can at least
#   start on machines without SANE or TWAIN
#
# Revision 1.4  2002/10/08 21:05:48  ncq
# - it is group scanning, not scan
#
# Revision 1.3  2002/10/08 20:55:34  ncq
# - sorry for the cruft
#
# Revision 1.2  2002/10/08 20:54:26  ncq
# - clean up
# - use GNU barcode via pipe
#
# Revision 1.1  2002/10/06 23:25:49  ncq
# - scan-med_docs converted to using sizers
# - prepared for becoming a GnuMed plugin
#
# Revision 1.31  2002/09/30 08:13:36  ncq
# - unify show_doc_ID
#
# Revision 1.30  2002/09/29 16:06:26  ncq
# - cleaned up config file
#
# Revision 1.29  2002/09/16 23:20:58  ncq
# - added missing _()
#
# Revision 1.28  2002/09/13 10:46:04  ncq
# - change _ to - in random ID mode
#
# Revision 1.27  2002/09/12 23:51:15  ncq
# - close last known bug on moving pages - cannot move to end of list
#
# Revision 1.26  2002/09/12 20:43:42  ncq
# - import docDocument
#
# Revision 1.25  2002/09/12 20:42:22  ncq
# - fix double scan bug
# - move call_viewer into docDocument
#
# Revision 1.24  2002/09/10 21:18:12  ncq
# - saving/displaying now works
#
# Revision 1.23  2002/09/10 17:50:26  ncq
# - try this
#
