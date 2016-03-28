#!/usr/bin/env python
# encoding=utf-8

# Copyright (c) 2008, Michael Ramirez
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other #materials provided with the distribution.
#   * Neither the name of the <ORGANIZATION> nor the names of its contributors 
#     may be used to endorse or promote products derived from this software 
#     without specific #prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pyparsing
from pyparsing import (
    Keyword, Literal, CaselessLiteral, Word,
    Combine, ZeroOrMore, Regex, Optional,
    QuotedString, nestedExpr,
    delimitedList,
    Forward,
)
from asAction import (
    parseASPackage,
    parseASClass,
    parseASInterface,
    parseASVirtualMethod,
    parseImports,
    parseASMetaTag,
    parseASArg,
    parseASMethod,
    parseASVariable,
    parseASMethodBody,
)

KEYWORDS = {
    'package': Keyword('package'),
    'class': Keyword('class'),
    'implements': Keyword('implements'),
    'extends': Keyword('extends'),
    'function': Keyword('function'),
    'import': Keyword('import'),
    'include': Keyword('include'),
    'interface': Keyword('interface'),
    'internal': Keyword('internal'),
    'public': Keyword('public'),
    'private': Keyword('private'),
    'protected': Keyword('protected'),
    'mxinternal': Keyword('mx_internal'),
    'static': Keyword('static'),
    'prototype': Keyword('prototype'),
    'final': Keyword('final'),
    'override': Keyword('override'),
    'native': Keyword('native'),
    'dynamic': Keyword('dynamic'),
    'use': Keyword('use'),
    'namespace': Keyword('namespace'),
    'var': Keyword('var'),
    'const': Keyword('const'),
    'get': Keyword('get'),
    'set': Keyword('set'),
}

COMMA, COLON, SEMI, EQUAL = list(map(Literal, ',:;='))
LPARN, RPARN, LCURL, RCURL, LSQUARE, RSQUARE = list(map(Literal, '(){}[]'))
UNDERSCORE = Literal('_')
STAR = Literal('*')
DOT = Literal('.')
REST = Literal('...')
TERMINATOR = Optional(SEMI)

# 数字
point = Literal('.')
e = CaselessLiteral('E')
plusOrMinus = Literal('+') | Literal('-')
number = Word(pyparsing.nums)
integer = Combine(Optional(plusOrMinus) + number)
floatnumber = Combine(
    integer
    + Optional(point + Optional(number))
    + Optional(e + integer)
)
hex_integer = '0x' + Word(pyparsing.hexnums)

'''  NEW GRAMMAR DEFINITION  '''
# 标识符, 首字母可以为字母或_或$
IDENTIFIER = Word(pyparsing.alphas + '_' + '$', pyparsing.alphanums + '_')
QUALIFIED_IDENTIFIER = Combine(
    IDENTIFIER
    + ZeroOrMore(DOT + IDENTIFIER)
)
# 泛型
GENERIC_IDENTIFIER = Forward()
GENERIC_IDENTIFIER <<= Combine(
    IDENTIFIER
    + ZeroOrMore(DOT + '<' + GENERIC_IDENTIFIER + '>')
)
# 注释相关
SINGLE_LINE_COMMENT = pyparsing.dblSlashComment
MULTI_LINE_COMMENT = pyparsing.cStyleComment
JAVADOC_COMMENT = (
    Regex(r'/\*\*(?:[^*]*\*+)+?/')
)
COMMENTS = (
    SINGLE_LINE_COMMENT
    ^ JAVADOC_COMMENT
    ^ MULTI_LINE_COMMENT
)

