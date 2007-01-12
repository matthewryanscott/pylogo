"""
Structures for Logo
"""

def logorepr(item):
    if hasattr(item, '__logorepr__'):
        return item.__logorepr__()
    elif isinstance(item, (list, tuple)):
        return '[%s]' % ' '.join(logorepr(i) for i in item)
    else:
        return repr(item)

class logolist(list):

    def __str__(self):
        return ' '.join(str(i) for i in self)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            list.__repr__(self))

class sourcelist(logolist):

    def __new__(self, *args, **kw):
        val = logolist.__new__(self, *args)
        if 'lineno' in kw:
            val.linenos = [(0, kw.pop('lineno'))]
        elif 'linenos' in kw:
            val.linenos = kw.pop('linenos')
        else:
            val.linenos = []
        if kw:
            raise TypeError(
                "Unexpected keyword arguments: %r" % kw)
        return val

    def __init__(self, *args, **kw):
        logolist.__init__(self, *args)

    def __repr__(self):
        return '%s(%s, linenos=%r)' % (
            self.__class__.__name__,
            list.__repr__(self),
            self.linenos)

    def extend(self, other):
        if isinstance(other, self.__class__):
            for pos, lineno in other.linenos:
                self.linenos.append((len(self)+pos), lineno)
        logolist.extend(self, other)

    @classmethod
    def join(cls, *args):
        lst = cls(args[0])
        for arg in args[1:]:
            lst.extend(arg)
        return lst

    def insert(self, pos, item):
        for i in range(len(self.linenos)):
            if self.linenos[i][0] >= pos:
                self.linenos[i][0] += 1
        logolist.insert(self, pos, item)

    
                

class logosymbol(unicode):

    def __logorepr__(self):
        return self

    def __repr__(self):
        return 'logosymbol(%s)' % unicode.__repr__(self)

class logostring(unicode):

    def __logorepr__(self):
        return '"%s' % self

    def __repr__(self):
        return 'logostring(%r)' % unicode.__repr__(self)

class logovar(unicode):

    def __logorepr__(self):
        return ':%s' % self

    def __repr__(self):
        return 'logovar(%s)' % unicode.__repr__(self)

class logoexpression(object):

    def __init__(self, parts, paren=True):
        self.parts = parts
        self.paren = paren

    def __logorepr__(self):
        if self.paren:
            return '(%s)' % ' '.join(
                logorepr(item) for item in self.parts)
        else:
            return ' '.join(logorepr(item) for item in self.parts)

    def __repr__(self):
        return '<logo expression %s>' % logorepr(self)

class operator(unicode):

    def __logorepr__(self):
        return self

    def __repr__(self):
        return 'operator(%r)' % unicode.__repr__(self)
