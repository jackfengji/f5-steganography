import unittest
import sys, os
import time
import StringIO
import struct
import jpype

tests_dir = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(tests_dir, '..'))
import jpeg_extract
from util import JavaF5Random
from jpeg_extract import JpegExtract

class JpegExtractTest(unittest.TestCase):
    def test_extract_with_compressed_data(self):
        image_path = os.path.join(tests_dir, 'encoded.jpg')
        password = 'abc123'

        jafile = jpype.JClass('java.io.File')(image_path)
        jainput = jpype.JClass('java.io.FileInputStream')(jafile)
        jaoutput = jpype.JClass('java.io.ByteArrayOutputStream')()
        jaextract = jpype.JClass('net.f5.Extract')
        jaextract.extract(jainput, jafile.length(), jaoutput, password)
        jaarray = jaoutput.toByteArray()

        #from pydev import pydevd
        #pydevd.settrace('192.168.22.1', port=12345, stdoutToServer=True, stderrToServer=True)
        jpeg_extract.F5Random = JavaF5Random
        pyoutput = StringIO.StringIO()
        pyinput = open(image_path, 'rb')
        JpegExtract.extract(pyinput.read(), pyoutput, password)
        pyarray = pyoutput.getvalue()
        pyinput.close()
        pyoutput.close()

        self.assertEqual(len(jaarray), len(pyarray))
        for i in range(len(jaarray)):
            aa = int(jaarray[i])
            bb = struct.unpack('b', pyarray[i])[0]
            self.assertEqual(aa, bb)

if __name__ == '__main__':
    classpath = '-Djava.class.path=%s' % os.path.join(os.path.dirname(__file__), 'f5.jar')
    jpype.startJVM(jpype.getDefaultJVMPath(), classpath)
    unittest.main()
    jpype.shutdownJVM()

