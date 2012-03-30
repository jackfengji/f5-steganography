#!/usr/bin/env python
import Image
from jpeg_encoder import JpegEncoder
import sys
import os
from jpeg_extract import JpegExtract
import StringIO
import optparse
import logging

parser = optparse.OptionParser(usage="Usage: %prog [options] [args]")
group = optparse.OptionGroup(parser, 'Jpeg f5 steganography encoder and decoder')

group.add_option('-t', '--type', type='string', default='e',
        help='e for encode or x for decode')
group.add_option('-i', '--image', type='string', help='input image')
group.add_option('-d', '--data', type='string', help='data to be embeded, only for encode')
group.add_option('-o', '--output', type='string', help='output image name, only for encode')
group.add_option('-p', '--password', type='string', default='abc123',
        help='password')
group.add_option('-c', '--comment', type='string', default='written by fengji',
        help='comment to put in the image, only for encode')

parser.add_option_group(group)
parser.add_option('-q', '--quiet', action='store_true')
parser.add_option('-v', '--verbose', action='store_true')

options, args = parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)-15s [%(name)-9s] %(message)s', 
            level=options.quiet and logging.ERROR
                or options.verbose and logging.DEBUG or logging.INFO)
    if options.image and os.path.isfile(options.image):
        if options.type == 'e' and options.data:
            image = Image.open(options.image)
            data = options.data
            if not data:
                print 'there\'s no data to embed'
                sys.exit(0)

            if not options.output:
                print 'you didn\'t specify the output jpeg file, if will be default output.jpg'
                options.output = 'output.jpg'
            elif os.path.exists(options.output) and os.path.isfile(options.output):
                print 'the output file exists, do you really want to override it?'
                answer = raw_input('y/n: ')
                if answer != 'y':
                    print 'exit'
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
            JpegExtract(output, options.password).extract(image.read())

            if not options.output:
                print output.getvalue()

            image.close()
            output.close()
    else:
        print 'you didn\'t give a image or the image is not there'
        parser.print_help()
