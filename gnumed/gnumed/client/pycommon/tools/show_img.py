#!/usr/bin/env python
###############################################################
# This is a tool to show images from files in client/artwork/
#
# @Date: $Date: 2004-06-21 18:47:10 $
###############################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/tools/show_img.py,v $
__version__ = "$Revision: 1.1 $"
__license__ = "GPL (details at http://www.gnu.org)"
__author__ = "Sebastian Hilbert"

import cPickle, zlib, string 

from wxPython.wx import *

from Gnumed.pycommon import gmCLI

class indexPnl(wxPanel):
	def __init__(self, parent):
		wxPanel.__init__(self, parent, -1, wxDefaultPosition, wxDefaultSize)
		self.load_image()
		
	def load_image(self):
		# -- main panel -----------------------
		self.PNL_main = wxPanel(
			id = -1,
			name = 'main panel',
			parent = self,
			style = wxTAB_TRAVERSAL
		)
#		file = gmCLI.arg['--image']
		image = gmCLI.arg['--image']
#		image = string.split(file,'/')[-1][:-3]
		exec "from Gnumed.artwork import %s as image" % image
		bmp = wxBitmapFromImage(image.getImage())
		image = wxBitmapButton (
			parent = self.PNL_main,
			id = -1,
			bitmap = bmp,
			style = wxBU_EXACTFIT | wxNO_BORDER
		)
#		print bmp

if __name__ == '__main__':
	if gmCLI.has_arg('--image'):
		try:
			wxInitAllImageHandlers()
			application = wxPyWidgetTester(size=(800,600))
			application.SetWidget(indexPnl)
			application.MainLoop()
		except StandardError:
			exc = sys.exc_info()
			raise
	else: 
		print "what's wrong with you man \nname a file"

#=====================================================================
# $Log: show_img.py,v $
# Revision 1.1  2004-06-21 18:47:10  ncq
# - this shows images from artwork/ by using getImage()
#
