import unittest
import sys, os
import time
import StringIO
import struct
import jpype

tests_dir = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(tests_dir, '..'))
import jpeg_extract
from test_util import JavaF5Random
from jpeg_extract import JpegExtract

class JpegExtractTest(unittest.TestCase):

    def _extract_image(self, image_path):
        password = 'abc123'

        jafile = jpype.JClass('java.io.File')(image_path)
        jainput = jpype.JClass('java.io.FileInputStream')(jafile)
        jaoutput = jpype.JClass('java.io.ByteArrayOutputStream')()
        jaextract = jpype.JClass('net.f5.Extract')
        jaextract.extract(jainput, jafile.length(), jaoutput, password)
        jaarray = jaoutput.toByteArray()

        jpeg_extract.F5Random = JavaF5Random
        pyoutput = StringIO.StringIO()
        pyinput = open(image_path, 'rb')
        JpegExtract(pyoutput, password).extract(pyinput.read())
        pyarray = pyoutput.getvalue()
        pyinput.close()
        pyoutput.close()

        self.assertEqual(len(jaarray), len(pyarray))
        for i in range(len(jaarray)):
            aa = int(jaarray[i])
            bb = struct.unpack('b', pyarray[i])[0]
            self.assertEqual(aa, bb)

    def test_extract_short_compressed_data(self):
        self._extract_image(os.path.join(tests_dir, 'encoded_short.jpg'))

    def test_extract_long_compressed_data(self):
        self._extract_image(os.path.join(tests_dir, 'encoded_long.jpg'))

if __name__ == '__main__':
    classpath = '-Djava.class.path=%s' % os.path.join(os.path.dirname(__file__), 'f5.jar')
    jpype.startJVM(jpype.getDefaultJVMPath(), classpath)
    unittest.main()
    jpype.shutdownJVM()

