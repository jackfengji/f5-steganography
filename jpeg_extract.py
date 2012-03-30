from huffman_decode import HuffmanDecode
from util import PythonF5Random as F5Random
from util import BreakException
from util import Permutation
import logging

logger = logging.getLogger('jpeg_decoder')

class JpegExtract(object):
    de_zig_zag = [
            0, 1, 5, 6, 14, 15, 27, 28, 2, 4, 7, 13, 16, 26, 29, 
            42, 3, 8, 12, 17, 25, 30, 41, 43, 9, 11, 18, 24, 31, 
            40, 44, 53, 10, 19, 23, 32, 39, 45, 52, 54, 20, 22, 
            33, 38, 46, 51, 55, 60, 21, 34, 37, 47, 50, 56, 59, 
            61, 35, 36, 48, 49, 57, 58, 62, 63]

    def __init__(self, out, password):
        self.out = out
        self.password = password

    def write_extracted_byte(self):
        self.extracted_byte ^= self.f5random.get_next_byte()
        self.out.write(chr(self.extracted_byte & 0xff))

        self.extracted_byte = 0
        self.available_extracted_bits = 0
        self.n_bytes_extracted += 1

    def cal_embedded_length(self, permutation, coeff):
        self.extracted_file_length = 0
        self.pos = -1
        i = 0

        while i < 32:
            self.pos += 1
            shuffled_index = permutation.get_shuffled(self.pos)
            if shuffled_index % 64 == 0:
                continue
            cc = coeff[shuffled_index - shuffled_index % 64 + self.de_zig_zag[shuffled_index % 64]]
            if cc == 0:
                continue
            elif cc > 0:
                extracted_bit = cc & 1
            else:
                extracted_bit = 1 - (cc & 1)

            self.extracted_file_length |= extracted_bit << i
            i += 1

        self.extracted_file_length ^= self.f5random.get_next_byte()
        self.extracted_file_length ^= self.f5random.get_next_byte() << 8
        self.extracted_file_length ^= self.f5random.get_next_byte() << 16
        self.extracted_file_length ^= self.f5random.get_next_byte() << 24

    def extract(self, data):
        hd = HuffmanDecode(data)
        logger.info('huffman decoding starts')
        coeff = hd.decode()

        logger.info('permutation starts')
        self.f5random = F5Random(self.password)
        permutation = Permutation(len(coeff), self.f5random)
        logger.info('%d indices shuffled' % len(coeff))

        self.extracted_byte = 0
        self.available_extracted_bits = 0
        self.n_bytes_extracted = 0
        self.extracted_bit = 0

        logger.info('extraction starts')

        self.cal_embedded_length(permutation, coeff)
        k = (self.extracted_file_length >> 24) % 32
        n = (1 << k) - 1
        self.extracted_file_length &= 0x007fffff
        logger.info('length of embedded file: %d bytes' % self.extracted_file_length)

        if n > 1:
            vhash = 0
            logger.info('(1, %d, %d) code used' % (n, k))

            try:
                while True:
                    vhash = 0
                    code = 1
                    while code <= n:
                        self.pos += 1
                        if self.pos >= len(coeff):
                            raise BreakException()
                        shuffled_index = permutation.get_shuffled(self.pos)
                        if shuffled_index % 64 == 0:
                            continue
                        shuffled_index = shuffled_index - shuffled_index % 64 + self.de_zig_zag[shuffled_index % 64]
                        if coeff[shuffled_index] == 0:
                            continue
                        if coeff[shuffled_index] > 0:
                            extracted_bit = coeff[shuffled_index] & 1
                        else:
                            extracted_bit = 1 - (coeff[shuffled_index] & 1)
                        if extracted_bit == 1:
                            vhash ^= code
                        code += 1

                    for i in range(k):
                        self.extracted_byte |= (vhash >> i & 1) << self.available_extracted_bits
                        self.available_extracted_bits += 1
                        if self.available_extracted_bits == 8:
                            self.write_extracted_byte()
                            if self.n_bytes_extracted == self.extracted_file_length:
                                raise BreakException()
            except BreakException:
                pass
        else:
            logger.info('default code used')
            while self.pos < len(coeff):
                self.pos += 1
                shuffled_index = permutation.get_shuffled(self.pos)
                if shuffled_index % 64 == 0:
                    continue
                shuffled_index = shuffled_index - shuffled_index % 64 + self.de_zig_zag[shuffled_index % 64]
                if coeff[shuffled_index] == 0:
                    continue
                if coeff[shuffled_index] > 0:
                    extracted_bit = coeff[shuffled_index] & 1
                else:
                    extracted_bit = 1 - (coeff[shuffled_index] & 1)
                self.extracted_byte |= extracted_bit << self.available_extracted_bits
                self.available_extracted_bits += 1

                if self.available_extracted_bits == 8:
                    self.write_extracted_byte()
                    if self.n_bytes_extracted == self.extracted_file_length:
                        break

        if self.n_bytes_extracted != self.extracted_file_length:
            logger.info('incomplete file: only %d of %d bytes extracted' % (self.n_bytes_extracted, self.extracted_file_length))
