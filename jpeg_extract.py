from huffman_decode import HuffmanDecode
from util import JavaF5Random as F5Random
from util import BreakException
from util import Permutation

class JpegExtract(object):
    de_zig_zag = [0, 1, 5, 6, 14, 15, 27, 28, 2, 4, 7, 13, 16, 26, 29, 42, 3, 8, 12, 17, 25, 30, 41, 43, 9, 11, 18, 24, 31, 
            40, 44, 53, 10, 19, 23, 32, 39, 45, 52, 54, 20, 22, 33, 38, 46, 51, 55, 60, 21, 34, 37, 47, 50, 56, 59, 61, 
            35, 36, 48, 49, 57, 58, 62, 63]

    @classmethod
    def extract(cls, data, out, password):
        hd = HuffmanDecode(data)
        print 'huffman decoding starts'
        coeff = hd.decode()

        print 'permutation starts'
        f5random = F5Random(password)
        permutation = Permutation(len(coeff), f5random)
        print len(coeff), 'indices shuffled'

        extracted_byte = 0
        available_extracted_bits = 0
        extracted_file_length = 0
        n_bytes_extracted = 0
        shuffled_index = 0
        extracted_bit = 0

        print 'extraction starts'
        i = -1
        while available_extracted_bits < 32:
            i += 1
            shuffled_index = permutation.get_shuffled(i)
            if shuffled_index % 64 == 0:
                continue
            shuffled_index = shuffled_index - shuffled_index % 64 + cls.de_zig_zag[shuffled_index % 64]
            if coeff[shuffled_index] == 0:
                continue
            if coeff[shuffled_index] > 0:
                extracted_bit = coeff[shuffled_index] & 1
            else:
                extracted_bit = 1 - (coeff[shuffled_index] & 1)

            extracted_file_length |= extracted_bit << available_extracted_bits
            available_extracted_bits += 1
        i += 1

        extracted_file_length ^= f5random.get_next_byte()
        extracted_file_length ^= f5random.get_next_byte() << 8
        extracted_file_length ^= f5random.get_next_byte() << 16
        extracted_file_length ^= f5random.get_next_byte() << 24

        k = (extracted_file_length >> 24) % 32
        n = (1 << k) - 1
        extracted_file_length &= 0x007fffff
        print 'length of embedded file: %d bytes' % extracted_file_length

        available_extracted_bits = 0
        if n > 0:
            start_of_n = i
            vhash = 0
            print '(1, %d, %d) code used' % (n, k)

            try:
                while True:
                    vhash = 0
                    code = 1
                    i = -1
                    while code <= n:
                        i += 1
                        if start_of_n + i >= len(coeff):
                            raise BreakException()
                        shuffled_index = permutation.get_shuffled(start_of_n + i)
                        if shuffled_index % 64 == 0:
                            continue
                        shuffled_index = shuffled_index - shuffled_index % 64 + cls.de_zig_zag[shuffled_index % 64]
                        if coeff[shuffled_index] == 0:
                            continue
                        if coeff[shuffled_index] > 0:
                            extracted_bit = coeff[shuffled_index] & 1
                        else:
                            extracted_bit = 1 - (coeff[shuffled_index] & 1)
                        if extracted_bit == 1:
                            vhash ^= code
                        code += 1
                    i += 1

                    start_of_n += i
                    for i in range(k):
                        extracted_byte |= (vhash >> i & 1) << available_extracted_bits
                        available_extracted_bits += 1
                        if available_extracted_bits == 8:
                            extracted_byte ^= f5random.get_next_byte()
                            out.write(chr(extracted_byte & 0xff))

                            extracted_byte = 0
                            available_extracted_bits = 0
                            n_bytes_extracted += 1

                            if n_bytes_extracted == extracted_file_length:
                                raise BreakException()
            except BreakException:
                pass
        else:
            print 'default code used'
            i -= 1
            while i < len(coeff):
                i += 1
                shuffled_index = permutation.get_shuffled(i)
                if shuffled_index % 64 == 0:
                    continue
                shuffled_index = shuffled_index - shuffled_index % 64 + cls.de_zig_zag[shuffled_index % 64]
                if coeff[shuffled_index] == 0:
                    continue
                if coeff[shuffled_index] > 0:
                    extracted_bit = coeff[shuffled_index] & 1
                else:
                    extracted_bit = 1 - (coeff[shuffled_index] & 1)
                extracted_byte | extracted_bit << available_extracted_bits
                available_extracted_bits += 1

                if available_extracted_bits == 8:
                    extracted_byte ^= f5random.get_next_byte()
                    out.write(chr(extracted_byte & 0xff))

                    extracted_byte = 0
                    available_extracted_bits = 0
                    n_bytes_extracted += 1
                    if n_bytes_extracted == extracted_file_length:
                        break

        if n_bytes_extracted != extracted_file_length:
            print 'incomplete file: only %d of %d bytes extracted' % (n_bytes_extracted, extracted_file_length)
