"""
builtins for pylogo
  Ian Bicking <ianb@colorstudy.com>

These implement the builtins, as much as possible using the standard
library of UCBLogo as a model:
  http://www.cs.berkeley.edu/~bh/logo.html
UCBLogo manual:
  http://www.cs.berkeley.edu/~bh/usermanual

Organization of this module follows the organization of the UCB
manual.

All missing functions are noted in comments and marked with '@@'
"""


import os, random, sys
import operator, math, time
import threading
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from pylogo.common import *
from pylogo import reader

class NoDefault:
    pass


########################################
## Data Structure Primitives
########################################

## Constructors

def word(*args):
    """
    WORD word1 word2
    (WORD word1 word2 word3 ...)

    outputs a word formed by concatenating its inputs.
    """
    return ''.join(map(str, args))
word.arity = 2

def logoList(*args):
    """
    LIST thing1 thing2
    (LIST thing1 thing2 thing3 ...)

    outputs a list whose members are its inputs, which can be any
    Logo datum (word, list, or array).
    """
    return list(args)
logoList.logoName = 'list'
logoList.arity = 2

def logoRepr(arg):
    if isinstance(arg, list):
        return '[%s]' % _join(map(logoSoftRepr, arg))
    elif isinstance(arg, str):
        return '"%s' % arg
    else:
        return repr(arg)

def logoSoftRepr(arg):
    """
    Like logoRepr, only we're already in a quoted context, so
    we don't have to quote strings.
    """
    if isinstance(arg, str):
        return arg
    else:
        return logoRepr(arg)

def _join(args):
    """
    Join the arguments with spaces, except newlines which don't
    need to be padded.
    """
    result = StringIO()
    skipSpace = True
    for arg in args:
        if skipSpace:
            skipSpace = False
        else:
            result.write(' ')
        if arg == '\n':
            skipSpace = True
        result.write(arg)
    return result.getvalue()

def logoStr(arg):
    if isinstance(arg, list):
        return ' '.join(map(logoSoftRepr, arg))
    else:
        return str(arg)

def sentence(*args):
    """
    SENTENCE thing1 thing2
    SE thing1 thing2
    (SENTENCE thing1 thing2 thing3 ...)
    (SE thing1 thing2 thing3 ...)

    outputs a list whose members are its inputs, if those inputs are
    not lists, or the members of its inputs, if those inputs are lists.
    """
    result = []
    for arg in args:
        if isinstance(arg, list):
            result.extend(arg)
        else:
            result.append(arg)
    return result
sentence.arity = 2
sentence.aliases = ['se']

def fput(thing, l):
    """
    FPUT thing list

    outputs a list equal to its second input with one extra member,
    the first input, at the beginning.
    """
    return [thing] + l

def lput(thing, l):
    """
    LPUT thing list
    
    outputs a list equal to its second input with one extra member,
    the first input, at the end.
    """
    return l + [thing]

# @@: array, mdarray, listtoarray, arraytolist

def combine(thing1, thing2):
    """
    COMBINE thing1 thing2

    if thing2 is a word, outputs WORD thing1 thing2.  If thing2 is a list,
    outputs FPUT thing1 thing2.
    """
    if wordp(thing2):
        return word(thing1, thing2)
    elif listp(thing2):
        return fput(thing1, thing2)
    else:
        raise ValueError

def reverse(l):
    """
    REVERSE list

    outputs a list whose members are the members of the input list, in
    reverse order.
    """
    l = l[:]
    l.reverse()
    return l

_synnum = 0
_synnumLock = threading.Lock()
def gensym():
    """
    GENSYM

    outputs a unique word each time it's invoked.  The words are of the
    form G1, G2, etc.
    """
    global _synnum
    _synnumLock.acquire()
    try:
        _synnum += 1
        return 'G%i' % _synnum
    finally:
        _synnumLock.release()

## Selectors

def first(thing):
    """
    FIRST thing

    if the input is a word, outputs the first character of the word.
    If the input is a list, outputs the first member of the list.
    If the input is an array, outputs the origin of the array (that
    is, the INDEX OF the first member of the array).
    """
    return thing[0]

def firsts(things):
    """
    FIRSTS list

    outputs a list containing the FIRST of each member of the input
    list.  It is an error if any member of the input list is empty.
    (The input itself may be empty, in which case the output is also
    empty.)  This could be written as::

        to firsts :list
	    output map \"first :list
        end

    but is provided as a primitive in order to speed up the iteration
    tools MAP, MAP.SE, and FOREACH::
 
        to transpose :matrix
            if emptyp first :matrix [op []]
            op fput firsts :matrix transpose bfs :matrix
        end
    """
    return [first(thing) for thing in things]

def last(thing):
    """
    LAST wordorlist

    if the input is a word, outputs the last character of the word.
    If the input is a list, outputs the last member of the list.
    """
    return thing[-1]

def butfirst(thing):
    """
    BUTFIRST wordorlist
    BF wordorlist

    if the input is a word, outputs a word containing all but the first
    character of the input.  If the input is a list, outputs a list
    containing all but the first member of the input.
    """
    if isinstance(thing, str):
        return thing[1:]
    else:
        return thing[1:]
butfirst.aliases = ['bf']

def butfirsts(things):
    """
    BUTFIRSTS list
    BFS list

    outputs a list containing the BUTFIRST of each member of the input
    list.  It is an error if any member of the input list is empty or an
    array.  (The input itself may be empty, in which case the output is
    also empty.)  This could be written as::

        to butfirsts :list
	    output map \"butfirst :list
        end

    but is provided as a primitive in order to speed up the iteration
    tools MAP, MAP.SE, and FOREACH.
    """
    return [butfirst(thing) for thing in things]
butfirsts.aliases = ['bfs']

def butlast(thing):
    """
    BUTLAST wordorlist
    BL wordorlist

    if the input is a word, outputs a word containing all but the last
    character of the input.  If the input is a list, outputs a list
    containing all but the last member of the input.
    """
    if isinstance(thing, str):
        return thing[:-1]
    else:
        return thing[:-1]
