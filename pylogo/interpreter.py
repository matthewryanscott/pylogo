"""
interpreter for pylogo
  Ian Bicking <ianb@colorstudy.com>

A Logo interpreter.
"""


from types import *
from pylogo import reader
import inspect, os, sys
from pylogo.common import *
import imp

class Interpreter:
    """
    The interpreter gets tokens (from a reader.TrackingStream) and
    runs them.  It holds the namespace, which is dynamically scoped.  
    
    You execute one expression by calling interpreter.expr(tokenizer),
    where tokenizer may be reader.TrackingStream or other tokenizer
    instance.  It returns the value of the expression.

    The RootFrame and Frame subclasses implement the namespace
    operations (this class is abstract).
    """

    special_forms = {}
    "Methods register themselves using this dictionary"

    def special(name, special_forms=special_forms):
        def decorator(func):
            special_forms[name] = func
            return func
        return decorator

    def __init__(self, tokenizer=None):
        self.tokenizers = []
        if tokenizer is not None:
            self.tokenizers.append(tokenizer)

    def tokenizer__get(self):
        """
        Gets the current tokenizer.
        """
        return self.tokenizers[-1]
    tokenizer = property(tokenizer__get)

    def push_tokenizer(self, tokenizer):
        """
        You can stack up multiple tokenizers, as the interpreter goes
        from evaluating a file to a list to a sublist, etc.  New
        interpreters are created for a new scope.
        """
        #print "Pushing %r onto %r" % (tokenizer, self)
        self.tokenizers.append(tokenizer)

    def pop_tokenizer(self):
        #print "Popping %r from %r" % (self.tokenizers[-1], self)
        self.tokenizers.pop()

    def expr(self):
        """
        Top level expression-getter/evaluator (see also expr_top).
        """
        try:
            val = self.expr_without_error()
        except LogoError, e:
            # This is used for creating the traceback
            e.set_frame(self)
            raise
        except (LogoControl, SystemExit, KeyboardInterrupt,
                StopIteration):
            # These exceptions are mostly harmless
            raise
        except Exception, e:
            # Here we wrap other exceptions... this needs some work
            import traceback
            traceback.print_exc()
            # @@: should add the exception traceback to this somehow
            newExc = LogoError(str(e), description=str(e))
            newExc.set_frame(self)
            raise newExc
        return val

    def expr_top(self):
        """
        Unlike expr(), this ignores empty lines; should only be used
        in top-level expressions (including expressions taken from
        lists).
        """
        try:
            p = self.tokenizer.peek()
        except StopIteration:
            p = None
        if p == '\n':
            self.tokenizer.next()
            return None
        elif p == ';':
            while 1:
                p = self.tokenizer.next()
                if p == '\n':
                    break
            return None
        elif p is EOF:
            return EOF
        return self.expr()

    def expr_without_error(self):
        """
        Get a full expression from the tokenizer, execute it, and
        return the value.
        
        expr ::= exprInner <operator> exprInner
             ::= exprInner
        """
        while 1:
            # Strip out any comments:
            # (typically the reader would do this, but we do it more
            # lazily so we can get the comments if we want them)
            p = self.tokenizer.peek()
            if p == ';':
                while 1:
                    p = self.tokenizer.next()
                    if p == '\n':
                        break
            else:
                break
        val = self.expr_inner()
        while 1:
            # Check if there's any infix operators:
            p = self.tokenizer.peek()
            if p not in ['/', '*', '+', '-', '>', '<', '=',
                         '>=', '=>', '<=', '=<', '<>']:
                break
            self.tokenizer.next()
            e = self.expr_inner()
            # @@: no order of precedence
            if p == '/':
                val = float(val) / e
            elif p == '*':
                val *= e
            elif p == '-':
                val -= e
            elif p == '+':
                val += e
            elif p == '<':
                val = val < e
            elif p == '>':
                val = val > e
            elif p == '=':
                val = val == e
            elif p == '>=' or p == '=>':
                val = val >= e
            elif p == '<=' or p == '=<':
                val = val <= e
            elif p == '<>':
                val = val != e
            else:
                assert 0, "Unknown symbol: %s" % p
        return val


    def expr_inner(self):
        """
        An 'inner' expression, an expression that does not include
        infix operators.

        exprInner ::= <literal int or float>
                  ::= '-' expr
                  ::= '+' expr
                  ::= ('\"' or 'QUOTE') <word>
                  ::= ':' <word>
                  ::= MAKE (':' or '\"') <word> expr
                  ::= MAKE <word> expr
                  ::= TO <to expression>
                  ::= '[' <list expression> ']'
                  ::= '(' <word> <expr> ... <expr> ')'
                  ::= <word> <expr> ... <expr>

        Things to note:
        * ``MAKE :x 10``, ``MAKE \"x 10``, and ``MAKE x 10`` all work
          equivalently (make is a special form, unlike in UCBLogo).
        * <list expression> is a nested list of tokens.
        * <to expression> is TO func_name var1 var2 <int>, where <int>
          is the default arity (number of variables).  Variables, like
          with make, can be prefixed with : or \", but need not be.
        * () is not used to force precedence, but to force execution
          with a specific arity.  In other words, () works like Lisp.
        """
        tok = self.tokenizer.next()

        if tok == '\n':
            raise LogoEndOfLine("The end of the line was not expected")
            return self.expr_inner()

        elif tok is EOF:
            raise LogoEndOfCode("The end of the code block was not expected")

        elif type(tok) is not str:
            # Some other fundamental type (usually int or float)
            return tok

        elif tok == '-':
            # This works really poorly in practice, because "-" usually
            # gets interpreted as an infix operator.
            return -self.expr()

        elif tok == '+':
            return self.expr()

        elif tok in ('/', '*'):
            raise LogoError("Operator not expected: %s" % tok)

        elif tok == '"' or tok.lower() == 'quote':
            tok = self.tokenizer.next()
            return tok

        elif tok == ':':
            tok = self.tokenizer.next()
            return self.get_variable(tok)

        elif tok == '[':
            self.tokenizer.push_context('[')
            result = self.expr_list()
            self.tokenizer.pop_context()
            return result

        elif tok == ';':
            while 1:
                tok = self.tokenizer.next()
                if tok == '\n' or tok is EOF:
                    break

        elif tok == '(':
            self.tokenizer.push_context('(')
            try:
                func = self.tokenizer.peek()
                if not reader.is_word(func):
                    # We don't actually have a function call then, but
                    # just a sub-expression.
                    val = self.expr()
                    if not self.tokenizer.next() == ')':
                        raise LogoSyntaxError("')' expected")
                    return val
                else:
                    self.tokenizer.next()
                if self.special_forms.has_key(func.lower()):
                    val = self.special_forms[func.lower()](self, greedy=True)
                else:
                    args = []
                    while 1:
                        tok = self.tokenizer.peek()
                        if tok == ')':
                            break
                        elif tok == '\n':
                            self.tokenizer.next()
                            continue
                        elif tok is EOF:
                            raise LogoEndOfCode("Unexpected end of code (')' expected)")
                        args.append(self.expr())
                    val = self.apply(self.get_function(func), args)
                if not self.tokenizer.next() == ')':
                    raise LogoSyntaxError("')' was expected.")
            finally:
                self.tokenizer.pop_context()
            return val

        else:
            if not reader.is_word(tok):
                raise LogoSyntaxError("Unknown token: %r" % tok)
            if tok.lower() in self.special_forms:
                val = self.special_forms[tok.lower()](self, greedy=False)
            else:
                func = self.get_function(tok)
                n = arity(func)
                self.tokenizer.push_context('func')
                try:
                    args = []
                    # -1 arity means the function is greedy
                    if n == -1:
                        while 1:
                            tok = self.tokenizer.peek()
                            if tok == '\n' or tok is EOF:
                                self.tokenizer.next()
                                break
                            args.append(self.expr())
                    else:
                        for i in range(n):
                            args.append(self.expr())
                finally:
                    self.tokenizer.pop_context()
                return self.apply(func, args)
        
    @special('make')
    def special_make(self, greedy):
        """
        The special MAKE form (special because a variable in the
        first argument isn't evaluated).
        """
        tok = self.tokenizer.next()
        if tok in ('"', ':'):
            tok = self.tokenizer.next()
        self.set_variable(tok, self.expr())

    @special('localmake')
    def special_localmake(self, greedy):
        """
        The special LOCALMAKE form
        """
        tok = self.tokenizer.next()
        if tok in ('"', ':'):
            tok = self.tokenizer.next()
        self.set_variable_local(tok, self.expr())

    @special('to')
    def special_to(self, greedy):
        """
        The special TO form.
        """
        self.tokenizer.push_context('to')
        vars = []
        default = None
        name = self.tokenizer.next()
        while 1:
            tok = self.tokenizer.next()
            if tok == '\n':
                break
            elif tok == '"' or tok == ':':
                continue
            elif type(tok) is int:
                default = tok
                continue
            vars.append(tok)
        body = []
        # END can only occur immediately after a newline, so we keep track
        lastNewline = False
        while 1:
            tok = self.tokenizer.next()
            if (lastNewline and isinstance(tok, str)
                and tok.lower() == 'end'):
                break
            lastNewline = (tok == '\n')
            if tok is EOF:
                raise LogoEndOfCode("The end of the file was not expected in a TO; use END")
            body.append(tok)
        func = UserFunction(name, vars, default, body)
        self.functions[name.lower()] = func
        self.tokenizer.pop_context()
        return func

    @special('local')
    def special_local(self, greedy):
        """
        The special LOCAL form (with unevaluated variables).  (Should
        this be generally greedy?)
        """
        vars = []
        if greedy:
            while 1:
                tok = self.tokenizer.peek()
                if tok in (':', '"'):
                    self.tokenizer.next()
                    continue
                elif not reader.is_word(tok):
                    break
                vars.append(tok)
                self.tokenizer.next()
        else:
            if self.tokenizer.peek() in (':', '"'):
                self.tokenizer.next()
            vars = [self.tokenizer.next()]
        for v in vars:
            self.makeLocal(v)
        return None

    @special('for')
    def special_for(self, greedy):
        """
        Special FOR form.  Again with the variable name.
        """
        varName = self.tokenizer.next()
        if varName in (':', '"'):
            varName = self.tokenizer.next()
        seq = self.expr()
        block = self.expr()
        try:
            for v in seq:
                self.set_variable_local(varName, v)
                try:
                    val = self.eval(block)
                except LogoContinue:
                    pass
        except LogoStop:
            pass
        return val

    def expr_list(self):
        """
        Grab a list (the '[' has already been grabbed).
        """
        body = []
        while 1:
            tok = self.tokenizer.next()
            if tok == ']':
                return LogoList(body, self.tokenizer.file)
            elif tok == '[':
                tok = self.expr_list()
            body.append(tok)

    def eval(self, lst):
        """
        Evaluate a list in this scope.
        """
        tokenizer = reader.ListTokenizer(lst)
        val = None
        self.push_tokenizer(tokenizer)
        try:
            while 1:
                tok = self.tokenizer.peek()
                if tok is EOF:
                    return val
                val = self.expr_top()
        finally:
            self.pop_tokenizer()
        return val

    def apply(self, func, args):
        """
        Apply the `args` to the `func`.  If the function has an
        attribute `logo_aware`, which is true, then the first argument
        passed to the function will be this interpreter object.  This
        allows special functions, like IF or WHILE, to manipulate the
        interpreter.
        """
        if getattr(func, 'logo_aware', 0):
            return func(self, *args)
        else:
            return func(*args)

    def import_function(self, import_function, names=None):
        """
        Inputs the function `func` into the namespace, using the name
        it was originally defined with.  The special attribute
        `logo_name` overrides the function name, and `aliases` provides
        abbreviations for the function (like FD for FORWARD).
        """
        d = import_function.func_dict
        if d.get('logo_hide'):
            return
        if names is None:
            name = d.get('logo_name', import_function.func_name)
            if name.startswith('_'): return
            names = [name] + list(d.get('aliases', []))
        #print "Importing functions %s" % ', '.join(names)
        for n in names:
            self.setFunction(n, import_function)

    def import_module(self, mod):
        """
        Import a module (either a module object, or the string name of
        the module), moving all of its exported functions into the
        current namespace (nested namespaces are not supported).

        If a file ``defs/modulename.logodef`` exists, it will be
        loaded to find extra information about the module.  This file
        contains one line for each annotated function (# or ; for
        comment lines).  See loadDefs for more.
        """
        if type(mod) is str:
            mod = loadModule(mod)
        print "Importing %s" % mod.__name__
        if os.path.exists('defs/%s.logodef' % mod.__name__):
            defs = self.load_defs('defs/%s.logodef' % mod.__name__)
        else:
            defs = {}
        main_name = mod.__name__.split('.')[-1] + '_main'
        main_func = None
        for n in dir(mod):
            obj = getattr(mod, n)
            if type(obj) is FunctionType:
                if n == main_name:
                    main_func = obj
                name = obj.func_name
                if defs.has_key(name.lower()):
                    useName, arity, aliases = defs.get(name.lower())
                    if arity is not None:
                        obj.arity = arity
                    if useName:
                        names = [name]
                    else:
                        names = []
                    names.extend(aliases)
                    if not names:
                        continue
                    self.import_function(obj, names)
                else:
                    self.import_function(obj)
        if main_func:
            main_func(self)
            
    def load_defs(self, filename):
        """
        Load function definitions from a file.  This file should have
        one function annotation on a line (lines starting with # or ;
        are comments).

        Each line starts with the function name and a color.  A star
        (*) means that the original function name should not be used.
        A word like arity:N will set the default arity of the function
        to N (if the default arity differs from the number of
        arguments the function takes).  Other words are interpreted as
        aliases for a function.  E.g.::
        
            forward: fd
            up: * penup pu
            ; RGB arguments only:
            color: arity:3
        """
        f = open(filename)
        defs = {}
        for l in f.readlines():
            l = l.strip()
            if not l or l.startswith('#') or l.startswith(';'):
                continue
            funcName, rest = l.split(':', 1)
            funcName = funcName.strip().lower()
            arity = None
            aliases = []
            useName = True
            for n in rest.split():
                if n == '*':
                    useName = False
                elif n.lower().startswith('arity:'):
                    arity = int(n[6:])
                else:
                    aliases.append(n)
            defs[funcName] = useName, arity, aliases
        return defs

    def import_logo(self, filename):
        """
        Import a logo file.  This executes the file, including any TO
        statements, putting everything into the normal namespace/scope.
        """
        print "Loading %s." % filename
        f = open(filename)
        tokenizer = reader.FileTokenizer(f)
        self.push_tokenizer(tokenizer)
        try:
            while 1:
                v = self.expr_top()
                if v is EOF: break
        finally:
            self.pop_tokenizer()
        try:
            main_name = os.path.splitext(os.path.basename(filename))[0] + '_main'
            func = self.get_function(main_name)
        except LogoNameError:
            pass
        else:
            self.apply(func, ())
        f.close()

    def input_loop(self, input, output):
        """
        Read-Eval-Print-Repeat loop, i.e., the standard prompt.
        """
        tokenizer = reader.FileTokenizer(input, output=output,
                                         prompt=self.prompts)
        self.push_tokenizer(tokenizer)
        try:
            while 1:
                try:
                    v = self.expr_top()
                except LogoError, e:
                    print e.description, ':', e
                    v = None
                except KeyboardInterrupt:
                    if tokenizer.context:
                        tokenizer.context = []
                        print 'Aborted'
                    else:
                        print "Bye"
                        break
                except SystemExit:
                    break
                except Exception, e:
                    import traceback
                    traceback.print_exc()
                    v = None
                if v is EOF:
                    break
                if v is not None:
                    print "%s" % repr(v)
        finally:
            self.pop_tokenizer()

    # Some standard prompts:
    prompts = {
        None: '??? ',
        'to': 'to? ',
        '[': ' [ ? ',
        '(': ' ( ? ',
        'func': '..? ',
        }

    del special

