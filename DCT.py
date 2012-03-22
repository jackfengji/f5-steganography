import math

class DCT(object):
    N = 8
    QUALITY = 80
    
    def __init__(self, quality):
        self.N = 8
        self.QUALITY = 80
        self.quantum = [None] * 2
        self.divisors = [None] * 2
        self.quantum_luminance = [0] * (self.N * self.N)
        self.divisors_luminance = [0] * (self.N * self.N)
        self.quantum_chrominance = [0] * (self.N * self.N)
        self.divisors_chrominance = [0] * (self.N * self.N)

        self.init_matrix(quality)

    def init_matrix(self, quality):
        AAN_scale_factor = [1.0, 1.387039845, 1.306562965, 1.175875602, 1.0, 0.785694958, 0.541196100, 0.275899379]
        if quality <= 0:
            quality = 1
        if quality > 100:
            qulity = 100
        if quality < 50:
            quality = 5000 / quality
        else:
            quality = 200 - quality * 2

        self.quantum_luminance[0] = 16
        self.quantum_luminance[1] = 11
        self.quantum_luminance[2] = 10
        self.quantum_luminance[3] = 16
        self.quantum_luminance[4] = 24
        self.quantum_luminance[5] = 40
        self.quantum_luminance[6] = 51
        self.quantum_luminance[7] = 61
        self.quantum_luminance[8] = 12
        self.quantum_luminance[9] = 12
        self.quantum_luminance[10] = 14
        self.quantum_luminance[11] = 19
        self.quantum_luminance[12] = 26
        self.quantum_luminance[13] = 58
        self.quantum_luminance[14] = 60
        self.quantum_luminance[15] = 55
        self.quantum_luminance[16] = 14
        self.quantum_luminance[17] = 13
        self.quantum_luminance[18] = 16
        self.quantum_luminance[19] = 24
        self.quantum_luminance[20] = 40
        self.quantum_luminance[21] = 57
        self.quantum_luminance[22] = 69
        self.quantum_luminance[23] = 56
        self.quantum_luminance[24] = 14
        self.quantum_luminance[25] = 17
        self.quantum_luminance[26] = 22
        self.quantum_luminance[27] = 29
        self.quantum_luminance[28] = 51
        self.quantum_luminance[29] = 87
        self.quantum_luminance[30] = 80
        self.quantum_luminance[31] = 62
        self.quantum_luminance[32] = 18
        self.quantum_luminance[33] = 22
        self.quantum_luminance[34] = 37
        self.quantum_luminance[35] = 56
        self.quantum_luminance[36] = 68
        self.quantum_luminance[37] = 109
        self.quantum_luminance[38] = 103
        self.quantum_luminance[39] = 77
        self.quantum_luminance[40] = 24
        self.quantum_luminance[41] = 35
        self.quantum_luminance[42] = 55
        self.quantum_luminance[43] = 64
        self.quantum_luminance[44] = 81
        self.quantum_luminance[45] = 104
        self.quantum_luminance[46] = 113
        self.quantum_luminance[47] = 92
        self.quantum_luminance[48] = 49
        self.quantum_luminance[49] = 64
        self.quantum_luminance[50] = 78
        self.quantum_luminance[51] = 87
        self.quantum_luminance[52] = 103
        self.quantum_luminance[53] = 121
        self.quantum_luminance[54] = 120
        self.quantum_luminance[55] = 101
        self.quantum_luminance[56] = 72
        self.quantum_luminance[57] = 92
        self.quantum_luminance[58] = 95
        self.quantum_luminance[59] = 98
        self.quantum_luminance[60] = 112
        self.quantum_luminance[61] = 100
        self.quantum_luminance[62] = 103
        self.quantum_luminance[63] = 99

        self.quantum_chrominance[0] = 17
        self.quantum_chrominance[1] = 18
        self.quantum_chrominance[2] = 24
        self.quantum_chrominance[3] = 47
        self.quantum_chrominance[4] = 99
        self.quantum_chrominance[5] = 99
        self.quantum_chrominance[6] = 99
        self.quantum_chrominance[7] = 99
        self.quantum_chrominance[8] = 18
        self.quantum_chrominance[9] = 21
        self.quantum_chrominance[10] = 26
        self.quantum_chrominance[11] = 66
        self.quantum_chrominance[12] = 99
        self.quantum_chrominance[13] = 99
        self.quantum_chrominance[14] = 99
        self.quantum_chrominance[15] = 99
        self.quantum_chrominance[16] = 24
        self.quantum_chrominance[17] = 26
        self.quantum_chrominance[18] = 56
        self.quantum_chrominance[19] = 99
        self.quantum_chrominance[20] = 99
        self.quantum_chrominance[21] = 99
        self.quantum_chrominance[22] = 99
        self.quantum_chrominance[23] = 99
        self.quantum_chrominance[24] = 47
        self.quantum_chrominance[25] = 66
        self.quantum_chrominance[26] = 99
        self.quantum_chrominance[27] = 99
        self.quantum_chrominance[28] = 99
        self.quantum_chrominance[29] = 99
        self.quantum_chrominance[30] = 99
        self.quantum_chrominance[31] = 99
        self.quantum_chrominance[32] = 99
        self.quantum_chrominance[33] = 99
        self.quantum_chrominance[34] = 99
        self.quantum_chrominance[35] = 99
        self.quantum_chrominance[36] = 99
        self.quantum_chrominance[37] = 99
        self.quantum_chrominance[38] = 99
        self.quantum_chrominance[39] = 99
        self.quantum_chrominance[40] = 99
        self.quantum_chrominance[41] = 99
        self.quantum_chrominance[42] = 99
        self.quantum_chrominance[43] = 99
        self.quantum_chrominance[44] = 99
        self.quantum_chrominance[45] = 99
        self.quantum_chrominance[46] = 99
        self.quantum_chrominance[47] = 99
        self.quantum_chrominance[48] = 99
        self.quantum_chrominance[49] = 99
        self.quantum_chrominance[50] = 99
        self.quantum_chrominance[51] = 99
        self.quantum_chrominance[52] = 99
        self.quantum_chrominance[53] = 99
        self.quantum_chrominance[54] = 99
        self.quantum_chrominance[55] = 99
        self.quantum_chrominance[56] = 99
        self.quantum_chrominance[57] = 99
        self.quantum_chrominance[58] = 99
        self.quantum_chrominance[59] = 99
        self.quantum_chrominance[60] = 99
        self.quantum_chrominance[61] = 99
        self.quantum_chrominance[62] = 99
        self.quantum_chrominance[63] = 99

        for i in range(64):
            tmp = (self.quantum_luminance[i] * quality + 50) / 100
            self.quantum_luminance[i] = 1 if tmp <= 0 else (255 if tmp > 255 else tmp)

            tmp = (self.quantum_chrominance[i] * quality + 50) / 100
            self.quantum_chrominance[i] = 1 if tmp <= 0 else (255 if tmp > 255 else tmp)

        index = 0
        for i in range(8):
            for j in range(8):
                tmp = AAN_scale_factor[i] * AAN_scale_factor[j] * 8.0
                self.divisors_luminance[index] = 1.0 / self.quantum_luminance[index] / tmp
                self.divisors_chrominance[index] = 1.0 / self.quantum_chrominance[index] / tmp
                index += 1

        self.quantum = [self.quantum_luminance, self.quantum_chrominance]
        self.divisors = [self.divisors_luminance, self.divisors_chrominance]

    def forward_dct_extreme(self, indata):
        output = [[0.0] * self.N for i in range(0, self.N)]
        my_cos = lambda x: math.cos((2.0 * x + 1) * u * math.PI / 16)
        special = lambda x: 1.0 / math.sqrt(2) if x == 0 else 1.0
        for v in range(8):
            for u in range(8):
                for x in range(8):
                    for y in range(8):
                        output[v][u] += indata[x][y] * my_cos(x) * my_cos(y)
                output[v][u] *= 0.25 * special(u) * special(v)

        return output

    def forward_dct(self, indata):
        output = [[indata[i][j] - 128.0 for j in range(0, 8)] for i in range(0, 8)]
        for i in range(8):
            tmp0 = output[i][0] + output[i][7]
            tmp7 = output[i][0] - output[i][7]
            tmp1 = output[i][1] + output[i][6]
            tmp6 = output[i][1] - output[i][6]
            tmp2 = output[i][2] + output[i][5]
            tmp5 = output[i][2] - output[i][5]
            tmp3 = output[i][3] + output[i][4]
            tmp4 = output[i][3] - output[i][4]

            tmp10 = tmp0 + tmp3
            tmp13 = tmp0 - tmp3
            tmp11 = tmp1 + tmp2
            tmp12 = tmp1 - tmp2

            output[i][0] = tmp10 + tmp11
            output[i][4] = tmp10 - tmp11

            z1 = (tmp12 + tmp13) * 0.707106781
            output[i][2] = tmp13 + z1
            output[i][6] = tmp13 - z1

            tmp10 = tmp4 + tmp5
            tmp11 = tmp5 + tmp6
            tmp12 = tmp6 + tmp7

            z5 = (tmp10 - tmp12) * 0.382683433
            z2 = 0.541196100 * tmp10 + z5
            z4 = 1.306562965 * tmp12 + z5
            z3 = tmp11 * 0.707106781

            z11 = tmp7 + z3
            z13 = tmp7 - z3

            output[i][5] = z13 + z2
            output[i][3] = z13 - z2
            output[i][1] = z11 + z4
            output[i][7] = z11 - z4

        for i in range(8):
            tmp0 = output[0][i] + output[7][i]
            tmp7 = output[0][i] - output[7][i]
            tmp1 = output[1][i] + output[6][i]
            tmp6 = output[1][i] - output[6][i]
            tmp2 = output[2][i] + output[5][i]
            tmp5 = output[2][i] - output[5][i]
            tmp3 = output[3][i] + output[4][i]
            tmp4 = output[3][i] - output[4][i]

            tmp10 = tmp0 + tmp3
            tmp13 = tmp0 - tmp3
            tmp11 = tmp1 + tmp2
            tmp12 = tmp1 - tmp2

            output[0][i] = tmp10 + tmp11
            output[4][i] = tmp10 - tmp11

            z1 = (tmp12 + tmp13) * 0.707106781
            output[2][i] = tmp13 + z1
            output[6][i] = tmp13 - z1

            tmp10 = tmp4 + tmp5
            tmp11 = tmp5 + tmp6
            tmp12 = tmp6 + tmp7

            z5 = (tmp10 - tmp12) * 0.382683433
            z2 = 0.541196100 * tmp10 + z5
            z4 = 1.306562965 * tmp12 + z5
            z3 = tmp11 * 0.707106781

            z11 = tmp7 + z3
            z13 = tmp7 - z3

            output[5][i] = z13 + z2
            output[3][i] = z13 - z2
            output[1][i] = z11 + z4
            output[7][i] = z11 - z4

        return output

    def quantize_block(self, indata, code):
        output = [0] * (self.N * self.N)
        index = 0
        for i in range(8):
            for j in range(8):
                output[index] = int(round(indata[i][j] * self.divisors[code][index]))
                index += 1

        return output

    def quantize_block_extreme(self, indata, code):
        output = [0] * (self.N * self.N)
        index = 0
        for i in range(8):
            for j in range(8):
                output[index] = int(round(indata[i][j] * self.quantum[code][index]))
                index += 1

        return output


