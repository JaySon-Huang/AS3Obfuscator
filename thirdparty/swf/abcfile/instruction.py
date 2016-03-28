#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import struct
from six import BytesIO
from ..stream import SWFStream

__all__ = [
    'Instruction',
    'InstructionAdd',
    'InstructionAdd_I',
    'InstructionSubtract',
    'InstructionSubtract_I',
    'InstructionMultiply',
    'InstructionMultiply_I',
    'InstructionDivide',
    'InstructionModulo',
    'InstructionNegate',
    'InstructionNegate_I',
    'InstructionAstype',
    'InstructionAstypelate',
    'InstructionBitand',
    'InstructionBitnot',
    'InstructionBitor',
    'InstructionBitxor',
    'InstructionCall',
    'InstructionCallmethod',
    'InstructionCallproperty',
    'InstructionCallproplex',
    'InstructionCallpropvoid',
    'InstructionCallstatic',
    'InstructionCallsuper',
    'InstructionCallsupervoid',
    'InstructionCheckfilter',
    'InstructionCoerce',
    'InstructionCoerce_A',
    'InstructionCoerce_S',
    'InstructionCoerce_O',
    'InstructionConstruct',
    'InstructionConstructprop',
    'InstructionConstructsuper',
    'InstructionConvert_S',
    'InstructionConvert_I',
    'InstructionConvert_U',
    'InstructionConvert_D',
    'InstructionConvert_B',
    'InstructionConvert_O',
    'InstructionDebug',
    'InstructionDebugline',
    'InstructionDebugfile',
    'InstructionDeclocal',
    'InstructionDeclocal_I',
    'InstructionDecrement',
    'InstructionDecrement_I',
    'InstructionDeleteproperty',
    'InstructionDup',
    'InstructionDxns',
    'InstructionDxnslate',
    'InstructionEquals',
    'InstructionStrictequals',
    'InstructionLessthan',
    'InstructionLessequals',
    'InstructionGreaterthan',
    'InstructionGreaterequals',
    'InstructionEsc_Xelem',
    'InstructionEsc_Xattr',
    'InstructionFindproperty',
    'InstructionFindpropstrict',
    'InstructionGetdescendants',
    'InstructionGetlex',
    'InstructionGetglobalscope',
    'InstructionGetglobalslot',
    'InstructionSetglobalslot',
    'InstructionGetlocal',
    'InstructionSetlocal',
    'InstructionGetlocal0',
    'InstructionGetlocal1',
    'InstructionGetlocal2',
    'InstructionGetlocal3',
    'InstructionSetlocal0',
    'InstructionSetlocal1',
    'InstructionSetlocal2',
    'InstructionSetlocal3',
    'InstructionGetscopeobject',
    'InstructionGetproperty',
    'InstructionSetproperty',
    'InstructionGetslot',
    'InstructionSetslot',
    'InstructionGetsuper',
    'InstructionSetsuper',
    'InstructionGetouterscope',
    'InstructionHasnext',
    'InstructionHasnext2',
    'InstructionJump',
    'InstructionIfnlt',
    'InstructionIfnle',
    'InstructionIfngt',
    'InstructionIfnge',
    'InstructionIftrue',
    'InstructionIffalse',
    'InstructionIfeq',
    'InstructionIfne',
    'InstructionIflt',
    'InstructionIfle',
    'InstructionIfgt',
    'InstructionIfge',
    'InstructionIfstricteq',
    'InstructionIfstrictne',
    'InstructionIn',
    'InstructionInclocal',
    'InstructionInclocal_I',
    'InstructionIncrement',
    'InstructionIncrement_I',
    'InstructionInitproperty',
    'InstructionInstanceof',
    'InstructionIstype',
    'InstructionIstypelate',
    'InstructionKill',
    'InstructionLabel',
    'InstructionLookupswitch',
    'InstructionLshift',
    'InstructionRshift',
    'InstructionUrshift',
    'InstructionNewactivation',
    'InstructionNewarray',
    'InstructionNewcatch',
    'InstructionNewfunction',
    'InstructionNewobject',
    'InstructionNewclass',
    'InstructionNextname',
    'InstructionNextvalue',
    'InstructionNop',
    'InstructionNot',
    'InstructionPop',
    'InstructionPopscope',
    'InstructionPushbyte',
    'InstructionPushshort',
    'InstructionPushstring',
    'InstructionPushint',
    'InstructionPushuint',
    'InstructionPushdouble',
    'InstructionPushnamespace',
    'InstructionPushwith',
    'InstructionPushnull',
    'InstructionPushundefined',
    'InstructionPushtrue',
    'InstructionPushfalse',
    'InstructionPushnan',
    'InstructionPushscope',
    'InstructionSwap',
    'InstructionThrow',
    'InstructionTypeof',
    'InstructionReturnvoid',
    'InstructionReturnvalue'
]


