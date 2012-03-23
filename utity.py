import Image
from jpeg_encoder import JpegEncoder
import sys
import os
from jpeg_extract import JpegExtract
import StringIO
import optparse

parser = optparse.OptionParser()
group = optparse.OptionGroup(parser, 'jpeg f5 encoder and decoder')

group.add_option('-t', '--type', type='string', default='e')
group.add_option('-i', '--image', type='string')
group.add_option('-d', '--data', type='string')
group.add_option('-o', '--output', type='string')
group.add_option('-p', '--password', type='string', default='abc123')
group.add_option('-c', '--comment', type='string', default='written by fengji  ')

options, args = parser.parse_args()

if __name__ == '__main__':
    if options.image and os.path.isfile(options.image):
        if options.type == 'e' and options.data:
            image = Image.open(options.image)
            data = options.data

            if not options.output:
                print 'you didn\'t specify the output jpeg file, if will be default output.jpg'
                options.output = 'output.jpg'
            elif os.path.exists(options.output) and os.path.isfile(options.output):
                print 'the output file exists, do you really want to override it?'
                answer = raw_input('y/n: ')
                if answer == 'n':
                    sys.exit(0)
            output = open(options.output, 'wb')

            encoder = JpegEncoder(image, 80, output, options.comment)
            encoder.compress(data, options.password)
            output.close()
        if options.type == 'x':
            if options.output:
                output = open(options.output, 'wb')
            else:
                output = StringIO.StringIO()
            image = open(options.image, 'rb')
            JpegExtract.extract(image.read(), output, options.password)

            if not options.output:
                print output.getvalue()

            image.close()
            output.close()
    else:
        print 'you didn\'t give a image or the image is not there'
