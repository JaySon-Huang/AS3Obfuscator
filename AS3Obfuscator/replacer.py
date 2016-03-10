#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import copy
import struct
import pprint
from collections import defaultdict

from six import BytesIO
import lxml
from lxml import etree

from swf.movie import SWF
from swf.stream import SWFStream
from swf.tag import (TagDoABC, TagSymbolClass, TagDefineBinaryData)
from swf.abcfile import ABCFile, StMethodInfo, StMultiname, CONSTANT_KIND_NAME
from swf.abcfile.trait import (
    StTraitClass,
    StTraitFunction,
    StTraitMethod,
    StTraitSlot
)
from swf.abcfile.instruction import (
    Instruction,
    InstructionDebugline,
    InstructionDebugfile,
    InstructionDebug,
    InstructionFindpropstrict,
    InstructionGetproperty,
)
from utils import (
    filepath2module, module2filepath,
    splitABCName, joinPackageClassName,
)

from converter import (
    TagDoABCConverter,
    TagSymbolConverter,
    TagDefineBinaryDataConverter,
)

range = xrange

'''
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
        return source
'''


class SWFFileReplacer(object):

    def __init__(self, packages, names_map):
        super(SWFFileReplacer, self).__init__()
        self.packages = packages
        self.names_map = {
            'module': {},
            'class': {},
            'method': names_map['method'],
        }
        for key in names_map['module']:
            self.names_map['module'][filepath2module(key)] = filepath2module(
                names_map['module'][key]
            )
        for key in names_map['class']:
            self.names_map['class'][filepath2module(key)] = filepath2module(
                names_map['class'][key]
            )
        self.symbols = {}

    def _load_symbols_id(self, swf):
        for tag in swf.tags:
            if tag.type == TagSymbolClass.TYPE:
                for symbol in tag.symbols:
                    self.symbols[symbol.tagId] = symbol.name

    def replace(self, swf_filename, out_filename):
        with open(swf_filename, 'rb') as infile:
            s = SWF(infile, is_quick_mode=True)
            infile.seek(0)
            original_bytes = infile.read()
            self._load_symbols_id(s)
        with open(out_filename, 'wb') as outfile:
            outfile.write('FWS')
            outfile.write(struct.pack('B', s.header.version))
            outfile.write(struct.pack('<I', 0))  # 先占4bytes空间, 最后再seek到这里写入数据
            outfile.write(original_bytes[
                3 + 1 + 4:s.tags[0].file_offset  # copy 'FWS' + version + length 到 第一个tag之间的内容
            ])
            for tag in s.tags:
                print('0x{0:04x}({1:5d}) Tag:{2}'.format(
                    tag.file_offset, tag.header.tag_length, tag.name
                ))
                # tag替换内容提炼为Replacer系列类的功能
                # tag转换为bytes提炼为Converter系列类的功能
                if tag.type == TagDoABC.TYPE:
                    new_tag = TagDoABCReplacer(self.packages, self.names_map).replace(tag)
                    if new_tag is not tag:
                        print('modified TagDoABC: {0}'.format(tag.abcName))
                    else:
                        print('not modified TagDoABC: {0}'.format(tag.abcName))
                    outfile.write(TagDoABCConverter.to_bytes(new_tag))
                elif tag.type == TagSymbolClass.TYPE:
                    new_tag = TagSymbolReplacer(self.packages, self.names_map).replace(tag)
                    outfile.write(TagSymbolConverter.to_bytes(new_tag))
                elif tag.type == TagDefineBinaryData.TYPE:
                    print(tag.name, tag.characterId, self.symbols[tag.characterId])
                    if self.symbols[tag.characterId] not in self.names_map['class']:
                        new_tag = tag
                    else:
                        new_tag = TagDefineBinaryDataReplacer(self.names_map, self.symbols).replace(tag)
                    outfile.write(TagDefineBinaryDataConverter.to_bytes(new_tag))
                else:
                    # 其他tag保持原有bytes
                    outfile.write(original_bytes[
                        tag.file_offset:(tag.file_offset + tag.header.tag_length)
                    ])
                    continue
            file_length = outfile.tell()
            outfile.seek(3 + 1)
            outfile.write(struct.pack('<I', file_length))