butlast.aliases = ['bl']

def item(index, thing):
    """
    ITEM index thing

    if the ``thing`` is a word, outputs the ``index``th character of
    the word.  If the ``thing`` is a list, outputs the ``index``th
    member of the list.  If the ``thing`` is an array, outputs the
    ``index``th member of the array.  ``Index`` starts at 1 for words
    and lists; the starting index of an array is specified when the
    array is created.
    """
    if isinstance(thing, dict):
        return thing[index]
    else:
        return thing[index-1]

# @@: mditem

def pick(l):
    """
    PICK list

    outputs a randomly chosen member of the input list.
    """
    return random.choice(l)

def remove(thing, l):
    """
    REMOVE thing list

    outputs a copy of ``list`` with every member equal to ``thing``
    removed.
    """
    l = l[:]
    l.remove(thing)
    return l

def remdup(l):
    """
    REMDUP list

    outputs a copy of ``list`` with duplicate members removed.  If two
    or more members of the input are equal, the rightmost of those
    members is the one that remains in the output.
    """
    items = {}
    newL = []
    for item in l:
        if not items.has_key(item):
            newL.append(item)
            items[item] = None
    return newL

## Mutators

def setitem(index, thing, value):
    """
    SETITEM index array value

    command.  Replaces the ``index``th member of ``array`` with the new
    ``value``.  Ensures that the resulting array is not circular, i.e.,
    ``value`` may not be a list or array that contains ``array``.
    """
    if isinstance(thing, dict):
        thing[index] = value
    else:
        thing[index-1] = value
    return thing

def dotsetfirst(lst, value):
    """
    .SETFIRST list value

    command.  Changes the first member of ``list`` to be ``value``.
    WARNING: Primitives whose names start with a period are DANGEROUS.
    Their use by non-experts is not recommended.  The use of .SETFIRST
    can lead to circular list structures, which will get some Logo
    primitives into infinite loops; and unexpected changes to other data
    structures that share storage with the list being modified.
    """
    lst[0] = value
dotsetfirst.logoName = '.setfirst'

def dotsetbf(lst, value):
    """
    .SETBF list value

    command.  Changes the butfirst of ``list`` to be ``value``.
    WARNING: Primitives whose names start with a period are DANGEROUS.
    Their use by non-experts is not recommended.  The use of .SETBF
    can lead to circular list structures, which will get some Logo
    primitives into infinite loops; unexpected changes to other data
    structures that share storage with the list being modified.
    list.
    """
    assert isinstance(value, list), "Only a list may be passed to .SETBF (you gave: %r)" % value
    while len(lst) != 1:
        lst.pop()
    lst.append(value)
dotsetbf.logoName = '.setbf'

## Predicates

def wordp(thing):
    """
    WORDP thing
    WORD? thing

    outputs TRUE if the input is a word, FALSE otherwise.
    """
    return type(thing) is str
wordp.aliases = ['word?']

def listp(val):
    """
    LISTP thing
    LIST? thing
    
    outputs TRUE if the input is a list, FALSE otherwise.
    """
    return isinstance(val, list)
listp.aliases = ['list?']

def emptyp(thing):
    """
    EMPTYP thing
    EMPTY? thing

    outputs TRUE if the input is the empty word or the empty list,
    FALSE otherwise.
    """
    return thing == '' or thing == [] or thing == () or thing == {}
emptyp.aliases = ['empty?']

def equalp(thing1, thing2):
    """
    EQUALP thing1 thing2
    EQUAL? thing1 thing2
    thing1 = thing2

    outputs TRUE if the inputs are equal, FALSE otherwise.  Two
    numbers are equal if they have the same numeric value.  Two
    non-numeric words are equal if they contain the same characters in
    the same order.  If there is a variable named CASEIGNOREDP whose
    value is TRUE, then an upper case letter is considered the same as
    the corresponding lower case letter.  (This is the case by
    default.)  Two lists are equal if their members are equal.  An
    array is only equal to itself; two separately created arrays are
    never equal even if their members are equal.  (It is important to
    be able to know if two expressions have the same array as their
    value because arrays are mutable; if, for example, two variables
    have the same array as their values then performing SETITEM on one
    of them will also change the other.)
    """
    return thing1 == thing2
equalp.aliases = ['equal?']

def beforep(word1, word2):
    """
    BEFOREP word1 word2
    BEFORE? word1 word2

    outputs TRUE if word1 comes before word2 in ASCII collating
    sequence (for words of letters, in alphabetical order).
    Case-sensitivity is determined by the value of CASEIGNOREDP.  Note
    that if the inputs are numbers, the result may not be the same as
    with LESSP; for example, BEFOREP 3 12 is false because 3 collates
    after 1.
    """
    return word1 < word2
beforep.aliases = ['before?']

def doteq(thing1, thing2):
    """
    .EQ thing1 thing2
    
    outputs TRUE if its two inputs are the same datum, so that
    applying a mutator to one will change the other as well.  Outputs
    FALSE otherwise, even if the inputs are equal in value.
    """
    return thing1 is thing2
doteq.logoName = '.eq'

def memberp(thing1, l):
    """
    MEMBERP thing1 thing2
    MEMBER? thing1 thing2

    if ``thing2`` is a list or an array, outputs TRUE if ``thing1`` is
    EQUALP to a member of ``thing2``, FALSE otherwise.  If ``thing2``
    is a word, outputs TRUE if ``thing1`` is a one-character word
    EQUALP to a character of ``thing2``, FALSE otherwise.
    """
    return thing1 in l
memberp.aliases = ['member?']

def substringp(thing1, thing2):
    """
    SUBSTRINGP thing1 thing2
    SUBSTRING? thing1 thing2

    if ``thing1`` or ``thing2`` is a list or an array, outputs FALSE.
    If ``thing2`` is a word, outputs TRUE if ``thing1`` is EQUALP to a
    substring of ``thing2``, FALSE otherwise.
    """
    return type(thing2) is str and type(thing1) is str \
           and thing2.find(thing1) != -1
