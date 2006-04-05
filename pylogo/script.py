#!/usr/bin/python

import os, sys

try:
    here = __file__
except NameError:
    here = sys.argv[0]

if os.path.basename(os.path.dirname(here)) == 'scripts':
    # Then we're probably running without having been installed
    # with setup.py...
    sys.path.append(os.path.dirname(os.path.dirname(here)))

from pylogo import Logo

def main():
    doit(sys.argv[1:])

def doit(args):
    quit_after = False
    use_ide = True
    for filename in sys.argv[1:]:
        if filename in ('-q', '--quit'):
            quit_after = True
            continue
        if filename in ('-c', '--console'):
            use_ide = False
            continue
        if filename == '-h':
            print "Usage: pylogo [OPTIONS] [FILES]"
            print "  -q or --quit     quit after loading and running files"
            print "  -c or --console  run the interpreter in the console (not the GUI)"
            sys.exit()
        Logo.importLogo(filename)

    if not quit_after:
        if use_ide:
            from pylogo import ide
            ide.main()
        else:
            Logo.inputLoop(sys.stdin, sys.stdout)
