#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import re
import copy
import struct
import pprint
import os.path
from collections import defaultdict
import six
from six import BytesIO
range = xrange

from swf.movie import SWF
from swf.stream import SWFStream
from swf.tag import (TagDoABC, TagSymbolClass)
from swf.abcfile import ABCFile, StMethodInfo
from swf.abcfile.trait import (
    StTraitClass,
    StTraitFunction,
    StTraitMethod,
    StTraitSlot
)

from utils import (
    filepath2module, module2filepath,
    splitABCName, joinPackageClassName,
)
from asdox.asGrammar import (
    METHOD_SIGNATURE, METHOD_MODIFIER,
    IDENTIFIER,
    IMPORT_DEFINITION,
)
METHOD_SIGNATURE.parseWithTabs()
METHOD_MODIFIER.parseWithTabs()
IDENTIFIER.parseWithTabs()
IMPORT_DEFINITION.parseWithTabs()


class SourceCodeReplacer(object):
    """
    替换 .as/.mxml 中的源代码, 但是在替换属性的时候会比较麻烦, 没继续往下写
    """

    @staticmethod
    def replace(source, cls, packages, modulepath, names_map):
        new_lines = []
        for line in source.splitlines():
            # 替换包名
            m = re.search(r'package\s+' + modulepath, line)
            if m:
                filepath = module2filepath(modulepath)
                line = re.sub(
                    r'package\s+' + modulepath,
                    'package ' + filepath2module(names_map['module'][filepath]),
                    line
                )
            # 替换类名
            m = re.search(r'class\s+' + cls.name, line)
            if m:
                line = re.sub(
                    r'class\s+' + cls.name,
                    'class ' + cls.fuzzy.name,
                    line
                )
            # TODO 替换成员变量名
            new_lines.append(line)
        source = '\n'.join(new_lines)
        # 替换 import
        imported_classes = []
        for result in reversed(list(IMPORT_DEFINITION.scanString(source))):
            name, beg, end = result; name = name[0];
            # print('import', name, '@', beg, end)
            imported_classes.append(name)
            key = module2filepath(name)
            if key in names_map['class']:
                source = '{0}import {1};{2}'.format(
                    source[:beg],
                    filepath2module(names_map['class'][key]),
                    source[end:]
                )
            # TODO 替换 import a.b.*;
        # 默认把当前包下的类包含进来
        imported_classes += packages[modulepath].classes.keys()
        # TODO 替换变量所属类名
        for imported_cls in imported_classes:
            # 没有混淆的类, 跳过
            key = module2filepath(imported_cls)
            if key not in names_map['class']:
                continue
            short_name = imported_cls.split('.')[-1]
            for result in reversed(list(IDENTIFIER.scanString(source))):
                name, beg, end = result; name = name[0];
                if name == short_name:
                    # 替换被混淆的类名
                    source = (
                        source[:beg]
                        + os.path.split(names_map['class'][key])[-1]
                        + source[end:]
                    )
                    # TODO 替换被混淆的类的方法名/公有变量名
        # 替换函数
        for method in cls.methods.values():
            if method.visibility == 'private':
                # print('private method', method, method.visibility)
                # 私有函数, 只在该文件中出现
                for result in reversed(list(IDENTIFIER.scanString(source))):
                    name, beg, end = result; name = name[0];
                    if name == method.name:
                        # print(name, '@', beg, end)
                        source = (
                            source[:beg]
                            + cls.fuzzy.methods[method.name].name
                            + source[end:]
                        )
            elif method.name == cls.name:
                # print('construct method', method, method.visibility)
                # 构造函数, 在别的文件中相当于类名
                for result in reversed(list(IDENTIFIER.scanString(source))):
                    name, beg, end = result; name = name[0];
                    if name == method.name:
                        source = (
                            source[:beg]
                            + cls.fuzzy.name
                            + source[end:]
                        )
            else:
                # TODO public/protected
                # print('method', method, method.visibility)
                pass
        # from IPython import embed;embed();
        '''
        # 替换变量
        for var in cls.variables.values():
            if var.visibility == 'private':
                # 私有变量
                for result in reversed(list(IDENTIFIER.scanString(source))):
                    name, beg, end = result; name = name[0];
                    if name == var.name:
                        source = (
                            source[:beg]
                            + cls.fuzzy.variables[var.name].name
                            + source[end:]
                        )
            else:
                # TODO public/protected
                # print('var', var, var.visibility)
                pass
        '''
        return source


