from wxPython.wx import *

import gmMultiColumnList

if __name__== "__main__":
	sys.path.append('./patient')
	sys.path.append('../pycommon')

#--------------------------------------------------------------------
# A class for displaying patients active problems
# This code is shit and needs fixing, here for gui development only
# TODO: almost everything
#--------------------------------------------------------------------
class ActiveProblems(wxPanel):
	def __init__(self, parent,id):
		wxPanel.__init__(
			self,
			parent,
			id,
			wxDefaultPosition,
			wxDefaultSize,
			0
		)
		activeproblemsamplelist = { 1:'1980 Hypertension',2:'1982 Acute myocardial infartion', 3:'1992 NIDDM',4: "another list"}
		sizer = wxBoxSizer(wxVERTICAL)
		#activeproblems_listbox = wxListBox(
		#	self,
		#	-1,
		#	wxDefaultPosition,
		#	wxDefaultSize,
		#	activeproblemsamplelist,
		#	wxLB_SINGLE
		#)
		activeproblems_listbox = gmMultiColumnList.MultiColumnList( self, -1)


		sizer.Add(activeproblems_listbox,100,wxEXPAND)
		activeproblems_listbox.SetBackgroundColour(wxColor(255,255,197))
		activeproblems_listbox.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		self.SetSizer(sizer)  #set the sizer 
		sizer.Fit(self)             #set to minimum size as calculated by sizer
		self.SetAutoLayout(True)                 #tell frame to use the sizer
        #self.Show(True) 
		self.list = activeproblems_listbox
		self.data = None


	


	def getListBox(self):
		return self.list

	def SetData(self, data, fitClientSize):
		self.list.SetDataItems(data, fitClientSize)
		
		
	def getLabels(self):
	#	c = self.list.GetCount()
	#	list = []
	#	for i in xrange(0, c):
	#		list.append(self.list.GetString(i) )
	#	return list	
		return ""
			
		
	def getData(self):
		return self.list.GetData()

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 100))
	app.SetWidget(ActiveProblems, -1)
	app.MainLoop()
