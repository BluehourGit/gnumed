# GnuMed form printer design study

__doc__ = """
Module to print a form using the wx toolkit.
includes dialogues for printer calibration, etc.
and new form wizard.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/handler_devel/client/wxpython/Attic/gmFormPrinter.py,v $
# $Id: gmFormPrinter.py,v 1.1 2003-02-23 04:08:03 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Ian Haywood"


from wxPython.wx import *
import string, gettext
import gmPG, gmCfg, gmLog, gmI18N
_ = lambda x: x

cache_form = 0 # cached variables to allow repeat of last form
cache_params = {}

SCRIPT = -100 # fake form ID that maps to the default prescription form
              # for this locale
PATH = -101
RADIOL = -102

class FormPrinter:

    def __init__ (self):
        self._cfg = gmCfg.gmDefCfgFile
        xos = self._cfg.get ("printer", "x_offset")
        if xos is None:
            self.printer_unset = 1
            gpsd = gmPrinterSetupDialog (self)
        else:
            self.printer_unset = 0
            self.x_off = float (xos) # in mm from paper-edge
            self.y_off = float (self._cfg.get ("printer", "y_offset")) # in mm from paper-edge
            self.x_scale = float (self._cfg.get ("printer", "x_scaling")) # no. of logical units = 1mm
            self.y_scale = float (self._cfg.get ("printer", "y_scaling")) # no. logical units  = 1mm
        self._log = gmLog.gmDefLog.Log

    def save (self):
        self._cfg.set ("printer", "x_offset", self.x_off)
        self._cfg.set ("printer", "y_offset", self.y_off)
        self._cfg.set ("printer", "x_scaling", self.x_scale)
        self._cfg.set ("printer", "y_scaling", self.x_scale)
        self._cfg.store ()
    
    def printform (id, param):
        """
        Print a form. id is the database ID of the form, params is a dictionary of
        parameters, defined by the type of form (see gmoffice.sql)
        """
        cached_form = id
        cached_params = param
        if self.printer_unset: # printer is unset, cache and return
            return
        backend = gmPG.GetConnectionPool ()
        db = backend.GetConnection('office')
        curs = db.cursor()
        if id == SCRIPT:
            curs.execute ("select length, width, fontsize from forms, papersizes where id_papersize = papersizes.id and forms.type = 's' and default") 
        elif id == PATH:
            curs.execute ("select length, width, fontsize from forms, papersizes where id_papersize = papersizes.id and forms.type = 'p' and default")
        elif id == RADIOL:
            curs.execute ("select length, width, fontsize from forms, papersizes where id_papersize = papersizes.id and forms.type = 'r' and default")
        else:
            curs.execute('select length, width, fontsize from forms, papersizes where id = %s and id_papersize = papersizes.id' % id)
        p_len, p_wid, fontsize, font = curs.fetchone()
        curs.execute('select x, y, wraparound, service, query, page from formfield, queries where id_form = %s and id_query = query.id order by page' % id)
        curr_page = 1
        # magic to set up Printer DC
        pd = wxPrintData ()
        if wxPlatform == '__WXMSW__':
            dc = wxPrinterDC (pd)
        else:
            # use PostScript
            # FIXME: how do we print under Mac??
            dc = wxPostScriptDC (pd)
        font = wxFont (fontsize, wxDEFAULT, wxNORMAL, wxNORMAL)
        dc.SetFont (font)
        dc.SetBrush (wxBLACK_BRUSH)
        dc.StartDoc ("")
        dc.StartPage ()
        for (x, y, wraparound, service, query, page) in curs.fetchall ():
            qdb = backend.GetConnection (service)
            qcurs = qdb.cursor ()
            qcurs.execute (self.subst_param (query, params))
            if page <> curr_page:
                # new page
                dc.EndPage ()
                dc.StartPage ()
                curr_page = page
            for row in qcurs.fetchall ():
                text = string.join ([str(i) for i in row], ' ')
                for line in string.split (text, '\n'): # honour \n in string
                    y = self.printtext (dc, x, y, wraparound, line)
            qcurs.close ()
            backend.ReleaseConnection (service)
        curs.close()
        dc.EndPage ()
        dc.EndDoc ()
        del dc
        

        def subst_param (query, param):
            for (name, value) in param.items ():
                query = replace (query, '$' + name, value)

        def printtext (dc, x, y, wrap, text):
            """
            Prints text, with word wrapping.
            Returns where it leaves y (the next virtual line)
            """
            w, h = dc.GetTextExtent (text)
            nextline = ""
            while w/float (self.x_scale) > wrap: # text is too wide
                text.strip ()
                # nibble from the end of text and add to nextline
                # until we encounter whitespace
                # re-calculate text width
                pos = string.rfind (text, ' ') # returns -1 if cannot find
                nextline = text[pos:] + nextline
                text = text[:pos]
                w, h = dc.GetTextExtent (text)
            px = (x+self.x_off)*self.x_scale
            py = (y+self.y_off)*self.y_scale
            dc.DrawText (px, py, text)
            y += (h/float (self.y_scale))*1.2 # advance one line, give 20% space
            # do the wrapped line if neccessary
            if len (nextline) > 0:
                y = self.printtext (dc, x, y, wrap, nextline)
            # return new y position
            return y

class gmPrinterSetupDialog (wxDialog):
    def __init__(self, formprinter):
        # begin wxGlade: __init__
        wxDialog.__init__(self, None, -1, _("Printer Setup"))
        self.formprinter = formprinter
        self.label_1 = wxStaticText(self, -1, "Horiz. Offset")
        self.horiz_off_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0)
        self.label_2 = wxStaticText(self, -1, "Vert. Offset")
        self.vert_off_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0, style=wxSP_ARROW_KEYS)
        self.label_3 = wxStaticText(self, -1, "Horiz. Scaling")
        self.horiz_scale_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0, style=wxSP_ARROW_KEYS)
        self.label_4 = wxStaticText(self, -1, "Vert. Scaling")
        self.vert_scale_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0)
        REPRINT_ID = wxNewId ()
        self.reprint_button = wxButton(self, REPRINT_ID, "Re-print")
        CALIB_ID = wxNewId ()
        self.calib_button = wxButton(self, CALIB_ID, "Re-calibrate")
        DISMISS_ID = wxNewId ()
        self.dismiss_button = wxButton(self, DISMISS_ID, "Dismiss")
        self.text_ctrl_1 = wxTextCtrl(self, -1, "You need to enter parameters so forms print properly on this printer", style=wxTE_MULTILINE|wxTE_READONLY)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        if not self.formprinter.printer_unset:
            self.horiz_off_spin.SetValue (self.formprinter.x_off)
            self.vert_off_spin.SetValue (self.formprinter.y_off)
            self.horiz_scale_spin.SetValue (self.formprinter.x_scale)
            self.vert_scale_spin.SetValue (self.formprinter.y_scale)
        else:
            self.horiz_off_spin.SetValue (0)
            self.horiz_scale_spin.SetValue (28.3)
            self.vert_off_spin.SetValue (0) # this is a sensible value on UNIX
            self.vert_scale_spin.SetValue (28.3)
        EVT_BUTTON (self, REPRINT_ID, self.OnReprint)
        EVT_BUTTON (self, CALIB_ID, self.OnRecalibrate)
        EVT_BUTTON (self, DISMISS_ID, self.OnDismiss)
        self.Show ()

    def OnDismiss (self, event):
        # load spins back into form engine
        self.formprinter.x_off = self.horiz_off_spin.GetValue ()
        self.formprinter.y_off = self.vert_off_spin.GetValue ()
        self.formprinter.x_scale = self.horiz_scale_spin.GetValue ()
        self.formprinter.y_scale = self.vert_scale_spin.GetValue ()
        self.formprinter.save ()
        self.Destroy ()

    def OnReprint (self, event):
        # load spins back into form engine
        self.formprinter.x_off = self.horiz_off_spin.GetValue ()
        self.formprinter.y_off = self.vert_off_spin.GetValue ()
        self.formprinter.x_scale = self.horiz_scale_spin.GetValue ()
        self.formprinter.y_scale = self.vert_scale_spin.GetValue ()
        self.formprinter.printer_unset = 0
        if cache_form != 0:
            self.formprinter.printform (cache_form, cache_params)

    def OnRecalibrate (self, event):
        dialog = gmCalibrationDialog ()
        pd = wxPrintData ()
        pd.SetPrinterCommand ("lpr")
        if wxPlatform == '__WXMSW__':
            dc = wxPrinterDC (pd)
        else:
            dc = wxPostScriptDC (pd)
        dc.StartDoc ("")
        dc.StartPage ()
        dc.SetBrush (wxBLACK_BRUSH)
        dc.DrawRectangle (1000, 1000, 200, 200)
        dc.DrawRectangle (2000, 2000, 200, 200)
        dc.EndPage ()
        dc.EndDoc ()
        del dc
        dialog.ShowModal ()
        x1, y1, x2, y2 = dialog.GetValues ()
        dialog.Destroy ()
        self.formprinter.x_scale = (x2-x1)/1000.0
        self.formprinter.y_scale = (y2-y1)/1000.0
        self.formprinter.x_off = x1-(x2-x1)
        self.formprinter.y_off = y1-(y2-y1)
        self.formprinter.printer_unset = 0
        self.horiz_off_spin.SetValue (self.formprinter.x_off)
        self.vert_off_spin.SetValue (self.formprinter.y_off)
        self.horiz_scale_spin.SetValue (self.formprinter.x_scale)
        self.vert_scale_spin.SetValue (self.formprinter.y_scale)
        self.formprinter.save ()

    def __set_properties(self):
        # begin wxGlade: __set_properties
        self.SetTitle("Setup Printer for Forms")
        self.vert_off_spin.SetToolTipString("Move text down (in millimetres)")
        self.horiz_scale_spin.SetToolTipString("Horizontal scaling (units per mm)")
        self.vert_scale_spin.SetToolTipString("Vertical scaling (units per mm)")
        self.reprint_button.SetToolTipString("Re-print the last printed form")
        self.calib_button.SetToolTipString("Print a table to calibrate this printer")
        self.dismiss_button.SetToolTipString("Dismiss this dialog box")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: __do_layout
        sizer_1 = wxBoxSizer(wxHORIZONTAL)
        sizer_2 = wxBoxSizer(wxVERTICAL)
        sizer_3 = wxBoxSizer(wxVERTICAL)
        sizer_7 = wxBoxSizer(wxHORIZONTAL)
        sizer_6 = wxBoxSizer(wxHORIZONTAL)
        sizer_5 = wxBoxSizer(wxHORIZONTAL)
        sizer_4 = wxBoxSizer(wxHORIZONTAL)
        sizer_4.Add(self.label_1, 0, wxALL, 10)
        sizer_4.Add(self.horiz_off_spin, 0, wxALL, 10)
        sizer_3.Add(sizer_4, 1, wxEXPAND, 0)
        sizer_5.Add(self.label_2, 0, wxALL, 10)
        sizer_5.Add(self.vert_off_spin, 0, wxALL, 10)
        sizer_3.Add(sizer_5, 1, wxEXPAND, 0)
        sizer_6.Add(self.label_3, 0, wxALL, 10)
        sizer_6.Add(self.horiz_scale_spin, 0, wxALL, 10)
        sizer_3.Add(sizer_6, 1, wxEXPAND, 0)
        sizer_7.Add(self.label_4, 0, wxALL, 10)
        sizer_7.Add(self.vert_scale_spin, 0, wxALL, 10)
        sizer_3.Add(sizer_7, 1, wxEXPAND, 0)
        sizer_1.Add(sizer_3, 1, wxEXPAND, 0)
        sizer_2.Add(self.reprint_button, 0, wxALL|wxEXPAND, 10)
        sizer_2.Add(self.calib_button, 0, wxALL|wxEXPAND, 10)
        sizer_2.Add(self.dismiss_button, 0, wxALL|wxEXPAND, 10)
        sizer_2.Add(self.text_ctrl_1, 1, wxEXPAND, 0)
        sizer_1.Add(sizer_2, 1, wxALL|wxEXPAND|wxALIGN_RIGHT, 30)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

# end of class Printer

class gmCalibrationDialog(wxDialog):
    def __init__(self):
        # begin wxGlade: __init__
        #kwds["style"] = wxDIALOG_MODAL|wxCAPTION
        wxDialog.__init__(self, None, -1, _("Calibration"))
        self.label_9 = wxStaticText(self, -1, """Calibration Page now printing.\n