substringp.aliases = ['substring?']

def numberp(thing):
    """
    NUMBERP thing
    NUMBER? thing

    outputs TRUE if the input is a number, FALSE otherwise.
    """
    return type(thing) is int or type(thing) is float
numberp.aliases = ['number?']

## Queries

def count(thing):
    """
    COUNT thing

    outputs the number of characters in the input, if the input is a
    word; outputs the number of members in the input, if it is a list
    or an array.  (For an array, this may or may not be the index of
    the last member, depending on the array's origin.)
    """
    return len(thing)

def ascii(char):
    """
    ASCII char

    outputs the integer (between 0 and 255) that represents the input
    character in the ASCII code.
    """
    ## UCB: Interprets control characters as representing backslashed
    ## punctuation, and returns the character code for the
    ## corresponding punctuation character without backslash.
    ## (Compare RAWASCII.)
    return ord(char)

def char(int):
    """
    CHAR int
    
    outputs the character represented in the ASCII code by the input,
    which must be an integer between 0 and 255.
    """
    return chr(int)

def member(thing1, thing2):
    """
    MEMBER thing1 thing2

    if ``thing2`` is a word or list and if MEMBERP with these inputs
    would output TRUE, outputs the portion of ``thing2`` from the
    first instance of ``thing1`` to the end.  If MEMBERP would output
    FALSE, outputs the empty word or list according to the type of
    ``thing2``.  It is an error for ``thing2`` to be an array.
    """
    if type(thing2) is str:
        i = thing2.find(thing1)
        if i == -1:
            return ''
        else:
            return thing2[i:]
    else:
        i = thing2.index(thing1)
        if i == -1:
            return []
        else:
            return thing2[i:]

def lowercase(word):
    """
    LOWERCASE word

    outputs a copy of the input word, but with all uppercase letters
    changed to the corresponding lowercase letter.
    """
    return word.lower()

def uppercase(word):
    """
    UPPERCASE word

    outputs a copy of the input word, but with all lowercase letters
    changed to the corresponding uppercase letter.
    """
    return word.upper()

# @@: standout, parse, runparse

########################################
## Communication
########################################

##############################
## Transmitters

def pr(*args):
    """
    PRINT thing thing2 thing3 ...
    PR thing
    (PRINT thing1 thing2 ...)
    (PR thing1 thing2 ...)

    command.  Prints the input or inputs to the current write stream
    (initially the terminal).  All the inputs are printed on a single
    line, separated by spaces, ending with a newline.  If an input is a
    list, square brackets are not printed around it, but brackets are
    printed around sublists.  Braces are always printed around arrays.
    """
    trans = []
    for arg in args:
        if isinstance(arg, list):
            trans.append(_join(map(logoSoftRepr, arg)))
        else:
            trans.append(logoSoftRepr(arg))
    print ' '.join(trans)
pr.aliases = ['print']
pr.arity = -1

def logoType(*args):
    """
    TYPE thing thing2 thing3 ...
    (TYPE thing1 thing2 ...)
    
    command.  Prints the input or inputs like PRINT, except that no
    newline character is printed at the end and multiple inputs are
    not separated by spaces.
    """
    trans = []
    for arg in args:
        if isinstance(arg, list):
            trans.append(' '.join(map(repr, arg)))
        else:
            trans.append(repr(arg))
    sys.stdout.write(' '.join(trans))
    sys.stdout.flush()
logoType.logoName = 'type'
logoType.arity = -1

def show(*args):
    """
    SHOW thing thing2 thing3 ...
    (SHOW thing1 thing2 ...)
    
    command.  Prints the input or inputs like PRINT, except that
    if an input is a list it is printed inside square brackets.
    """
    print ' '.join(map(repr(args)))

##############################
## Receivers

def readlist():
    """
    READLIST
    RL

    reads a line from the read stream (initially the terminal) and
    outputs that line as a list.  The line is separated into members
    as though it were typed in square brackets in an instruction.  If
    the read stream is a file, and the end of file is reached,
    READLIST outputs the empty word (not the empty list).  READLIST
    processes backslash, vertical bar, and tilde characters in the
    read stream; the output list will not contain these characters but
    they will have had their usual effect.  READLIST does not,
    however, treat semicolon as a comment character.
    """
    tokenizer = reader.FileTokenizer(sys.stdin)
    result = []
    while 1:
        tok = tokenizer.next()
        if tok is reader.EOF or tok == '\n':
            break
        result.append(tok)
    return result

def readrawline():
    """
    READRAWLINE

    reads a line from the read stream and outputs that line as a word.
    The output is a single word even if the line contains spaces,
    brackets, etc.  If the read stream is a file, and the end of file is
    reached, READRAWLINE outputs the empty list (not the empty word).
    READRAWLINE outputs the exact string of characters as they appear
    in the line, with no special meaning for backslash, vertical bar,
    tilde, or any other formatting characters.
    """
    try:
        v = sys.stdin.readline()
        if not v:
            return []
        # remove trailing newline
        return v[:-1]
    except EOFError:
        return []
                  
# @@: readchars/rcs, shell

##############################
## File access

# @@: all unimplemented

##############################
## Terminal Access

# @@: all unimplemented

def sum(*args):
    """
    SUM num1 num2
    (SUM num1 num2 num3 ...)
    num1 + num2

    outputs the sum of its inputs.
    """
    return reduce(operator.add, args)
sum.arity = 2

def difference(num1, num2):
    """
    DIFFERENCE num1 num2
    num1 - num2
    
    outputs the difference of its inputs.  Minus sign means infix
    difference in ambiguous contexts (when preceded by a complete
    expression), unless it is preceded by a space and followed
    by a nonspace.  (See also MINUS.)
    """
    return num1 - num2

def minus(num):
    """
    MINUS num
    - num

    outputs the negative of its input.  Minus sign means unary minus if
    the previous token is an infix operator or open parenthesis, or it is
    preceded by a space and followed by a nonspace.  There is a difference
    in binding strength between the two forms::

        MINUS 3 + 4     ; means    -(3+4)
        - 3 + 4	        ; means    (-3)+4
    """
    return -num

