import Image
from jpeg_encoder import JpegEncoder
import sys

if __name__ == '__main__':
    if sys.argv[1] == 'e':
        image = Image.open('logo.jpg')
        output = open('logo-python.jpg', 'wb')
        encoder = JpegEncoder(image, 80, output, '')
        encoder.compress('test embed\n', 'abc123')
        output.close()
