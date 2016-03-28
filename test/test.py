#!/usr/bin/env python
# encoding=utf-8
from __future__ import print_function

import sys, os.path
sys.path.append(os.path.abspath('..'))

import thirdparty.asdox
import thirdparty.asdox.asBuilder

builder = thirdparty.asdox.asBuilder.Builder()

# 主要测试 import/namespace 语句
# builder.addSource('samples/simple/simple_import.as')
# p = builder.packages['']

# 相对完整的类定义测试
# builder.addSource('samples/simple/checkRegDlg_simple.as')
# p = builder.packages['']
# c = p.classes['checkRegDlg']

# 完整的文件测试
# FIXME: 静态初始块解析错误
# builder.addSource('samples/simple/checkRegDlg.as')
# p = builder.packages['']
# c = p.classes['checkRegDlg']

# 简单的文件夹下所有类测试
# builder.addSource('samples/a')
# p = builder.packages['']

# 清除注释块
# with open('samples/comment/checkRegDlg.as', 'rb') as infile:
# with open('samples/tofix/sandiyiqiAs.as', 'rb') as infile:
#     source = infile.read()
# source = utils.TidySourceFile.trim_comments(source)
# source = utils.TidySourceFile.tidy(source)
# with open('samples/comment_clear/checkRegDlg.as', 'w') as outfile:
#     outfile.write(source)

# 方法为默认命名空间
# builder.addSource('samples/tofix/sandiyiqiAs.as')
# p = builder.packages['']
# c = p.classes['checkRegDlg']
# from asdox import asGrammar
# s = '''
#     function nameCbChange(e:Event){
#         myItem = ModelPanel(getMolecule());
#         if(myItem == null) return;
#         myItem.changeNameTFVisible((CheckBox)(e.currentTarget).selected);
#     }'''
# m = asGrammar.METHOD_DEFINITION.parseString(s)[0]

# 静态初始块
# builder.addSource('samples/tofix/AnimaItem.as')

# 多个metadata
# FIXME: class 的metadata信息不完整
# builder.addSource('samples/tofix/baiduDropdown.as')

# var 为默认命名空间
# builder.addSource('samples/tofix/ModelPanel.as')

# method 上有metadata
# builder.addSource('samples/tofix/CellDivisionList.as')

# Object 对象的初始化
# builder.addSource('samples/tofix/ChemEquationLabel.as')

# interface 对象
# builder.addSource('samples/tofix/IBlank.as')

# 泛型
# builder.addSource('samples/tofix/SnapChemExpEquip.as')
# import asdox.asGrammar
# v = asdox.asGrammar.GENERIC_IDENTIFIER.parseString('''Vector.<Object>''')
# v = asdox.asGrammar.VARIABLE_DEFINITION.parseString('''
# private var objectListForDirNameAndStartAndCount:Vector.<Object> = new <Object>[];
# ''')[0]

# const 无范围声明
# builder.addSource('samples/tofix/GuanLianClass.as')

# 函数名为 get 与关键字重复
# builder.addSource('samples/tofix/AdjMatrixGraph.as')


# builder.addSource('samples/tofix/ExperimentTJ.as')

# from ASObfuscator.replacer import OutputStream
# from swf.stream import SWFStream
# from six import BytesIO
# out_stream = OutputStream()
# from IPython import embed;embed();

# mxml 文件解析
# builder.addMXMLSource('samples/tofix/Main.mxml', '')

# 递归泛型
# from pyparsing import Forward, Combine, ZeroOrMore
# from asdox.asGrammar import IDENTIFIER, DOT
# s = 'Vector.<Vector.<Mesh>>'
# GENERIC_IDENTIFIER = Forward()
# GENERIC_IDENTIFIER <<= Combine(
#     IDENTIFIER
#     + ZeroOrMore(DOT + '<' + GENERIC_IDENTIFIER + '>')
# )
# print(GENERIC_IDENTIFIER.parseString(s))

# from AS3Obfuscator import AS3Obfuscator
# obfuscator = AS3Obfuscator(
#     './samples/as_test/src',
#     './samples/as_test/obfuscated',
#     ignore_paths=[],
#     ignore_classes=[]
# )
# obfuscator.run('./samples/as_test/out/production/as_test/Main.decompressed.swf')

import sys
sys.path.append('../thirdparty')
from AS3Obfuscator import AS3Obfuscator
obfuscator = AS3Obfuscator(
    r'D:\Projects\Lab\czxkpt\trunk\Bio\src',
    r'D:\Projects\Lab\czxkpt\trunk\Bio\obfused',
    ignore_paths=['res', ],
    ignore_classes=[],
    keep_classname_classes=['TeachConfig.as', ],
    keep_static_constant_name=['TeachConfig::s_subject', ]
)
obfuscator.run(r'D:\Projects\Lab\czxkpt\trunk\Bio\out\production\Bio\Teach.decompressed.swf')
# obfuscator.debug('./samples/Bio/out/production/Bio/Teach.decompressed.swf')


# from AS3Obfuscator import AS3Obfuscator
# obfuscator = AS3Obfuscator(
#     './samples/Chem/src',
#     './samples/Chem/obfuscated',
#     ignore_paths=['res', ],
#     ignore_classes=[],
#     keep_classname_classes=['TeachConfig.as', ],
#     keep_static_constant_name=['TeachConfig::s_subject', ]
# )
# obfuscator.run('./samples/Chem/out/production/Chem/Teach.decompressed.swf')
# # obfuscator.debug('./samples/Chem/out/production/Chem/Teach.decompressed.swf')


# builder.addMXMLSource('./samples/MesWnd.mxml', '')

# from AS3Obfuscator import AS3Obfuscator
# obfuscator = AS3Obfuscator(
#     './samples/Math/src',
#     './samples/Math/obfuscated',
#     ignore_paths=['res', ],
#     ignore_classes=[],
#     keep_classname_classes=['TeachConfig.as', ],
#     keep_static_constant_name=['TeachConfig::s_subject', ]
# )
# obfuscator.run('./samples/Math/out/production/Math/Teach.decompressed.swf')
# # obfuscator.debug('./samples/Math/out/production/Math/Teach.decompressed.swf')

# from IPython import embed;embed();