def product(*args):
    """
    PRODUCT num1 num2
    (PRODUCT num1 num2 num3 ...)
    num1 * num2

    outputs the product of its inputs.
    """
    return reduce(operator.mul, args)
product.arity = 2

def quotient(num1, num2):
    """
    QUOTIENT num1 num2
    (QUOTIENT num)
    num1 / num2

    outputs the quotient of its inputs.  The quotient of two integers
    is an integer if and only if the dividend is a multiple of the divisor.
    (In other words, QUOTIENT 5 2 is 2.5, not 2, but QUOTIENT 4 2 is
    2, not 2.0 -- it does the right thing.)  With a single input,
    QUOTIENT outputs the reciprocal of the input.
    """
    return num1 / num2

def remainder(num1, num2):
    """
    REMAINDER num1 num2

    outputs the remainder on dividing ``num1`` by ``num2``; both must
    be integers and the result is an integer with the same sign as
    num1.
    """
    v = num1 % num2
    if v < 0 and num1 > 0 or v > 0 and num1 < 0:
        v = v + num1
    return v

def modulo(num1, num2):
    """
    MODULO num1 num2

    outputs the remainder on dividing ``num1`` by ``num2``; both must be
    integers and the result is an integer with the same sign as num2.
    """
    return num1 % num2

def logoInt(num):
    """
    INT num

    outputs its input with fractional part removed, i.e., an integer
    with the same sign as the input, whose absolute value is the
    largest integer less than or equal to the absolute value of
    the input.
    """
    return int(num)
logoInt.logoName = 'int'

def logoRound(v, *args):
    """
    ROUND num

    outputs the nearest integer to the input.
    """
    return round(v, *args)
logoRound.logoName = 'round'
logoRound.arity = 1

def logoAbs(v):
    return abs(v)
logoAbs.logoName = 'abs'

def sqrt(v):
    """
    SQRT num

    outputs the square root of the input, which must be nonnegative.
    """
    return math.sqrt(v)

def power(num1, num2):
    """
    POWER num1 num2

    outputs ``num1`` to the ``num2`` power.  If num1 is negative, then
    num2 must be an integer.
    """
    ## @@: integer not required with negative num1...?
    return num1**num2

def exp(v):
    """
    EXP num

    outputs e (2.718281828+) to the input power.
    """
    return math.exp(v)

def log10(v):
    """
    LOG10 num

    outputs the common logarithm of the input.
    """
    return math.log10(v)

def ln(v):
    """
    LN num

    outputs the natural logarithm of the input.
    """
    return math.log(v)

def _toDegrees(num):
    return (num / math.pi) * 180
def _toRadians(num):
    return (num / 180.0) * math.pi

def sin(num):
    """
    SIN degrees

    outputs the sine of its input, which is taken in degrees.
    """
    return math.sin(_toRadians(num))

def radsin(v):
    """
    RADSIN radians

    outputs the sine of its input, which is taken in radians.
    """
    return math.sin(v)

def cos(num):
    """
    COS degrees

    outputs the cosine of its input, which is taken in degrees.
    """
    return math.cos(_toRadians(num))

def radcos(v):
    """
    RADCOS radians

    outputs the cosine of its input, which is taken in radians.
    """
    return math.cos(v)

def arctan(num, second=None):
    """
    ARCTAN num
    (ARCTAN x y)

    outputs the arctangent, in degrees, of its input.  With two
    inputs, outputs the arctangent of y/x, if x is nonzero, or
    90 or -90 depending on the sign of y, if x is zero.
    """
    return _toDegrees(radarctan(num, second))

def radarctan(num, second=None):
    """
    RADARCTAN num
    (RADARCTAN x y)

    outputs the arctangent, in radians, of its input.  With two
    inputs, outputs the arctangent of y/x, if x is nonzero, or
    pi/2 or -pi/2 depending on the sign of y, if x is zero.
    
    The expression 2*(RADARCTAN 0 1) can be used to get the
    value of pi.
    """
    if second is not None:
        return math.atan2(num, second)
    else:
        return math.atan(num)

def iseq(fromNum, toNum):
    """
    ISEQ from to

    outputs a list of the integers from FROM to TO, inclusive::

        ? show iseq 3 7
        [3 4 5 6 7]
        ? show iseq 7 3
        [7 6 5 4 3]
    """
    return range(fromNum, toNum+1)

def rseq(fromNum, toNum, length):
    """
    RSEQ from to count

    outputs a list of COUNT equally spaced rational numbers
    between FROM and TO, inclusive::

        ? show rseq 3 5 9
        [3 3.25 3.5 3.75 4 4.25 4.5 4.75 5]
        ? show rseq 3 5 5
        [3 3.5 4 4.5 5]
    """
    result = [fromNum + (float(i)*(toNum-fromNum)/(length-1))
              for i in range(length-1)]
    result.append(toNum)
    return result

##############################
## Predicates

def lessp(num1, num2):
    """
    LESSP num1 num2
    LESS? num1 num2
    num1 < num2
    
    outputs TRUE if its first input is strictly less than its second.
    """
    return num1 < num2
lessp.aliases = ['less?']

def greaterp(num1, num2):
    """
    GREATERP num1 num2
    GREATER? num1 num2
    num1 > num2

    outputs TRUE if its first input is strictly greater than its second.
    """
    return num1 > num2
greaterp.aliases = ['greater?']

##############################
## Random Numbers

def logoRandom(num):
    """
    RANDOM num

    outputs a random nonnegative integer less than its input, which
    must be an integer.
    """
    return random.randint(0, num-1)
logoRandom.logoName = 'random'

def rerandom(seed=None):
    """
    RERANDOM
    (RERANDOM seed)

    command.  Makes the results of RANDOM reproducible.  Ordinarily
    the sequence of random numbers is different each time Logo is
    used.  If you need the same sequence of pseudo-random numbers
    repeatedly, e.g. to debug a program, say RERANDOM before the
    first invocation of RANDOM.  If you need more than one repeatable
    sequence, you can give RERANDOM an integer input; each possible
    input selects a unique sequence of numbers.
    """
    if seed is None:
        seed = time.time()
    random.seed(seed)

