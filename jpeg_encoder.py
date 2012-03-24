import Image
import math
import operator

from util import PythonF5Random as F5Random
from util import Permutation
from util import BreakException
from util import EmbedData
from util import JPEG_NATURAL_ORDER
from util import create_array

from huffman import Huffman
from DCT import DCT

def eight_byte(first, second):
    return (first << 4) + second

class JpegInfo(object):
    precision = 8
    comp_num = 3
    com_id = [1, 2, 3]
    ss = 0
    se = 63
    ah = 0
    al = 0
    hsamp_factor = [2, 1, 1]
    vsamp_factor = [2, 1, 1]
    qtable_number = [0, 1, 1]
    dctable_number = [0, 1, 1]
    actable_number = [0, 1, 1]

    def __init__(self, image, comment):
        self.components   = create_array(None, self.comp_num)
        self.comp_width   = create_array(0, self.comp_num)
        self.comp_height  = create_array(0, self.comp_num)
        self.block_width  = create_array(0, self.comp_num)
        self.block_height = create_array(0, self.comp_num)

        self.comment = comment
        self.image_width, self.image_height = image.size
        self.pixels = image.load()

        self.get_ycc_array()

    def down_sample(self, C, comp):
        def cal_result(inrow, incol, bias):
            return sum([C[inrow][incol], 
                    C[inrow][incol+1],
                    C[inrow+1][incol],
                    C[inrow+1][incol+1],
                    bias]) / 4.0

        return [[cal_result(outrow << 1, outcol << 1, outcol % 2 + 1)
                for outcol in range(self.comp_width[comp])] 
                for outrow in range(self.comp_height[comp])]

    def get_ycc_array(self):
        max_hsamp_factor = max(self.hsamp_factor)
        max_vsamp_factor = max(self.vsamp_factor)

        for i in range(self.comp_num):
            self.comp_width[i] = int(math.ceil(self.image_width / 8.0) * 8)
            self.comp_width[i] = self.comp_width[i] / max_hsamp_factor * self.hsamp_factor[i]
            self.block_width[i] = int(math.ceil(self.comp_width[i] / 8.0))

            self.comp_height[i] = int(math.ceil(self.image_height / 8.0) * 8)
            self.comp_height[i] = self.comp_height[i] / max_vsamp_factor * self.vsamp_factor[i]
            self.block_height[i] = int(math.ceil(self.comp_height[i] / 8.0))

        values = self.pixels
        Y  = create_array(0, self.comp_height[0], self.comp_width[0])
        Cb = create_array(0, self.comp_height[0], self.comp_width[0])
        Cr = create_array(0, self.comp_height[0], self.comp_width[0])

        for y in range(self.image_height):
            for x in range(self.image_width):
                r, g, b = values[x, y]
                Y[y][x]  =  0.299   * r + 0.587   * g + 0.114   * b
                Cb[y][x] = -0.16874 * r - 0.33126 * g + 0.5     * b + 128
                Cr[y][x] =  0.5     * r - 0.41869 * g - 0.08131 * b + 128

        self.components = [Y, self.down_sample(Cb, 1), self.down_sample(Cr, 2)]

    def get_comment(self):
        return self.comment

