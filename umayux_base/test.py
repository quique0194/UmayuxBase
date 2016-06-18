import socket
import time
import threading
import signal
import sys

def singleton(cls):
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls


@singleton
class Hola(object):
    A = 2
    B = 3

h = Hola()
h.A = 34
i = Hola()
print h.A, i.A