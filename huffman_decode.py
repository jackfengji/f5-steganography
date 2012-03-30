from util import EmbedData
from util import create_array
import logging

logger = logging.getLogger('huffman_decode')

class HuffTable(object):
    def __init__(self, data, l):
        self.bits     = create_array(0, 17)
        self.huffval  = create_array(0, 256)
        self.huffcode = create_array(0, 257)
        self.huffsize = create_array(0, 257)
        self.ehufco   = create_array(0, 257)
        self.ehufsi   = create_array(0, 257)
        self.mincode  = create_array(0, 17)
        self.maxcode  = create_array(0, 18)
        self.valptr   = create_array(0, 17)

        self.data = data
        self.ln = 19 + self.get_table_data()

        self.generate_size_table()
        self.generate_code_table()
        self.order_codes()
        self.decode_tables()

    def get_table_data(self):
        count = 0
        for x in range(1, 17):
            self.bits[x] = self.get_byte()
            count += self.bits[x]

        for x in range(0, count):
            self.huffval[x] = self.get_byte()

        return count

    def generate_size_table(self):
        k, i, j = 0, 1, 1
        while True:
            if j > self.bits[i]:
                j = 1
                i += 1
                if i > 16:
                    break
            else:
                self.huffsize[k] = i
                k += 1
                j += 1

        self.huffsize[k] = 0
        self.lastk = k

    def generate_code_table(self):
        k, code, si = 0, 0, self.huffsize[0]
        while True:
            self.huffcode[k] = code
            k += 1
            code += 1

            if self.huffsize[k] == si:
                continue
            if self.huffsize[k] == 0:
                break

            while True:
                code <<= 1
                si += 1
                if self.huffsize[k] == si:
                    break

    def order_codes(self):
        k = 0
        while True:
            i = self.huffval[k]
            self.ehufco[i] = self.huffcode[k]
            self.ehufsi[i] = self.huffsize[k]
            k += 1
            if k >= self.lastk:
                break

    def decode_tables(self):
        i, j = 0, 0
        while True:
            i += 1
            if i > 16:
                return

            if self.bits[i] == 0:
                self.maxcode[i] = -1
            else:
                self.valptr[i] = j
                self.mincode[i] = self.huffcode[j]
                j += self.bits[i] - 1
                self.maxcode[i] = self.huffcode[j]
                j += 1

    def get_byte(self):
        return self.data.read()

    def get_huffval(self):
        return self.huffval

    def get_len(self):
        return self.ln

    def get_maxcode(self):
        return self.maxcode

    def get_mincode(self):
        return self.mincode

    def get_valptr(self):
        return self.valptr