class Instruction(object):

    @property
    def name(self):
        return 'instruction'

    def __init__(self):
        self.code = ''
        self.code_offset_beg = 0
        self.code_offset_end = 0

    def __repr__(self):
        return '<Instruction {0}>'.format(self.name)

    @classmethod
    def parse_code(cls, code_bytes):
        return list(cls.iter_instructions(code_bytes))

    @staticmethod
    def iter_instructions(code_bytes):
        stream = SWFStream(BytesIO(code_bytes))
        while 1:
            code_beg = stream.tell()
            try:
                ch = stream.readUI8()
            except struct.error:
                break

            if ch == 0xa0:
                instruction = InstructionAdd()
            elif ch == 0xc5:
                instruction = InstructionAdd_I()
            elif ch == 0xa1:
                instruction = InstructionSubtract()
            elif ch == 0xc6:
                instruction = InstructionSubtract_I()
            elif ch == 0xa2:
                instruction = InstructionMultiply()
            elif ch == 0xc7:
                instruction = InstructionMultiply_I()
            elif ch == 0xa3:
                instruction = InstructionDivide()
            elif ch == 0xa4:
                instruction = InstructionModulo()
            elif ch == 0x90:
                instruction = InstructionNegate()
            elif ch == 0xc4:
                instruction = InstructionNegate_I()

            elif ch == 0x86:
                index = stream.readEncodedU32()
                instruction = InstructionAstype(index)
            elif ch == 0x87:
                instruction = InstructionAstypelate()
            elif ch == 0xb2:
                index = stream.readEncodedU32()
                instruction = InstructionIstype(index)
            elif ch == 0xb3:
                instruction = InstructionIstypelate()

            elif ch == 0xa8:
                instruction = InstructionBitand()
            elif ch == 0x97:
                instruction = InstructionBitnot()
            elif ch == 0xa9:
                instruction = InstructionBitor()
            elif ch == 0xaa:
                instruction = InstructionBitxor()

            elif ch == 0x41:
                arg_count = stream.readEncodedU32()
                instruction = InstructionCall(arg_count)
            elif ch == 0x43:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallmethod(index, arg_count)
            elif ch == 0x46:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallproperty(index, arg_count)
            elif ch == 0x4c:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallproplex(index, arg_count)
            elif ch == 0x4f:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallpropvoid(index, arg_count)
            elif ch == 0x44:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallstatic(index, arg_count)
            elif ch == 0x45:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallsuper(index, arg_count)
            elif ch == 0x4e:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionCallsupervoid(index, arg_count)

            elif ch == 0x78:
                instruction = InstructionCheckfilter()

            elif ch == 0x80:
                index = stream.readEncodedU32()
                instruction = InstructionCoerce(index)
            elif ch == 0x82:
                instruction = InstructionCoerce_A()
            elif ch == 0x85:
                instruction = InstructionCoerce_S()
            elif ch == 0x89:
                instruction = InstructionCoerce_O()

            elif ch == 0x42:
                arg_count = stream.readEncodedU32()
                instruction = InstructionConstruct(arg_count)
            elif ch == 0x4a:
                index = stream.readEncodedU32()
                arg_count = stream.readEncodedU32()
                instruction = InstructionConstructprop(index, arg_count)
            elif ch == 0x49:
                arg_count = stream.readEncodedU32()
                instruction = InstructionConstructsuper(arg_count)

            elif ch == InstructionConvert_S.FORM:
                instruction = InstructionConvert_S()
            elif ch == 0x73:
                instruction = InstructionConvert_I()
            elif ch == 0x74:
                instruction = InstructionConvert_U()
            elif ch == 0x75:
                instruction = InstructionConvert_D()
            elif ch == 0x76:
                instruction = InstructionConvert_B()
            elif ch == 0x77:
                instruction = InstructionConvert_O()

            elif ch == 0xef:
                debug_type = stream.readUI8()
                index = stream.readEncodedU32()
                reg = stream.readUI8()
                extra = stream.readEncodedU32()  # currently unused
                instruction = InstructionDebug(debug_type, index, reg, extra)
            elif ch == 0xf0:
                linenum = stream.readEncodedU32()
                instruction = InstructionDebugline(linenum)
            elif ch == 0xf1:
                index = stream.readEncodedU32()
                instruction = InstructionDebugfile(index)

            elif ch == 0x94:
                index = stream.readEncodedU32()
                instruction = InstructionDeclocal(index)
            elif ch == 0xc3:
                index = stream.readEncodedU32()
                instruction = InstructionDeclocal_I(index)
            elif ch == 0x92:
                index = stream.readEncodedU32()
                instruction = InstructionInclocal(index)
            elif ch == 0xc2:
                index = stream.readEncodedU32()
                instruction = InstructionInclocal_I(index)

            elif ch == 0x93:
                instruction = InstructionDecrement()
            elif ch == 0xc1:
                instruction = InstructionDecrement_I()
            elif ch == 0x91:
                instruction = InstructionIncrement()
            elif ch == 0xc0:
                instruction = InstructionIncrement_I()

            elif ch == 0x6a:
                index = stream.readEncodedU32()
                instruction = InstructionDeleteproperty(index)
            elif ch == 0x66:
                index = stream.readEncodedU32()
                instruction = InstructionGetproperty(index)
            elif ch == 0x61:
                index = stream.readEncodedU32()
                instruction = InstructionSetproperty(index)
            elif ch == 0x68:
                index = stream.readEncodedU32()
                instruction = InstructionInitproperty(index)
            elif ch == 0x5e:
                index = stream.readEncodedU32()
                instruction = InstructionFindproperty(index)
            elif ch == 0x5d:
                index = stream.readEncodedU32()
                instruction = InstructionFindpropstrict(index)

            elif ch == 0x2a:
                instruction = InstructionDup()

            elif ch == 0x06:
                index = stream.readEncodedU32()
                instruction = InstructionDxns(index)
            elif ch == 0x07:
                instruction = InstructionDxnslate()

            elif ch == 0xab:
                instruction = InstructionEquals()
            elif ch == 0xac:
                instruction = InstructionStrictequals()
            elif ch == 0xad:
                instruction = InstructionLessthan()
            elif ch == 0xae:
                instruction = InstructionLessequals()
            elif ch == 0xaf:
                instruction = InstructionGreaterthan()
            elif ch == 0xb0:
                instruction = InstructionGreaterequals()

            elif ch == 0x71:
                instruction = InstructionEsc_Xelem()
            elif ch == 0x72:
                instruction = InstructionEsc_Xattr()

            elif ch == 0x59:
                index = stream.readEncodedU32()
                instruction = InstructionGetdescendants(index)
            elif ch == 0x60:
                index = stream.readEncodedU32()
                instruction = InstructionGetlex(index)
            elif ch == 0x64:
                instruction = InstructionGetglobalscope()
            elif ch == 0x6e:
                slot_index = stream.readEncodedU32()
                instruction = InstructionGetglobalslot(slot_index)
            elif ch == 0x6f:
                slot_index = stream.readEncodedU32()
                instruction = InstructionSetglobalslot(slot_index)

            elif ch == 0x62:
                index = stream.readEncodedU32()
                instruction = InstructionGetlocal(index)
            elif ch == 0x63:
                index = stream.readEncodedU32()
                instruction = InstructionSetlocal(index)
            elif ch == 0xd0:
                instruction = InstructionGetlocal0()
            elif ch == 0xd1:
                instruction = InstructionGetlocal1()
            elif ch == 0xd2:
                instruction = InstructionGetlocal2()
            elif ch == 0xd3:
                instruction = InstructionGetlocal3()
            elif ch == 0xd4:
                instruction = InstructionSetlocal0()
            elif ch == 0xd5:
                instruction = InstructionSetlocal1()
            elif ch == 0xd6:
                instruction = InstructionSetlocal2()
            elif ch == 0xd7:
                instruction = InstructionSetlocal3()

            elif ch == 0x65:
                index = stream.readUI8()
                instruction = InstructionGetscopeobject(index)

            elif ch == 0x6c:
                slot_index = stream.readEncodedU32()
                instruction = InstructionGetslot(slot_index)
            elif ch == 0x6d:
                slot_index = stream.readEncodedU32()
                instruction = InstructionSetslot(slot_index)

            elif ch == 0x04:
                index = stream.readEncodedU32()
                instruction = InstructionGetsuper(index)
            elif ch == 0x05:
                index = stream.readEncodedU32()
                instruction = InstructionSetsuper(index)

            elif ch == 0x1f:
                instruction = InstructionHasnext()
            elif ch == 0x32:
                # is these reg index are EncodedU32?
                object_reg = stream.readEncodedU32()
                index_reg = stream.readEncodedU32()
                instruction = InstructionHasnext2(object_reg, index_reg)
                # raise NotImplementedError('type of object_reg, index_reg remain unknown.')
            elif ch == 0x1e:
                instruction = InstructionNextname()
            elif ch == 0x23:
                instruction = InstructionNextvalue()

            elif ch == 0x96:
                instruction = InstructionNot()
            elif ch == 0x10:
                offset = stream.readS24()
                instruction = InstructionJump(offset)
            elif ch == 0x0c:
                offset = stream.readS24()
                instruction = InstructionIfnlt(offset)
            elif ch == 0x0d:
                offset = stream.readS24()
                instruction = InstructionIfnle(offset)
            elif ch == 0x0e:
                offset = stream.readS24()
                instruction = InstructionIfngt(offset)
            elif ch == 0x0f:
                offset = stream.readS24()
                instruction = InstructionIfnge(offset)
            elif ch == 0x11:
                offset = stream.readS24()
                instruction = InstructionIftrue(offset)
            elif ch == 0x12:
                offset = stream.readS24()
                instruction = InstructionIffalse(offset)
            elif ch == 0x13:
                offset = stream.readS24()
                instruction = InstructionIfeq(offset)
            elif ch == 0x14:
                offset = stream.readS24()
                instruction = InstructionIfne(offset)
            elif ch == 0x15:
                offset = stream.readS24()
                instruction = InstructionIflt(offset)
            elif ch == 0x16:
                offset = stream.readS24()
                instruction = InstructionIfle(offset)
            elif ch == 0x17:
                offset = stream.readS24()
                instruction = InstructionIfgt(offset)
            elif ch == 0x18:
                offset = stream.readS24()
                instruction = InstructionIfge(offset)
            elif ch == 0x19:
                offset = stream.readS24()
                instruction = InstructionIfstricteq(offset)
            elif ch == 0x1a:
                offset = stream.readS24()
                instruction = InstructionIfstrictne(offset)

            elif ch == 0xb4:
                instruction = InstructionIn()

            elif ch == 0xb1:
                instruction = InstructionInstanceof()

            elif ch == 0x08:
                index = stream.readEncodedU32()
                instruction = InstructionKill(index)
            elif ch == 0x09:
                instruction = InstructionLabel()
            elif ch == 0x1b:
                default_offset = stream.readS24()
                case_count = stream.readEncodedU32()
                case_offsets = []
                # there are case_count+1 case offsets
                for _ in range(case_count + 1):
                    case_offsets.append(stream.readS24())
                instruction = InstructionLookupswitch(default_offset, case_offsets)

            elif ch == 0xa5:
                instruction = InstructionLshift()
            elif ch == 0xa6:
                instruction = InstructionRshift()
            elif ch == 0xa7:
                instruction = InstructionUrshift()

            elif ch == 0x57:
                instruction = InstructionNewactivation()
            elif ch == 0x56:
                arg_count = stream.readEncodedU32()
                instruction = InstructionNewarray(arg_count)
            elif ch == 0x5a:
                index = stream.readEncodedU32()
                instruction = InstructionNewcatch(index)
            elif ch == 0x40:
                index = stream.readEncodedU32()
                instruction = InstructionNewfunction(index)
            elif ch == 0x55:
                arg_count = stream.readEncodedU32()
                instruction = InstructionNewobject(arg_count)
            elif ch == 0x58:
                index = stream.readEncodedU32()
                instruction = InstructionNewclass(index)

            elif ch == 0x02:
                instruction = InstructionNop()

            elif ch == 0x29:
                instruction = InstructionPop()
            elif ch == 0x1d:
                instruction = InstructionPopscope()

            elif ch == 0x24:
                byte_value = stream.readUI8()
                instruction = InstructionPushbyte(byte_value)
            elif ch == 0x25:
                value = stream.readEncodedU32()
                instruction = InstructionPushshort(value)
            elif ch == 0x2c:
                index = stream.readEncodedU32()
                instruction = InstructionPushstring(index)
            elif ch == 0x2d:
                index = stream.readEncodedU32()
                instruction = InstructionPushint(index)
            elif ch == 0x2e:
                index = stream.readEncodedU32()
                instruction = InstructionPushuint(index)
            elif ch == 0x2f:
                index = stream.readEncodedU32()
                instruction = InstructionPushdouble(index)
            elif ch == 0x31:
                index = stream.readEncodedU32()
                instruction = InstructionPushnamespace(index)
            elif ch == 0x1c:
                instruction = InstructionPushwith()
            elif ch == 0x20:
                instruction = InstructionPushnull()
            elif ch == 0x21:
                instruction = InstructionPushundefined()
            elif ch == 0x26:
                instruction = InstructionPushtrue()
            elif ch == 0x27:
                instruction = InstructionPushfalse()
            elif ch == 0x28:
                instruction = InstructionPushnan()
            elif ch == 0x30:
                instruction = InstructionPushscope()

            elif ch == 0x2b:
                instruction = InstructionSwap()

            elif ch == 0x03:
                instruction = InstructionThrow()
            elif ch == 0x95:
                instruction = InstructionTypeof()

            elif ch == 0x47:
                instruction = InstructionReturnvoid()
            elif ch == 0x48:
                instruction = InstructionReturnvalue()

            # not appear in avm2overview but appear in actual code
            elif ch == 0x53:
                num = stream.readEncodedU32()  # guess that it is an Encoded U32 number
                instruction = InstructionApplytype(num)

            else:
                raise Exception("unhandled code byte 0x{0:02x}".format(ch))
            code_end = stream.tell()
            instruction.code = stream.f.getvalue()[code_beg:code_end]
            instruction.code_offset_beg = code_beg
            instruction.code_offset_end = code_end
            yield instruction