class TagSymbolReplacer(object):
    def __init__(self, packages, names_map):
        self.packages = packages
        self.names_map = names_map

    def replace(self, original_tag):
        new_tag = TagSymbolClass()
        symbols_length = 0
        for symbol in original_tag.symbols:
            new_symbol = copy.copy(symbol)
            if symbol.name in self.names_map['class']:
                new_symbol.name = self.names_map['class'][symbol.name]
            new_tag.symbols.append(new_symbol)
            # 2 for id, others for c-string size
            symbols_length += 2 + len(new_symbol.name) + 1
        # 2 for num of symbols, others for symbols' size
        new_tag.header = copy.copy(original_tag.header)
        new_tag.header.content_length = 2 + symbols_length
        return new_tag


def is_class_in_packages(packages, packagename, classname):
    return (packagename in packages
            and (classname in packages[packagename].classes
                 or classname in packages[packagename].interfaces))


def get_class_from_packages(packages, packagename, classname):
    if classname in packages[packagename].classes:
        return packages[packagename].classes[classname]
    elif classname in packages[packagename].interfaces:
        return packages[packagename].interfaces[classname]
    else:
        raise Exception('PKG:{0} CLASS:{1} not FOUND')


class TagDoABCReplacer(object):
    def __init__(self, packages, names_map):
        self.packages = packages
        self.names_map = names_map

    def replace(self, original_tag):
        # 官方库返回原来的tag
        if (original_tag.abcName.startswith('flashx/')
                or original_tag.abcName.startswith('mx/')
                or original_tag.abcName.startswith('spark/')):
            return original_tag
        # 从ABCName中获取包名,类名
        packagename, classname = splitABCName(original_tag.abcName)
        # 没有源代码的类(第三方库)返回原来的tag
        if not is_class_in_packages(self.packages, packagename, classname):
            return original_tag

        print('Obfuscating Tag', original_tag.abcName, '...')
        # 从包名,类名中获取源代码中解析出的信息
        abcclass = get_class_from_packages(self.packages, packagename, classname)

        # 开始生成新的 DoABC tag
        new_tag = TagDoABC()
        new_tag.header = copy.copy(original_tag.header)
        # new_tag.abcName = original_tag.abcName
        new_tag.abcName = ''  # 替换debug信息中的abcName
        new_tag.lazyInitializeFlag = original_tag.lazyInitializeFlag
        # 替换abcfile的bytes
        abcfile = ABCFile()
        abcfile.parse(SWFStream(BytesIO(original_tag.bytes)))
        replacer = ABCFileReplacer(
            abcfile, abcclass, packagename, classname,
            self.names_map, self.packages,
            is_replace_public_constant=True,
            is_clear_debug_messages=False
        )
        new_abcfile = replacer.replace()
        # 把替换后的abcfile转换为bytes
        from converter import ABCFileConverter
        new_tag.bytes = ABCFileConverter.to_bytes(new_abcfile)
        # 重新计算 tag_length
        new_tag.header.content_length = (
            4                           # flags
            + len(new_tag.abcName) + 1  # name
            + len(new_tag.bytes)        # bytes
        )
        return new_tag