class HuffmanDecode(object):
    APP = [0xe0, 0xe1, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee, 0xef]
    DRI, DNL, EOI = 0xdd, 0xdc, 0xd9
    deZZ = [[0, 0], [0, 1], [1, 0], [2, 0], [1, 1], [0, 2], [0, 3], [1, 2], [2, 1], [3, 0], [4, 0], [3, 1], [2, 2], [1, 3], [0, 4], [0, 5], [1, 4], [2, 3], [3, 2], [ 4, 1 ], [ 5, 0 ], [ 6, 0 ], [ 5, 1 ], [ 4, 2 ], [ 3, 3 ], [ 2, 4 ], [ 1, 5 ], [ 0, 6 ], [ 0, 7 ], [ 1, 6 ], [ 2, 5 ], [ 3, 4 ], [ 4, 3 ], [ 5, 2 ], [ 6, 1 ], [ 7, 0 ], [ 7, 1 ], [ 6, 2 ], [ 5, 3 ], [ 4, 4 ], [ 3, 5 ], [ 2, 6 ], [ 1, 7 ], [ 2, 7 ], [ 3, 6 ], [ 4, 5 ], [ 5, 4 ], [ 6, 3 ], [ 7, 2 ], [ 7, 3 ], [ 6, 4 ], [ 5, 5 ], [ 4, 6 ], [ 3, 7 ], [ 4, 7 ], [ 5, 6 ], [ 6, 5 ], [ 7, 4 ], [ 7, 5 ], [ 6, 6 ], [ 5, 7 ], [ 6, 7 ], [ 7, 6 ], [ 7, 7 ] ]

    de_zig_zag = [0, 1, 5, 6, 14, 15, 27, 28, 2, 4, 7, 13, 16, 26, 29, 42, 3, 8, 12, 17, 25, 30, 41, 43, 9, 11, 18, 24, 
            31, 40, 44, 53, 10, 19, 23, 32, 39, 45, 52, 54, 20, 22, 33, 38, 46, 51, 55, 60, 21, 34, 37, 47, 50, 56, 59, 61,
            35, 36, 48, 49, 57, 58, 62, 63]

    def __init__(self, data):
        self.huffval = create_array([], 4)
        self.valptr = create_array([], 4)
        self.mincode = create_array([], 4)
        self.maxcode = create_array([], 4)
        self.zz = create_array(0, 64)
        self.qnt = create_array(0, 4, 64)

        self.data = EmbedData(data)
        self.size = len(self.data)
        self.ri = 0

        while True:
            if self.get_byte() == 255:
                b = self.get_byte()
                if b == 192:
                    self.sof0()
                elif b == 196:
                    self.dht()
                elif b == 219:
                    self.dqt()
                elif b == 217 or b == 218:
                    break
                elif b in self.APP:
                    self.skip_variable()
                elif b == self.DRI:
                    self.dri()

    def available(self):
        return self.data.available()

    def get_double_four_bits(self):
        b = self.get_byte()
        return b >> 4, b & 0x0f

    def get_byte(self):
        return self.data.read()

    def get_int(self):
        return (self.get_byte() << 8) ^ self.get_byte()

    def get_next_bit(self):
        if not self.CNT:
            self.CNT = 8
            self.B = self.get_byte()
            if self.B == 255:
                self.get_byte()

        BIT = self.B & 0x80
        BIT >>= 7
        self.CNT -= 1
        self.B <<= 1
        return BIT

    def get_block_count(self):
        square = lambda x: x * x
        if self.nf == 1:
            return square((self.x + 7) / 8)
        elif self.nf == 3:
            return 6 * square((self.x + 15) / 16)
        else:
            logger.error('nf is not 1 neither 3')

    def _internal_decode(self):
        i, cd = 1, self.get_next_bit()
        while cd > self.maxcode[self.hftbl][i]:
            cd = (cd << 1) + self.get_next_bit()
            i += 1

        j = self.valptr[self.hftbl][i]
        j += cd - self.mincode[self.hftbl][i]
        return self.huffval[self.hftbl][j]

    def receive(self, sss):
        v, i = 0, 0
        while i != sss:
            i += 1
            v = (v << 1) + self.get_next_bit()
        return v

    def extend(self, v, t):
        if t == 0:
            return v
        vt = 0x01 << t - 1
        if v < vt:
            vt = (-1 << t) + 1
            v += vt
        return v

    def decode_ac_coefficients(self):
        k = 1
        self.zz = [0] * 64

        while True:
            rs = self._internal_decode()
            ssss = rs % 16
            r = rs >> 4
            if ssss == 0:
                if r == 15:
                    k += 16
                else:
                    return
            else:
                k += r
                self.zz[k] = self.extend(self.receive(ssss), ssss)
                if k == 63:
                    return
                else:
                    k += 1

    def decode(self):
        pred = create_array(0, self.nf)
        self.CNT = 0
        self.ls = self.get_int()
        self.ns = self.get_byte()

        cs = create_array(0, self.ns)
        td = create_array(0, self.ns)
        ta = create_array(0, self.ns)
        for lp in range(self.ns):
            cs[lp] = self.get_byte()
            td[lp], ta[lp] = self.get_double_four_bits()

        self.ss = self.get_byte()
        self.se = self.get_byte()
        self.ah, self.al = self.get_double_four_bits()

        buff = create_array(0, 2 * 8 * 8 * self.get_block_count())
        pos, mcu_count = 0, 0

        while True:
            for n_comp in range(0, self.nf):
                for cnt in range(self.h[n_comp] * self.v[n_comp]):
                    self.hftbl = td[n_comp] * 2
                    tmp = self._internal_decode()
                    self.diff = self.receive(tmp)
                    self.zz[0] = pred[0] + self.extend(self.diff, tmp)
                    pred[n_comp] = self.zz[0]

                    self.hftbl = ta[n_comp] * 2 + 1
                    self.decode_ac_coefficients()

                    for lp in range(64):
                        buff[pos] = self.zz[lp]
                        pos += 1

            mcu_count += 1
            if mcu_count == self.ri:
                mcu_count = 0
                self.CNT = 0
                pred[n_comp] = create_array(0, self.nf)

                self.get_byte()
                tmp_b = self.get_byte()
                if tmp_b == EOI:
                    break

            if self.available() <= 2:
                if self.available() == 2:
                    self.get_byte()
                    if self.get_byte() != self.EOI:
                        logger.error('file does not end with EOI')
                else:
                    if self.available() == 1:
                        logger.error('last byte: %X' % self.get_byte())
                    logger.error('file does not end with EOI')
                break

        return buff[:pos]

    def sof0(self):
        self.lf = self.get_int()
        self.p = self.get_byte()
        self.y = self.get_int()
        self.x = self.get_int()
        self.nf = self.get_byte()
        
        self.c = create_array(0, self.nf)
        self.h = create_array(0, self.nf)
        self.v = create_array(0, self.nf)
        self.t = create_array(0, self.nf)

        for lp in range(self.nf):
            self.c[lp] = self.get_byte()
            self.h[lp], self.v[lp] = self.get_double_four_bits()
            self.t[lp] = self.get_byte()

    def dht(self):
        self.lh = self.get_int()
        def _fill_value(index):
            ht = HuffTable(self.data, self.lh)
            self.lh -= ht.get_len()
            self.huffval[index] = ht.get_huffval()
            self.valptr[index] = ht.get_valptr()
            self.maxcode[index] = ht.get_maxcode()
            self.mincode[index] = ht.get_mincode()
        
        while self.lh > 0:
            self.tc, self.th = self.get_double_four_bits()

            if self.th == 0:
                if self.tc == 0:
                    _fill_value(0)
                else:
                    _fill_value(1)
            else:
                if self.tc == 0:
                    _fill_value(2)
                else:
                     _fill_value(3)
    
    def dqt(self):
        self.lq = self.get_int()
        self.pq, self.tq = self.get_double_four_bits()
        
        if self.tq in range(4):
            for lp in range(64):
                self.qnt[self.tq][lp] = self.get_byte()

    def dri(self):
        self.get_int()
        self.ri = self.get_int()

    def skip_variable(self):
        for i in range(self.get_int() - 2):
            self.get_byte()

