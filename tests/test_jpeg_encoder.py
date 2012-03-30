#coding: utf-8
import unittest
import sys
import os
import struct
import StringIO
import logging

import Image
import jpype
import optparse

tests_dir = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(tests_dir, '..'))
import jpeg_encoder
from jpeg_encoder import JpegInfo, JpegEncoder
from test_util import JavaF5Random
from test_util import F5TestCase
from huffman import Huffman

class JpegInfoTest(F5TestCase):
    def test_init(self):
        image_path = os.path.join(tests_dir, 'origin.jpg')
        image = jpype.JClass('java.awt.Toolkit').getDefaultToolkit().getImage(image_path)
        b = jpype.JClass('james.JpegInfo')(image, '')
        b = jpype.JClass('james.JpegInfo')(image, '')
        bc = b.Components

        image = Image.open(image_path)
        a = JpegInfo(image, '')
        ac = a.components

        self.assertEqual(len(ac), len(bc))
        for i in range(len(ac)):
            self.assertEqual(len(ac[i]), len(bc[i]))
            for j in range(len(ac[i])):
                self.assertEqual(len(ac[i][j]), len(bc[i][j]))
                for k in range(len(ac[i][j])):
                    self.assertAlmostEqual(float(ac[i][j][k]), float(bc[i][j][k]), places=4)

        self.assertEqual(len(a.block_width), len(b.BlockWidth))
        for i in range(len(a.block_width)):
            self.assertEqual(a.block_width[i], b.BlockWidth[i])

class HuffmanTest(F5TestCase):
    def test_init(self):
        huffman = Huffman(100, 100)
        pydc = huffman.dc_matrix
        pyac = huffman.ac_matrix
        huffman = jpype.JClass('james.Huffman')(100, 100)
        jadc = huffman.DC_matrix
        jaac = huffman.AC_matrix

        def check(py, ja):
            self.assertEqual(len(py), len(ja))
            for i in range(len(py)):
                self.assertEqual(len(py[i]), len(ja[i]))
                for j in range(len(py[i])):
                    self.assertEqual(len(py[i][j]), len(ja[i][j]))
                    for k in range(len(py[i][j])):
                        self.assertEqual(py[i][j][k], ja[i][j][k], '%d %d %d %d %d' % (i, j, k, py[i][j][k], ja[i][j][k])) 
                        
        check(pyac, jaac)
        check(pydc, jadc)

class JpegEncoderTest(F5TestCase):
    def _test_compress(self, embed_data):
        image_path = os.path.join(tests_dir, 'origin.jpg')

        jaoutput = jpype.JClass('java.io.ByteArrayOutputStream')()
        jaimage = jpype.JClass('java.awt.Toolkit').getDefaultToolkit().getImage(image_path)
        jaencoder = jpype.JClass('james.JpegEncoder')(jaimage, 80, jaoutput, '')
        if embed_data:
            jaencoder.Compress(jpype.JClass('java.io.ByteArrayInputStream')(
                jpype.java.lang.String(embed_data.decode('utf-8')).getBytes()), 'abc123')
        else:
            jaencoder.Compress()
        jaarray = jaoutput.toByteArray()

        jpeg_encoder.F5Random = JavaF5Random
        pyoutput = StringIO.StringIO()
        pyimage = Image.open(image_path)
        pyencoder = JpegEncoder(pyimage, 80, pyoutput, '')
        pyencoder.compress(embed_data, 'abc123')
        pyarray = pyoutput.getvalue()
        pyoutput.close()

        self.assertEqual(len(jaarray), len(pyarray), 'length is not same')
        for i in range(len(jaarray)):
            aa = int(jaarray[i])
            bb = struct.unpack('b', pyarray[i])[0]
            self.assertEqual(aa, bb, '%d %d %d' % (i, aa, bb))

    def test_compress_no_embedded_data(self):
        self._test_compress(None)

    def test_compress_with_short_embedded_data(self):
        self._test_compress('i')

    def test_compress_with_long_embedded_data(self):
        self._test_compress('test eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeembed\n')
        
    def test_compress_with_chinese_embedded_data(self):
        self._test_compress('我的测试用例')

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="Usage: %prog [options] [args]")
    parser.add_option('-q', '--quiet', action='store_true')
    parser.add_option('-v', '--verbose', action='store_true')
    options, args = parser.parse_args()
    logging.basicConfig(format='%(asctime)-15s [%(name)-9s] %(message)s', 
            level=options.quiet and logging.ERROR
                or options.verbose and logging.DEBUG or logging.INFO)

    unittest.main()