Measure the position of the boxes and enter""")
        self.label_5 = wxStaticText(self, -1, "Distance of first box from top of page")
        self.first_top_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0)
        self.label_6 = wxStaticText(self, -1, "Distance of first box from left of page")
        self.first_left_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0)
        self.label_7 = wxStaticText(self, -1, "Distance of second box of top of page")
        self.sec_top_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0)
        self.label_8 = wxStaticText(self, -1, "Distance of second box from left of page")
        self.sec_left_spin = wxSpinCtrl(self, -1, min=0, max=100, initial=0)
        ID = wxNewId ()
        self.ok_button = wxButton(self, ID, "OK")
        EVT_BUTTON (self, ID, self.OnOK)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.Show ()

    def __set_properties(self):
        # begin wxGlade: __set_properties
        self.SetTitle("Calibration")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: __do_layout
        sizer_8 = wxBoxSizer(wxVERTICAL)
        grid_sizer_2 = wxFlexGridSizer(4, 2, 0, 0)
        sizer_8.Add(self.label_9, 0, wxALL|wxEXPAND, 10)
        grid_sizer_2.Add(self.label_5, 0, 0, 0)
        grid_sizer_2.Add(self.first_top_spin, 0, 0, 0)
        grid_sizer_2.Add(self.label_6, 0, 0, 0)
        grid_sizer_2.Add(self.first_left_spin, 0, 0, 0)
        grid_sizer_2.Add(self.label_7, 0, 0, 0)
        grid_sizer_2.Add(self.sec_top_spin, 0, 0, 0)
        grid_sizer_2.Add(self.label_8, 0, 0, 0)
        grid_sizer_2.Add(self.sec_left_spin, 0, 0, 0)
        grid_sizer_2.AddGrowableRow(0)
        grid_sizer_2.AddGrowableRow(1)
        grid_sizer_2.AddGrowableRow(2)
        grid_sizer_2.AddGrowableRow(3)
        grid_sizer_2.AddGrowableCol(0)
        sizer_8.Add(grid_sizer_2, 1, wxEXPAND, 0)
        sizer_8.Add(self.ok_button, 0, wxALL|wxALIGN_CENTER_HORIZONTAL, 10)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_8)
        sizer_8.Fit(self)
        self.Layout() 
        # end wxGlade

    def OnOK (self, event):
        self.Hide ()

    def GetValues (self):
        return (self.first_top_spin.GetValue (),
                self.first_left_spin.GetValue (),
                self.sec_top_spin.GetValue (),
                self.sec_left_spin.GetValue ())

# end of class gmCalibrationDialog

fp = FormPrinter ()
psd = gmPrinterSetupDialog (fp)



