import unittest
import Image
import sys, os
import json
sys.path.insert(0, os.path.abspath('.'))
from jpeg_encoder import JpegInfo, JpegEncoder
from huffman import Huffman
from subprocess import check_output
import jpype
import time
import StringIO
import struct

class JpegInfoTest(unittest.TestCase):
    def test_init(self):
        image = jpype.JClass('java.awt.Toolkit').getDefaultToolkit().getImage('/home/jackfengji/douban/f5/logo.jpg')
        b = jpype.JClass('james.JpegInfo')(image, '')
        b = jpype.JClass('james.JpegInfo')(image, '')
        bc = b.Components

        image = Image.open('logo.jpg')
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

class HuffmanTest(unittest.TestCase):
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

class JpegEncoderTest(unittest.TestCase):
    def test_compress_no_embedded_data(self):
        image_path = '/home/jackfengji/douban/f5/logo.jpg'

        jaoutput = jpype.JClass('java.io.ByteArrayOutputStream')()
        jaimage = jpype.JClass('java.awt.Toolkit').getDefaultToolkit().getImage(image_path)
        jaencoder = jpype.JClass('james.JpegEncoder')(jaimage, 80, jaoutput, '')
        jaencoder.Compress()
        jaarray = jaoutput.toByteArray()

        from pydev import pydevd
        #pydevd.settrace('10.0.1.98', port=12345, stdoutToServer=True, stderrToServer=True)
        pyoutput = StringIO.StringIO()
        pyimage = Image.open(image_path)
        pyencoder = JpegEncoder(pyimage, 80, pyoutput, '')
        pyencoder.compress()
        pyarray = pyoutput.getvalue()
        pyoutput.close()

        self.assertEqual(len(jaarray), len(pyarray))
        for i in range(len(jaarray)):
            aa = int(jaarray[i])
            bb = struct.unpack('b', pyarray[i])[0]
            self.assertEqual(aa, bb)

    def test_compress_with_embedded_data(self):
        image_path = '/home/jackfengji/douban/f5/logo.jpg'

        jaoutput = jpype.JClass('java.io.ByteArrayOutputStream')()
        jaimage = jpype.JClass('java.awt.Toolkit').getDefaultToolkit().getImage(image_path)
        jaencoder = jpype.JClass('james.JpegEncoder')(jaimage, 80, jaoutput, '')
        jaencoder.Compress(jpype.JClass('java.io.ByteArrayInputStream')(
            jpype.java.lang.String('test embed\n').getBytes()), 'abc123')
        jaarray = jaoutput.toByteArray()

        from pydev import pydevd
#        pydevd.settrace('10.0.1.98', port=12345, stdoutToServer=True, stderrToServer=True)
        pyoutput = StringIO.StringIO()
        pyimage = Image.open(image_path)
        pyencoder = JpegEncoder(pyimage, 80, pyoutput, '')
        pyencoder.compress('test embed\n', 'abc123')
        pyarray = pyoutput.getvalue()
        pyoutput.close()

        self.assertEqual(len(jaarray), len(pyarray), 'length is not same')
        for i in range(len(jaarray)):
            aa = int(jaarray[i])
            bb = struct.unpack('b', pyarray[i])[0]
            self.assertEqual(aa, bb, '%d %d %d' % (i, aa, bb))
        

if __name__ == '__main__':
    jpype.startJVM(jpype.getDefaultJVMPath(), '-Xdebug -Xrunjdwp:transport=dt_shmem,server=n,address=javadebug,onthrow=<FQ exception class name>,suspend=y,onuncaught=<y/n>')
    unittest.main()
    jpype.shutdownJVM()

