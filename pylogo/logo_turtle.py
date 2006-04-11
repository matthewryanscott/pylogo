import turtle
import math
import weakref
import threading
import sys

from common import *

_allTurtles = []

class Turtle:

    _allTurtles = []

    def __init__(self):
        self.pen = turtle.Pen()
        self.pen.degrees()
        self._allTurtles.append(weakref.ref(self))

    
@logofunc(hide=True)
def cur(interp):
    return interp.get_variable('turtle')

@logofunc(aliases=['fd'], aware=True)
def forward(interp, v):
    interp.add_command(cur(interp).forward, v)
    interp.add_command(canvas.update)

@logofunc(aliases=['back', 'bk'], aware=True)
def backward(interp, v):
    interp.add_command(cur(interp).backward, v)
    interp.add_command(canvas.update)

@logofunc(aliases=['lt'], aware=True)
def left(interp, v):
    interp.add_command(cur(interp).left, v)

@logofunc(aliases=['rt'], aware=True)
def right(interp, v):
    interp.add_command(cur(interp).right, v)

@logofunc(aliases=['pu'], aware=True)
def penup(interp):
    interp.add_command(cur(interp).up)

@logofunc(aliases=['pd'], aware=True)
def pendown(interp):
    interp.add_command(cur(interp).down)

@logofunc(aware=True)
def penwidth(interp, v):
    interp.add_command(cur(interp).width, v)

@logofunc(aliases=['pc', 'color'], aware=True,
          arity=1)
def pencolor(interp, *args):
    interp.add_command(cur(interp).color, *args)

@logofunc(aliases=['ht'], aware=True)
def hideturtle(interp):
    interp.add_command(cur(interp).tracer, 0)

@logofunc(aliases=['st'], aware=True)
def showturtle(interp):
    interp.add_command(cur(interp).tracer, 1)

@logofunc(aliases=['turtleprint', 'turtlepr'],
          aware=True, arity=1)
def turtlewrite(interp, text, move=False):
    if isinstance(text, list):
        text = ' '.join(map(str, text))
    else:
        text = str(text)
    interp.add_command(cur(interp).write, text, move)
    interp.add_command(canvas.update)

@logofunc(aware=True)
def startfill(interp):
    interp.add_command(cur(interp).fill, 1)

@logofunc(aware=True)
def endfill(interp):
    interp.add_command(cur(interp).fill, 0)
    interp.add_command(canvas.update)

@logofunc(aware=True)
def setxy(interp, x, y):
    interp.add_command(cur(interp).goto, x, y)
    interp.add_command(canvas.update)

@logofunc(aware=True)
def setx(interp, x):
    t = cur(interp)
    interp.add_command(t.goto, x, t.position()[1])
    interp.add_command(canvas.update)

@logofunc(aware=True)
def sety(interp, y):
    t = cur(interp)
    interp.add_command(t.goto, t.position()[0], y)
    interp.add_command(canvas.update)

@logofunc(aware=True)
def posx(interp):
    return cur(interp).position()[0]

@logofunc(aware=True)
def posy(interp):
    return cur(interp).position()[1]

@logofunc(aware=True)
def heading(interp):
    return cur(interp).heading()

@logofunc(aware=True)
def setheading(interp, v):
    interp.add_command(cur(interp).setheading, v)

@logofunc(aware=True)
def home(interp):
    interp.add_command(cur(interp).setheading, 0)
    interp.add_command(cur(interp).goto, 0, 0)
    interp.add_command(canvas.update)

@logofunc(aliases=['cs', 'clearscreen'], aware=True)
def clear(interp):
    home(interp)
    interp.add_command(cur(interp).clear)
    interp.add_command(canvas.update)

@logofunc(aware=True, arity=1)
def distance(interp, other, orig=None):
    if orig is None:
        orig = cur(interp)
    return math.sqrt((orig.position()[0]-other.position()[0])**2 +
                     (orig.position()[1]-other.position()[1])**2)

def allturtles():
    return [t() for t in _allTurtles if t()]

def newturtle():
    global canvas
    assert canvas, "A canvas must be created before newturtle() is called"
    p = turtle.RawPen(canvas)
    p.degrees()
    _allTurtles.append(weakref.ref(p))
    return p

@logofunc(aware=True)
def tell(interp, t, block):
    interp = interp.new()
    interp.set_variable_local('turtle', t)
    return interp.eval(block)

canvas = None

@logofunc(aware=True)
def logo_turtle_main(interp):
    global canvas
    if getattr(interp, 'canvas', None):
        canvas = interp.canvas

@logofunc(aware=True)
def _newmainturtle(interp):
    turtle = newturtle()
    interp.set_variable('turtle', turtle)

class LogoTurtle:

    logo_aware = True

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
    
    @logofunc(arity=1)
    def pencolor(self, *args):
        self.pen.color(*args)
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

#def logo_turtle_main(interp):
#    pass