##############################
## Print Formatting

# @@: form

##############################
## Bitwise operations

def bitand(*args):
    """
    BITAND num1 num2
    (BITAND num1 num2 num3 ...)

    outputs the bitwise AND of its inputs, which must be integers.
    """
    return reduce(operator.and_, args)
bitand.arity = 2

def bitor(*args):
    """
    BITOR num1 num2
    (BITOR num1 num2 num3 ...)

    outputs the bitwise OR of its inputs, which must be integers.
    """
    return reduce(operator.or_, args)
bitor.arity = 2

def bitxor(*args):
    """
    BITXOR num1 num2
    (BITXOR num1 num2 num3 ...)

    outputs the bitwise EXCLUSIVE OR of its inputs, which must be
    integers.
    """
    return reduce(operator.xor, args)
bitxor.arity = 2

def bitnot(num):
    """
    BITNOT num

    outputs the bitwise NOT of its input, which must be an integer.
    """
    return ~num

def ashift(num1, num2):
    """
    ASHIFT num1 num2

    outputs ``num1`` arithmetic-shifted to the left by ``num2`` bits.
    If num2 is negative, the shift is to the right with sign
    extension.  The inputs must be integers.
    """
    return num1 >> num2

def lshift(num1, num2):
    """
    LSHIFT num1 num2

    outputs ``num1`` logical-shifted to the left by ``num2`` bits.
    If num2 is negative, the shift is to the right with zero fill.
    The inputs must be integers.
    """
    return num1 << num2

##############################
## Logical statements

def logoAnd(interp, *vals):
    """
    AND tf1 tf2
    (AND tf1 tf2 tf3 ...)
    
    outputs TRUE if all inputs are TRUE, otherwise FALSE.  An input
    can be a list, in which case it is taken as an expression to run;
    that expression must produce a TRUE or FALSE value.  List
    expressions are evaluated from left to right; as soon as a FALSE
    value is found, the remaining inputs are not examined.  Example::

        MAKE \"RESULT AND [NOT (:X = 0)] [(1 / :X) > .5]

    to avoid the division by zero if the first part is false.
    """
    for val in vals:
        if isinstance(val, list):
            val = interp.eval(val)
        if not val:
            return False
    return True
logoAnd.arity = 2
logoAnd.logoName = 'and'
logoAnd.logoAware = True

def logoOr(interp, *vals):
    """
    OR tf1 tf2
    (OR tf1 tf2 tf3 ...)

    outputs TRUE if any input is TRUE, otherwise FALSE.  An input can
    be a list, in which case it is taken as an expression to run; that
    expression must produce a TRUE or FALSE value.  List expressions
    are evaluated from left to right; as soon as a TRUE value is
    found, the remaining inputs are not examined.  Example::

        IF OR :X=0 [some.long.computation] [...]

    to avoid the long computation if the first condition is met.
    """
    for val in vals:
        if isinstance(val, list):
            val = logo.eval(val)
        if val:
            return True
    return False
logoOr.arity = 2
logoOr.logoName = 'or'
logoOr.logoAware = True

def logoNot(interp, val):
    """
    NOT tf

    outputs TRUE if the input is FALSE, and vice versa.  The input can be
    a list, in which case it is taken as an expression to run; that
    expression must produce a TRUE or FALSE value.
    """
    if isinstance(val, list):
        val = interp.eval(val)
    return not val
logoNot.logoName = 'not'
logoNot.logoAware = True


########################################
## Graphics
########################################

# @@: from logo_turtle.py

########################################
## Workspace Management
########################################

##############################
## Procedure Definition

def logoDefine(interp, procname, text):
    """
    DEFINE procname text

    command.  Defines a procedure with name ``procname`` and text
    ``text``.  If there is already a procedure with the same name, the
    new definition replaces the old one.  The text input must be a
    list whose members are lists.  The first member is a list of
    inputs; it looks like a TO line but without the word TO, without
    the procedure name, and without the colons before input names.  In
    other words, the members of this first sublist are words for the
    names of required inputs and lists for the names of optional or
    rest inputs.  The remaining sublists of the text input make up the
    body of the procedure, with one sublist for each instruction line
    of the body.  (There is no END line in the text input.)
    """
    body = []
    args = text[0]
    for l in text[1:]:
        body.extend(l)
        body.append('\n')
    func = interpreter.UserFunction(procname, args, None, body)
    interp.setFunction(procname, func)
logoDefine.logoAware = True
logoDefine.logoName = 'define'

def text(interp, procname):
    """
    TEXT procname
    
    outputs the text of the procedure named ``procname`` in the form
    expected by DEFINE: a list of lists, the first of which describes
    the inputs to the procedure and the rest of which are the lines of
    its body.  The text does not reflect formatting information used
    when the procedure was defined, such as continuation lines and
    extra spaces.
    """
    func = interp.getFunction(procname)
    if not isinstance(func, interpreter.UserFunction):
        return []
    args = func.vars
    body = [args]
    lastline = []
    for tok in func.body:
        if tok == '\n':
            body.append(lastline)
            lastline = []
        else:
            lastline.append(tok)
    if lastline:
        body.append(lastline)
    return body


# @@: fulltext, copydef

##############################
## Variable Definition

# builtin: make, local, localmake

def thing(interp, v):
    """
    THING varname
    :quoted.varname

    outputs the value of the variable whose name is the input.  If
    there is more than one such variable, the innermost local variable
    of that name is chosen.  The colon notation is an abbreviation not
    for THING but for the combination so that :FOO means THING \"FOO.
    """
    return interp.getVariable(v)
thing.logoAware = True

# @@: global

##############################
## Property Lists

# @@: ucbcompat

##############################
## Predicates

def procedurep(interp, name):
    """
    PROCEDUREP name
    PROCEDURE? name

    outputs TRUE if the input is the name of a procedure.
    """
    return interp.root.functions.has_key(name)
