#!/usr/bin/env python
# encoding=utf-8

from thirdparty.swf.abcfile import StMethodInfo, StInstanceInfo
from thirdparty.swf.abcfile.trait import TraitFactory
from thirdparty.swf.abcfile.constant_pool import StMultiname
from stream import ABCFileOutputStream


class MultinameConverter(object):

    @staticmethod
    def to_bytes(multiname):
        out_stream = ABCFileOutputStream()

        out_stream.writeU8(multiname.kind)
        if multiname.kind in (StMultiname.QName, StMultiname.QNameA):
            out_stream.writeU30(multiname.ns)
            out_stream.writeU30(multiname.name)
        elif multiname.kind in (StMultiname.RTQName, StMultiname.RTQNameA):
            out_stream.writeU30(multiname.name)
        elif multiname.kind in (StMultiname.RTQNameL, StMultiname.RTQNameLA):
            pass
        elif multiname.kind in (StMultiname.Multiname, StMultiname.MultinameA):
            out_stream.writeU30(multiname.name)
            out_stream.writeU30(multiname.ns_set)
        elif multiname.kind in (StMultiname.MultinameL, StMultiname.MultinameLA):
            out_stream.writeU30(multiname.ns_set)
        elif multiname.kind == StMultiname.TYPENAME:
            out_stream.writeU30(multiname.qname_index)
            params_length = len(multiname.params)
            out_stream.writeU30(params_length)
            for param in multiname.params:
                out_stream.writeU30(param)

        return out_stream.getvalue()


class ConstantPoolConverter(object):

    # noinspection PyProtectedMember
    @staticmethod
    def to_bytes(pool):
        out_stream = ABCFileOutputStream()

        count = len(pool.integers)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for integer in pool.integers[1:]:
                out_stream.writeS32(integer)

        count = len(pool.uintegers)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for uinteger in pool.uintegers[1:]:
                out_stream.writeU32(uinteger)

        count = len(pool.doubles)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for d in pool.doubles[1:]:
                out_stream.writeD64(d)

        count = len(pool._strings)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for s in pool._strings[1:]:
                str_size = len(s)
                out_stream.writeU30(str_size)
                out_stream.write(s)

        count = len(pool._namespaces)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for kind, name in pool._namespaces[1:]:
                out_stream.writeU8(kind)
                out_stream.writeU30(name)

        count = len(pool._ns_sets)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for ns_set in pool._ns_sets[1:]:
                ns_count = len(ns_set)
                out_stream.writeU30(ns_count)
                for ns in ns_set:
                    out_stream.writeU30(ns)

        count = len(pool._multinames)
        if count <= 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(count)
            for multiname in pool._multinames[1:]:
                m_bytes = MultinameConverter.to_bytes(multiname)
                out_stream.write(m_bytes)

        return out_stream.getvalue()


class StMethodInfoConverter(object):

    @staticmethod
    def to_bytes(method_info):
        out_stream = ABCFileOutputStream()
        param_count = len(method_info.param_types)
        out_stream.writeU30(param_count)
        out_stream.writeU30(method_info.return_type)
        for param_type in method_info.param_types:
            out_stream.writeU30(param_type)
        out_stream.writeU30(method_info.name)
        out_stream.writeU8(method_info.flags)
        if method_info.flags & StMethodInfo.HAS_OPTIONAL:
            option_count = len(method_info.options)
            out_stream.writeU30(option_count)
            for option in method_info.options:
                out_stream.writeU30(option['val'])
                out_stream.writeU8(option['kind'])
        if method_info.flags & StMethodInfo.HAS_PARAM_NAMES:
            for param_name in method_info.param_names:
                out_stream.writeU30(param_name)
        return out_stream.getvalue()


class StTraitConverter(object):

    @staticmethod
    def to_bytes(trait):
        out_stream = ABCFileOutputStream()
        out_stream.writeU30(trait.name)
        out_stream.writeU8(trait.kind)
        trait_type = trait.kind & 0x0f
        if trait_type in (TraitFactory.Trait_Slot, TraitFactory.Trait_Const):
            out_stream.writeU30(trait.slot_id)
            out_stream.writeU30(trait.type_name)
            out_stream.writeU30(trait.vindex)
            if trait.vindex != 0:
                out_stream.writeU8(trait.vkind)
        elif trait_type == TraitFactory.Trait_Class:
            out_stream.writeU30(trait.slot_id)
            out_stream.writeU30(trait.classi)
        elif trait_type == TraitFactory.Trait_Function:
            out_stream.writeU30(trait.slot_id)
            out_stream.writeU30(trait.function)
        elif trait_type in (
                TraitFactory.Trait_Method,
                TraitFactory.Trait_Getter,
                TraitFactory.Trait_Setter):
            out_stream.writeU30(trait.disp_id)
            out_stream.writeU30(trait.method)

        if (trait.kind >> 4) & TraitFactory.ATTR_Metadata:
            count = len(trait.metadatas)
            out_stream.writeU30(count)
            for metadata in trait.metadatas:
                out_stream.writeU30(metadata)

        return out_stream.getvalue()


class StInstanceInfoConverter(object):

    @staticmethod
    def to_bytes(instance):
        out_stream = ABCFileOutputStream()
        out_stream.writeU30(instance.name)
        out_stream.writeU30(instance.super_name)
        out_stream.writeU8(instance.flags)
        if instance.flags & StInstanceInfo.CONSTANT_ClassProtectedNs:
            out_stream.writeU30(instance.protectedNs)
        out_stream.writeU30(instance.intrf_count)
        for interf in instance.interfaces:
            out_stream.writeU30(interf)
        out_stream.writeU30(instance.iinit)
        # Trait
        out_stream.writeU30(instance.trait_count)
        for trait in instance.traits:
            trait_bytes = StTraitConverter.to_bytes(trait)
            out_stream.write(trait_bytes)
        return out_stream.getvalue()