class InstructionAdd(Instruction):

    FORM = 0xa0

    @property
    def name(self):
        return 'add'

    def __init__(self):
        super(InstructionAdd, self).__init__()
        self.code = '\xa0'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionAdd_I(Instruction):

    FORM = 0xc5

    @property
    def name(self):
        return 'add_i'

    def __init__(self):
        super(InstructionAdd_I, self).__init__()
        self.code = '\xc5'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionSubtract(Instruction):

    FORM = 0xa1

    @property
    def name(self):
        return 'subtract'

    def __init__(self):
        super(InstructionSubtract, self).__init__()
        self.code = '\xa1'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionSubtract_I(Instruction):

    FORM = 0xc6

    @property
    def name(self):
        return 'subtract_i'

    def __init__(self):
        super(InstructionSubtract_I, self).__init__()
        self.code = '\xc6'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionMultiply(Instruction):

    FORM = 0xa2

    @property
    def name(self):
        return 'multiply'

    def __init__(self):
        super(InstructionMultiply, self).__init__()
        self.code = '\xa2'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionMultiply_I(Instruction):

    FORM = 0xc7

    @property
    def name(self):
        return 'multiply_i'

    def __init__(self):
        super(InstructionMultiply_I, self).__init__()
        self.code = '\xc7'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionDivide(Instruction):

    FORM = 0xa3

    @property
    def name(self):
        return 'divide'

    def __init__(self):
        super(InstructionDivide, self).__init__()
        self.code = '\xa3'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionModulo(Instruction):

    FORM = 0xa4

    @property
    def name(self):
        return 'modulo'

    def __init__(self):
        super(InstructionModulo, self).__init__()
        self.code = '\xa4'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionNegate(Instruction):

    FORM = 0x90

    @property
    def name(self):
        return 'negate'

    def __init__(self):
        super(InstructionNegate, self).__init__()
        self.code = '\x90'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionNegate_I(Instruction):

    FORM = 0xc4

    @property
    def name(self):
        return 'negate_i'

    def __init__(self):
        super(InstructionNegate_I, self).__init__()
        self.code = '\xc4'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionAstype(Instruction):

    FORM = 0x86

    @property
    def name(self):
        return 'astype'

    def __init__(self, index):
        super(InstructionAstype, self).__init__()
        self.code = '\x86'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index)
        ])