class ABCFileReplacer(object):

    def __init__(self, abcfile, abcclass, packagename, classname, names_map, packages,
                 is_replace_public_constant=False,
                 is_clear_debug_messages=False):
        self.abcfile = abcfile
        self.abcclass = abcclass
        self.new_abcfile = copy.deepcopy(abcfile)
        self.packagename = packagename
        self.classname = classname
        self.names_map = names_map
        self.packages = packages
        self.is_replace_public_constant = is_replace_public_constant
        self.is_clear_debug_messages = is_clear_debug_messages

    def replace(self):
        self._replace_multiname(self.packagename, self.classname)
        self._replace_instances(self.packagename, self.classname)
        self._replace_classes(self.packagename, self.classname)

        # noinspection PyProtectedMember
        pprint.pprint(list(enumerate(zip(
            self.new_abcfile.const_pool._strings, self.abcfile.const_pool._strings
        ))))

        # 丢弃函数传入参数名信息
        for method in self.new_abcfile.methods:
            # 这一bit置0, 则转换为bytes时不会写入参数名信息到bytes中
            method.flags &= (~StMethodInfo.HAS_PARAM_NAMES)

        self._replace_method_body()
        return self.new_abcfile

    """ private methods for access protected member in abcFile's constant pool """

    # noinspection PyProtectedMember
    def _get_original_string(self, index):
        return self.abcfile.const_pool._strings[index]

    # noinspection PyProtectedMember
    def _get_new_string(self, index):
        return self.new_abcfile.const_pool._strings[index]

    # noinspection PyProtectedMember
    def _set_new_string(self, index, string):
        self.new_abcfile.const_pool._strings[index] = string

    # noinspection PyProtectedMember
    def _get_original_namespace(self, index):
        str_index = self.abcfile.const_pool.namespaces[index]
        return self.abcfile.const_pool._strings[str_index]

    # noinspection PyProtectedMember
    def _set_new_namespace(self, index, namespace):
        str_index = self.new_abcfile.const_pool._namespaces[index][1]
        self._set_new_string(str_index, namespace)

    # noinspection PyProtectedMember
    def _get_original_namespace_set(self, index):
        return self.abcfile.const_pool._ns_sets[index]

    # noinspection PyProtectedMember
    def _get_original_multiname_all(self):
        return self.abcfile.const_pool._multinames

    def _get_original_multiname(self, index):
        return self._get_original_multiname_all()[index]

    """ private methods for replace strings in abcFile's constant pool """

    def _replace_multiname(self, packagename, classname):
        for index, multiname in enumerate(self._get_original_multiname_all()):
            if index == 0:
                continue
            print(self.abcfile.const_pool.get_multiname_string(index))
            # 只处理QName/QNameA的 multiname
            if multiname.kind not in (StMultiname.QName, StMultiname.QNameA):
                continue
            info = self.abcfile.const_pool.get_multiname(index)
            if info['namespace'] == joinPackageClassName(packagename, classname):
                # 私有方法/私有成员变量
                if info['name'] in self.abcclass.methods:
                    new_method_name = self.abcclass.fuzzy.methods[info['name']].name
                    self._set_new_string(multiname.name, new_method_name)
                    print(u'Replace by {0}({1})'.format(new_method_name, multiname.name))
                elif info['name'] in self.abcclass.variables:
                    new_var_name = self.abcclass.fuzzy.variables[info['name']].name
                    self._set_new_string(multiname.name, new_var_name)
                    print(u'Replace by {0}({1})'.format(new_var_name, multiname.name))
            elif info['namespace'] == '':
                # 根package中其他文件中定义的类
                if info['name'] in self.packages[''].classes:
                    other_class = self.packages[''].classes[info['name']]
                    new_classname = other_class.fuzzy.name
                    self._set_new_string(multiname.name, new_classname)
                    print('Replace by {0}({1})'.format(new_classname, multiname.name))
            elif info['namespace'] in self.names_map['module']:
                if not is_class_in_packages(self.packages, info['namespace'], info['name']):
                    continue
                # 其他文件中定义的类
                other_class = get_class_from_packages(
                    self.packages,
                    info['namespace'], info['name']
                )
                # 替换为混淆后的类名
                new_classname = other_class.fuzzy.name
                self._set_new_string(multiname.name, new_classname)
                # 替换为混淆后的包名
                new_namespace = self.names_map['module'][info['namespace']]
                self._set_new_namespace(multiname.ns, new_namespace)
                print(u'Replace by {0}({1}) {2}({3})'.format(
                    new_classname, multiname.name,
                    new_namespace, self.abcfile.const_pool.namespaces[multiname.ns]
                ))

    # noinspection PyUnusedLocal
    def _replace_instances(self, packagename, classname):
        for instance in self.abcfile.instances:
            # 替换实现的 interface
            if len(instance.interfaces) != 0:
                print('Implemented interfaces:')
                for interface in instance.interfaces:
                    multiname = self._get_original_multiname(interface)
                    assert multiname.kind == StMultiname.Multiname
                    ns_set = self._get_original_namespace_set(multiname.ns_set)
                    assert len(ns_set) == 1
                    print(self.abcfile.const_pool.get_multiname_string(interface))
                    pkg_name = self._get_original_namespace(ns_set[0])
                    interface_name = self._get_original_string(multiname.name)
                    if not is_class_in_packages(self.packages, pkg_name, interface_name):
                        continue
                    new_pkg_name, new_interface_name = \
                        self._get_new_interface(pkg_name, interface_name)
                    self._set_new_namespace(ns_set[0], new_pkg_name)
                    self._set_new_string(multiname.name, new_interface_name)
                    print('Interface Replace by {0}.{1}'.format(
                        new_pkg_name,
                        new_interface_name
                    ))
            # 替换方法名
            for trait in instance.traits:
                if isinstance(trait, StTraitMethod):
                    self._replace_method_trait(trait, packagename)
                else:
                    # TODO 常量等其他 strait
                    pass

    def _get_new_interface(self, package_name, interface_name):
        parts = self.names_map['class']['.'.join([package_name, interface_name])].split('.')
        new_package_name = '.'.join(parts[:-1])
        new_interface_name = parts[-1]
        return new_package_name, new_interface_name

    # noinspection PyProtectedMember,PyUnusedLocal
    def _replace_classes(self, packagename, classname):
        # 类静态成员的slot
        for class_ in self.abcfile.classes:
            for trait in class_.traits:
                if self.is_replace_public_constant and isinstance(trait, StTraitSlot):
                    print(
                        'Name:',
                        self.abcfile.const_pool.get_multiname_string(trait.name)
                    )
                    info = self.abcfile.const_pool.get_multiname(trait.name)
                    if info['name'] in self.abcclass.variables:
                        const_name_index = self.abcfile.const_pool._multinames[trait.name].name
                        self._set_new_string(
                            const_name_index,
                            self.abcclass.fuzzy.variables[info['name']].name
                        )
                        print('Replace by', self._get_new_string(const_name_index))

    def _replace_method_trait(self, trait, packagename):
        methodname_index = self.abcfile.methods[trait.method].name
        info = self.parse_class_method_name(self._get_original_string(methodname_index))
        new_info = copy.copy(info)
        if info['accessor'] == 'get':
            # Suppress getter
            # new_info['methodname'] = self.abcclass.fuzzy.getter_methods[info['methodname']].name
            pass
        elif info['accessor'] == 'set':
            # Suppress setter
            # new_info['methodname'] = self.abcclass.fuzzy.setter_methods[info['methodname']].name
            pass
        else:
            if info['methodname'] not in self.abcclass.fuzzy.methods:
                return
            new_info['methodname'] = self.abcclass.fuzzy.methods[info['methodname']].name
        new_info['classname'] = self.get_new_package_class_name(packagename, self.abcclass)
        self._set_new_string(
            methodname_index,
            self.combine_class_method_info(new_info)
        )
        directname_index = self._get_original_multiname(trait.name).name
        self._set_new_string(
            directname_index,
            new_info['methodname']
        )
        print(u"instance's method trait name Replace by {0}({1}) {2}({3})".format(
            self._get_new_string(directname_index), directname_index,
            self._get_new_string(methodname_index), methodname_index
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
            name += u'/{0}:{1}'.format(info['visibility'], info['methodname'])
        else:
            name += u'/' + info['methodname']
        if info['accessor']:
            name += u'/' + info['accessor']
        return name

    """ private methods for replace instruction in abcFile's method body """

    def _replace_method_body(self):
        # 丢弃字节中的debug信息, 从而消除局部变量名
        for method_body in self.new_abcfile.method_bodies:
            method_name_index = self.new_abcfile.methods[method_body.method].name
            print(
                u'Method name:',
                self._get_original_string(method_name_index)
            )
            replacer = InstructionReplacer(
                self.names_map, self.packages,
                self.abcfile.const_pool
            )
            new_code_bytes = replacer.replace(
                method_body.code,
                self.new_abcfile.const_pool,
                is_remove_local_name=self.is_clear_debug_messages,
                is_replace_public_constant=self.is_replace_public_constant
            )
            print(method_body.code.encode('hex'))
            method_body.code = new_code_bytes
            print(method_body.code.encode('hex'))


class InstructionReplacer(object):

    def __init__(self, names_map, packages, const_pool):
        self.names_map = names_map
        self.packages = packages
        self.const_pool = const_pool

    # noinspection PyProtectedMember
    def replace(self, code_bytes,
                new_const_pool,
                is_remove_local_name=True,
                is_replace_public_constant=False):
        new_code_bytes = ''
        print('Replacing Debug messages...')
        for instruct in Instruction.iter_instructions(code_bytes):
            print(
                instruct.resolve(self.const_pool),
                '({0})'.format(repr(instruct.code.encode('hex')))
            )
            if (is_remove_local_name
                and instruct.FORM in
                    (InstructionDebugline.FORM,
                     InstructionDebugfile.FORM,
                     InstructionDebug.FORM)):
                    # debug指令的bytes用nop/label填充
                    # TODO nop/label 随机填充来增大混乱信息?
                    new_code_bytes += '\x02' * len(instruct.code)
                    # 替换 debug 时显示的 string
                    if isinstance(instruct, InstructionDebugfile):
                        new_const_pool._strings[instruct.index] = ''
            else:
                new_code_bytes += instruct.code

        if is_replace_public_constant:
            # 替换类公有常量名在其他代码中的引用
            print('Replacing public constant names...')
            instructions = Instruction.parse_code(code_bytes)
            for index, instruct in enumerate(instructions):
                if instruct.FORM == InstructionFindpropstrict.FORM:
                    next1_instruct = instructions[index + 1]
                    next2_instruct = instructions[index + 2]
                    # 符合 Findpropstrict -> Getproperty -> Getproperty 模式
                    if not (next1_instruct.FORM == InstructionGetproperty.FORM
                            and next2_instruct.FORM == InstructionGetproperty.FORM):
                        continue
                    print(
                        instruct.resolve(self.const_pool),
                        '({0})'.format(repr(instruct.code.encode('hex')))
                    )
                    if (self.const_pool._multinames[instruct.index].kind
                            not in (StMultiname.QName, StMultiname.QNameA)):
                        continue
                    info = self.const_pool.get_multiname(instruct.index)
                    if (info['namespace'] not in self.packages
                            or info['name'] not in self.packages[info['namespace']].classes):
                        print('This Constant(`{0}`) is not replaceable.'.format(info['name']))
                        continue
                    cls = self.packages[info['namespace']].classes[info['name']]
                    print(
                        next2_instruct.resolve(self.const_pool),
                        '({0})'.format(repr(instruct.code.encode('hex')))
                    )
                    info = self.const_pool.get_multiname(next2_instruct.index)
                    if info['name'] not in cls.fuzzy.variables:
                        print('`{0}` may be a getter method.'.format(info['name']))
                        continue
                    const = cls.fuzzy.variables[info['name']]
                    const_name_index = self.const_pool._multinames[next2_instruct.index].name
                    # 替换为混淆后的常量名
                    new_const_pool._strings[const_name_index] = const.name
        return new_code_bytes


class TagDefineBinaryDataReplacer(object):
    def __init__(self, names_map, symbols):
        self.names_map = names_map
        self.symbols = symbols

    def replace(self, original_tag):
        new_tag = TagDefineBinaryData()
        new_tag.header = copy.copy(original_tag.header)
        new_tag.characterId = original_tag.characterId
        new_tag.reserved = original_tag.reserved

        tree = etree.parse(BytesIO(original_tag.data))
        panels_node = tree.getroot()
        if panels_node.tag == 'Panels' and 'TYPE' in panels_node.attrib:
            type_ = panels_node.attrib['TYPE']
            if type_ == 'Bio':
                new_tag.data = self._replace_xml_data_bio(panels_node)
            elif type_ == 'Chem':
                new_tag.data = self._replace_xml_data_chem(panels_node)
        else:
            new_tag.data = original_tag.data
        # 2 for charaterID, 4 for reserved, other for data
        new_tag.header.content_length = 2 + 4 + len(new_tag.data)
        return new_tag

    def _replace_xml_data_chem(self, panels_node):
        assert panels_node.tag == 'Panels'
        classname = panels_node.attrib['BELONG']
        method_names_map = self.names_map['method'][classname]
        new_panels_node = etree.Element(panels_node.tag)
        for panel_node in panels_node.xpath('Panel'):
            new_panel_node = etree.SubElement(
                new_panels_node,
                panel_node.tag, panel_node.attrib
            )
            for shape_node in panel_node.xpath('Shape'):
                new_shape_node = etree.SubElement(new_panel_node, shape_node.tag)
                for key, val in shape_node.attrib.items():
                    if key == 'InitMethodName' and val != '':
                        # 替换为混淆后的初始化函数名
                        new_val = method_names_map[val]
                        new_shape_node.set(key, new_val)
                    else:
                        new_shape_node.set(key, val)
        return etree.tostring(
            new_panels_node,
            # pretty_print=True,
            encoding='utf-8', xml_declaration=True
        )

    def _replace_xml_data_bio(self, panels_node):
        assert panels_node.tag == 'Panels'
        new_panels_node = etree.Element(panels_node.tag)
        for panel_node in panels_node:
            if isinstance(panel_node, lxml.etree._Comment):
                continue
            assert panel_node.tag == 'Panel'
            print('{} BeginId {}'.format(
                panel_node.tag,
                panel_node.attrib['BeginId'],
            ))
            # copy panel 结点的内容
            new_panel_node = etree.SubElement(new_panels_node, panel_node.tag)
            new_panel_node.set('BeginId', panel_node.attrib['BeginId'])
            for shape_node in panel_node:
                if isinstance(shape_node, lxml.etree._Comment):
                    continue
                assert shape_node.tag == 'Shape'
                print(u'{} ShapeClass {} PropClass {}'.format(
                    shape_node.tag,
                    shape_node.attrib['ShapeClass'],
                    shape_node.attrib['PropClass']
                ))
                # copy shape 结点的内容
                new_shape_node = etree.SubElement(
                    new_panel_node, shape_node.tag
                )
                new_shape_node.set('Id', shape_node.attrib['Id'])
                new_shape_node.set('Caption', shape_node.attrib['Caption'])
                shape_class = shape_node.attrib['ShapeClass']
                if shape_class in self.names_map['class']:
                    new_shape_node.set(
                        'ShapeClass',
                        self.names_map['class'][shape_class]
                    )
                    print('Replace ShapeClass {0} by {1}'.format(
                        shape_class,
                        self.names_map['class'][shape_class]
                    ))
                else:
                    new_shape_node.set(
                        'ShapeClass',
                        shape_node.attrib['ShapeClass']
                    )
                prop_class = shape_node.attrib['PropClass']
                if prop_class in self.names_map['class']:
                    new_shape_node.set(
                        'PropClass',
                        self.names_map['class'][prop_class]
                    )
                    print('Replace PropClass {0} by {1}'.format(
                        prop_class,
                        self.names_map['class'][prop_class]
                    ))
                else:
                    new_shape_node.set(
                        'PropClass',
                        shape_node.attrib['PropClass']
                    )
        return etree.tostring(
            new_panels_node,
            # pretty_print=True,
            encoding='utf-8', xml_declaration=True
        )
