import interpreter
from types import *

class OOFrame(interpreter.Frame):

    def __init__(self, *args, **kw):
        interpreter.Frame.__init__(self, *args, **kw)
        self.actors = []

    def push_actor(self, actor):
        self.actors.insert(0, actor)

    def get_variable(self, v):
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
        return interpreter.Frame.get_variable(self, v)

    def set_variable(self, v, value):
        # We won't set member variables for now
        return interpreter.Frame.set_variable(self, v, value)
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
        interpreter.Frame.set_variable(self, v, value)

    def get_function(self, name):
        for actor in self.actors:
            func = getattr(actor, name, None)
            if hasattr(func, 'logo_aware'):
                return func
            if isinstance(func, (FunctionType, MethodType)):
                return func
        return interpreter.Frame.get_function(self, name)

@logofunc(aware=True)
def tell(interp, obj, block):
    interp = interp.new()
    interp.push_actor(obj)
    interp.eval(block)

def install():
    interpreter.Logo.Frame = OOFrame
    interpreter.Logo.import_function(tell)

class Writer(object):

    def __init__(self, output):
        self.output = output

    def pr(self, *args):
        pass
    