class InstructionAstypelate(Instruction):

    FORM = 0x87

    @property
    def name(self):
        return 'astypelate'

    def __init__(self):
        super(InstructionAstypelate, self).__init__()
        self.code = '\x87'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionBitand(Instruction):

    FORM = 0xa8

    @property
    def name(self):
        return 'bitand'

    def __init__(self):
        super(InstructionBitand, self).__init__()
        self.code = '\xa8'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionBitnot(Instruction):

    FORM = 0x97

    @property
    def name(self):
        return 'bitnot'

    def __init__(self):
        super(InstructionBitnot, self).__init__()
        self.code = '\x97'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionBitor(Instruction):

    FORM = 0xa9

    @property
    def name(self):
        return 'bitor'

    def __init__(self):
        super(InstructionBitor, self).__init__()
        self.code = '\xa9'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionBitxor(Instruction):

    FORM = 0xaa

    @property
    def name(self):
        return 'bitxor'

    def __init__(self):
        super(InstructionBitxor, self).__init__()
        self.code = '\xaa'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionCall(Instruction):

    FORM = 0x41

    @property
    def name(self):
        return 'call'

    def __init__(self, arg_count):
        super(InstructionCall, self).__init__()
        self.code = '\x41'
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([self.name, str(self.arg_count)])


class InstructionCallmethod(Instruction):

    FORM = 0x43

    @property
    def name(self):
        return 'callmethod'

    def __init__(self, index, arg_count):
        super(InstructionCallmethod, self).__init__()
        self.code = '\x43'
        self.index = index
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index),  # method index
            str(self.arg_count)
        ])


class InstructionCallproperty(Instruction):

    FORM = 0x46

    @property
    def name(self):
        return 'callproperty'

    def __init__(self, index, arg_count):
        super(InstructionCallproperty, self).__init__()
        self.code = '\x46'
        self.index = index
        self.arg_count = arg_count

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
            str(self.arg_count)
        ])


class InstructionCallproplex(Instruction):

    FORM = 0x4c

    @property
    def name(self):
        return 'callproplex'

    def __init__(self, index, arg_count):
        super(InstructionCallproplex, self).__init__()
        self.code = '\x4c'
        self.index = index
        self.arg_count = arg_count

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
            str(self.arg_count)
        ])


class InstructionCallpropvoid(Instruction):

    FORM = 0x4f

    @property
    def name(self):
        return 'callpropvoid'

    def __init__(self, index, arg_count):
        super(InstructionCallpropvoid, self).__init__()
        self.code = '\x4f'
        self.index = index
        self.arg_count = arg_count

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
            str(self.arg_count)
        ])


class InstructionCallstatic(Instruction):

    FORM = 0x44

    @property
    def name(self):
        return 'callstatic'

    def __init__(self, index, arg_count):
        super(InstructionCallstatic, self).__init__()
        self.code = '\x44'
        self.index = index
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        # FIXME method name
        return ' '.join([
            self.name,
            str(self.index),  # method index
            str(self.arg_count)
        ])


class InstructionCallsuper(Instruction):

    FORM = 0x45

    @property
    def name(self):
        return 'callsuper'

    def __init__(self, index, arg_count):
        super(InstructionCallsuper, self).__init__()
        self.code = '\x45'
        self.index = index
        self.arg_count = arg_count

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
            str(self.arg_count)
        ])


class InstructionCallsupervoid(Instruction):

    FORM = 0x4e

    @property
    def name(self):
        return 'callsupervoid'

    def __init__(self, index, arg_count):
        super(InstructionCallsupervoid, self).__init__()
        self.code = '\x4e'
        self.index = index
        self.arg_count = arg_count

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
            str(self.arg_count)
        ])


class InstructionCheckfilter(Instruction):

    FORM = 0x78

    @property
    def name(self):
        return 'checkfilter'

    def __init__(self):
        super(InstructionCheckfilter, self).__init__()
        self.code = '\x78'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionCoerce(Instruction):

    FORM = 0x80

    @property
    def name(self):
        return 'coerce'

    def __init__(self, index):
        super(InstructionCoerce, self).__init__()
        self.code = '\x80'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


# noinspection PyPep8Naming
class InstructionCoerce_A(Instruction):

    FORM = 0x82

    @property
    def name(self):
        return 'coerce_a'

    def __init__(self):
        super(InstructionCoerce_A, self).__init__()
        self.code = '\x82'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionCoerce_S(Instruction):

    FORM = 0x85

    @property
    def name(self):
        return 'coerce_s'

    def __init__(self):
        super(InstructionCoerce_S, self).__init__()
        self.code = '\x85'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionCoerce_O(Instruction):

    FORM = 0x89

    @property
    def name(self):
        return 'coerce_o'

    def __init__(self):
        super(InstructionCoerce_O, self).__init__()
        self.code = '\x89'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionConstruct(Instruction):

    FORM = 0x42

    @property
    def name(self):
        return 'construct'

    def __init__(self, arg_count):
        super(InstructionConstruct, self).__init__()
        self.code = '\x42'
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name, str(self.arg_count)
        ])


class InstructionConstructprop(Instruction):

    FORM = 0x4a

    @property
    def name(self):
        return 'constructprop'

    def __init__(self, index, arg_count):
        super(InstructionConstructprop, self).__init__()
        self.code = '\x4a'
        self.index = index
        self.arg_count = arg_count

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
            str(self.arg_count)
        ])


class InstructionConstructsuper(Instruction):

    FORM = 0x49

    @property
    def name(self):
        return 'constructsuper'

    def __init__(self, arg_count):
        super(InstructionConstructsuper, self).__init__()
        self.code = '\x49'
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.arg_count)
        ])