def arity(func):
    """
    Get the arity of a function (the number of arguments it takes).
    If the function has an `arity` attribute, this will be used as an
    override, otherwise `inspect` is used to find the number of
    arguments.

    Since `logo_aware` functions take an interpreter as the first
    argument, the arity of these functions is reduced by one.
    """
    if hasattr(func, 'arity'):
        return func.arity
    args, varargs, varkw, defaults = inspect.getargspec(func)
    a = len(args) - len(defaults or [])
    if func.func_dict.get('logo_aware'):
        a -= 1
    return a

class UserFunction(object):

    """
    A function the user defines, using TO.  When this function is
    called, the contents of the TO statement are executed.  The
    contents are not interpreted until then -- they are kept as tokens
    in a list.
    """

    def __init__(self, name, vars, default, body):
        self.name = name
        self.vars = vars
        if default is None:
            self.arity = len(vars)
        else:
            self.arity = default
        self.body = body
        self.logo_aware = 1

    def __call__(self, interpreter, *args):
        tokenizer = reader.ListTokenizer(LogoList(self.body, None))
        interpreter = interpreter.new(tokenizer)
        if len(args) < len(self.vars):
            args = args + (None,)*(len(self.vars)-len(args))
        for var, arg in zip(self.vars, args):
            interpreter.set_variable_local(var, arg)
        if len(args) > len(self.vars):
            interpreter.set_variable_local('rest', args[len(self.vars):])
        while 1:
            tok = tokenizer.peek()
            if tok is EOF:
                return
            try:
                interpreter.expr_top()
            except LogoOutput, exc:
                return exc.value

    def __repr__(self):
        return 'Function: %s' % self.name

    