procedurep.logoAware = 1
procedurep.aliases = ['procedure?']

def primitivep(interp, name):
    """
    PRIMITIVEP name
    PRIMITIVE? name

    outputs TRUE if the input is the name of a primitive procedure
    (one built into Logo).
    """
    try:
        func = interp.getFunction(name)
    except LogoNameError:
        return False
    return not isinstance(func, intepreter.UserFunction)
primitivep.logoAware = True
primitivep.aliases = ['primitive?']

def definedp(interp, name):
    """
    DEFINEDP name
    DEFINED? name

    outputs TRUE if the input is the name of a user-defined procedure.
    """
    try:
        func = interp.getFunction(name)
    except LogoNameError:
        return False
    return isinstance(func, intepreter.UserFunction)
definedp.logoAware = True
definedp.aliases = ['defined?']
    
def namep(interp, name):
    """
    NAMEP name
    NAME? name

    outputs TRUE if the input is the name of a variable.
    """
    try:
        interp.getVariable(name)
        return True
    except LogoNameError:
        return False
namep.logoAware = 1
namep.aliases = ['name?']

##############################
## Queries

# @@: contents, buried, traced, stepped

def procedures(interp):
    """
    PROCEDURES

    outputs a list of the names of all unburied user-defined procedures
    in the workspace.  
    """
    return interp.functions.keys()
procedures.logoAware = 1

def names(interp):
    """
    NAMES

    outputs a contents list consisting of an empty list (indicating
    no procedure names) followed by a list of all unburied variable
    names in the workspace.
    """
    return interp.variableNames()
names.logoAware = 1

# @@: plists, namelist, pllist, nodes

##############################
## Inspection

# @@: po, poall, pops, pons, popls, pon, popl, pot, pots

##############################
## Workspace Control

def erase(interp, l):
    """
    ERASE contentslist
    ER contentslist

    command.  Erases from the workspace the procedures, variables,
    and property lists named in the input.  Primitive procedures may
    not be erased unless the variable REDEFP has the value TRUE.
    """
    if type(l) is str:
        l = [l]
    for n in l:
        interp.eraseName(n)
erase.logoAware = 1
erase.aliases = ['er']

def erall(interp):
    """
    ERALL

    command.  Erases all unburied procedures, variables, and property
    lists from the workspace.  Abbreviates ERASE CONTENTS.
    """
    # @@: No buried makes this dangerous
    erase(interp, names(interp))
    erase(interp, procedures(interp))
erall.logoAware = 1

def erps(interp):
    """
    ERPS

    command.  Erases all unburied procedures from the workspace.
    Abbreviates ERASE PROCEDURES.
    """
    erase(interp, procedures(interp))
erall.logoAware = 1

def erns(interp):
    """
    ERNS

    command.  Erases all unburied variables from the workspace.
    Abbreviates ERASE NAMES.
    """
    erase(interp, names(interp))
erns.logoAware = 1

# @@: ern, erpl, bury, buryall, buryname, unbury, unburyall
# @@: buriedp/buried?, trace, untrace, tracedp/traced?, step, unstep
# @@: steppedp/stepped?, edit/ed, editfile, edall, edps, edns, edpls,
# @@: edn, edpl, savel

def load(interp, name):
    if name.endswith('.logo'):
        _loadLogo(interp, name)
    elif name.endswith('.py'):
        _loadPython(interp, name)
    elif os.path.exists(name + ".logo"):
        _loadLogo(interp, name + ".logo")
    elif os.path.exists(name + ".py"):
        _loadPython(interp, name + ".py")
    else:
        _loadPython(interp, name)
load.logoAware = 1

def _loadLogo(interp, name):
    interp.importLogo(name)

def _loadPython(interp, name):
    if name.endswith('.py'):
        name = name[:-3]
    mod = __import__(name)
    interp.importModule(mod)

def logoHelp(interp, name):
    """
    HELP name

    command.  Prints information from the reference manual about the
    primitive procedure named by the input.
    """
    func = interp.getFunction(name)
    print func.__doc__
logoHelp.logoAware = True

# @@: gc

########################################
## Control Structures
########################################

def logoRun(interp, l):
    """
    RUN instructionlist
    
    command or operation.  Runs the Logo instructions in the input
    list; outputs if the list contains an expression that outputs.
    """
    try:
        interp.eval(l)
    except LogoOutput, e:
        return e.value
    return None
logoRun.logoAware = True
logoRun.logoName = 'run'

# @@: runresult

def logoEval(interp, l):
    return interp.eval(l)
logoEval.logoAware = 1
logoEval.logoName = 'eval'

def repeat(interp, n, block):
    """
    REPEAT num instructionlist

    command.  Runs the ``instructionlist`` repeatedly, ``num`` times.
    """
    lastVal = None
    if hasattr(interp, '_repcount'):
        lastrepcount = interp._repcount
    try:
        for i in xrange(n):
            interp._repcount = i+1
            try:
                lastVal = interp.eval(block)
            except LogoContinue:
                pass
    except LogoBreak:
        lastVal = None
        pass
    try:
        setattr(interp, '_repcount', lastrepcount)
    except NameError:
        del interp._repcount
    return lastVal
repeat.logoAware = 1

def forever(interp, block):
    if hasattr(interp, '_repcount'):
        lastrepcount = interp._repcount
    try:
        while 1:
            try:
                logoEval(interp, block)
            except LogoContinue:
                pass
    except LogoBreak:
        pass
    try:
        setattr(interp, '_repcount', lastrepcount)
    except NameError:
        del interp._repcount
forever.logoAware = 1

def repcount(interp):
    """
    REPCOUNT

    outputs the repetition count of the innermost current REPEAT or
    FOREVER, starting from 1.  If no REPEAT or FOREVER is active,
    outputs -1.
    """
    try:
        return interp._repcount
    except AttributeError:
        return -1
repcount.logoAware = True

def test(interp, val):
    interp.setVariableLocal('lasttestvalue', val)
test.logoAware = True

