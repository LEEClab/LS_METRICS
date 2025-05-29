import wx
import wx.lib.scrolledpanel as scrolled

class TestPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        vbox = wx.BoxSizer(wx.HORIZONTAL)

        desc = wx.StaticText(self, -1, '')

        desc.SetForegroundColour("Blue")
        vbox.Add(desc, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(wx.StaticLine(self, -1, size=(1024, -1)), 0, wx.ALL, 5)
        vbox.Add((20, 20))

        self.SetSizer(vbox)
        self.SetupScrolling()


app = wx.App(0)
frame = wx.Frame(None, wx.ID_ANY)
fa = TestPanel(frame)
frame.Show()
app.MainLoop()