# noinspection PyPep8Naming
class InstructionConvert_S(Instruction):

    FORM = 0x70

    @property
    def name(self):
        return 'convert_s'

    def __init__(self):
        super(InstructionConvert_S, self).__init__()
        self.code = '\x70'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionConvert_I(Instruction):

    FORM = 0x73

    @property
    def name(self):
        return 'convert_i'

    def __init__(self):
        super(InstructionConvert_I, self).__init__()
        self.code = '\x73'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionConvert_U(Instruction):

    FORM = 0x74

    @property
    def name(self):
        return 'convert_u'

    def __init__(self):
        super(InstructionConvert_U, self).__init__()
        self.code = '\x74'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionConvert_D(Instruction):

    FORM = 0x75

    @property
    def name(self):
        return 'convert_d'

    def __init__(self):
        super(InstructionConvert_D, self).__init__()
        self.code = '\x75'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionConvert_B(Instruction):

    FORM = 0x76

    @property
    def name(self):
        return 'convert_b'

    def __init__(self):
        super(InstructionConvert_B, self).__init__()
        self.code = '\x76'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionConvert_O(Instruction):

    FORM = 0x77

    @property
    def name(self):
        return 'convert_o'

    def __init__(self):
        super(InstructionConvert_O, self).__init__()
        self.code = '\x77'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionDebug(Instruction):

    FORM = 0xef

    @property
    def name(self):
        return 'debug'

    def __init__(self, debug_type, index, reg, extra):
        super(InstructionDebug, self).__init__()
        self.code = '\xef'
        self.debug_type = debug_type
        self.index = index
        self.reg = reg
        self.extra = extra

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.debug_type),
            constant_pool.get_string(self.index),  # strings index
            str(self.reg),
            str(self.extra)
        ])


class InstructionDebugline(Instruction):

    FORM = 0xf0

    @property
    def name(self):
        return 'debugline'

    def __init__(self, linenum):
        super(InstructionDebugline, self).__init__()
        self.code = '\xf0'
        self.linenum = linenum

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.linenum)
        ])


class InstructionDebugfile(Instruction):

    FORM = 0xf1

    @property
    def name(self):
        return 'debugfile'

    def __init__(self, index):
        super(InstructionDebugfile, self).__init__()
        self.code = '\xf1'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_string(self.index)  # strings index
        ])


class InstructionDeclocal(Instruction):

    FORM = 0x94

    @property
    def name(self):
        return 'declocal'

    def __init__(self, index):
        super(InstructionDeclocal, self).__init__()
        self.code = '\x94'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index)  # local register index
        ])


# noinspection PyPep8Naming
class InstructionDeclocal_I(Instruction):

    FORM = 0xc3

    @property
    def name(self):
        return 'declocal_i'

    def __init__(self, index):
        super(InstructionDeclocal_I, self).__init__()
        self.code = '\xc3'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index)  # local register index
        ])


class InstructionInclocal(Instruction):

    FORM = 0x92

    @property
    def name(self):
        return 'inclocal'

    def __init__(self, index):
        super(InstructionInclocal, self).__init__()
        self.code = '\x92'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index)  # local register index
        ])


# noinspection PyPep8Naming
class InstructionInclocal_I(Instruction):

    FORM = 0xc2

    @property
    def name(self):
        return 'inclocal_i'

    def __init__(self, index):
        super(InstructionInclocal_I, self).__init__()
        self.code = '\xc2'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index)  # local register index
        ])


class InstructionDecrement(Instruction):

    FORM = 0x93

    @property
    def name(self):
        return 'decrement'

    def __init__(self):
        super(InstructionDecrement, self).__init__()
        self.code = '\x93'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionDecrement_I(Instruction):

    FORM = 0xc1

    @property
    def name(self):
        return 'decrement_i'

    def __init__(self):
        super(InstructionDecrement_I, self).__init__()
        self.code = '\xc1'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionIncrement(Instruction):

    FORM = 0x91

    @property
    def name(self):
        return 'increment'

    def __init__(self):
        super(InstructionIncrement, self).__init__()
        self.code = '\x91'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionIncrement_I(Instruction):

    FORM = 0xc0

    @property
    def name(self):
        return 'increment_i'

    def __init__(self):
        super(InstructionIncrement_I, self).__init__()
        self.code = '\xc0'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionDeleteproperty(Instruction):

    FORM = 0x6a

    @property
    def name(self):
        return 'deleteproperty'

    def __init__(self, index):
        super(InstructionDeleteproperty, self).__init__()
        self.code = '\x6a'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionDup(Instruction):

    FORM = 0x2a

    @property
    def name(self):
        return 'dup'

    def __init__(self):
        super(InstructionDup, self).__init__()
        self.code = '\x2a'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionDxns(Instruction):

    FORM = 0x06

    @property
    def name(self):
        return 'dxns'

    def __init__(self, index):
        super(InstructionDxns, self).__init__()
        self.code = '\x06'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_string(self.index),  # string index
        ])


class InstructionDxnslate(Instruction):

    FORM = 0x07

    @property
    def name(self):
        return 'dxnslate'

    def __init__(self):
        super(InstructionDxnslate, self).__init__()
        self.code = '\x07'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionEquals(Instruction):

    FORM = 0xab

    @property
    def name(self):
        return 'equals'

    def __init__(self):
        super(InstructionEquals, self).__init__()
        self.code = '\xab'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionStrictequals(Instruction):

    FORM = 0xac

    @property
    def name(self):
        return 'strictequals'

    def __init__(self):
        super(InstructionStrictequals, self).__init__()
        self.code = '\xac'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionLessthan(Instruction):

    FORM = 0xad

    @property
    def name(self):
        return 'lessthan'

    def __init__(self):
        super(InstructionLessthan, self).__init__()
        self.code = '\xad'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionLessequals(Instruction):

    FORM = 0xae

    @property
    def name(self):
        return 'lessequals'

    def __init__(self):
        super(InstructionLessequals, self).__init__()
        self.code = '\xae'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGreaterthan(Instruction):

    FORM = 0xaf

    @property
    def name(self):
        return 'greaterthan'

    def __init__(self):
        super(InstructionGreaterthan, self).__init__()
        self.code = '\xaf'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGreaterequals(Instruction):

    FORM = 0xb0

    @property
    def name(self):
        return 'greaterequals'

    def __init__(self):
        super(InstructionGreaterequals, self).__init__()
        self.code = '\xb0'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionEsc_Xelem(Instruction):

    FORM = 0x71

    @property
    def name(self):
        return 'esc_xelem'

    def __init__(self):
        super(InstructionEsc_Xelem, self).__init__()
        self.code = '\x71'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


