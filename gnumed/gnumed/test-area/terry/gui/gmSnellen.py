#!/usr/bin/python

# Tool to emulate a Snellen chart onscreen
# author: Ian Haywood
# licence: GPL
# Changelog:
# 21/6/02: inital version




from wxPython.wx import *
import gmPlugin
import math
import random
import gettext
_ = gettext.gettext

ID_SNELLENMENU = wxNewId ()


class SnellenChart (wxFrame):
    def convert (self, X,Y):
        """
        Converts a pair of co-ordinates from block co-ords to real.
        startX, startY  -- define top-left corner of current character
        """
        if self.mirror:
            X = 5-X
        return wxPoint ((X*self.blockX)+self.startX, (Y*self.blockY)+self.startY)

    def rect (self, x1, y1, x2, y2):
        """
        Draw a rectangle
        """
        x1, y1 = self.convert (x1, y1)
        x2, y2 = self.convert (x2, y2)
        width = x2 - x1
        if width < 0:
            width = -width
            x = x2
        else:
            x = x1
        height = y2 - y1
        if height < 0:
            height = -height
            y = y2
        else:
            y = y1
        self.dc.DrawRectangle (x, y, width, height)

    def straight (self, x1, y1, x2, y2, width = 1):
        """
        Draws straight descending letter-stroke, (x1, y1) is top-left,
        (x2, y2) is bottom left point
        """
        
        list = [self.convert (x1, y1), self.convert (x1+width, y1),
        self.convert (x2+width, y2), self.convert (x2, y2)]
        self.dc.DrawPolygon (list)

    def reverse (self):
        """
        Swap fore- and background pens
        """
        background = self.dc.GetBackground ()
        foreground = self.dc.GetBrush ()
        self.dc.SetBrush (background)
        self.dc.SetBackground (foreground)
        

    def arc (self, x, y, arm, start, end):
        """
        Draws an arc-stroke, 1 unit wide, subtending (x, y), the outer
        distance is arm, between start and end angle
        """
        topx, topy = self.convert (x-arm, y-arm)
        botx, boty = self.convert (x+arm, y+arm)
        width = botx - topx
        if width < 0:
            width = -width
            t = botx
            botx = topx
            topx = t
        height = boty - topy
        self.dc.DrawEllipticArc(topx, topy, width, height, start, end)
        # now do wedge as background, to give arc pen-stroke
        arm -= 1
        self.reverse ()
        topx, topy = self.convert (x-arm, y-arm)
        botx, boty = self.convert (x+arm, y+arm)
        width = botx - topx
        if width < 0:
            width = -width
            t = botx
            botx = topx
            topx = t
        height = boty- topy
        self.dc.DrawEllipticArc(topx, topy, width, height, start, end)
        self.reverse ()

    def O (self):
        """
        Draws the letter O
        """
        self.arc (2.5, 2.5, 2.5, 0, 360)

    def Q (self):
        self.O ()
        self.straight (2.6, 3, 4, 5)

    def C (self):
        if self.mirror:
            self.arc (2.5, 2.5, 2.5, 140, -140)
        else:
            self.arc (2.5, 2.5, 2.5, 40, 320)

    def G (self):
        if self.mirror:
            self.arc (2.5, 2.5, 2.5, 140, -150)
        else:
            self.arc (2.5, 2.5, 2.5, 40, 330)
        self.rect (2.5, 2.7, 5, 3.7)
        self.rect (4, 2.7, 5, 5)

    def W (self):
        self.straight (0, 0, 1, 5)
        self.straight (2, 0, 1, 5)
        self.straight (2, 0, 3, 5)
        self.straight (4, 0, 3, 5)

    def V (self):
        self.straight (0, 0, 2, 5)
        self.straight (4, 0, 2, 5)

    def T (self):
        self.rect (0, 0, 5, 1)
        self.rect (2, 1, 3, 5)

    def I (self):
        self.rect (2, 0, 3, 5)

    def A (self):
        self.straight (2, 0, 0, 5)
        self.straight (2, 0, 4, 5)
        self.rect (1.4, 2.5, 3.6, 3.5)

    def F (self):
        self.rect (0, 0, 1, 5)
        self.rect (1, 0, 5, 1)
        self.rect (1, 2, 5, 3)

    def E (self):
        self.rect (0, 0, 1, 5)
        self.rect (0, 0, 5, 1)
        self.rect (0, 2, 5, 3)
        self.rect (0, 4, 5, 5)

    def BackE (self):
        self.rect (4, 0, 5, 5)
        self.rect (0, 0, 5, 1)
        self.rect (0, 2, 5, 3)
        self.rect (0, 4, 5, 5)

    def UpE (self):
        self.rect (0, 4, 5, 5)
        self.rect (0, 0, 1, 5)
        self.rect (2, 0, 3, 5)
        self.rect (4, 0, 5, 5)

    def DownE (self):
        self.rect (0, 0, 5, 1)
        self.rect (0, 0, 1, 5)
        self.rect (2, 0, 3, 5)
        self.rect (4, 0, 5, 5)

    def H (self):
        self.rect (0, 0, 1, 5)
        self.rect (4, 0, 5, 5)
        self.rect (1, 2, 4, 3)

    def K (self):
        self.rect (0, 0, 1, 5)
        self.straight (3.5, 0, 0.5, 2.5, width = 1.5)
        self.straight (0.5, 2.5, 3.5, 5, width = 1.5)

    def L (self):
        self.rect (0, 0, 1, 5)
        self.rect (1, 4, 5, 5)

    def Z (self):
        self.rect (0, 0, 5, 1)
        self.rect (0, 4, 5, 5)
        self.straight (3.5, 1, 0, 4, width = 1.5)

    def X (self):
        self.straight (4, 0, 0, 5)
        self.straight (0, 0, 4, 5)

    def NM (self):
        """
        Sidebars common to N and M
        """
        self.rect (0, 0, 1, 5)
        self.rect (4, 0, 5, 5)

    def N (self):
        self.NM ()
        self.straight (0, 0, 4, 5)

    def BackN (self):
        self.NM ()
        self.straight (4, 0, 0, 5)

    def M (self):
        self.NM ()
        self.straight (0, 0, 2, 5)
        self.straight (4, 0, 2, 5)

    def gamma (self):
        self.rect (0, 0, 5, 1)
        self.rect (0, 0, 1, 5)

    def delta (self):
        self.straight (2, 0, 0, 5)
        self.straight (2, 0, 4, 5)
        self.rect (0.5, 4, 4.5, 5)

    def pi (self):
        self.rect (0, 0, 5, 1)
        self.rect (0, 0, 1, 5)
        self.rect (4, 0, 5, 5)

    def cross (self):
        self.rect (2, 0, 3, 5)
        self.rect (0, 2, 5, 3)

    def star (self):
        """
        Star of 5 points
        """
        n = 5 # can change here
        list = []
        for i in xrange (0, n):
            theta = (i+0.00001)/n*2*math.pi # points on a circle inside the 5x5 grid
            x = 2.5 + 2.5*math.sin (theta)
            y = 2.5 - 2.5*math.cos (theta)
            list.append (self.convert (x, y)) # add point to list
            theta = (i+0.5)/n*2*math.pi
            x = 2.5 + math.sin (theta)
            y = 2.5 - math.cos (theta)
            list.append (self.convert (x, y)) 
        self.dc.DrawPolygon (list, fill_style = wxWINDING_RULE)

    latin = [A, C,
             C, E, F, G,
             H, I, K, L, M,
             N, O, Q, T, V,
             W, X, Z]

    fourE = [E, UpE, DownE, BackE]
    greek = [A, gamma, delta, E,
             Z, H, I, K, M,
             N, O, pi, T, X]
    cyrillic = [A, delta, E, BackN,
               K, M, H, O, pi,
               T, C, X]
    symbol = [O, cross, star]
    alphabets = {_("Latin"):latin, _("Greek"):greek,
                 _("Cyrillic"):cyrillic, _("Four Es"):fourE,
                 _("Symbol"):symbol}


    def set_distance (self, n):
        """
        Sets standard viewing distance, against which patient is
        compared. n is an index to the list self.distances
        """
        self.distance = n
        # Snellen characters are the smallest readable characters by
        # an average person at the stated distance. They are defined
        # exactly as being in a box which subtends 5' of an arc on the
        # patient's eye, each stroke subtending 1' of arc
        one_minute = (math.pi/180)/60
        blocksize = self.distances[n]*100*math.atan(one_minute) # in cm
        # convert to pixels
        self.blockX = int (blocksize/self.sizeX*self.screen_x)
        self.blockY = int (blocksize/self.sizeY*self.screen_y)
        # how many characters can we fit now?
        chars = int (self.screen_x / (self.blockX*5)) - 1
        if chars < 1:
            chars = 1
        if chars > 7:
            chars = 7
        if chars < len (self.alphabet):
            self.choices = []
            while len (self.choices) < chars:
                c = random.choice (self.alphabet)
                if not c in self.choices:
                    self.choices.append (c)
        else:
            self.choices = [random.choice (self.alphabet) for i in
                            range (1, chars)]
        self.spacing = int ((self.screen_x -
        (chars*self.blockX*5))/(chars+1))
        if self.spacing < 0:
            self.spacing = 0
        self.startY = int ((self.screen_y-(self.blockY*5))/2)

    def draw (self):
        """
        displays characters in the centre of the screen from the
        selected alphabet
        """

        # clear the screen
        self.reverse ()
        self.dc.DrawRectangle (0,0, self.screen_x, self.screen_y)
        self.reverse ()
        # draw size
        self.dc.DrawText (str(self.distances[self.distance]), 20, 20)
        self.startX = self.spacing
        for i in self.choices:
            i (self)
            self.startX += self.blockX*5
            self.startX += self.spacing


    def setup_DC (self):
        self.dc.SetFont (wxFont (36, wxROMAN, wxNORMAL, wxNORMAL))
        self.dc.SetBrush (wxBLACK_BRUSH)
        self.dc.SetBackground (wxWHITE_BRUSH)
        self.dc.SetPen (wxTRANSPARENT_PEN)


    def OnPaint (self, event):
        self.dc = wxPaintDC (self)
        self.setup_DC ()
        self.draw ()
        self.dc = None 

    def OnKeyUp (self, key):
        if key.GetKeyCode () == WXK_UP and self.distance < len (self.distances)-1:
            self.set_distance (self.distance+1)
        if key.GetKeyCode () == WXK_DOWN and self.distance > 0:
            self.set_distance (self.distance-1)
        if key.GetKeyCode () == WXK_ESCAPE:
            self.Destroy ()

    def OnLeftDown (self, key):
        if self.distance > 0:
            self.set_distance (self.distance-1)
        self.Refresh ()

    def OnRightDown (self, key):
        if self.distance < len(self.distances)-1:
            self.set_distance (self.distance+1)
        self.Refresh ()

    def OnDClick (self, key):
        self.Destroy ()
        
    def OnClose (self, event):
        self.Destroy ()
   
    def __init__(self, sizeX, sizeY,
                 alpha = symbol, mirr = 0):
        """
        Initialise. sizeX and sizeY define the physical size of the
        CRT in cm.
        """
        wxFrame.__init__ (self, NULL, -1, _("Snellen Chart"))
        EVT_CLOSE (self, self.OnClose)
        # sizeX/Y is screen size (X/Y in cm)
        # distance is distance in metres between CRT and the "average" patient
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.distances = [3, 5, 6, 7.5, 9, 12, 15, 18, 24, 30, 48, 60]
        self.mirror = mirr
        self.alphabet = alpha
        EVT_KEY_DOWN (self, self.OnKeyUp)
        EVT_LEFT_UP (self, self.OnLeftDown)
        EVT_RIGHT_UP (self, self.OnRightDown)
        EVT_LEFT_DCLICK (self, self.OnDClick)
        EVT_PAINT (self, self.OnPaint)
        self.ShowFullScreen (1)
        self.screen_x, self.screen_y = self.GetClientSizeTuple ()
        self.set_distance (2)
        screensizes = {_("14 inch"):(28, 21), _("16 inch"):(30, 23)}

