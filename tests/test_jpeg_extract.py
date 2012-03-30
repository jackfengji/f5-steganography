import unittest
import sys, os
import time
import StringIO
import struct
import jpype
import optparse
import logging

tests_dir = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(tests_dir, '..'))
import jpeg_extract
from test_util import JavaF5Random
from test_util import F5TestCase
from jpeg_extract import JpegExtract

class JpegExtractTest(F5TestCase):

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
    parser = optparse.OptionParser(usage="Usage: %prog [options] [args]")
    parser.add_option('-q', '--quiet', action='store_true')
    parser.add_option('-v', '--verbose', action='store_true')
    options, args = parser.parse_args()
    logging.basicConfig(format='%(asctime)-15s [%(name)-9s] %(message)s', 
            level=options.quiet and logging.ERROR
                or options.verbose and logging.DEBUG or logging.INFO)

    unittest.main()