# noinspection PyPep8Naming
class InstructionEsc_Xattr(Instruction):

    FORM = 0x72

    @property
    def name(self):
        return 'esc_xattr'

    def __init__(self):
        super(InstructionEsc_Xattr, self).__init__()
        self.code = '\x72'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionFindproperty(Instruction):

    FORM = 0x5e

    @property
    def name(self):
        return 'findproperty'

    def __init__(self, index):
        super(InstructionFindproperty, self).__init__()
        self.code = '\x5e'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionFindpropstrict(Instruction):

    FORM = 0x5d

    @property
    def name(self):
        return 'findpropstrict'

    def __init__(self, index):
        super(InstructionFindpropstrict, self).__init__()
        self.code = '\x5d'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionGetdescendants(Instruction):

    FORM = 0x59

    @property
    def name(self):
        return 'getdescendants'

    def __init__(self, index):
        super(InstructionGetdescendants, self).__init__()
        self.code = '\x59'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionGetlex(Instruction):

    FORM = 0x60

    @property
    def name(self):
        return 'getlex'

    def __init__(self, index):
        super(InstructionGetlex, self).__init__()
        self.code = '\x60'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionGetglobalscope(Instruction):

    FORM = 0x64

    @property
    def name(self):
        return 'getglobalscope'

    def __init__(self):
        super(InstructionGetglobalscope, self).__init__()
        self.code = '\x64'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGetglobalslot(Instruction):

    FORM = 0x6e

    @property
    def name(self):
        return 'getglobalslot'

    def __init__(self, slot_index):
        super(InstructionGetglobalslot, self).__init__()
        self.code = '\x6e'
        self.slot_index = slot_index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        # FIXME slot name
        return ' '.join([
            self.name,
            str(self.slot_index)  # slot index
        ])


class InstructionSetglobalslot(Instruction):

    FORM = 0x6f

    @property
    def name(self):
        return 'setglobalslot'

    def __init__(self, slot_index):
        super(InstructionSetglobalslot, self).__init__()
        self.code = '\x6f'
        self.slot_index = slot_index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        # FIXME slot name
        return ' '.join([
            self.name,
            str(self.slot_index),  # slot index
        ])


class InstructionGetlocal(Instruction):

    FORM = 0x62

    @property
    def name(self):
        return 'getlocal'

    def __init__(self, index):
        super(InstructionGetlocal, self).__init__()
        self.code = '\x62'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index),  # register index
        ])


class InstructionSetlocal(Instruction):

    FORM = 0x63

    @property
    def name(self):
        return 'setlocal'

    def __init__(self, index):
        super(InstructionSetlocal, self).__init__()
        self.code = '\x63'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index),  # register index
        ])


class InstructionGetlocal0(Instruction):

    FORM = 0xd0

    @property
    def name(self):
        return 'getlocal0'

    def __init__(self):
        super(InstructionGetlocal0, self).__init__()
        self.code = '\xd0'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGetlocal1(Instruction):

    FORM = 0xd1

    @property
    def name(self):
        return 'getlocal1'

    def __init__(self):
        super(InstructionGetlocal1, self).__init__()
        self.code = '\xd1'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGetlocal2(Instruction):

    FORM = 0xd2

    @property
    def name(self):
        return 'getlocal2'

    def __init__(self):
        super(InstructionGetlocal2, self).__init__()
        self.code = '\xd2'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGetlocal3(Instruction):

    FORM = 0xd3

    @property
    def name(self):
        return 'getlocal3'

    def __init__(self):
        super(InstructionGetlocal3, self).__init__()
        self.code = '\xd3'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionSetlocal0(Instruction):

    FORM = 0xd4

    @property
    def name(self):
        return 'setlocal0'

    def __init__(self):
        super(InstructionSetlocal0, self).__init__()
        self.code = '\xd4'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionSetlocal1(Instruction):

    FORM = 0xd5

    @property
    def name(self):
        return 'setlocal1'

    def __init__(self):
        super(InstructionSetlocal1, self).__init__()
        self.code = '\xd5'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionSetlocal2(Instruction):

    FORM = 0xd6

    @property
    def name(self):
        return 'setlocal2'

    def __init__(self):
        super(InstructionSetlocal2, self).__init__()
        self.code = '\xd6'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionSetlocal3(Instruction):

    FORM = 0xd7

    @property
    def name(self):
        return 'setlocal3'

    def __init__(self):
        super(InstructionSetlocal3, self).__init__()
        self.code = '\xd7'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionGetscopeobject(Instruction):

    FORM = 0x65

    @property
    def name(self):
        return 'getscopeobject'

    def __init__(self, index):
        super(InstructionGetscopeobject, self).__init__()
        self.code = '\x65'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index)  # index of scope object
        ])


class InstructionGetproperty(Instruction):

    FORM = 0x66

    @property
    def name(self):
        return 'getproperty'

    def __init__(self, index):
        super(InstructionGetproperty, self).__init__()
        self.code = '\x66'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionSetproperty(Instruction):

    FORM = 0x61

    @property
    def name(self):
        return 'setproperty'

    def __init__(self, index):
        super(InstructionSetproperty, self).__init__()
        self.code = '\x61'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionGetslot(Instruction):

    FORM = 0x6c

    @property
    def name(self):
        return 'getslot'

    def __init__(self, slot_index):
        super(InstructionGetslot, self).__init__()
        self.code = '\x6c'
        self.slot_index = slot_index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        # FIXME slot name
        return ' '.join([
            self.name,
            str(self.slot_index),  # slot index
        ])


class InstructionSetslot(Instruction):

    FORM = 0x6d

    @property
    def name(self):
        return 'setslot'

    def __init__(self, slot_index):
        super(InstructionSetslot, self).__init__()
        self.code = '\x6d'
        self.slot_index = slot_index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        # FIXME slot name
        return ' '.join([
            self.name,
            str(self.slot_index),  # slot index
        ])


class InstructionGetsuper(Instruction):

    FORM = 0x04

    @property
    def name(self):
        return 'getsuper'

    def __init__(self, index):
        super(InstructionGetsuper, self).__init__()
        self.code = '\x04'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionSetsuper(Instruction):

    FORM = 0x05

    @property
    def name(self):
        return 'setsuper'

    def __init__(self, index):
        super(InstructionSetsuper, self).__init__()
        self.code = '\x05'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionGetouterscope(Instruction):

    FORM = 0x67

    @property
    def name(self):
        return 'getouterscope'

    def __init__(self):
        super(InstructionGetouterscope, self).__init__()
        self.code = '\x67'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionHasnext(Instruction):

    FORM = 0x1f

    @property
    def name(self):
        return 'hasnext'

    def __init__(self):
        super(InstructionHasnext, self).__init__()
        self.code = '\x1f'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionHasnext2(Instruction):

    FORM = 0x32

    @property
    def name(self):
        return 'hasnext2'

    def __init__(self, object_reg, index_reg):
        super(InstructionHasnext2, self).__init__()
        self.code = '\x32'
        self.object_reg = object_reg
        self.index_reg = index_reg

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        # FIXME reg name
        return ' '.join([
            self.name,
            str(self.object_reg),
            str(self.index_reg),
        ])


