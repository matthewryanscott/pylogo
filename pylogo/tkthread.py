"""
Intended to allow multi-threaded use of Tk, by queuing up access
to Tkinter functions for execution by the main thread.  Doesn't
work right now, more or less disabled (used by logo_turtle.py)
"""

import threading

commandQueue = []
def commandPoll():
    while 1:
        try:
            command = commandQueue.pop()
        except IndexError:
            continue
        if command == 'quit':
            break
        try:
            val = command[1](*command[2], **command[3])
        except Exception, e:
            raise
            command[0].extend([True, e])
        else:
            command[0].extend([False, val])

def addQueue(func, *args, **kw):
    # Disabling:
    return func(*args, **kw)
    out = []
    commandQueue.append((out, func, args, kw))
    while 1:
        if not out:
            continue
    if out[0]:
        raise out[1]
    else:
        return out[1]

def quit():
    commandQueue.append('quit')

def start(func, *args, **kw):
    print "Start() in %s" % threading.currentThread()
    t = threading.Thread(target=func, args=args, kwargs=kw)
    t.start()
    print "Start() after in %s" % threading.currentThread()
    commandPoll()

