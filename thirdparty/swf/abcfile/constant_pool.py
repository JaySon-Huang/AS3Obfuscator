#!/usr/bin/env python
# encoding=utf-8

import cStringIO as StringIO
from pprint import pformat
from swf.stream import int32


# noinspection PyUnresolvedReferences
class StMultiname(object):
    QName       = 0x07
    QNameA      = 0x0D
    RTQName     = 0x0F
    RTQNameA    = 0x10
    RTQNameL    = 0x11
    RTQNameLA   = 0x12
    Multiname   = 0x09
    MultinameA  = 0x0E
    MultinameL  = 0x1B
    MultinameLA = 0x1C
    # According to jpexs-decompiler
    # https://github.com/jindrapetrik/jpexs-decompiler/ \
    #   blob/master/libsrc/ffdec_lib/src/ \
    #   com/jpexs/decompiler/flash/abc/types/Multiname.java
    TYPENAME    = 0x1D

    def __init__(self):
        self.kind = None

    def __repr__(self):
        s = '<StMultiname'
        if self.kind in (StMultiname.QName, StMultiname.QNameA):
            s += '(QName/QNameA) name:{self.name} namespace:{self.ns}>'
        elif self.kind in (StMultiname.RTQName, StMultiname.RTQNameA):
            s += '(RTQName/RTQNameA) name:{self.name}>'
        elif self.kind in (StMultiname.RTQNameL, StMultiname.RTQNameLA):
            s += '(RTQNameL/RTQNameLA) >'
        elif self.kind in (StMultiname.Multiname, StMultiname.MultinameA):
            s += '(Multiname/MultinameA) name:{self.name} ns_set:{self.ns_set}>'
        elif self.kind in (StMultiname.MultinameL, StMultiname.MultinameLA):
            s += '(MultinameL/MultinameLA) ns_set:{self.ns_set}>'
        elif self.kind == StMultiname.TYPENAME:
            s += '(TYPENAME) qname:{self.qname_index} params:{self.params}>'
        return s.format(self=self)

    @classmethod
    def create(cls, stream):
        obj = cls()
        obj.kind = stream.readUI8()
        if obj.kind in (cls.QName, cls.QNameA):
            obj.ns = stream.readEncodedU32()
            obj.name = stream.readEncodedU32()
        elif obj.kind in (cls.RTQName, cls.RTQNameA):
            obj.name = stream.readEncodedU32()
        elif obj.kind in (cls.RTQNameL, cls.RTQNameLA):
            pass
        elif obj.kind in (cls.Multiname, cls.MultinameA):
            obj.name = stream.readEncodedU32()
            obj.ns_set = stream.readEncodedU32()
        elif obj.kind in (cls.MultinameL, cls.MultinameLA):
            obj.ns_set = stream.readEncodedU32()
        elif obj.kind == cls.TYPENAME:
            # Multiname index!!!
            obj.qname_index = stream.readEncodedU32()
            params_length = stream.readEncodedU32()
            # multiname indices!
            obj.params = [
                stream.readEncodedU32()
                for _ in range(params_length)
            ]
        else:
            raise Exception('Unknown kind: {0:02x}'.format(obj.kind))
        return obj

    def solve_name(self, const_pool):
        if self.kind in (self.QName, self.QNameA):
            return {
                'name': const_pool.get_string(self.name),
                'namespace': const_pool.get_namespace(self.ns),
            }
        elif self.kind in (self.RTQName, self.RTQNameA):
            return {
                'name': const_pool.get_string(self.name),
            }
        elif self.kind in (self.RTQNameL, self.RTQNameLA):
            return {}
        elif self.kind in (self.Multiname, self.MultinameA):
            return {
                'name': const_pool.get_string(self.name),
                'ns_set': const_pool.get_ns_set(self.ns_set),
            }
        elif self.kind in (self.MultinameL, self.MultinameLA):
            return {
                'ns_set': const_pool.get_ns_set(self.ns_set),
            }
        elif self.kind == self.TYPENAME:
            return {
                'qname': const_pool.get_multiname(self.qname_index),
                'params': [const_pool.get_multiname(i) for i in self.params]
            }