class InstructionNextname(Instruction):

    FORM = 0x1e

    @property
    def name(self):
        return 'nextname'

    def __init__(self):
        super(InstructionNextname, self).__init__()
        self.code = '\x1e'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionNextvalue(Instruction):

    FORM = 0x23

    @property
    def name(self):
        return 'nextvalue'

    def __init__(self):
        super(InstructionNextvalue, self).__init__()
        self.code = '\x23'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionJump(Instruction):

    FORM = 0x10

    @property
    def name(self):
        return 'jump'

    def __init__(self, offset):
        super(InstructionJump, self).__init__()
        self.code = '\x10'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfnlt(Instruction):

    FORM = 0x0c

    @property
    def name(self):
        return 'ifnlt'

    def __init__(self, offset):
        super(InstructionIfnlt, self).__init__()
        self.code = '\x0c'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfnle(Instruction):

    FORM = 0x0d

    @property
    def name(self):
        return 'ifnle'

    def __init__(self, offset):
        super(InstructionIfnle, self).__init__()
        self.code = '\x0d'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfngt(Instruction):

    FORM = 0x0e

    @property
    def name(self):
        return 'ifngt'

    def __init__(self, offset):
        super(InstructionIfngt, self).__init__()
        self.code = '\x0e'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfnge(Instruction):

    FORM = 0x0f

    @property
    def name(self):
        return 'ifnge'

    def __init__(self, offset):
        super(InstructionIfnge, self).__init__()
        self.code = '\x0f'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIftrue(Instruction):

    FORM = 0x11

    @property
    def name(self):
        return 'iftrue'

    def __init__(self, offset):
        super(InstructionIftrue, self).__init__()
        self.code = '\x11'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIffalse(Instruction):

    FORM = 0x12

    @property
    def name(self):
        return 'iffalse'

    def __init__(self, offset):
        super(InstructionIffalse, self).__init__()
        self.code = '\x12'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfeq(Instruction):

    FORM = 0x13

    @property
    def name(self):
        return 'ifeq'

    def __init__(self, offset):
        super(InstructionIfeq, self).__init__()
        self.code = '\x13'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfne(Instruction):

    FORM = 0x14

    @property
    def name(self):
        return 'ifne'

    def __init__(self, offset):
        super(InstructionIfne, self).__init__()
        self.code = '\x14'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIflt(Instruction):

    FORM = 0x15

    @property
    def name(self):
        return 'iflt'

    def __init__(self, offset):
        super(InstructionIflt, self).__init__()
        self.code = '\x15'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfle(Instruction):

    FORM = 0x16

    @property
    def name(self):
        return 'ifle'

    def __init__(self, offset):
        super(InstructionIfle, self).__init__()
        self.code = '\x16'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfgt(Instruction):

    FORM = 0x17

    @property
    def name(self):
        return 'ifgt'

    def __init__(self, offset):
        super(InstructionIfgt, self).__init__()
        self.code = '\x17'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfge(Instruction):

    FORM = 0x18

    @property
    def name(self):
        return 'ifge'

    def __init__(self, offset):
        super(InstructionIfge, self).__init__()
        self.code = '\x18'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfstricteq(Instruction):

    FORM = 0x19

    @property
    def name(self):
        return 'ifstricteq'

    def __init__(self, offset):
        super(InstructionIfstricteq, self).__init__()
        self.code = '\x19'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIfstrictne(Instruction):

    FORM = 0x1a

    @property
    def name(self):
        return 'ifstrictne'

    def __init__(self, offset):
        super(InstructionIfstrictne, self).__init__()
        self.code = '\x1a'
        self.offset = offset

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_end + self.offset),
        ])


class InstructionIn(Instruction):

    FORM = 0xb4

    @property
    def name(self):
        return 'in'

    def __init__(self):
        super(InstructionIn, self).__init__()
        self.code = '\xb4'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionInitproperty(Instruction):

    FORM = 0x68

    @property
    def name(self):
        return 'initproperty'

    def __init__(self, index):
        super(InstructionInitproperty, self).__init__()
        self.code = '\x68'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionInstanceof(Instruction):

    FORM = 0xb1

    @property
    def name(self):
        return 'instanceof'

    def __init__(self):
        super(InstructionInstanceof, self).__init__()
        self.code = '\xb1'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionIstype(Instruction):

    FORM = 0xb2

    @property
    def name(self):
        return 'istype'

    def __init__(self, index):
        super(InstructionIstype, self).__init__()
        self.code = '\xb2'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_multiname_string(self.index),  # multiname index
        ])


class InstructionIstypelate(Instruction):

    FORM = 0xb3

    @property
    def name(self):
        return 'istypelate'

    def __init__(self):
        super(InstructionIstypelate, self).__init__()
        self.code = '\xb3'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionKill(Instruction):

    FORM = 0x08

    @property
    def name(self):
        return 'kill'

    def __init__(self, index):
        super(InstructionKill, self).__init__()
        self.code = '\x08'
        self.index = index

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.index),  # register index
        ])


class InstructionLabel(Instruction):

    FORM = 0x09

    @property
    def name(self):
        return 'label'

    def __init__(self):
        super(InstructionLabel, self).__init__()
        self.code = '\x09'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionLookupswitch(Instruction):

    FORM = 0x1b

    @property
    def name(self):
        return 'lookupswitch'

    def __init__(self, default_offset, case_offsets):
        super(InstructionLookupswitch, self).__init__()
        self.code = '\x1b'
        self.default_offset = default_offset
        self.case_offsets = case_offsets

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            'ofs{0:04x}'.format(self.code_offset_beg + self.default_offset),
            str(list(map(
                lambda ofs: 'ofs{0:04x}'.format(self.code_offset_beg + ofs),
                self.case_offsets
            ))),
        ])


class InstructionLshift(Instruction):

    FORM = 0xa5

    @property
    def name(self):
        return 'lshift'

    def __init__(self):
        super(InstructionLshift, self).__init__()
        self.code = '\xa5'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionRshift(Instruction):

    FORM = 0xa6

    @property
    def name(self):
        return 'rshift'

    def __init__(self):
        super(InstructionRshift, self).__init__()
        self.code = '\xa6'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionUrshift(Instruction):

    FORM = 0xa7

    @property
    def name(self):
        return 'urshift'

    def __init__(self):
        super(InstructionUrshift, self).__init__()
        self.code = '\xa7'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionNewactivation(Instruction):

    FORM = 0x57

    @property
    def name(self):
        return 'newactivation'

    def __init__(self):
        super(InstructionNewactivation, self).__init__()
        self.code = '\x57'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionNewarray(Instruction):

    FORM = 0x56

    @property
    def name(self):
        return 'newarray'

    def __init__(self, arg_count):
        super(InstructionNewarray, self).__init__()
        self.code = '\x56'
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.arg_count),
        ])


class InstructionNewcatch(Instruction):

    FORM = 0x5a

    @property
    def name(self):
        return 'newcatch'

    def __init__(self, index):
        super(InstructionNewcatch, self).__init__()
        self.code = '\x5a'
        self.index = index

    def resolve(self, constant_pool):
        # FIXME exception index
        return ' '.join([
            self.name,
            str(self.index),
        ])


