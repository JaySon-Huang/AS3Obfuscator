#!/usr/bin/env python
# encoding=utf-8

import sys, os.path
sys.path.append(os.path.abspath('..'))

from six import BytesIO
from swf.stream import SWFStream, int32
from AS3Obfuscator.stream import ABCFileOutputStream

hex_bytes = '06ffffffff078080808008010296feffff0f0097e9c2ff0f80f6e0c208'
nums = [6, 2147483647, -2147483648, 1, 2, -234, 0, -1002345, -2007483648]
in_stream = SWFStream(BytesIO(hex_bytes.decode('hex')))
in_nums = [int32(in_stream.readEncodedU32()) for _ in range(len(nums))]
print(nums)
print(in_nums)

out_stream = ABCFileOutputStream()
[out_stream.writeS32(_) for _ in nums]
print(hex_bytes)
print(out_stream.getvalue().encode('hex'))
# from IPython import embed;embed()
