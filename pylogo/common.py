class LogoError(Exception):

    """
    A generic Logo error.  It tracks file position and someday a
    bit of the (Logo) traceback.
    """

    def __init__(self, *args, **kw):
        Exception.__init__(self, *args)
        if kw.has_key('tokenizer'):
            tokenizer = kw['tokenizer']
            del kw['tokenizer']
        else:
            tokenizer = None
        self.kw = kw
        if tokenizer is not None:
            self.setTokenizer(tokenizer)
        self.msg = ' '.join(args)
        self.frame = None
        if kw.has_key('description'):
            self.description = kw['description']

    def setFrame(self, frame):
        if self.frame:
            return
        self.frame = frame
        self.stack = [FrozenFrame(frame, frame.tokenizer,
                                  row=self.kw.get('row'),
                                  col=self.kw.get('col'))]
        self._tracebackInitialized = False
        self.initializeTraceback()

    def initializeTraceback(self):
        frame = self.frame
        tokenizers = frame.tokenizers[:-1]
        while 1:
            if not tokenizers:
                if frame.root is frame:
                    break
                frame = frame.parent
                tokenizers = frame.tokenizers
                continue
            self.stack.append(FrozenFrame(frame, tokenizers[-1]))
            tokenizers = tokenizers[:-1]
        self._tracebackInitialized = True
        self.stack.reverse()

    def traceback(self):
        #if not self._tracebackInitialized:
        #    self.initializeTraceback()
        return ''.join([str(f) for f in self.stack])

    def __str__(self):
        s = '\n'
        s += self.traceback()
        s += self.description + ': ' + Exception.__str__(self)
        #s += self.msg
        return s

class FrozenFrame:

    def __init__(self, frame, tokenizer, row=None, col=None, pos=None):
        self.frame = frame
        self.tokenizer = tokenizer
        if hasattr(tokenizer, 'list'):
            self.file = None
            self.list = tokenizer.list
            self.pos = pos
            if self.pos is None:
                try:
                    self.pos = self.tokenizer.pos - len(self.tokenizer.peeked)
                except AttributeError:
                    pass
        elif hasattr(tokenizer, 'file'):
            self.list = None
            self.file = tokenizer.file
            self.row = row
            self.col = col
            if self.row is None:
                try:
                    self.row = self.file.row
                except AttributeError:
                    pass
            if self.col is None:
                try:
                    self.col = self.file.col
                except AttributeError:
                    pass
        else:
            assert 0, "Unknown tokenizer: %r" % tokenizer

    def __repr__(self):
        if self.file:
            return '<FrozenFrame %x in %s:%s:%s>' % \
                   (id(self), self.file.name, self.row, self.col)
        elif self.list is not None:
            return '<FrozenFrame %x for %r>' % \
                   (id(self), self.list)
        else:
            assert 0, "Unknown frame/tokenizer type"

    def __str__(self):
        if self.file:
            return errorForFile(self.file, self.row, self.col)
        elif self.list is not None:
            return errorForList(self.list, self.pos)
        else:
            assert 0, "Unknown frame/tokenizer type"

def errorForFile(errorFile, row=None, col=None):
    try:
        name = errorFile.name
    except AttributeError:
        name = '<string>'
    if not row is None:
        try:
            row = errorFile.row
        except AttributeError:
            pass
    if not col:
        try:
            col = errorFile.col
        except AttributeError:
            pass
    if row is not None:
        s = 'File %s, line %i\n' % (name, row)
        l = errorFile.rowLine(row)
        if l is not None:
            s += l
            s += '%s^\n' % (' '*col)
    else:
        s = 'File %s\n' % name
    return s

def errorForList(lst, pos=None):
    try:
        f = lst.sourceList
        s = errorForFile(f) + '\n'
    except AttributeError:
        s = ''
    if pos is not None:
        segment = '[' + ' '.join(map(str, lst[:pos]))
        segment = segment.split('\n')[-1]
        rest = ' '.join(map(str, lst[pos:])) + ']'
        rest = rest.split('\n')[0]
        s += segment + ' ' + rest + '\n'
        s += (' '*len(segment)) + '^\n'
    else:
        s += repr(lst) + '\n'
    return s

class LogoSyntaxError(LogoError):
    description = 'Syntax error'

class LogoNameError(LogoError):
    description = 'Name not found error'

class LogoUndefinedError(LogoNameError):
    description = 'Function undefined error'

class LogoEndOfLine(LogoError):
    description = 'Unexpected end of line error'

class LogoEndOfCode(LogoError):
    description = 'Unexpected end of code block error'

class LogoList(list):

    #def __new__(cls, body, sourceFile):
    #    self = list.__new__(cls, body)
    #    self.file = sourceFile
    #    return self

    def __init__(self, body=None, sourceFile=None):
        #self.body = body
        if body is None:
            body = []
        list.__init__(self, body)
        self.file = sourceFile

    def __repr__(self):
        return '[%s]' % ' '.join(map(str, self))

class LogoControl(Exception):
    pass

class LogoOutput(LogoControl):

    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

class LogoContinue(LogoControl):
    pass

class LogoBreak(LogoControl):
    pass

class EOF:
    pass