class StClassInfoConverter(object):

    @staticmethod
    def to_bytes(class_):
        out_stream = ABCFileOutputStream()
        out_stream.writeU30(class_.cinit)
        trait_count = len(class_.traits)
        out_stream.writeU30(trait_count)
        for trait in class_.traits:
            trait_bytes = StTraitConverter.to_bytes(trait)
            out_stream.write(trait_bytes)
        return out_stream.getvalue()


class StMethodBodyConverter(object):

    @staticmethod
    def to_bytes(body):
        out_stream = ABCFileOutputStream()
        out_stream.writeU30(body.method)
        out_stream.writeU30(body.max_stack)
        out_stream.writeU30(body.local_count)
        out_stream.writeU30(body.init_scope_depth)
        out_stream.writeU30(body.max_scope_depth)
        code_length = len(body.code)
        out_stream.writeU30(code_length)
        out_stream.write(body.code)
        exception_count = len(body.exceptions)
        out_stream.writeU30(exception_count)
        for exception in body.exceptions:
            out_stream.writeU30(exception.from_)
            out_stream.writeU30(exception.to)
            out_stream.writeU30(exception.target)
            out_stream.writeU30(exception.exc_type)
            out_stream.writeU30(exception.var_name)
        trait_count = len(body.traits)
        out_stream.writeU30(trait_count)
        for trait in body.traits:
            trait_bytes = StTraitConverter.to_bytes(trait)
            out_stream.write(trait_bytes)
        return out_stream.getvalue()


class ABCFileConverter(object):

    # noinspection PyProtectedMember
    @staticmethod
    def to_bytes(abcfile):
        out_stream = ABCFileOutputStream()
        out_stream.writeU16(abcfile._version['minor'])
        out_stream.writeU16(abcfile._version['major'])
        pool_bytes = ConstantPoolConverter.to_bytes(abcfile.const_pool)
        out_stream.write(pool_bytes)
        # method
        count = len(abcfile.methods)
        out_stream.writeU30(count)
        for method in abcfile.methods:
            method_bytes = StMethodInfoConverter.to_bytes(method)
            out_stream.write(method_bytes)
        # metadata
        count = len(abcfile.metadatas)
        out_stream.writeU30(count)
        for metadata in abcfile.metadatas:
            out_stream.writeU30(metadata['name'])
            item_count = len(metadata['items'])
            out_stream.writeU30(item_count)
            for item in metadata['items']:
                out_stream.writeU30(item['key'])
                out_stream.writeU30(item['value'])
        # class/instance
        count = len(abcfile.instances)
        out_stream.writeU30(count)
        for instance in abcfile.instances:
            instance_bytes = StInstanceInfoConverter.to_bytes(instance)
            out_stream.write(instance_bytes)
        for class_ in abcfile.classes:
            class_bytes = StClassInfoConverter.to_bytes(class_)
            out_stream.write(class_bytes)
        # script
        count = len(abcfile.scripts)
        out_stream.writeU30(count)
        for script in abcfile.scripts:
            out_stream.writeU30(script['init'])
            trait_count = len(script['traits'])
            out_stream.writeU30(trait_count)
            for trait in script['traits']:
                trait_bytes = StTraitConverter.to_bytes(trait)
                out_stream.write(trait_bytes)
        # method body
        count = len(abcfile.method_bodies)
        out_stream.writeU30(count)
        for body in abcfile.method_bodies:
            body_bytes = StMethodBodyConverter.to_bytes(body)
            out_stream.write(body_bytes)
        return out_stream.getvalue()


class TagHeaderConverter(object):

    @staticmethod
    def to_bytes(tag_type, header):
        out_stream = ABCFileOutputStream()
        if header.content_length < 0x3f:
            out_stream.writeUI16(
                (tag_type << 6) | header.content_length
            )
        else:
            out_stream.writeUI16((tag_type << 6) | 0x3f)
            out_stream.writeUI32(header.content_length)
        return out_stream.getvalue()


class TagDoABCConverter(object):

    @staticmethod
    def to_bytes(tag):
        out_stream = ABCFileOutputStream()
        out_stream.write(TagHeaderConverter.to_bytes(tag.type, tag.header))
        out_stream.writeSI32(tag.lazyInitializeFlag)
        out_stream.write(tag.abcName + '\x00')
        out_stream.write(tag.bytes)
        return out_stream.getvalue()


class TagSymbolConverter(object):

    @staticmethod
    def to_bytes(tag):
        out_stream = ABCFileOutputStream()
        out_stream.write(TagHeaderConverter.to_bytes(tag.type, tag.header))
        out_stream.writeUI16(len(tag.symbols))
        for symbol in tag.symbols:
            out_stream.writeUI16(symbol.tagId)
            out_stream.write(symbol.name + '\x00')
        return out_stream.getvalue()


class TagDefineBinaryDataConverter(object):

    @staticmethod
    def to_bytes(tag):
        out_stream = ABCFileOutputStream()
        out_stream.write(TagHeaderConverter.to_bytes(tag.type, tag.header))
        out_stream.writeUI16(tag.characterId)
        out_stream.writeUI32(tag.reserved)
        out_stream.write(tag.data)
        return out_stream.getvalue()