DBL_QUOTED_STRING = QuotedString(quoteChar="\"", escChar='\\')
SINGLE_QUOTED_STRING = QuotedString(quoteChar="'", escChar='\\')
ARRAY_INIT = LSQUARE + RSQUARE
OBJECT_INIT = nestedExpr("{", "}")
VALUE = (
    floatnumber ^ QUALIFIED_IDENTIFIER
    ^ DBL_QUOTED_STRING ^ SINGLE_QUOTED_STRING
    ^ integer ^ hex_integer
)
INIT = (
    QuotedString(quoteChar="=", endQuoteChar=";", multiline=True)
    ^ (
        EQUAL
        + (DBL_QUOTED_STRING ^ ARRAY_INIT ^ OBJECT_INIT)
        + TERMINATOR
    )
)
# 作用域相关
USE_NAMESPACE = (
    KEYWORDS['use']
    + KEYWORDS['namespace']
    + QUALIFIED_IDENTIFIER + TERMINATOR
)
NAMESPACE_DEFINITION = (
    Optional(KEYWORDS['public'])
    + KEYWORDS['namespace']
    + IDENTIFIER('name')
    + TERMINATOR
)
INCLUDE_DEFINITION = (
    KEYWORDS['include']
    + QuotedString(quoteChar="\"", escChar='\\')
    + TERMINATOR
)
IMPORT_DEFINITION = (
    KEYWORDS['import']
    + Combine(
        QUALIFIED_IDENTIFIER
        + Optional(DOT + STAR)
    ).setResultsName(
        'name'
    )
    + TERMINATOR
).setParseAction(parseImports)

