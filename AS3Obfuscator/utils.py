#!/usr/bin/env python
# encoding=utf-8

import os
import zlib
from six import BytesIO


def filepath2module(filepath):
    return '.'.join(filepath.split(os.sep))


def module2filepath(modulepath):
    return os.sep.join(modulepath.split('.'))


def splitABCName(abcName):
    package, classname = os.path.split(abcName)
    package = '.'.join(package.split('/'))
    return package, classname


def joinPackageClassName(package, classname):
    if package == '':
        return classname
    return '{0}:{1}'.format(package, classname)


def decompress(data):
    signature = data[:3]
    version = data[3]
    length = data[4:8]
    if signature[0] == 'C':
        decompressed_data = BytesIO()
        decompressed_data.write('FWS')
        decompressed_data.write(version)
        decompressed_data.write(length)
        decompressed_data.write(zlib.decompress(data[8:]))
        return decompressed_data.getvalue()
    else:
        return data


def compress(data):
    signature = data[:3]
    version = data[3]
    length = data[4:8]
    if signature[0] == 'F':
        compressed_data = BytesIO()
        compressed_data.write('CWS')
        compressed_data.write(version)
        compressed_data.write(length)
        compressed_data.write(zlib.compress(data[8:]))
        return compressed_data.getvalue()
    else:
        return data