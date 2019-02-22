import os
import wx
import MplayerCtrl as mpc
import time
import wx.lib.buttons as buttons


class Player(wx.Frame):
    def __init__(self, parent, title, mplayer):
        super(Player, self).__init__(parent, title=title)

        self.colors = {'main': (50, 50, 50),
                       'sub': (100, 100, 100),
                       'main_fg': (255, 255, 255)}

        width, height = wx.DisplaySize()
        self.SetSize((width*.5, height*.5))
        self.SetBackgroundColour(self.colors['main'])

        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()

        # Images
        quit_image = wx.Bitmap('Images/exit.png')
        open_image = wx.Bitmap('Images/open.png')
        play_image = wx.Bitmap('Images/play.png')
        pause_image = wx.Bitmap('Images/pause.png')
        stop_image = wx.Bitmap('Images/stop.png')

        # Menus
        menubar = wx.MenuBar()
        menu = wx.Menu()
        quit_menuitem = wx.MenuItem(menu, 1, '&Quit\tCtrl+Q')
        open_menuitem = wx.MenuItem(menu, 1, '&Open Vid\tCtrl+O')

        quit_menuitem.SetBitmap(quit_image)
        open_menuitem.SetBitmap(open_image)
        menu.Append(quit_menuitem)
        menu.Append(open_menuitem)
        menubar.Append(menu, 'File')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_menuitem)
        self.Bind(wx.EVT_MENU, self.OnSelectVid, open_menuitem)

        self.main_box = wx.BoxSizer(wx.VERTICAL)
        slider_button_box = wx.BoxSizer(wx.VERTICAL)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        slider_box = wx.BoxSizer(wx.HORIZONTAL)

        # Top Toolbar -- Play / Pause / Stop

        self.mplayer = mpc.MplayerCtrl(self, -1, mplayer)
        self.playback_slider = wx.Slider(self, size=wx.DefaultSize)
        self.trackCounter = wx.StaticText(self, label="00:00")
        self.trackCounter.SetForegroundColour(self.colors['main_fg'])
        font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.trackCounter.SetFont(font)

        self.playbackTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_playback)

        toolbar = wx.ToolBar(self)
        play_tool = toolbar.AddTool(wx.ID_ANY, 'Play', play_image)
        pause_tool = toolbar.AddTool(wx.ID_ANY, 'Pause', pause_image)
        stop_tool = toolbar.AddTool(wx.ID_ANY, 'Stop', stop_image)
        toolbar.SetBackgroundColour(self.colors['sub'])
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.on_pause, pause_tool)
        self.Bind(wx.EVT_TOOL, self.on_play, play_tool)
        self.Bind(wx.EVT_TOOL, self.on_stop, stop_tool)

        wildcard = "Media Files (*.*)|*.*"
        self.file_picker = wx.FilePickerCtrl(self, message="Choose a video", wildcard=wildcard)
        self.file_picker.SetBackgroundColour(self.colors['sub'])

        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSelectVid, self.file_picker)

        slider_button_box.Add(slider_box, 1, wx.ALL | wx.EXPAND)
        button_box.Add(toolbar, 1, wx.ALL | wx.EXPAND)
        button_box.Add(self.file_picker, 0, wx.ALL | wx.EXPAND)
        slider_box.Add(self.playback_slider, 1, wx.ALL | wx.EXPAND)
        slider_box.Add(self.trackCounter, 0, wx.ALL | wx.EXPAND)
        self.main_box.Add(self.mplayer, 1, wx.ALL | wx.EXPAND)
        self.main_box.Add(slider_button_box, 0, wx.ALL | wx.EXPAND)
        self.main_box.Add(button_box, 0, wx.ALL | wx.EXPAND)
        # self.SetSizer(slider_button_box)
        # self.SetSizer(slider_box)
        self.SetSizer(self.main_box)

        # self.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
        # self.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
        # self.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
        # self.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)

        self.Layout()

    def OnQuit(self, event):
        self.Close()

    def OnSelectVid(self, event):
        path = self.file_picker.GetPath()
        trackPath = '"%s"' % path.replace("\\", "/")
        print(path)
        self.mplayer.Loadfile(trackPath)
        self.mplayer.DragAcceptFiles(self.mplayer)
        t_len = self.mplayer.GetTimeLength()
        print t_len
        self.playback_slider.SetRange(0, t_len)
        self.playbackTimer.Start(100)

    def on_pause(self, event):
        if self.playbackTimer.IsRunning():
            print "Pausing..."
            self.mplayer.Pause()
            self.playbackTimer.Stop()

    def on_play(self, event):
        if not self.playbackTimer.IsRunning():
            print "Playing..."
            self.mplayer.Pause()
            self.playbackTimer.Start()

    def on_stop(self, event):
        """"""
        print "Stopping..."
        self.mplayer.Stop()
        self.playbackTimer.Stop()

    def on_update_playback(self, event):
        """
        Updates playback slider and track counter
        """
        try:
            offset = self.mplayer.GetTimePos()
        except:
            return
        print offset
        mod_off = str(offset)[-1]
        if mod_off == '0':
            print "mod_off"
            offset = int(offset)
            self.playback_slider.SetValue(offset)
            secsPlayed = time.strftime('%M:%S', time.gmtime(offset))
            self.trackCounter.SetLabel(secsPlayed)


app = wx.App()
frame = Player(None, title='Dick Cheese Player', mplayer='Mplayer/mplayer.exe')
frame.Centre()
frame.SetIcon(wx.Icon('Images/dickcheese.ico'))
frame.Show()

app.MainLoop()