class RootFrame(Interpreter):

    """
    The root/global frame object.  This holds all the function
    definitions, and global variables.  All the algorithms end up
    being different than for Frame, so they don't even inherit from
    each other, though they present the same interface.  Huh.
    """

    def __init__(self, tokenizer=None):
        Interpreter.__init__(self, tokenizer=tokenizer)
        self.vars = {}
        self.functions = {}
        self.root = self

    def __repr__(self):
        try:
            return '<RootFrame %x parsing "%r">' % \
                   (id(self), self.tokenizer)
        except:
            return '<RootFrame %x>' % id(self)

    def tokenizerStack(self):
        return self.tokenizers[:]

    def get_variable(self, v):
        v = v.lower()
        if self.vars.has_key(v):
            return self.vars[v]
        raise LogoNameError(
            "Variable :%s has not been set." % v)

    def set_variable(self, v, value):
        self.vars[v.lower()] = value

    def set_variable_local(self, v, value):
        self.vars[v.lower()] = value

    def _setVariableIfPresent(self, v, value):
        if self.vars.has_key(v):
            self.vars[v] = value
            return 1
        else:
            return 0

    def new(self, tokenizer=None):
        return self.Frame(self, tokenizer=tokenizer or self.tokenizer)

    def get_function(self, name):
        try:
            return self.functions[name.lower()]
        except KeyError:
            raise LogoNameError("I don't know how  to %s" % name)

    def setFunction(self, name, func):
        self.functions[name.lower()] = func

    def variableNames(self):
        return self.vars.keys()

    def functionNames(self):
        names = self.functions.keys()
        names.sort()
        return names

    def _setVariableNames(self, d):
        for n in self.vars.keys():
            d[n] = 1
        return d

    def eraseName(self, name):
        if self.vars.has_key(name.lower()):
            del self.vars[name.lower()]
        if self.functions.has_key(name.lower()):
            del self.functions[name.lower()]

    def makeLocal(self, v):
        raise LogoSyntaxError(
            "You can only use LOCAL in a function (TO).")

    def add_command(self, func, *args, **kw):
        return self.app.add_command(func, *args, **kw)

