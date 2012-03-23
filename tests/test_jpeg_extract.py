import unittest
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from jpeg_extract import JpegExtract
import jpype
import time
import StringIO
import struct

class JpegExtractTest(unittest.TestCase):
    def test_extract_no_compress_data(self):
        image_path = '/home/jackfengji/douban/f5/logo.jpg'
        password = 'abc123'

        jafile = jpype.JClass('java.io.File')(image_path)
        jainput = jpype.JClass('java.io.FileInputStream')(jafile)
        jaoutput = jpype.JClass('java.io.ByteArrayOutputStream')()
        jaextract = jpype.JClass('net.f5.Extract')
        jaextract.extract(jainput, jafile.length(), jaoutput, password)
        jaarray = jaoutput.toByteArray()

        from pydev import pydevd
        #pydevd.settrace('192.168.22.1', port=12345, stdoutToServer=True, stderrToServer=True)
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
    jpype.startJVM(jpype.getDefaultJVMPath(), '-Xdebug -Xrunjdwp:transport=dt_shmem,server=n,address=javadebug,onthrow=<FQ exception class name>,suspend=y,onuncaught=<y/n>')
    unittest.main()
    jpype.shutdownJVM()

