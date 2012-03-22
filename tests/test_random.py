import unittest
import Image
import sys, os
import json
sys.path.insert(0, os.path.abspath('.'))
from jpeg_encoder import JpegInfo, JpegEncoder, F5Random
from huffman import Huffman
from subprocess import check_output
import jpype
import time
import StringIO
import struct

class F5RandomTest(unittest.TestCase):
    def test_random_next_byte(self):
        password = 'abc123'
        N = 100


        pyrandom = F5Random(password)

        for i in range(N):
            jarandom.engineNextBytes(b)
            self.assertEqual(int(b[0]), pyrandom.get_next_byte())

if __name__ == '__main__':
    #sys.path.insert(0, '/home/jackfengji/douban/f5-steganography/build')
    jpype.startJVM(jpype.getDefaultJVMPath(), '-Xdebug -Xrunjdwp:transport=dt_shmem,server=n,address=javadebug,onthrow=<FQ exception class name>,suspend=y,onuncaught=<y/n>')
    unittest.main()
    jpype.shutdownJVM()

