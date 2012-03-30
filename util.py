import random

JPEG_NATURAL_ORDER = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7,
        14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46,
        53, 60, 61, 54, 47, 55, 62, 63]

def create_array(default_value=None, *args):
    if len(args) and args[0]:
        return [create_array(default_value, *args[1:]) for i in range(args[0])] 
    else:
        return default_value

class BreakException(Exception):
    def __init__(self):
        super(BreakException, self).__init__('break to outside loop')

class EmbedData(object):
    def __init__(self, data):
        self._data = data
        self.now = 0
        self.len = len(data)

    def __len__(self):
        return self.len

    def read(self):
        self.now += 1
        if self.now > self.len:
            return 0
        return ord(self._data[self.now - 1])

    def available(self):
        return self.len - self.now

class Permutation(object):
    def __init__(self, size, f5random):
        self.shuffled = range(size)
        max_random = size
        for i in range(size):
            random_index = f5random.get_next_value(max_random)
            max_random -= 1
            tmp = self.shuffled[random_index]
            self.shuffled[random_index] = self.shuffled[max_random]
            self.shuffled[max_random] = tmp

    def get_shuffled(self, i):
        return self.shuffled[i]

class FilteredCollection(object):
    def __init__(self, l, filter_func):
        self.iterator = l
        self.filter_func = filter_func
        self.now = 0

    def offer(self, count=1):
        result = []
        while count:
            while self.now < len(self.iterator) and not self.filter_func(self.iterator[self.now]):
                self.now += 1
            if self.now < len(self.iterator):
                count -= 1
                result.append(self.iterator[self.now])
                self.now += 1
            else:
                raise FilteredCollection.ListNotEnough(count)
        return result

    def reset(self):
        self.now = 0

    class ListNotEnough(Exception):
        def __init__(self, count):
            super(FilteredCollection.ListNotEnough, self).__init__('sorry list is not enough to provide %d elements' % count)

class F5Random(object):
    def get_next_byte(self):
        raise Exception('not implemented')

    def get_next_value(self, max_value):
        ret_val = self.get_next_byte() | self.get_next_byte() << 8 | \
                self.get_next_byte() << 16 | self.get_next_byte() << 24
        ret_val %= max_value
        if ret_val < 0: ret_val += max_value
        return ret_val
    
class PythonF5Random(F5Random):
    def __init__(self, password):
        random.seed(password)

    def get_next_byte(self):
        return random.randint(-128, 127)