ATTRIBUTES = (
    Optional(IDENTIFIER("key") + EQUAL)
    + VALUE("value")
).setResultsName("attributes", listAllMatches=True)
METATAG = (
    LSQUARE  # [
    + IDENTIFIER('name')
    + Optional(LPARN + delimitedList(ATTRIBUTES) + RPARN)
    + RSQUARE  # ]
).setParseAction(parseASMetaTag)
# 变量相关
TYPE = COLON + (QUALIFIED_IDENTIFIER ^ GENERIC_IDENTIFIER ^ STAR)('type_')
VARIABLE_MODIFIERS = (
    Optional(KEYWORDS['static']('static'))
    & Optional(~KEYWORDS['var'] + ~KEYWORDS['const'] + IDENTIFIER('visibility'))
)
VARIABLE_DEFINITION = (
    ZeroOrMore(METATAG)('metatag')
    + VARIABLE_MODIFIERS
    + (KEYWORDS['const'] ^ KEYWORDS['var'])("kind")
    + IDENTIFIER('name')
    + Optional(TYPE)
    + (INIT ^ TERMINATOR)
).setParseAction(parseASVariable)
VARIABLE_INITIALIZATION = (
    IDENTIFIER('name')
    + (INIT ^ TERMINATOR)
)
BLOCK = nestedExpr('{', '}')('block')
# 加上静态初始化块
BASE_BLOCK = USE_NAMESPACE ^ INCLUDE_DEFINITION ^ BLOCK ^ VARIABLE_INITIALIZATION
# 方法相关的语法
METHOD_MODIFIER = (
    Optional(KEYWORDS['static']('static'))
    & (Optional(KEYWORDS['override']('override'))
       & Optional(KEYWORDS['final']('final'))
       & Optional(~KEYWORDS['function'] + IDENTIFIER('visibility'))
       )
)
METHOD_PARAMETER = (
    IDENTIFIER('name')
    + TYPE
    + Optional(EQUAL + VALUE)
).setParseAction(parseASArg)
METHOD_PARAMETERS = delimitedList(METHOD_PARAMETER)
METHOD_SIGNATURE = (
    KEYWORDS['function']
    # getter, setter
    + Optional(KEYWORDS['get'] ^ KEYWORDS['set'])("accessor")
    # 函数名
    + IDENTIFIER('name')
    + LPARN  # (
    # 以 ',' 分割的参数
    + Optional(METHOD_PARAMETERS('arguments'))
    # ... 任意长参数
    + Optional(Optional(COMMA) + REST + IDENTIFIER)
    + RPARN  # )
    # 返回值类型
    + Optional(TYPE)
)
METHOD_DEFINITION = (
    ZeroOrMore(METATAG)('metatag')
    + Optional(METHOD_MODIFIER)
    + METHOD_SIGNATURE
    + BLOCK('body').setParseAction(parseASMethodBody)
).setParseAction(parseASMethod)
# 类相关的语法
CLASS_IMPLEMENTS = (
    KEYWORDS['implements']
    + delimitedList(
        QUALIFIED_IDENTIFIER
    ).setResultsName('implements')
)
CLASS_BLOCK = (
    LCURL  # {
    + ZeroOrMore(
        IMPORT_DEFINITION
        ^ BASE_BLOCK
        ^ VARIABLE_DEFINITION.setResultsName('variables', listAllMatches=True)
        ^ METHOD_DEFINITION.setResultsName('methods', listAllMatches=True)
    )
    + RCURL  # }
)
CLASS_EXTENDS = (
    KEYWORDS['extends']
    + QUALIFIED_IDENTIFIER('extends')
)
INTERFACE_EXTENDS = (
    KEYWORDS['extends']
    + delimitedList(QUALIFIED_IDENTIFIER)
)
BASE_MODIFIERS = KEYWORDS['internal'] ^ KEYWORDS['public']
CLASS_MODIFIERS = (
    Optional(KEYWORDS['final']('final'))
    & Optional(KEYWORDS['dynamic']('dynamic'))
    & Optional(BASE_MODIFIERS('visibility'))
)
CLASS_DEFINITION = (
    ZeroOrMore(METATAG)('metatag')
    + CLASS_MODIFIERS
    + KEYWORDS['class']
    + QUALIFIED_IDENTIFIER('name')
    + Optional(CLASS_EXTENDS)
    + Optional(CLASS_IMPLEMENTS)
    + CLASS_BLOCK
).setParseAction(parseASClass)
# 接口相关的语法
INTERFACE_BLOCK = (
    LCURL  # {
    + ZeroOrMore(
        IMPORT_DEFINITION
        ^ BASE_BLOCK
        ^ VARIABLE_DEFINITION.setResultsName('variables', listAllMatches=True)
        ^ (METHOD_SIGNATURE + TERMINATOR).setParseAction(
            parseASVirtualMethod
        ).setResultsName(
            'methods', listAllMatches=True
        )
    )
    + RCURL  # }
)
INTERFACE_DEFINITION = (
    Optional(BASE_MODIFIERS)
    + KEYWORDS['interface']
    + QUALIFIED_IDENTIFIER('name')
    + Optional(INTERFACE_EXTENDS)
    + INTERFACE_BLOCK
).setParseAction(parseASInterface)
# 包相关的语法
PACKAGE_BLOCK = (
    LCURL  # {
    + ZeroOrMore(IMPORT_DEFINITION)('imports')
    + ZeroOrMore(USE_NAMESPACE)('use_namespace')
    + (
        CLASS_DEFINITION('class_')
        ^ INTERFACE_DEFINITION('interface')
        ^ NAMESPACE_DEFINITION
    )
    + RCURL  # }
)
PACKAGE_DEFINITION = (
    KEYWORDS['package']
    + Optional(QUALIFIED_IDENTIFIER('name'))
    + PACKAGE_BLOCK
).setParseAction(parseASPackage)
# Windows 下文件的 BOM 头
BOM = Literal('\xEF\xBB\xBF')
PROGRAM = (
    Optional(BOM)
    + PACKAGE_DEFINITION('package')
)

MXML_SCRIPT_BLOCK = ZeroOrMore(
    IMPORT_DEFINITION
    ^ BASE_BLOCK
    ^ VARIABLE_DEFINITION.setResultsName('variables', listAllMatches=True)
    ^ METHOD_DEFINITION.setResultsName('methods', listAllMatches=True)
)