def iftrue(interp, lst):
    """
    IFTRUE instructionlist
    IFT instructionlist

    command.  Runs its input if the most recent TEST instruction had
    a TRUE input.  The TEST must have been in the same procedure or a
    superprocedure.
    """
    if interp.getVariable('lasttestvalue'):
        return interp.eval(lst)
iftrue.logoAware = True
iftrue.aliases = ['ift']

def iffalse(interp, lst):
    """
    IFFALSE instructionlist
    IFF instructionlist

    command.  Runs its input if the most recent TEST instruction had
    a FALSE input.  The TEST must have been in the same procedure or a
    superprocedure.
    """
    if not interp.getVariable('lasttestvalue'):
        return interp.eval(lst)
iffalse.logoAware = True
iffalse.aliases = ['iff']

def logoIf(interp, expr, block, elseBlock=None):
    """
    IF tf instructionlist
    (IF tf instructionlist1 instructionlist2)

    command.  If the first input has the value TRUE, then IF runs
    the second input.  If the first input has the value FALSE, then
    IF does nothing.  (If given a third input, IF acts like IFELSE,
    as described below.)  It is an error if the first input is not
    either TRUE or FALSE.
    """
    if expr:
        return logoEval(interp, block)
    elif elseBlock is not None:
        return logoEval(interp, elseBlock)
logoIf.logoAware = 1
logoIf.logoName = 'if'

def logoIfElse(interp, expr, trueBlock, falseBlock):
    """
    IFELSE tf instructionlist1 instructionlist2

    command or operation.  If the first input has the value TRUE, then
    IFELSE runs the second input.  If the first input has the value FALSE,
    then IFELSE runs the third input.  IFELSE outputs a value if the
    instructionlist contains an expression that outputs a value.
    """
    if expr:
        return logoEval(interp, trueBlock)
    else:
        return logoEval(interp, falseBlock)
logoIfElse.logoAware = 1
logoIfElse.logoName = 'ifelse'

def logoBreak():
    raise LogoBreak()

def stop():
    """
    STOP

    command.  Ends the running of the procedure in which it appears.
    Control is returned to the context in which that procedure was
    invoked.  The stopped procedure does not output a value.
    """
    raise LogoOutput(None)

def output(value):
    """
    OUTPUT value
    OP value
    RETURN value

    command.  Ends the running of the procedure in which it appears.
    That procedure outputs the value ``value`` to the context in which
    it was invoked.  Don't be confused: OUTPUT itself is a command,
    but the procedure that invokes OUTPUT is an operation.
    """
    raise LogoOutput(value)
output.aliases = ['op', 'return']

# @@: catch, throw, error, pause

def logoContinue():
    raise LogoContinue()
logoContinue.logoName = 'continue'
logoContinue.aliases = ['co']

def bye():
    sys.exit()

# @@: goto, tag

def ignore(value):
    """
    IGNORE value

    command.  Does nothing.  Used when an expression is evaluated for
    a side effect and its actual value is unimportant.
    """
    pass

def backtick(interp, lst):
    """
    BACKTICK list

    outputs a list equal to its input but with certain substitutions.
    If a member of the input list is the word ``,`` (comma) then the
    following member should be an instructionlist that produces an
    output when run.  That output value replaces the comma and the
    instructionlist.  If a member of the input list is the word ``@``
    (atsign) then the following member should be an instructionlist
    that outputs a list when run.  The members of that list replace the
    @ and the instructionlist.  Example::

        show `[foo baz ,[bf [a b c]] garply @[bf [a b c]]]

    will print::

        [foo baz [b c] garply b c]
    """
    result = []
    remaining = lst
    while remaining:
        if remaining[0] == ',':
            result.append(interp.eval(remaining[1]))
            remaining = remaining[2:]
        elif remaining[0] == '@':
            result.extend(interp.eval(remaining[1]))
            remaining = remaining[2:]
        else:
            result.append(remaining[0])
            remaining = remaining[1:]
    return result
backtick.logoAware = True

def logoFor(interp, forcontrol, lst):
    """
    FOR forcontrol instructionlist

    command.  The first input must be a list containing three or four
    members: (1) a word, which will be used as the name of a local
    variable; (2) a word or list that will be evaluated as by RUN to
    determine a number, the starting value of the variable; (3) a word
    or list that will be evaluated to determine a number, the limit value
    of the variable; (4) an optional word or list that will be evaluated
    to determine the step size.  If the fourth member is missing, the
    step size will be 1 or -1 depending on whether the limit value is
    greater than or less than the starting value, respectively.
    
    The second input is an instructionlist.  The effect of FOR is to run
    that instructionlist repeatedly, assigning a new value to the control
    variable (the one named by the first member of the forcontrol list)
    each time.  First the starting value is assigned to the control
    variable.  Then the value is compared to the limit value.  FOR is
    complete when the sign of (current - limit) is the same as the sign
    of the step size.  (If no explicit step size is provided, the
    instructionlist is always run at least once.  An explicit step size
    can lead to a zero-trip FOR, e.g., FOR [I 1 0 1] ...)  Otherwise, the
    instructionlist is run, then the step is added to the current value
    of the control variable and FOR returns to the comparison step::

        ? for [i 2 7 1.5] [print :i]
        2
        3.5
        5
        6.5
        ?
    """
    var = forcontrol[0]
    start = _opRun(forcontrol[1])
    end = _opRun(forcontrol[2])
    if len(forcontrol) > 3:
        step = _opRun(forcontrol[3])
    else:
        if start > end:
            step = -1
        else:
            step = 1
    curr = start
    while 1:
        if step > 0:
            if curr > end:
                break
        else:
            if curr < end:
                break
        interp.setVariable(var, curr)
        interp.eval(lst)
        curr += step
logoFor.logoAware = True
logoFor.logoName = 'for'
    
def _opRun(interp, v):
    if isinstance(v, str):
        v = [v]
    if isinstance(v, list):
        v = interp.eval(v)
    return v

