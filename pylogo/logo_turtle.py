import turtle
import math
import weakref
import threading
import sys
try:
    from pylogo.tkthread import addQueue
except ImportError:
    from src.tkthread import addQueue

_allTurtles = []

def cur(interp):
    return interp.getVariable('turtle')
cur.logoHide = True

def setup(func, *aliases, **kw):
    func.logoAware = True
    for name, value in kw.items():
        setattr(func, name, value)
    func.aliases = aliases
setup.logoHide = True

def forward(interp, v):
    addQueue(cur(interp).forward, v)
    addQueue(canvas.update)
setup(forward, 'fd')

def backward(interp, v):
    addQueue(cur(interp).backward, v)
    addQueue(canvas.update)
setup(backward, 'back', 'bk')

def left(interp, v):
    addQueue(cur(interp).left, v)
setup(left, 'lt')

def right(interp, v):
    addQueue(cur(interp).right, v)
setup(right, 'rt')

def penup(interp):
    addQueue(cur(interp).up)
setup(penup, 'pu', 'penup')

def pendown(interp):
    addQueue(cur(interp).down)
setup(pendown, 'pd', 'pendown')

def penwidth(interp, v):
    addQueue(cur(interp).width, v)
setup(penwidth)

def pencolor(interp, *args):
    addQueue(cur(interp).color, *args)
setup(pencolor, 'pc', 'color', arity=1)

def hideturtle(interp):
    addQueue(cur(interp).tracer, 0)
setup(hideturtle, 'ht')

def showturtle(interp):
    addQueue(cur(interp).tracer, 1)
setup(showturtle, 'st')


def turtlewrite(interp, text, move=False):
    if isinstance(text, list):
        text = ' '.join(map(str, text))
    else:
        text = str(text)
    addQueue(cur(interp).write, text, move)
    addQueue(canvas.update)
setup(turtlewrite, 'turtleprint', 'turtlepr', arity=1)

def startfill(interp):
    addQueue(cur(interp).fill, 1)
setup(startfill)

def endfill(interp):
    addQueue(cur(interp).fill, 0)
    addQueue(canvas.update)
setup(endfill)

def setxy(interp, x, y):
    addQueue(cur(interp).goto, x, y)
    addQueue(canvas.update)
setup(setxy)

def setx(interp, x):
    t = cur(interp)
    addQueue(t.goto, x, t.position()[1])
    addQueue(canvas.update)
setup(setx)

def sety(interp, y):
    t = cur(interp)
    addQueue(t.goto, t.position()[0], y)
    addQueue(canvas.update)
setup(sety)

def posx(interp):
    return cur(interp).position()[0]
setup(posx)

def posy(interp):
    return cur(interp).position()[1]
setup(posy)

def heading(interp):
    return cur(interp).heading()
setup(heading)

def setheading(interp, v):
    addQueue(cur(interp).setheading, v)
setup(setheading)

def home(interp):
    addQueue(cur(interp).setheading, 0)
    addQueue(cur(interp).goto, 0, 0)
    addQueue(canvas.update)
setup(home)

def clear(interp):
    home(inter)
    addQueue(cur(interp).clear)
    addQueue(canvas.update)
setup(clear, 'cs', 'clearscreen')

def distance(interp, other, orig=None):
    if orig is None:
        orig = cur(interp)
    return math.sqrt((orig.position()[0]-other.position()[0])**2 +
                     (orig.position()[1]-other.position()[1])**2)
setup(distance, arity=1)

def allturtles():
    return [t() for t in _allTurtles if t()]

def newturtle():
    p = turtle.Pen()
    p.degrees()
    _allTurtles.append(weakref.ref(p))
    return p

def tell(interp, t, block):
    interp = interp.new()
    interp.setVariableLocal('turtle', t)
    return interp.eval(block)
setup(tell)

canvas = None

def logo_turtle_main(interp):
    global canvas
    turtle = newturtle()
    interp.setVariable('turtle', turtle)
    canvas = turtle._canvas

class LogoTurtle:

    logoAware = True

    def __init__(self, interp):
        self.logo = interp
        self.canvas = interp.canvas
        self.pen = turtle.RawPen(self.canvas)
        self.q = interp.communicator

    def forward(self, v):
        self.q.do(self.pen.forward, v)
        self.q.do(self.canvas.update)
    fd = forward

    def backward(self, v):
        self.q.do(self.pen.backward, v)
        self.q.do(self.canvas.update)
    bk = backward

    def left(self, v):
        self.q.do(self.pen.left, v)
    lt = left

    def right(self, v):
        self.q.do(self.pen.right, v)
    rt = right

    def penup(self):
        self.pen.up()
    pu = penup

    def pendown(self):
        self.pen.down()
    pd = pendown

    def penwidth(self, v):
        self.pen.width(v)
    
    def pencolor(self, *args):
        self.pen.color(*args)
    pencolor.arity = 1
    color = pencolor
    pc = pencolor

    def hideturtle(self):
        self.pen.tracer(0)
    ht = hideturtle

    def showturtle(self):
        self.pen.tracer(1)
    st = showturtle

    def turtlewrite(text, move=False):
        if isinstance(text, list):
            text = ' '.join(map(str, text))
        else:
            text = str(text)
        self.q.do(self.pen.write, text, move)
        self.q.do(self.canvas.update)
    turtleprint = turtlewrite
    turtlepr = turtlewrite

    def startfill(self):
        self.pen.fill(1)

    def endfill(self):
        self.q.do(self.pen.fill, 0)
        self.q.do(self.canvas.update)

    def setxy(self, x, y):
        self.q.do(self.pen.goto, x, y)
        self.q.do(self.canvas.update)

    def setx(self, x):
        self.setxy(x, self.posy())

    def sety(self, y):
        self.setxy(self.posx(), y)

    def posx(self):
        return self.pen.position()[0]

    def posy(self):
        return self.pen.position()[1]

    def heading(self):
        return self.pen.heading()

    def setheading(self, v):
        self.q.do(self.pen.setheading, v)

    def home(self):
        self.setheading(0)
        self.setxy(0, 0)

    def clear(self):
        self.home()
        self.q.do(self.pen.clear)
        self.q.do(self.canvas.update)
    cs = clear
    clearscreen = clear

    def distance(self, other):
        return math.sqrt((self.position()[0]-other.position()[0])**2 +
                         (self.position()[1]-other.position()[1])**2)

def logo_turtle_main(interp):
    pass
