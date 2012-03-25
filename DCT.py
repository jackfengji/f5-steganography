import math

from util import create_array

class DCT(object):
    N = 8
    QUALITY = 80
    QUANTUM_LUMINANCE = [
            16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
            14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
            18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 
            92, 49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 
            100, 103, 99
        ]

    QUANTUM_CHROMINANCE = [
            17, 18, 24, 47, 99, 99, 99, 99, 18, 21, 26, 66, 99, 99, 99, 99,
            24, 26, 56, 99, 99, 99, 99, 99, 47, 66, 99, 99, 99, 99, 99, 99,
            99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
            99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99
        ]
    QUANTUM = [QUANTUM_LUMINANCE, QUANTUM_CHROMINANCE]
    
    def __init__(self, quality):
        self.N = 8
        self.QUALITY = 80
        self.quantum  = create_array(0, 2, self.N * self.N)
        self.divisors = create_array(0, 2, self.N * self.N)

        self.init_matrix(quality)

    def init_matrix(self, quality):
        AAN_scale_factor = [1.0, 1.387039845, 1.306562965, 1.175875602, 1.0, 0.785694958, 0.541196100, 0.275899379]
        if quality <= 0:
            quality = 1
        elif quality > 100:
            qulity = 100
        elif quality < 50:
            quality = 5000 / quality
        else:
            quality = 200 - quality * 2

        validate = lambda val: 1 if val <= 0 else (255 if val > 255 else val)
        cal_quantum = lambda quantum: validate((quantum * quality + 50) / 100)
        cal_divisors = lambda (i, quantum): 1.0 / quantum / (AAN_scale_factor[i / 8] * AAN_scale_factor[i % 8] * 8.0)

        for i in range(2):
            self.quantum[i] = map(cal_quantum, self.QUANTUM[i])
            self.divisors[i] = map(cal_divisors, enumerate(self.quantum[i]))

    def forward_dct_extreme(self, indata):
        output = create_array(0.0, self.N, self.N)
        my_cos = lambda x: math.cos((2.0 * x + 1) * u * math.PI / 16)
        special = lambda x: 1.0 / math.sqrt(2) if x == 0 else 1.0
        range_8 = range(8)

        for v in range_8:
            for u in range_8:
                for x in range_8:
                    for y in range_8:
                        output[v][u] += indata[x][y] * my_cos(x) * my_cos(y)
                output[v][u] *= 0.25 * special(u) * special(v)

        return output

    def forward_dct(self, indata):
        output = [[indata[i][j] - 128.0 for j in range(0, 8)] for i in range(0, 8)]
        tmp = create_array(0, 14)

        for i in range(8):
            for j in range(4):
                tmp[j]   = output[i][j] + output[i][7-j]
                tmp[7-j] = output[i][j] - output[i][7-j]

            output[i][0] = tmp[0] + tmp[3] + (tmp[1] + tmp[2])
            output[i][4] = tmp[0] + tmp[3] - (tmp[1] + tmp[2])

            tmp[12] = tmp[1] - tmp[2]
            tmp[13] = tmp[0] - tmp[3]
            z1 = (tmp[12] + tmp[13]) * 0.707106781
            output[i][2] = tmp[13] + z1
            output[i][6] = tmp[13] - z1

            tmp[10] = tmp[4] + tmp[5]
            tmp[11] = tmp[5] + tmp[6]
            tmp[12] = tmp[6] + tmp[7]

            z5 = (tmp[10] - tmp[12]) * 0.382683433
            z2 = 0.541196100 * tmp[10] + z5
            z4 = 1.306562965 * tmp[12] + z5
            z3 = tmp[11] * 0.707106781

            z11 = tmp[7] + z3
            z13 = tmp[7] - z3

            output[i][5] = z13 + z2
            output[i][3] = z13 - z2
            output[i][1] = z11 + z4
            output[i][7] = z11 - z4

        for i in range(8):
            for j in range(4):
                tmp[j]   = output[j][i] + output[7-j][i]
                tmp[7-j] = output[j][i] - output[7-j][i]

            output[0][i] = tmp[0] + tmp[3] + (tmp[1] + tmp[2])
            output[4][i] = tmp[0] + tmp[3] - (tmp[1] + tmp[2])

            tmp[12] = tmp[1] - tmp[2]
            tmp[13] = tmp[0] - tmp[3]
            z1 = (tmp[12] + tmp[13]) * 0.707106781
            output[2][i] = tmp[13] + z1
            output[6][i] = tmp[13] - z1

            tmp[10] = tmp[4] + tmp[5]
            tmp[11] = tmp[5] + tmp[6]
            tmp[12] = tmp[6] + tmp[7]

            z5 = (tmp[10] - tmp[12]) * 0.382683433
            z2 = 0.541196100 * tmp[10] + z5
            z4 = 1.306562965 * tmp[12] + z5
            z3 = tmp[11] * 0.707106781

            z11 = tmp[7] + z3
            z13 = tmp[7] - z3

            output[5][i] = z13 + z2
            output[3][i] = z13 - z2
            output[1][i] = z11 + z4
            output[7][i] = z11 - z4

        return output

    def quantize_block(self, indata, code):
        return map(lambda (i, divisors): int(round(indata[i / 8][i % 8] * divisors)), enumerate(self.divisors[code]))

    def quantize_block_extreme(self, indata, code):
        return map(lambda (i, quantum): int(round(indata[i / 8][i % 8] * quantum)), enumerate(self.quantum[code]))