class InstructionNewfunction(Instruction):

    FORM = 0x40

    @property
    def name(self):
        return 'newfunction'

    def __init__(self, index):
        super(InstructionNewfunction, self).__init__()
        self.code = '\x40'
        self.index = index

    def resolve(self, constant_pool):
        # FIXME method index
        return ' '.join([
            self.name,
            str(self.index),
        ])


class InstructionNewobject(Instruction):

    FORM = 0x55

    @property
    def name(self):
        return 'newobject'

    def __init__(self, arg_count):
        super(InstructionNewobject, self).__init__()
        self.code = '\x55'
        self.arg_count = arg_count

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.arg_count),
        ])


class InstructionNewclass(Instruction):

    FORM = 0x58

    @property
    def name(self):
        return 'newclass'

    def __init__(self, index):
        super(InstructionNewclass, self).__init__()
        self.code = '\x58'
        self.index = index

    def resolve(self, constant_pool):
        # FIXME class index
        return ' '.join([
            self.name,
            str(self.index),
        ])


class InstructionNop(Instruction):

    FORM = 0x02

    @property
    def name(self):
        return 'nop'

    def __init__(self):
        super(InstructionNop, self).__init__()
        self.code = '\x02'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionNot(Instruction):

    FORM = 0x96

    @property
    def name(self):
        return 'not'

    def __init__(self):
        super(InstructionNot, self).__init__()
        self.code = '\x96'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPop(Instruction):

    FORM = 0x29

    @property
    def name(self):
        return 'pop'

    def __init__(self):
        super(InstructionPop, self).__init__()
        self.code = '\x29'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPopscope(Instruction):

    FORM = 0x1d

    @property
    def name(self):
        return 'popscope'

    def __init__(self):
        super(InstructionPopscope, self).__init__()
        self.code = '\x1d'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushbyte(Instruction):

    FORM = 0x24

    @property
    def name(self):
        return 'pushbyte'

    def __init__(self, byte_value):
        super(InstructionPushbyte, self).__init__()
        self.code = '\x24'
        self.byte_value = byte_value

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            hex(self.byte_value)
        ])


class InstructionPushshort(Instruction):

    FORM = 0x25

    @property
    def name(self):
        return 'pushshort'

    def __init__(self, value):
        super(InstructionPushshort, self).__init__()
        self.code = '\x25'
        self.value = value

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(self.value),
        ])


class InstructionPushstring(Instruction):

    FORM = 0x2c

    @property
    def name(self):
        return 'pushstring'

    def __init__(self, index):
        super(InstructionPushstring, self).__init__()
        self.code = '\x2c'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            repr(constant_pool.get_string(self.index)),
        ])


class InstructionPushint(Instruction):

    FORM = 0x2d

    @property
    def name(self):
        return 'pushint'

    def __init__(self, index):
        super(InstructionPushint, self).__init__()
        self.code = '\x2d'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(constant_pool.integers[self.index]),
        ])


class InstructionPushuint(Instruction):

    FORM = 0x2e

    @property
    def name(self):
        return 'pushuint'

    def __init__(self, index):
        super(InstructionPushuint, self).__init__()
        self.code = '\x2e'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(constant_pool.uintegers[self.index]),
        ])


class InstructionPushdouble(Instruction):

    FORM = 0x2f

    @property
    def name(self):
        return 'pushdouble'

    def __init__(self, index):
        super(InstructionPushdouble, self).__init__()
        self.code = '\x2f'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            str(constant_pool.doubles[self.index]),
        ])


class InstructionPushnamespace(Instruction):

    FORM = 0x31

    @property
    def name(self):
        return 'pushnamespace'

    def __init__(self, index):
        super(InstructionPushnamespace, self).__init__()
        self.code = '\x31'
        self.index = index

    def resolve(self, constant_pool):
        return ' '.join([
            self.name,
            constant_pool.get_namespace(self.index),
        ])


class InstructionPushwith(Instruction):

    FORM = 0x1c

    @property
    def name(self):
        return 'pushwith'

    def __init__(self):
        super(InstructionPushwith, self).__init__()
        self.code = '\x1c'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushnull(Instruction):

    FORM = 0x20

    @property
    def name(self):
        return 'pushnull'

    def __init__(self):
        super(InstructionPushnull, self).__init__()
        self.code = '\x20'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushundefined(Instruction):

    FORM = 0x21

    @property
    def name(self):
        return 'pushundefined'

    def __init__(self):
        super(InstructionPushundefined, self).__init__()
        self.code = '\x21'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushtrue(Instruction):

    FORM = 0x26

    @property
    def name(self):
        return 'pushtrue'

    def __init__(self):
        super(InstructionPushtrue, self).__init__()
        self.code = '\x26'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushfalse(Instruction):

    FORM = 0x27

    @property
    def name(self):
        return 'pushfalse'

    def __init__(self):
        super(InstructionPushfalse, self).__init__()
        self.code = '\x27'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushnan(Instruction):

    FORM = 0x28

    @property
    def name(self):
        return 'pushnan'

    def __init__(self):
        super(InstructionPushnan, self).__init__()
        self.code = '\x28'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionPushscope(Instruction):

    FORM = 0x30

    @property
    def name(self):
        return 'pushscope'

    def __init__(self):
        super(InstructionPushscope, self).__init__()
        self.code = '\x30'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionSwap(Instruction):

    FORM = 0x2b

    @property
    def name(self):
        return 'swap'

    def __init__(self):
        super(InstructionSwap, self).__init__()
        self.code = '\x2b'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionThrow(Instruction):

    FORM = 0x03

    @property
    def name(self):
        return 'throw'

    def __init__(self):
        super(InstructionThrow, self).__init__()
        self.code = '\x03'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionTypeof(Instruction):

    FORM = 0x95

    @property
    def name(self):
        return 'typeof'

    def __init__(self):
        super(InstructionTypeof, self).__init__()
        self.code = '\x95'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionReturnvoid(Instruction):

    FORM = 0x47

    @property
    def name(self):
        return 'returnvoid'

    def __init__(self):
        super(InstructionReturnvoid, self).__init__()
        self.code = '\x47'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionReturnvalue(Instruction):

    FORM = 0x48

    @property
    def name(self):
        return 'returnvalue'

    def __init__(self):
        super(InstructionReturnvalue, self).__init__()
        self.code = '\x48'

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return self.name


class InstructionApplytype(Instruction):

    FORM = 0x53

    @property
    def name(self):
        return 'applytype'

    def __init__(self, num):
        super(InstructionApplytype, self).__init__()
        self.code = '\x53'
        self.num = num

    # noinspection PyUnusedLocal
    def resolve(self, constant_pool):
        return ' '.join([self.name, str(self.num)])
