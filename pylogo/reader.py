"""
reader for pylogo
  Ian Bicking <ianb@colorstudy.com>

Tokenizer/lexer.
"""


from __future__ import generators

import re
import sys
from common import *

wordMatcher = r'[a-zA-Z._][a-zA-Z0-9.?_]*'
wordRE = re.compile(wordMatcher)
onlyWordRE = re.compile(r'^%s$' % wordMatcher)
numberRE = re.compile(r'(?:[0-9][.0-9]*|-[0-9][0-9]*)')
symbols = '()[]+-/*":=><.;'
whiteRE = re.compile(r'[ \t\n\r]+')

class FileTokenizer:

    """
    An interator over the tokens of a file.  Will prompt interactively
    if `prompt` is given.
    """

    def __init__(self, f, output=None, prompt=None):
        if type(f) is file:
            f = TrackingStream(f)
        self.file = f
        self.generator = self._generator()
        self.peeked = []
        self.prompt = prompt
        self.output = output
        self.context = []

    def __repr__(self):
        try:
            return '<FileTokenizer %x parsing %s:%i:%i>' \
                   % (id(self), self.file.name, self.file.row,
                      self.file.col)
        except:
            return '<FileTokenizer %x parsing %r>' \
                   % (id(self), self.file)

    def printPrompt(self):
        if not self.prompt or not self.output:
            return
        if isinstance(self.prompt, str):
            prompt = self.prompt
        else:
            if self.context:
                context = self.context[-1]
            else:
                context = None
            prompt = self.prompt.get(context, '?')
        if prompt:
            self.output.write(prompt)
            self.output.flush()

    def pushContext(self, context):
        self.context.append(context)

    def popContext(self):
        self.context.pop()

    def next(self):
        try:
            return self.generator.next()
        except StopIteration:
            import traceback
            traceback.print_exc()
            import sys
            sys.exit()

    def peek(self):
        if self.peeked:
            return self.peeked[0]
        p = self.next()
        self.peeked = [p]
        return p

    def _generator(self):
        """
        Generator - gets one token from the TrackingStream
        """
        while 1:
            if self.peeked:
                v = self.peeked[0]
                del self.peeked[0]
                yield v
            self.printPrompt()
            l = self.file.readline()
            while 1:
                if self.peeked:
                    v = self.peeked[0]
                    del self.peeked[0]
                    yield v
                m = whiteRE.match(l, pos=self.file.col)
                if m:
                    self.file.col = m.end()
                if l == '':
                    yield EOF
                    break
                if len(l) <= self.file.col:
                    yield '\n'
                    break
                c = l[self.file.col]
                try:
                    cnext = l[self.file.col+1]
                except IndexError:
                    cnext = None
                if (numberRE.match(c) or
                    c == '-' and
                    cnext and numberRE.match(cnext)):
                    m = numberRE.match(l, pos=self.file.col)
                    assert m
                    self.file.col = m.end()
                    n = m.group(0)
                    try:
                        yield int(n)
                    except ValueError:
                        try:
                            yield float(n)
                        except ValueError:
                            raise LogoSyntaxError(self.file, 'Not a number: %s' % repr(n))
                if c in symbols:
                    self.file.col += 1
                    yield c
                elif wordRE.match(c):
                    m = wordRE.match(l, pos=self.file.col)
                    assert m
                    self.file.col = m.end()
                    yield m.group(0)
                else:
                    self.file.col += 1
                    yield c
                    # This seems like a bad idea:
                    #raise LogoSyntaxError('Unknown character: %s' % repr(c), errorFile=self.file)

def isWord(tok):
    if isinstance(tok, str):
        return bool(onlyWordRE.search(tok))
    else:
        return False

class ListTokenizer:

    """
    This is just a cache of previously tokenized expressions.  So that
    [a block] can be treated like a stream of tokens.  The tokens are
    taken from `l`.
    """

    def __init__(self, l):
        self.list = l
        try:
            self.file = l.file
        except AttributeError:
            self.file = None
        self.pos = 0
        self.peeked = []

    def __repr__(self):
        try:
            return '<ListTokenizer %x tokenizing list len=%i, pos=%i>' \
                   % (id(self), len(self.list), self.pos)
        except:
            return '<ListTokenizer %x>' % (id(self))

    def pushContext(self, context):
        pass

    def popContext(self):
        pass

    def peek(self):
        if self.peeked:
            return self.peeked[0]
        p = self.next()
        self.peeked = [p]
        return p

    def next(self):
        if self.peeked:
            v = self.peeked[0]
            del self.peeked[0]
            return v
        if self.pos >= len(self.list):
            return EOF
        self.pos += 1
        return self.list[self.pos-1]
            
class TrackingStream:

    """
    A file-like object that also keeps track of rows and columns,
    for tracebacks.
    """

    def __init__(self, file):
        self.file = file
        self.col = 0
        self.row = 0
        self.savedLines = []
        self.maxSavedLines = 10
        self.name = self.file.name

    def readline(self):
        self.row += 1
        self.col = 0
        l = self.file.readline()
        self.savedLines.insert(0, l)
        if len(self.savedLines) > self.maxSavedLines:
            del self.savedLines[self.maxSavedLines:]
        return l

    def rowLine(self, row):
        if row < self.row - len(self.savedLines):
            return None
        return self.savedLines[self.row-row]

    def __repr__(self):
        s = repr(self.file)[:-1]
        return '%s %s:%s>' % (s, self.row, self.col)
                
        
def main():
    import sys
    tok = FileTokenizer(TrackingStream(sys.stdin))
    while 1:
        print '>> %s' % repr(tok.next())

if __name__ == '__main__':
    main()