class Frame(RootFrame):

    """
    A local frame.  This frame usually has a parent frame, which is
    the scope that created this scope (usually via a function call).
    This chain implements the dynamic scoping; in a more typical
    lexically scoped language, the namespace would be attached to the
    container, not the previous caller.

    Lisps sometimes implement both of these policies (fluid-wind?),
    where certain variables are dynamic (usually marked like *this*),
    but other variables are lexical.  That might be neat.
    """

    def __init__(self, parent, tokenizer=None):
        Interpreter.__init__(self, tokenizer=tokenizer)
        self.parent = parent
        self.root = parent.root
        self.vars = {}
        # Holds the names of variables which have been declared local,
        # but may not have been set yet:
        self.localVars = {}

    def __repr__(self):
        return '<Frame %x parsing "%s">' % \
               (id(self), self.tokenizer)

    def tokenizerStack(self):
        stack = self.parent.tokenizerStack()
        stack.extend(self.tokenizers)
        return stack
        
    def new(self, tokenizer=None):
        """
        Add a new frame, and return that frame.
        """
        return self.__class__(self, tokenizer=tokenizer or self.tokenizer)

    def get_variable(self, v):
        v = v.lower()
        if self.vars.has_key(v):
            return self.vars[v]
        if self.localVars.has_key(v):
            raise LogoUndefinedError(
                "Variable :%s has not been set, but it has been "
                "declared LOCAL." % v)
        if self is self.root:
            raise LogoNameError(
                "Variable :%s has not been set." % v)
        return self.parent.get_variable(v)

    def set_variable(self, v, value):
        v = v.lower()
        if not self._setVariableIfPresent(v, value):
            self.vars[v] = value

    def _setVariableIfPresent(self, v, value):
        if self.localVars.has_key(v) or self.vars.has_key(v):
            self.vars[v] = value
            return 1
        else:
            return self.parent._setVariableIfPresent(v, value)

    def get_function(self, name):
        return self.root.get_function(name)

    def setFunction(self, name, func):
        return self.root.setFunction(name)

    def variableNames(self):
        return self._setVariableNames({}).keys()

    def functionNames(self):
        return self.root.functionNames()

    def _setVariableNames(self, d):
        for n in self.vars.keys():
            d[n] = 1
        return self.parent._setVariableNames(d)

    def eraseName(self, name):
        if self.vars.has_key(name.lower()):
            del self.vars[name.lower()]
        self.parent.eraseName(name)

    def makeLocal(self, v):
        self.localVars[v] = None

    def set_variable_local(self, v, value):
        self.vars[v.lower()] = value

    def add_command(self, add_command, *args, **kw):
        return self.root.add_command(add_command, *args, **kw)

RootFrame.Frame = Frame

def loadModule(name, path=None):
    """
    Loads a module given its name, because imp.find_module is
    annoying.
    """
    try:
        return sys.modules[name]
    except KeyError:
        pass
    names = name.split('.')
    if len(names) == 1:
        data = imp.find_module(names[0], path)
        mod = imp.load_module(names[0], *data)
        return mod
    else:
        mod = loadModule(names[0], path)
        return loadModule('.'.join(names[1:]), path=mod.__path__)

# Logo is the root, global interpreter object:
Logo = RootFrame()
from pylogo import builtins
Logo.import_module(builtins)
#if os.path.exists('init.logo'):
#    Logo.importLogo('init.logo')

if __name__ == '__main__':
    import sys
    filenames = sys.argv[1:]
    for filename in filenames:
        Logo.import_logo(filename)
    import sys
    Logo.input_loop(sys.stdin, sys.stdout)
