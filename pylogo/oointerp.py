import interpreter
from types import *

class OOFrame(interpreter.Frame):

    def __init__(self, *args, **kw):
        interpreter.Frame.__init__(self, *args, **kw)
        self.actors = []

    def pushActor(self, actor):
        self.actors.insert(0, actor)

    def getVariable(self, v):
        for actor in self.actors:
            try:
                return getattr(actor, v)
            except (AttributeError, NameError):
                pass
            try:
                return actor[v]
            except (AttributeError, NameError, KeyError, IndexError,
                    TypeError, ValueError):
                pass
        return interpreter.Frame.getVariable(self, v)

    def setVariable(self, v, value):
        # We won't set member variables for now
        return interpreter.Frame.setVariable(self, v, value)
        for actor in self.actors:
            try:
                prev = getattr(actor, v)
                if not isinstance(prev, (FunctionType, ClassType,
                                         MethodType, ModuleType,
                                         BuiltinFunctionType,
                                         BuiltinMethodType)):
                    setattr(actor, v, value)
                    return
            except (AttributeError, NameError):
                pass
            try:
                actor[v] = value
                return
            except (AttributeError, NameError, KeyError, IndexError,
                    TypeError, ValueError):
                pass
        interpreter.Frame.setVariable(self, v, value)

    def getFunction(self, name):
        for actor in self.actors:
            func = getattr(actor, name, None)
            if hasattr(func, 'logoAware'):
                return func
            if isinstance(func, (FunctionType, MethodType)):
                return func
        return interpreter.Frame.getFunction(self, name)

def tell(interp, obj, block):
    interp = interp.new()
    interp.pushActor(obj)
    interp.eval(block)
tell.logoAware = True

def install():
    interpreter.Logo.Frame = OOFrame
    interpreter.Logo.importFunction(tell)

class Writer(object):

    def __init__(self, output):
        self.output = output

    def pr(self, *args):
        pass
    
