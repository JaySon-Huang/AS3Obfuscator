#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import asdox
import asdox.asBuilder

builder = asdox.asBuilder.Builder()

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

# from AS3Obfuscator import AS3Obfuscator
# obfuscator = AS3Obfuscator(
#     './samples/as_test/src',
#     './samples/as_test/obfuscated',
#     ignore_paths=[],
#     ignore_classes=[]
# )
# obfuscator.run('./samples/as_test/out/production/as_test/Main.decompressed.swf')


from AS3Obfuscator import AS3Obfuscator
obfuscator = AS3Obfuscator(
    './samples/Bio/src',
    './samples/Bio/obfuscated',
    ignore_paths=['asds', 'res', 'Teach/UI/ToolBar/Menu/icon'],
    ignore_classes=[],
    keep_classname_classes=['TeachConfig.as', ]
)
# obfuscator.run('./samples/Bio/out/production/Bio/Teach.decompressed.swf')
obfuscator.debug('./samples/Bio/out/production/Bio/Teach.decompressed.swf')


# from IPython import embed;embed();
