#!/usr/bin/env python
# encoding=utf-8

import sys
import zlib
import os.path
import StringIO


def decompress(data):
    signature = data[:3]
    version = data[3]
    length = data[4:8]
    if signature[0] == 'C':
        decompressed_data = StringIO.StringIO()
        decompressed_data.write('FWS')
        decompressed_data.write(version)
        decompressed_data.write(length)
        decompressed_data.write(zlib.decompress(data[8:]))
        return decompressed_data.getvalue()
    else:
        return data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(-1)

    filename = sys.argv[1]
    with open(filename, 'rb') as infile:
        data = infile.read()
    # from IPython import embed;embed();
    name, ext = os.path.splitext(filename)
    outfilename = name + '.decompressed' + ext
    with open(outfilename, 'wb') as outfile:
        outfile.write(decompress(data))
    print('{0} -> {1}'.format(filename, outfilename))
