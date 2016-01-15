#!/usr/bin/env python
# encoding=utf-8

import struct

import six
from six import BytesIO


# noinspection PyPep8Naming,PyTypeChecker
class ABCFileOutputStream(BytesIO):

    def getvalue(self):
        def trans(s):
            if isinstance(s, unicode):
                return bytearray(s, encoding='utf-8')
            else:
                return bytearray(s)
        if self.buflist:
            self.buflist = list(map(trans, self.buflist))
            self.buf = bytearray()
            self.buf = self.buf.join(self.buflist)
            self.buflist = []
        return self.buf

    def writeU8(self, num):
        self.write(six.int2byte(num))

    def writeU16(self, num):
        self.write(struct.pack('H', num))

    def writeS24(self, num):
        self.writeU8(num & 0xFF)
        self.writeU8((num >> 8) & 0xFF)
        self.writeU8((num >> 16) & 0xFF)

    def writeU30(self, num):
        self.writeS32(num)

    def writeU32(self, num):
        self.writeS32(num)

    def writeS32(self, num):
        if num < 0:
            num &= 0xFFFFFFFF
        while num > 127:
            self.write(struct.pack('B', ((num & 0x7F) | 0x80)))
            num >>= 7
        self.write(struct.pack('B', num))

    def writeD64(self, num):
        self.write(struct.pack('d', num))

    """ ordinary methods """

    def writeUI16(self, num):
        self.write(struct.pack('H', num))

    def writeUI32(self, num):
        self.write(struct.pack('<I', num))

    def writeSI32(self, num):
        self.write(struct.pack('<i', num))