def dowhile(interp, lst, test):
    """
    DO.WHILE instructionlist tfexpression

    command.  Repeatedly evaluates the ``instructionlist`` as long as
    the evaluated ``tfexpression`` remains TRUE.  Evaluates the first
    input first, so the ``instructionlist`` is always run at least
    once.  The ``tfexpression`` must be an expressionlist whose value
    when evaluated is TRUE or FALSE.
    """
    lastVal = None
    try:
        while 1:
            try:
                lastVal = interp.eval(lst)
            except LogoContinue:
                pass
            v = interp.eval(test)
            if not v:
                break
    except LogoBreak:
        lastVal = None
        pass
    return lastVal

def logoWhile(interp, test, block):
    """
    WHILE tfexpression instructionlist

    command.  Repeatedly evaluates the ``instructionlist`` as long as
    the evaluated ``tfexpression`` remains TRUE.  Evaluates the first
    input first, so the ``instructionlist`` may never be run at all.
    The ``tfexpression`` must be an expressionlist whose value when
    evaluated is TRUE or FALSE.
    """
    lastVal = None
    try:
        while logoEval(interp, test):
            try:
                lastVal = logoEval(interp, block)
            except LogoContinue:
                pass
    except LogoBreak:
        lastVal = None
        pass
    return lastVal
logoWhile.logoAware = 1
logoWhile.logoName = 'while'

# @@: continue with do.until

def logoFor(interp, name, l, block):
    for item in l:
        interp.setVariable(name, item)
        try:
            logoEval(interp, block)
        except LogoContinue:
            pass
logoFor.logoAware = 1
logoFor.logoName = 'for'

def dowhile(interp, block, clause):
    try:
        logoEval(interp, block)
    except LogoContinue:
        pass
    logoWhile(interp, clause, block)
dowhile.logoAware = 1

def until(interp, clause, block):
    while not logoEval(interp, clause):
        try:
            logoEval(block)
        except LogoContinue:
            pass
until.logoAware = 1

def dountil(interp, block, clause):
    try:
        logoEval(interp, block)
    except LogoContinue:
        pass
    until(interp, clause, block)
dountil.logoAware = 1

########################################
## PyLogo primitives
########################################

def logoAssert(value, message=None):
    if message is None:
        assert value
    else:
        assert value, message
logoAssert.logoName = 'assert'

def assertequal(value1, value2, message=None):
    if value1 != value2:
        if message:
            message += '; '
        message = (message or '') + '%r != %r' % (value1, value2)
        raise AssertionError, message
        
def function(interp, name, default=NoDefault):
    if default is NoDefault:
        return interp.getFunc(name)
    else:
        try:
            return interp.getFunc(name)
        except LogoNameError:
            return default
function.logoAware = True
function.arity = 2

def catch(interp, block, *args):
    assert not len(args)%2, "You must provide a block and a list of exceptions and block handlers for those exceptions (and odd number of arguments)"
    try:
        value = logoEval(interp, block)
    except Exception, e:
        handler = None
        while 1:
            if not args:
                break
            if isinstance(args[0], str):
                if e.__class__.__name__.lower() == args[0].lower():
                    handler = args[1]
                    break
            elif isinstance(e, args[0]):
                handler = args[1]
                break
            args = args[2:]
        if not handler:
            raise
        interp.setVariable('exception', e)
        value = logoEval(interp, block)
    return value
catch.arity = 3

def logoGetattr(obj, attr, *args):
    return getattr(obj, attr, *args)
logoGetattr.logoName = 'getattr'

def logoSetattr(obj, attr, *args):
    return setattr(obj, attr, *args)
logoSetattr.logoName = 'setattr'

def logoNone():
    return None
logoNone.logoName = 'none'

def logoTrue():
    return True
logoTrue.logoName = 'true'

def logoFalse():
    return False
logoFalse.logoName = 'false'

_spawnnum = 0
_spawnnumLock = threading.Lock()
def spawn(interp, block, starter=None):
    global _spawnnum
    _spawnnumLock.acquire()
    try:
        mynum = _spawnnum + 1
        _spawnnum += 1
    finally:
        _spawnnumLock.release()
    interp = interp.new()
    if starter:
        interp.eval(block)
        block = starter
    threadname = 'thread_%i' % mynum
    interp.setVariableLocal('threadname', threadname)
    t = threading.Thread(target=logoEval, args=(interp, block),
                         name=threadname)
    t.start()
    return threadname
spawn.logoAware = True

def wait(sec):
    time.sleep(sec)

def timestamp():
    return time.time()

def startsync(interp):
    interp.setVariableLocal('synctimestamp', time.time())
startsync.logoAware = True

def sync(interp, sec):
    last = interp.getVariable('synctimestamp')
    now = time.time()
    t = last+sec-now
    if t > 0:
        time.sleep(t)
    interp.setVariable('synctimestamp', time.time())
sync.logoAware = True

def logoImport(interp, name):
    if isinstance(name, list):
        name = '.'.join(name)
    try:
        interp.importModule(name)
    except ImportError:
        #try:
            interp.importModule('pylogo.%s' % name)
        #except ImportError:
        #    interp.importModule('src.%s' % name)
logoImport.logoAware = True
logoImport.logoName = 'import'

def newdict(lst=None):
    if lst:
        if len(lst)%2:
            raise LogoError("You must give NEWDICT a list with an even number of items",
                            description="Invalid function call")
        items = []
        while 1:
            if not lst:
                break
            items.append((lst[0], lst[1]))
            lst = lst[2:]
        return dict(items)
    else:
        return {}

def keys(d):
    return d.keys()

def values(d):
    return d.values()

def items(d):
    return d.items()

def call(interp, func, *args):
    if isinstance(func, str):
        func = interp.getFunction(func)
    return func(*args)
call.logoAware = True

def logoNew(interp, cls):
    if getattr(cls, 'logoAware', False):
        inst = cls(interp)
    else:
        inst = cls()
    return inst
logoNew.logoAware = True
logoNew.logoName = 'new'

#def builtins_main(interp):
#    logoImport(interp, 'pylogo.logo_turtle')
