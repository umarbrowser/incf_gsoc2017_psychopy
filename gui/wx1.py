import wx

app = wx.App()
win = wx.Frame(None, title='simple incf hello', size=(300,200))
panel = wx.Panel(win)
label = wx.StaticText(panel,label='Hello developer',pos=(100,50))
win.Show(True)
app.MainLoop()
