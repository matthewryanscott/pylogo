import Tkinter
import Pmw
import threading
import reader
from Queue import Queue, Empty

root = Pmw.initialise()

class IDE:
    def __init__(self, parent):
        self.incomingHistory = Queue()
        self.incomingCommands = Queue()
        self.parent = parent

        self.menuBar = Pmw.MainMenuBar(parent)
        parent.configure(menu=self.menuBar)
        self.menuBar.addmenu('File', '')
        self.menuBar.addmenuitem('File', 'command', label='Exit',
                                 command=self.exit)
        self.parent.protocol('WM_DELETE_WINDOW', self.exit)
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
        self.updateCommands()
        return

    def addHistory(self, val):
        # This should actually put some event in place, so that the
        # main thread knows it should try to update the history when
        # it has the chance.
        self.incomingHistory.put(val)
        
    def updateHistory(self):
        history = []
        while 1:
            try:
                history.append(self.incomingHistory.get_nowait())
            except Empty:
                break
        for line in history:
            if line.endswith('\n') and 0:
                # @@: we shouldn't just ignore it, rather when
                # it's not present we should not append the text.
                # (or put it back on the history)
                line = line[:-1]
            self.history.appendtext(line)

    def exit(self):
        print "Exiting!"
        self.parent.destroy()
        self.logoCommunicator.exit()
        return

    def about(self):
        Pmw.aboutversion('0.2')
        Pmw.aboutcopyright('Copyright Ian Bicking 2003')
        Pmw.aboutcontact('For more information:\n  http://pylogo.org')
        about = Pmw.AboutDialog(self.parent, applicationname='PyLogo')
        about.show()

    def updateCommands(self):
        while 1:
            try:
                command = self.incomingCommands.get_nowait()
            except Empty:
                return
            if command == 'quit':
                self.exit()
            try:
                val = command[1](*command[2], **command[3])
            except Exception, e:
                if command[0]:
                    command[0].put([True, e])
            else:
                if command[0]:
                    command[0].put([False, val])

    def runCommand(self, func, *args, **kw):
        if kw.has_key('_nowait'):
            nowait = kw['_nowait']
            del kw['_nowait']
        else:
            nowait = 0
        if nowait:
            out = None
        else:
            out = Queue(1)
        self.incomingCommands.put((out, func, args, kw))
        if out:
            error, result = out.get()
            if error:
                raise result
            else:
                return result

    def addCommand(self, func, *args, **kw):
        kw['_nowait'] = 1
        return self.runCommand(func, *args, **kw)

class TurtleSpace(Pmw.ScrolledCanvas):

    def __init__(self, *args, **kw):
        Pmw.ScrolledCanvas.__init__(self, *args, **kw)


class LogoCommunicator:

    def __init__(self, app, interp):
        self.interp = interp
        self.app = app
        app.logoCommunicator = self
        interp.canvas = app.canvas
        interp.app = app
        self.pendingInput = Queue()
        self.pendingOutput = Queue()
        self.inputEvent = threading.Event()

    def start(self):
        self.logoThread = threading.Thread(
            target=self.interp.inputLoop,
            args=(reader.TrackingStream(self), self))
        self.logoThread.start()

    def exit(self):
        self.addInput('bye\n')

    def addInput(self, value):
        if not value.endswith('\n'):
            value += '\n'
        self.app.addHistory(value)
        self.pendingInput.put(value)
        self.inputEvent.set()

    def readline(self):
        result = self.pendingInput.get()
        return result

    def write(self, value):
        self.app.addHistory(value)

    def flush(self):
        pass

    name = '<ide>'

#import oointerp
#oointerp.install()
import interpreter

if __name__ == '__main__':

    TheApp = IDE(root)
    TheApp.input.component('entry').focus_force()
    comm = LogoCommunicator(TheApp, interpreter.Logo)
    import sys
    sys.stdout = comm
    import logo_turtle
    logo_turtle.logo_turtle_main(interpreter.Logo)
    logo_turtle._newmainturtle(interpreter.Logo)
    
    comm.start()
    
    root.mainloop()
