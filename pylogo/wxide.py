from wxPython.wx import *

ID_ABOUT = 101
ID_EXIT = 102

class MainFrame(wxFrame):
    def __init__(self, parent, ID, title):
        wxFrame.__init__(self, parent, ID, title,
                         wxDefaultPosition,
                         wxSize(200, 150))

        self.CreateStatusBar()
        fileMenu = wxMenu()
        fileMenu.Append(ID_EXIT, "E&xit", "Terminate the program")
        helpMenu = wxMenu()
        helpMenu.Append(ID_ABOUT, "&About",
                        "More information about this program")
        menuBar = wxMenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)
        EVT_MENU(self, ID_ABOUT, self.OnAbout)
        EVT_MENU(self, ID_EXIT, self.TimeToQuit)

        self.sizer = wxBoxSizer(wxVERTICAL)
        self.control1 = wxTextCtrl(self, 1, style=wxTE_MULTILINE)
        self.control2 = wxTextCtrl(self, 1, style=wxTE_MULTILINE)
        self.sizer.Add(self.control1, 3, wxEXPAND)
        self.sizer.Add(self.control2, 1, wxEXPAND)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Show(1)
        

    def OnAbout(self, event):
        dlg = wxMessageDialog(self, "This sample program shows off\n"
                              "frames, menus, statusbars, and this\n"
                              "message dialog.",
                              "About Me", wxOK | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def TimeToQuit(self, event):
        self.Close(true)
        


class IDE(wxApp):
    def OnInit(self):
        frame = MainFrame(NULL, -1, "Hello from Logo!")
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app = IDE(0)
app.MainLoop()