# noinspection PyPep8Naming,PyTypeChecker
class OutputStream(BytesIO):

    def writeU30(self, num):
        # FIXME: value >= 128
        while num > 127:
            self.write(struct.pack('B', ((num & 0x7F) | 0x80)))
            num >>= 7
        self.write(struct.pack('B', num))

    def writeU8(self, num):
        self.write(six.int2byte(num))

    def writeUI16(self, num):
        self.write(struct.pack('H', num))

    def writeUI32(self, num):
        self.write(struct.pack('<I', num))

    def writeSI32(self, num):
        self.write(struct.pack('<i', num))


class SWFFileReplacer(object):

    def __init__(self, packages, names_map):
        super(SWFFileReplacer, self).__init__()
        self.packages = packages
        self.names_map = {
            'module': {},
            'class': {},
        }
        for key in names_map['module']:
            self.names_map['module'][filepath2module(key)] = filepath2module(
                names_map['module'][key]
            )
        for key in names_map['class']:
            self.names_map['class'][filepath2module(key)] = filepath2module(
                names_map['class'][key]
            )

    def replace(self, swf_filename, out_filename):
        with open(swf_filename, 'rb') as infile:
            s = SWF(infile, is_quick_mode=True)
            infile.seek(0)
            original_bytes = infile.read()
        with open(out_filename, 'wb') as outfile:
            outfile.write('FWS')
            outfile.write(struct.pack('B', s.header.version))
            outfile.write(struct.pack('<I', 0))  # 先占4bytes空间, 最后再seek到这里写入数据
            outfile.write(original_bytes[3+1+4:s.tags[0].file_offset])
            for tag in s.tags:
                print('0x{0:04x}({1:5d}) Tag:{2}'.format(
                    tag.file_offset, tag.header.tag_length, tag.name
                ))
                # TODO 把tag转换为bytes提炼为一个类的功能
                if tag.name == 'DoABC':
                    new_tag = TagDoABCReplacer(self.packages, self.names_map, tag).replace()
                    if new_tag is not tag:
                        print('modified TagDoABC: {0}'.format(tag.abcName))
                    else:
                        print('not modified TagDoABC: {0}'.format(tag.abcName))
                    out_stream = OutputStream()
                    # FIXME 默认 TagDoABC 长度都大于63
                    out_stream.writeUI16((new_tag.type<<6) | 0x3f)
                    out_stream.writeSI32(new_tag.header.content_length)
                    out_stream.writeSI32(new_tag.lazyInitializeFlag)
                    out_stream.write(new_tag.abcName + '\x00')
                    out_stream.write(new_tag.bytes)
                    outfile.write(out_stream.getvalue())
                elif tag.name == 'SymbolClass':
                    new_tag = self._replaceTagSymbolClass(tag)
                    out_stream = OutputStream()
                    if new_tag.header.content_length < 0x3f:
                        out_stream.writeUI16(
                            (new_tag.type<<6) | new_tag.header.content_length
                        )
                    else:
                        out_stream.writeUI16((new_tag.type<<6) | 0x3f)
                        out_stream.writeUI32(new_tag.header.content_length)
                    out_stream.writeUI16(len(new_tag.symbols))
                    for symbol in new_tag.symbols:
                        out_stream.writeUI16(symbol.tagId)
                        out_stream.write(symbol.name + '\x00')
                    outfile.write(out_stream.getvalue())
                else:
                    # 其他tag保持原有bytes
                    outfile.write(original_bytes[
                        tag.file_offset:(tag.file_offset+tag.header.tag_length)
                    ])
                    continue
            file_length = outfile.tell()
            outfile.seek(3 + 1)
            outfile.write(struct.pack('<I', file_length))

    def _replaceTagSymbolClass(self, tag):
        new_tag = TagSymbolClass()
        symbols_length = 0
        for symbol in tag.symbols:
            new_symbol = copy.copy(symbol)
            if symbol.name in self.names_map['class']:
                new_symbol.name = self.names_map['class'][symbol.name]
            new_tag.symbols.append(new_symbol)
            # 2 for id, others for c-string size
            symbols_length += 2 + len(new_symbol.name) + 1
        # 2 for num of symbols, others for symbols' size
        new_tag.header = copy.copy(tag.header)
        new_tag.header.content_length = 2 + symbols_length
        return new_tag


