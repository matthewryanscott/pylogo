import Tkinter
import Pmw
import threading
import reader

root = Pmw.initialise()

class IDE:
    def __init__(self, parent):
        self.incomingHistory = []
        self.historyLock = threading.Lock()
        self.parent = parent

        self.menuBar = Pmw.MainMenuBar(parent)
        parent.configure(menu=self.menuBar)
        self.menuBar.addmenu('File', '')
        self.menuBar.addmenuitem('File', 'command', label='Exit',
                                 command=self.exit)
        self.menuBar.addmenu('Help', '')
        self.menuBar.addmenuitem('Help', 'command', label='About',
                                 command=self.about)

        #self.menuFrame = Tkinter.Frame(parent)
        #self.menuFrame.pack(fill='x', side='top', expand=0)
        #self.menuFrame.tk_menuBar(self.fileMenu(), self.helpMenu())

        self.pw = Pmw.PanedWidget(parent,
                                  hull_borderwidth=1,
                                  hull_relief='sunken')
        pane = self.pw.add('canvas', size=.5)
        self.scroller = TurtleSpace(pane,
                                    canvas_width=1000,
                                    canvas_height=1000,
                                    canvas_background="white")
        self.scroller.pack(side='top', expand=1)

        pane3 = self.pw.add('history', size=.4)
        self.history = Pmw.ScrolledText(pane3,
                                        borderframe=1,
                                        vscrollmode='static',
                                        text_width=70)
        self.history.pack(side='top', expand=1)

        pane2 = self.pw.add('entry', size=.1)
        self.input = Pmw.EntryField(pane2,
                                    command=self.feedInput,
                                    entry_width=72)
        self.input.pack(side='top', expand=1)

        self.pw.pack(expand=1, fill='both')
        self.canvas = canvas = self.scroller.component('canvas')
        #item = canvas.create_arc(5, 5, 35, 35, fill='red', extent=315)
        return

    def feedInput(self):
        value = self.input.getvalue() + '\n'
        self.logoCommunicator.addInput(value)
        self.input.clear()
        self.updateHistory()
        return

    def addHistory(self, val):
        self.historyLock.acquire()
        try:
            self.incomingHistory.append(val)
        finally:
            self.historyLock.release()
        
    def updateHistory(self):
        self.historyLock.acquire()
        try:
            history = self.incomingHistory
            self.incomingHistory = []
        finally:
            self.historyLock.release()
        for line in history:
            if line.endswith('\n'):
                # @@: we shouldn't just ignore it, rather when
                # it's not present we should not append the text.
                line = line[:-1]
            self.history.appendtext(line)

    def exit(self):
        self.parent.destroy()
        return
        self.logoConnection.exit()

    def about(self):
        Pmw.aboutversion('0.2')
        Pmw.aboutcopyright('Copyright Ian Bicking 2003')
        Pmw.aboutcontact('For more information:\n  http://pylogo.org')
        about = Pmw.AboutDialog(self.parent, applicationname='PyLogo')
        
        about.show()
        
                               
        

class TurtleSpace(Pmw.ScrolledCanvas):

    def __init__(self, *args, **kw):
        Pmw.ScrolledCanvas.__init__(self, *args, **kw)


class LogoCommunicator:

    def __init__(self, app, interp):
        self.interp = interp
        self.app = app
        app.logoCommunicator = self
        interp.canvas = app.canvas
        self.pendingInput = []
        self.pendingOutput = []
        self.inputEvent = threading.Event()

    def start(self):
        self.logoThread = threading.Thread(
            target=self.interp.inputLoop,
            args=(reader.TrackingStream(self), self))
        self.logoThread.start()

    def addInput(self, value):
        if not value.endswith('\n'):
            value += '\n'
        self.pendingInput.append(value)
        self.inputEvent.set()

    def readline(self):
        while 1:
            try:
                return self.pendingInput.pop()
            except IndexError:
                self.inputEvent.clear()
                self.inputEvent.wait()

    def write(self, value):
        self.app.addHistory(value)

    def flush(self):
        pass

    name = '<ide>'

import oointerp
oointerp.install()
import interpreter

TheApp = IDE(root)
comm = LogoCommunicator(TheApp, interpreter.Logo)

comm.start()

root.mainloop()