class ConstantPool(object):

    NAMESPACE = 0x08
    PACKAGE_NAMESPACE = 0x16
    PACKAGE_INTERNAL_NAMESPACE = 0x17
    PROTECTED_NAMESPACE = 0x18
    EXPLICIT_NAMESPACE = 0x19
    STATIC_PROTECTED_NS = 0x1A
    PRIVATE_NAMESPACE = 0x05

    def __init__(self):
        super(ConstantPool, self).__init__()
        self.offset = {}
        self.integers = [0, ]
        self.uintegers = [0, ]
        self.doubles = [0.0, ]
        self._strings = ['*', ]
        self._namespaces = [(None, 0), ]
        self._ns_sets = [[], ]
        self._multinames = [None, ]

    def details(self):
        return '''<ConstantPool>
integers   ({}):
{}
uintegers  ({}):
{}
doubles    ({}):
{}
strings    ({}):
{}
namespaces ({}):
{}
ns_sets    ({}):
{}
multinames ({}):
{}
</ConstantPool>'''.format(
    len(self.integers),   pformat(self.integers),
    len(self.uintegers),  pformat(self.uintegers),
    len(self.doubles),    pformat(self.doubles),
    len(self._strings),   pformat(self._strings),
    len(self.namespaces), pformat(self.namespaces),
    len(self._ns_sets),   pformat(self._ns_sets),
    len(self._multinames), pformat(self._multinames),
    self=self
)

    @property
    def namespaces(self):
        return [ns[1] for ns in self._namespaces]

    def get_string(self, index=None):
        if index is None:
            return self._strings
        return self._strings[index]

    def get_namespace(self, index=None):
        if index is None:
            return list(map(
                lambda ns: self._strings[ns[1]],
                self._namespaces
            ))
        return self._strings[self._namespaces[index][1]]

    def get_ns_set(self, index=None):
        if index is None:
            return list(map(
                lambda ns_set: list(map(
                    lambda ns: self.get_namespace(ns),
                    ns_set
                )),
                self._ns_sets
            ))
        return list(map(
            lambda ns: self.get_namespace(ns),
            self._ns_sets[index]
        ))

    def get_multiname(self, index=None):
        if index is None:
            return [
                self.get_multiname(i)
                for i in range(len(self._multinames))
            ]
        if index == 0:
            return {'name': '*', }
        return self._multinames[index].solve_name(self)

    def get_namespace_string(self, index):
        kind = self._namespaces[index][0]
        if kind == ConstantPool.PRIVATE_NAMESPACE:
            return 'PrivateNamespace("{0}")'.format(self.get_namespace(index))
        elif kind == ConstantPool.PROTECTED_NAMESPACE:
            return 'ProtectedNamespace("{0}")'.format(self.get_namespace(index))
        elif kind == ConstantPool.PACKAGE_NAMESPACE:
            return 'PakcageNamespace("{0}")'.format(self.get_namespace(index))
        else:
            return 'Namespace("{0}")'.format(self.get_namespace(index))

    def get_namespace_set_string(self, index):
        return 'NS_SET:<{0}>'.format(', '.join(
            map(self.get_namespace_string, self._ns_sets[index])
        ))

    def get_multiname_string(self, index):
        multiname = self._multinames[index]
        try:
            if multiname.kind in (StMultiname.QName, StMultiname.QNameA):
                ns = self.get_namespace_string(multiname.ns)
                name = self._strings[multiname.name]
                return u'QName({0}, "{1}")'.format(ns, name)
            elif multiname.kind in (StMultiname.RTQName, StMultiname.RTQNameA):
                name = self._strings[multiname.name]
                return u'RTQName("{0}")'.format(name)
            elif multiname.kind in (StMultiname.RTQNameL, StMultiname.RTQNameLA):
                return u'RTQNameL()'
            elif multiname.kind in (StMultiname.Multiname, StMultiname.MultinameA):
                name = self._strings[multiname.name]
                return u'Multiname({0}, "{1}")'.format(
                    self.get_namespace_set_string(multiname.ns_set),
                    name
                )
            elif multiname.kind in (StMultiname.MultinameL, StMultiname.MultinameLA):
                return u'MultinameL({0})'.format(
                    self.get_namespace_set_string(multiname.ns_set)
                )
            elif multiname.kind == StMultiname.TYPENAME:
                return u'TYPENAME({0}, {1})'.format(
                    self.get_multiname_string(multiname.qname_index),
                    multiname.params
                )
        except UnicodeDecodeError:
            info = self.get_multiname(index)
            return 'Parse Multiname error: ' + str(info)

    def parse(self, stream):
        self.offset['numbers'] = stream.tell()
        self._parse_numbers(stream)

        self.offset['strings'] = stream.tell()
        string_count = stream.readEncodedU32()
        for _ in range(string_count-1):
            size = stream.readEncodedU32()
            if size == 0:
                self._strings.append('')
                continue
            utf8_str = stream.read(size)
            self._strings.append(utf8_str)

        self.offset['namespaces'] = stream.tell()
        namespace_count = stream.readEncodedU32()
        for _ in range(namespace_count-1):
            kind = stream.readUI8()
            name = stream.readEncodedU32()
            self._namespaces.append((kind, name))

        self.offset['ns_sets'] = stream.tell()
        ns_set_count = stream.readEncodedU32()
        for _ in range(ns_set_count-1):
            count = stream.readEncodedU32()
            ns = [stream.readEncodedU32() for __ in range(count)]
            self._ns_sets.append(ns)

        self.offset['multinames'] = stream.tell()
        multiname_count = stream.readEncodedU32()
        for _ in range(multiname_count-1):
            self._multinames.append(StMultiname.create(stream))

    def _parse_numbers(self, stream):
        int_count = stream.readEncodedU32()
        for _ in range(int_count-1):
            self.integers.append(int32(stream.readEncodedU32()))

        uint_count = stream.readEncodedU32()
        for _ in range(uint_count-1):
            self.uintegers.append(stream.readEncodedU32())

        double_count = stream.readEncodedU32()
        for _ in range(double_count-1):
            self.doubles.append(stream.readDOUBLE())
