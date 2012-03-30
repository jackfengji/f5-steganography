import os
import jpype
import unittest
from util import F5Random

def startJVM():
    if not jpype.isJVMStarted():
        classpath = os.path.join(os.path.dirname(__file__), 'f5.jar')
        jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.class.path=%s' % classpath)

class F5TestCase(unittest.TestCase):
    def setUp(self):
        startJVM()

class JavaF5Random(F5Random):
    def __init__(self, password):
        startJVM()

        self.random = jpype.JClass('sun.security.provider.SecureRandom')()
        self.random.engineSetSeed(jpype.java.lang.String(password).getBytes())
        self.b = jpype.JArray(jpype.JByte, 1)(1)

    def get_next_byte(self):
        self.random.engineNextBytes(self.b)
        return self.b[0]