class TagDoABCReplacer(object):
    def __init__(self, packages, names_map, original_tag):
        self.packages = packages
        self.names_map = names_map
        self.original_tag = original_tag
        self.abcClass = None
        self.strings = ['*', ]

    def replace(self):
        # 官方库返回原来的tag
        if (self.original_tag.abcName.startswith('flashx/')
            or self.original_tag.abcName.startswith('mx/')
            or self.original_tag.abcName.startswith('spark/')):
            return self.original_tag
        # 从ABCName中获取包名,类名
        package, classname = splitABCName(self.original_tag.abcName)
        # 没有源代码的类(第三方库)返回原来的tag
        if (package not in self.packages
                or classname not in self.packages[package].classes):
            return self.original_tag

        # 开始生成新的 DoABC tag
        new_tag = TagDoABC()
        new_tag.header = copy.copy(self.original_tag.header)
        new_tag.abcName = self.original_tag.abcName  # FIXME 替换abcName
        new_tag.lazyInitializeFlag = self.original_tag.lazyInitializeFlag

        # 从包名,类名中获取源代码中解析出的信息
        self.abcClass = self.packages[package].classes[classname]

        out_stream = OutputStream()
        in_stream = SWFStream(BytesIO(self.original_tag.bytes))
        bytes_to_keep = in_stream.read(
            self.original_tag.abcFile.const_pool.offset['strings']
        )
        out_stream.write(bytes_to_keep)

        # 读入原来的 strings
        self._read_original_strings(in_stream)
        self._replace_multiname(package, classname)
        self._replace_methods(package, classname)
        self._replace_instances(package, classname)

        pprint.pprint(list(enumerate(zip(self.new_strings, self.strings))))
        # 重新写入 strings
        # FIXME 替换 debug string
        if len(self.new_strings) == 1:
            out_stream.writeU30(0)
        else:
            out_stream.writeU30(len(self.new_strings))
            for s in self.new_strings[1:]:
                out_stream.writeU30(len(s))
                out_stream.write(s)

        num_to_read = (
            self.original_tag.abcFile.offset['methods']
            - self.original_tag.abcFile.const_pool.offset['namespaces']
        )
        bytes_to_keep = in_stream.read(num_to_read)
        out_stream.write(bytes_to_keep)

        # 读入原来的 method_info
        self._read_original_methods(in_stream)
        # 重新写入 method_info, 并清除其中记录的参数名
        self._write_methods(out_stream, clean_param_name=True)

        # 读入剩下的bytes
        bytes_to_keep = in_stream.read()
        out_stream.write(bytes_to_keep)

        # TODO 丢弃字节中的debug信息
        

        new_tag.bytes = out_stream.getvalue()
        # 重新计算 tag_length
        new_tag.header.content_length = (
            4                           # flags
            + len(new_tag.abcName) + 1  # name
            + len(new_tag.bytes)        # bytes
        )
        return new_tag
        # pprint.pprint(list(enumerate(self.original_tag.abcFile.const_pool.get_string())))
        # pprint.pprint(self.original_tag.abcFile.const_pool.offset)
        # pprint.pprint(self.original_tag.abcFile.const_pool.get_namespace())
        # pprint.pprint(self.original_tag.abcFile.const_pool.get_ns_set())
        # pprint.pprint(self.original_tag.abcFile.const_pool.get_solved_multiname())
        # pprint.pprint(self.original_tag.abcFile.methods)
        # pprint.pprint(self.original_tag.abcFile.instances)

    """ private methods for replace strings in abcFile's constant pool """

    def _read_original_strings(self, stream):
        count = stream.readEncodedU32()
        for _ in range(count - 1):
            size = stream.readEncodedU32()
            if size == 0:
                self.strings.append('')
            else:
                self.strings.append(stream.read(size))
        self.new_strings = copy.copy(self.strings)

    def _replace_multiname(self, package, classname):
        for index, multiname in enumerate(self.original_tag.abcFile.const_pool.multinames):
            if index == 0:
                continue
            info = self.original_tag.abcFile.const_pool.get_solved_multiname(index)
            print(info)
            if 'namespace' not in info:
                continue
            # 处理包含 'namespace' 属性的 multiname
            if info['namespace'] == joinPackageClassName(package, classname):
                # 方法/成员变量
                if   info['name'] in self.abcClass.methods:
                    new_method_name = self.abcClass.fuzzy.methods[info['name']].name
                    self.new_strings[multiname.name] = new_method_name
                    print('Replace by {0}({1})'.format(new_method_name, multiname.name))
                elif info['name'] in self.abcClass.variables:
                    new_var_name = self.abcClass.fuzzy.variables[info['name']].name
                    self.new_strings[multiname.name] = new_var_name
                    print('Replace by {0}({1})'.format(new_var_name, multiname.name))
            elif info['namespace'] == '':
                # 根package中定义的类
                if   info['name'] in self.packages[''].classes:
                    new_classname = self.packages[''].classes[info['name']].fuzzy.name
                    self.new_strings[multiname.name] = new_classname
                    print('Replace by {0}({1})'.format(new_classname, multiname.name))
                # 根package中定义的类的public域
                else:
                    for cls in self.packages[''].classes.values():
                        if info['name'] in cls.methods:
                            new_method_name = cls.fuzzy.methods[info['name']].name
                            self.new_strings[multiname.name] = new_method_name
                            print('Replace by {0}({1})'.format(new_method_name, multiname.name))
                        elif info['name'] in cls.variables:
                            new_var_name = cls.fuzzy.variables[info['name']].name
                            self.new_strings[multiname.name] = new_var_name
                            print('Replace by {0}({1})'.format(new_var_name, multiname.name))
            elif info['namespace'] in self.names_map['module']:
                # 其他文件中定义的类
                if (info['namespace'] not in self.packages
                    or (info['name'] not in self.packages[info['namespace']].classes)):
                    continue
                new_classname = self.packages[info['namespace']].classes[info['name']].fuzzy.name
                self.new_strings[multiname.name] = new_classname
                new_namespace = self.names_map['module'][info['namespace']]
                # new_namespace = info['namespace']
                self.new_strings[self.original_tag.abcFile.const_pool.namespaces[multiname.ns]] = new_namespace
                print('Replace by {0}({1}) {2}({3})'.format(
                    new_classname, multiname.name,
                    new_namespace, self.original_tag.abcFile.const_pool.namespaces[multiname.ns]
                ))

    def _replace_methods(self, package, classname):
        for index, method in enumerate(self.original_tag.abcFile.methods):
            if self.strings[method.name] == '':
                continue
            info = self.parse_class_method_name(self.strings[method.name])
            new_info = copy.copy(info)
            if   info['accessor'] == 'get':
                # Suppress getter
                # new_info['methodname'] = self.abcClass.fuzzy.getter_methods[info['methodname']].name
                pass
            elif info['accessor'] == 'set':
                # Suppress setter
                # new_info['methodname'] = self.abcClass.fuzzy.setter_methods[info['methodname']].name
                pass
            else:
                if info['methodname'] not in self.abcClass.fuzzy.methods:
                    continue
                new_info['methodname'] = self.abcClass.fuzzy.methods[info['methodname']].name
            new_info['classname'] = self.get_new_package_class_name(package, self.abcClass)
            self.new_strings[method.name] = self.combine_class_method_info(new_info)
            print('Replace by {0}({1})'.format(self.new_strings[method.name], method.name))

    def _replace_instances(self, package, classname):
        for instance in self.original_tag.abcFile.instances:
            for trait in instance.traits:
                if not isinstance(trait, StTraitMethod):
                    continue
                name_index = self.original_tag.abcFile.const_pool.multinames[trait.name].name
                new_name_index = self.original_tag.abcFile.methods[trait.method].name
                self.new_strings[name_index] = self.parse_class_method_name(self.new_strings[new_name_index])['methodname']
                print("instance's trait methodname Replace by {0}({1})".format(
                    self.new_strings[name_index], name_index
                ))

    def get_new_package_class_name(self, package, cls):
        new_package = self.names_map['module'][package]
        return joinPackageClassName(new_package, cls.fuzzy.name)

    @staticmethod
    def parse_class_method_name(name):
        info = defaultdict(str)
        result = name.split('/')
        if len(result) == 2:
            info['classname'], info['methodname'] = result
        elif len(result) == 3:
            info['classname'], info['methodname'], info['accessor'] = result
        else:
            raise Exception(result)
        result = info['methodname'].split(':')
        if len(result) == 2:
            info['visibility'], info['methodname'] = result
        return info

    @staticmethod
    def combine_class_method_info(info):
        name = info['classname']
        if info['visibility']:
            name += '/{0}:{1}'.format(info['visibility'], info['methodname'])
        else:
            name += '/' + info['methodname']
        if info['accessor']:
            name += '/' + info['accessor']
        return name

    """ private methods for replace method_info in abcFile """

    def _read_original_methods(self, in_stream):
        self.methods = ABCFile.parse_methods(in_stream)

    def _write_methods(self, out_stream, clean_param_name=False):
        out_stream.writeU30(len(self.methods))
        for method in self.methods:
            param_count = len(method.param_types)
            out_stream.writeU30(param_count)
            out_stream.writeU30(method.return_type)
            for param_type in method.param_types:
                out_stream.writeU30(param_type)
            out_stream.writeU30(method.name)
            if clean_param_name:
                # 去除参数名
                method.flags &= (~StMethodInfo.HAS_PARAM_NAMES)
            out_stream.writeU8(method.flags)
            if method.flags & StMethodInfo.HAS_OPTIONAL:
                option_count = len(method.options)
                out_stream.writeU30(option_count)
                for option in method.options:
                    out_stream.writeU30(option['val'])
                    out_stream.writeU8(option['kind'])
            if method.flags & StMethodInfo.HAS_PARAM_NAMES:
                for param_name in method.param_names:
                    out_stream.writeU30(param_name)