class JpegEncoder(object):
    def __init__(self, image, quality, out, comment):
        self.quality = quality
        self.jpeg_obj = JpegInfo(image, comment)

        self.image_width, self.image_height = image.size
        self.out = out

        self.dct = DCT(self.quality)
        self.huf = Huffman(*image.size)

    def compress(self, embedded_data=None, password='abc123'):
        self.embedded_data = EmbedData(embedded_data) if embedded_data else None
        self.password = password

        self.write_headers()
        self.write_compressed_data()
        self.write_eoi()
        self.out.flush()

    def get_quality(self):
        return self.quality

    def set_quality(self, quality):
        self.quality = quality
        self.dct = DCT(quality)

    def write_array(self, data):
        length = ((data[2] & 0xff) << 8) + (data[3] & 0xff) + 2
        self.out.write(bytearray(data[:length]))

    def write_marker(self, data):
        self.out.write(bytearray(data[:2]))

    def write_eoi(self):
        EOI = [0xff, 0xD9]
        self.write_marker(EOI)

    def write_headers(self):
        SOI = [0xff, 0xD8]
        self.write_marker(SOI)

        JFIF = [0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 
                0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 
                0x00, 0x01, 0x00, 0x01, 0x00, 0x00]
        self.write_array(JFIF)

        comment = self.jpeg_obj.get_comment()
        if comment:
            length = len(comment)
            COM = [0xff, 0xfe, length >> 8 & 0xff, length & 0xff]
            COM.extend(comment)
            self.write_array(COM)

        DQT = [0xff, 0xdb, 0x00, 0x84]
        for k in range(2):
            DQT.append(k)
            DQT.extend([self.dct.quantum[k][JPEG_NATURAL_ORDER[i]] for i in range(64)])
        self.write_array(DQT)

        SOF = [0xff, 0xc0, 0x00, 0x11, 
                self.jpeg_obj.precision, 
                self.jpeg_obj.image_height >> 8 & 0xff, 
                self.jpeg_obj.image_height & 0xff, 
                self.jpeg_obj.image_width >> 8 & 0xff, 
                self.jpeg_obj.image_width & 0xff, 
                self.jpeg_obj.comp_num]
        for i in range(self.jpeg_obj.comp_num):
            SOF.append(self.jpeg_obj.com_id[i])
            SOF.append(eight_byte(self.jpeg_obj.hsamp_factor[i], self.jpeg_obj.vsamp_factor[i]))
            SOF.append(self.jpeg_obj.qtable_number[i])
        self.write_array(SOF)
        
        DHT = [0xff, 0xc4, 0, 0]
        for i in range(4):
            DHT.extend(self.huf.BITS[i])
            DHT.extend(self.huf.VAL[i])

        DHT[2] = len(DHT) - 2 >> 8 & 0xff
        DHT[3] = len(DHT) - 2 & 0xff
        self.write_array(DHT)

        SOS = [0] * 14
        SOS = [0xff, 0xda, 0x00, 0x0c, self.jpeg_obj.comp_num]
        for i in range(self.jpeg_obj.comp_num):
            SOS.append(self.jpeg_obj.com_id[i])
            SOS.append(eight_byte(self.jpeg_obj.dctable_number[i], self.jpeg_obj.actable_number[i]))

        SOS.append(self.jpeg_obj.ss)
        SOS.append(self.jpeg_obj.se)
        SOS.append(eight_byte(self.jpeg_obj.ah, self.jpeg_obj.al))
        self.write_array(SOS)

    def _get_coeff(self):
        dct_array1 = create_array(0.0, 8, 8)
        dct_array2 = create_array(0.0, 8, 8)
        dct_array3 = create_array(0, 64)

        coeff = []
        for r in range(min(self.jpeg_obj.block_height)):
            for c in range(min(self.jpeg_obj.block_width)):
                xpos = c * 8
                ypos = r * 8
                for comp in range(self.jpeg_obj.comp_num):
                    indata = self.jpeg_obj.components[comp]
                    maxa = self.image_height / 2 * self.jpeg_obj.vsamp_factor[comp] - 1
                    maxb = self.image_width / 2 * self.jpeg_obj.hsamp_factor[comp] - 1

                    for i in range(self.jpeg_obj.vsamp_factor[comp]):
                        for j in range(self.jpeg_obj.hsamp_factor[comp]):
                            ia = ypos * self.jpeg_obj.vsamp_factor[comp] + i * 8
                            ib = xpos * self.jpeg_obj.hsamp_factor[comp] + j * 8

                            for a in range(8):
                                for b in range(8):
                                    dct_array1[a][b] = indata[min(ia+a, maxa)][min(ib+b, maxb)]

                            dct_array2 = self.dct.forward_dct(dct_array1)
                            dct_array3 = self.dct.quantize_block(dct_array2, 
                                    self.jpeg_obj.qtable_number[comp])
                            coeff.extend(dct_array3[:64])
        return coeff

    def write_compressed_data(self):
        tmp = 0

        last_dc_value = create_array(0, self.jpeg_obj.comp_num)
        zero_array = create_array(0, 64)
        width, height = 0, 0

        min_block_width = min(self.jpeg_obj.block_width)
        min_block_height = min(self.jpeg_obj.block_height)


        print 'DCT/quantisation starts'
        print self.image_width, 'x', self.image_height

        coeff = self._get_coeff()
        coeff_count = len(coeff)

        print 'got %d DCT AC/DC coefficients' % coeff_count
        _changed, _embedded, _examined, _expected, _one, _large, _thrown, _zero = 0, 0, 0, 0, 0, 0, 0, 0
        shuffled_index = 0
        for i in range(coeff_count):
            if i % 64 == 0:
                continue
            if coeff[i] == 1 or coeff[i] == -1:
                _one += 1
            if coeff[i] == 0:
                _zero += 1

        _large = coeff_count - _zero - _one - coeff_count / 64
        _expected = _large + int(0.49 * _one)

        print 'one=', _one
        print 'large=', _large

        print 'expected capacity: %d bits' % _expected
        print 'expected capacity with'
        for i in range(1, 8):
            n = (1 << i) - 1
            usable = _expected * i / n - _expected * i / n % n
            #changed = coeff_count - _zero - coeff_count / 64
            #changed = changed * i / n - changed * i / n % n
            #changed = n * changed / (n + 1) / i
            changed = _large - _large % (n + 1)
            changed = (changed + _one + _one / 2 - _one / (n + 1)) / (n + 1)
            usable /= 8
            if usable == 0:
                break
            if i == 1:
                print 'default'
            else:
                print '(1, %d, %d)' % (n, i)

            print 'code: %d bytes (efficiency: %d.%d bits per change)' % (usable, usable * 8 / changed, usable * 80 / changed % 10)

        if self.embedded_data is not None:
            print 'permutation starts'
            random = F5Random(self.password)
            permutation = Permutation(coeff_count, random)

            next_bit_to_embed = 0
            byte_to_embed = len(self.embedded_data)
            available_bits_to_embed = 0

            print 'Embedding of %d bits (%d+4 bytes)' % (byte_to_embed * 8 + 32, byte_to_embed)

            if byte_to_embed > 0x007fffff:
                byte_to_embed = 0x007ffff

            for i in range(1, 8):
                self.n = (1 << i) - 1
                usable = _expected * i / self.n - _expected * i / self.n % self.n
                usable /= 8
                if usable == 0:
                    break
                if usable < byte_to_embed + 4:
                    break

            k = i - 1
            self.n = (1 << k) - 1

            if self.n == 0:
                print 'using default code, file will not fit'
                self.n = 1
            elif self.n == 1:
                print 'using default code'
            else:
                print 'using (1, %d, %d) code' % (self.n, k)

            byte_to_embed |= k << 24

            byte_to_embed ^= random.get_next_byte()
            byte_to_embed ^= random.get_next_byte() << 8
            byte_to_embed ^= random.get_next_byte() << 16
            byte_to_embed ^= random.get_next_byte() << 24
            next_bit_to_embed = byte_to_embed & 1
            byte_to_embed >>= 1
            available_bits_to_embed = 31
            _embedded += 1

            if self.n > 1:
                code_word = [0] * self.n
                is_last_byte = False

                for i in range(coeff_count):
                    shuffled_index = permutation.get_shuffled(i)
                    if shuffled_index % 64 == 0:
                        continue
                    if coeff[shuffled_index] == 0:
                        continue
                    if coeff[shuffled_index] > 0:
                        if (coeff[shuffled_index] & 1) != next_bit_to_embed:
                            coeff[shuffled_index] -= 1
                            _changed +=1
                    else:
                        if (coeff[shuffled_index] & 1) == next_bit_to_embed:
                            coeff[shuffled_index] += 1
                            _changed += 1
                    
                    if coeff[shuffled_index] != 0:
                        if available_bits_to_embed == 0:
                            break
                        next_bit_to_embed = byte_to_embed & 1
                        byte_to_embed >>= 1
                        available_bits_to_embed -= 1
                        _embedded += 1
                    else:
                        _thrown += 1

                start_of_n = i + 1
                try:
                    while not is_last_byte:
                        k_bits_to_embed = 0
                        for i in range(k):
                            if available_bits_to_embed == 0:
                                if not self.embedded_data.available():
                                    is_last_byte = True
                                    break
                                byte_to_embed = self.embedded_data.read()
                                byte_to_embed ^= random.get_next_byte()
                                available_bits_to_embed = 8
                            next_bit_to_embed = byte_to_embed & 1
                            byte_to_embed >>= 1
                            available_bits_to_embed -= 1
                            k_bits_to_embed |= next_bit_to_embed << i
                            _embedded += 1

                        while True:
                            j = start_of_n - 1
                            i = 0
                            while i < self.n:
                                j += 1
                                if j >= coeff_count:
                                    print 'capacity exhausted.'
                                    raise BreakException()
                                shuffled_index = permutation.get_shuffled(j)
                                if not shuffled_index % 64:
                                    continue
                                if not coeff[shuffled_index]:
                                    continue
                                code_word[i] = shuffled_index
                                i += 1
                            end_of_n = j + 1
                            vhash = 0
                            for i in range(self.n):
                                if coeff[code_word[i]] > 0:
                                    extracted_bit = coeff[code_word[i]] & 1
                                else:
                                    extracted_bit = 1 - (coeff[code_word[i]] & 1)
                                if extracted_bit == 1:
                                    vhash ^= i + 1
                            i = vhash ^ k_bits_to_embed
                            if not i:
                                break
                            i -= 1
                            if coeff[code_word[i]] > 0:
                                coeff[code_word[i]] -= 1
                            else:
                                coeff[code_word[i]] += 1
                            _changed += 1

                            if not coeff[code_word[i]]:
                                _thrown += 1
                            else:
                                break

                        start_of_n = end_of_n
                except BreakException:
                    pass
            else:
                for i in range(coeff_count):
                    shuffled_index = permutation.get_shuffled(i)
                    if shuffled_index % 64 == 0:
                        continue
                    if coeff[shuffled_index] == 0:
                        continue

                    _examined += 1
                    if coeff[shuffled_index] > 0:
                        if (coeff[shuffled_index] & 1) != next_bit_to_embed:
                            coeff[shuffled_index] -= 1
                            _changed +=1
                    else:
                        if (coeff[shuffled_index] & 1) == next_bit_to_embed:
                            coeff[shuffled_index] += 1
                            _changed -= 1
                    if coeff[shuffled_index] != 0:
                        if available_bits_to_embed == 0:
                            if not self.embedded_data.available():
                                break
                            byte_to_embed = self.embedded_data.read()
                            byte_to_embed ^= random.getNextByte()
                            available_bits_to_embed = 8
                        next_bit_to_embed = byte_to_embed & 1
                        byte_to_embed >>= 1
                        available_bits_to_embed -= 1
                        _embedded += 1
                    else:
                        _thrown += 1
            if _examined > 0:
                print _examined, 'coefficients examined'
            print _changed, 'coefficients changed (efficiency:,', _embedded / _changed, '.', _embedded * 10 / _changed % 10, 'bits per change'
            print _thrown, 'coefficients thrown (zeroed)'
            print _embedded, 'bits (', _embedded / 8, 'bytes) embedded'

        print 'starting hufman encoding'
        shuffled_index = 0

        for r in range(min_block_height):
            for c in range(min_block_width):
                for comp in range(self.jpeg_obj.comp_num):
                    for i in range(self.jpeg_obj.vsamp_factor[comp]):
                        for j in range(self.jpeg_obj.hsamp_factor[comp]):
                            dct_array3 = coeff[shuffled_index:shuffled_index+64]
                            self.huf.huffman_block_encoder(self.out, dct_array3, last_dc_value[comp],
                                    self.jpeg_obj.dctable_number[comp], self.jpeg_obj.actable_number[comp])
                            last_dc_value[comp] = dct_array3[0]
                            shuffled_index += 64
        
        self.huf.flush_buffer(self.out)