class SnellenDialogue (wxDialog):
    """
    Dialogue class to get Snellen chart settings.
    """
    
    def __init__ (self, parent):
        wxDialog.__init__(self, parent, -1, _("Snellen Chart Setup"),
                      wxDefaultPosition, wxSize(350, 200))
        vbox = wxBoxSizer (wxVERTICAL)
        hbox1 = wxBoxSizer (wxHORIZONTAL)
        hbox1.Add (wxStaticText(self, -1, _("Screen Height (cm): ")), 0, wxALL, 15)
        self.sizeY_ctrl = wxSpinCtrl (self, -1, value = "25", min = 10, max = 100)
        hbox1.Add (self.sizeY_ctrl, 1, wxTOP, 15)
        vbox.Add (hbox1, 1, wxEXPAND)
        hbox2 = wxBoxSizer (wxHORIZONTAL)
        hbox2.Add (wxStaticText(self, -1, _("Screen Width (cm): ")), 0, wxALL, 15)
        self.sizeX_ctrl = wxSpinCtrl (self, -1, value = "30", min = 10, max = 100)
        hbox2.Add (self.sizeX_ctrl, 1, wxTOP, 15)
        vbox.Add (hbox2, 1, wxEXPAND)
        hbox3 = wxBoxSizer (wxHORIZONTAL)
        hbox3.Add (wxStaticText(self, -1, _("Alphabet: ")), 0, wxALL, 15)
        self.alpha_ctrl = wxChoice (self, -1, choices=SnellenChart.alphabets.keys ())
        hbox3.Add (self.alpha_ctrl, 1, wxTOP, 15)
        vbox.Add (hbox3, 1, wxEXPAND)
        self.mirror_ctrl = wxCheckBox (self, -1, label = _("Mirror"))
        vbox.Add (self.mirror_ctrl, 0, wxALL, 15)
        vbox.Add (wxStaticText (self, -1,
_("""Control Snellen chart using mouse:
left-click increases text
right-click decreases text
double-click ends""")), 0, wxALL, 15)
        hbox5 = wxBoxSizer (wxHORIZONTAL)
        ok = wxButton(self, wxID_OK, _(" OK "), size=wxDefaultSize)
        cancel = wxButton (self, wxID_CANCEL, _(" Cancel "),
                           size=wxDefaultSize)
        hbox5.Add (ok, 1, wxTOP, 15)
        hbox5.Add (cancel, 1, wxTOP, 15)
        vbox.Add (hbox5, 1, wxEXPAND)
        self.SetSizer (vbox)
        self.SetAutoLayout (1)
        vbox.Fit (self)

        EVT_BUTTON (ok, wxID_OK, self.OnOK)
        EVT_BUTTON (cancel, wxID_CANCEL, self.OnCancel)
        EVT_CLOSE (self, self.OnClose )
        self.Show(1)

    def OnClose (self, event):
        self.Destroy ()

    def OnCancel (self, event):
        self.Destroy ()

    def OnOK (self, event):
        if self.Validate () and self.TransferDataFromWindow ():
            selected_alpha_string = self.alpha_ctrl.GetStringSelection ()
            if selected_alpha_string is None or len (selected_alpha_string) < 2:
                alpha = SnellenChart.latin
            else:
                alpha = SnellenChart.alphabets[selected_alpha_string]
            sizeY = self.sizeY_ctrl.GetValue ()
            sizeX = self.sizeX_ctrl.GetValue ()
            frame = SnellenChart (sizeX, sizeY, alpha
        = alpha, mirr = self.mirror_ctrl.GetValue ())
            frame.Show (1)
            self.Destroy ()




class gmSnellen (gmPlugin.wxBasePlugin):
    def name (self):
        return 'SnellenPlugin'

    def register (self):
        menu = self.gb['main.toolsmenu']
        menu.Append (ID_SNELLENMENU, "Snellen", "Snellen Chart")
        EVT_MENU (self.gb['main.frame'], ID_SNELLENMENU, self.OnSnellenTool)
        
    def OnSnellenTool (self, event):
        frame = SnellenDialogue (self.gb['main.frame'])
        frame.Show (1)
    

if __name__ == '__main__':
    class TestApp (wxApp):
        def OnInit (self):
            frame = SnellenDialogue (None)
            frame.Show (1)
            return 1

    def main ():
        gettext.textdomain ('gnumed')
        app = TestApp ()
        app.MainLoop ()

    main ()  
    






