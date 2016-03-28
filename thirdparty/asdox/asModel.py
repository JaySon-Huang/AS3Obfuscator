#!/usr/bin/env python
#encoding=utf-8

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


class Documentable(object):
    """ActionScript Object that allows for JavaDoc declaration"""
    pass


class Visible(object):
    def __init__(self):
        super(Visible, self).__init__()
        self.visibility = "internal"


class MetaTagable(object):
    """ActionScript Object that allows for MetaTags"""
    def __init__(self):
        super(MetaTagable, self).__init__()
        self.metadata = []


class FromTokens(object):

    def __init__(self):
        self.raw_tokens = None

    def setTokens(self, tokens):
        self.raw_tokens = tokens.asList()


class ASType(FromTokens):
    """ActionScript 3 Type"""

    def __init__(self, name, type_):
        super(ASType, self).__init__()
        self.name = name
        self.type_ = type_

    def __repr__(self):
        return '<ASType: {0}>'.format(self.name)

    def toTokens(self):
        for t in self.raw_tokens:
            yield t


class ASVariable(ASType, Visible, MetaTagable, FromTokens):
    """ActionScript 3 Variable"""

    def __init__(self, name='', type_='*'):
        super(ASVariable, self).__init__(name, type_)
        self.isStatic = False
        self.isConstant = False
        self.readable = False
        self.writable = False
        self.isProperty = False

    def __repr__(self):
        return '<ASVariable({1}): {0}>'.format(
            self.name,
            self.type_
        )

    def toTokens(self):
        for t in self.raw_tokens:
            yield t


class ASMetaTag(FromTokens):
    """ActionScript MetaTag Definition"""

    def __init__(self, name=''):
        super(ASMetaTag, self).__init__()
        self.name = name
        self.params = {}

    def __repr__(self):
        return '<ASMetaTag: {0}>'.format(self.name)


class ASImport(FromTokens):
    def __init__(self, name):
        super(ASImport, self).__init__()
        self.name = name

    def __repr__(self):
        return '<ASImport: {0}>'.format(self.name)

    def toTokens(self):
        for t in self.raw_tokens:
            yield t


def flatten_nested_tokens(lst):
    for elem in lst:
        if isinstance(elem, list):
            yield "{"
            for e in flatten_nested_tokens(elem):
                yield e
            yield "}"
        else:
            yield elem


class ASMethod(ASType, Visible, MetaTagable, FromTokens):
    """ActionScript Method Definition"""

    def __init__(self, name='', return_type='void'):
        super(ASMethod, self).__init__(name, 'function')
        self.isOverride = False
        self.isFinal = False
        self.isStatic = False
        self.accessor = None
        self.return_type = return_type
        self.arguments = {}
        self.body = None

    def __repr__(self):
        return '<ASMethod: {0}>'.format(self.name)

    def toTokens(self):
        for token in self.raw_tokens:
            if isinstance(token, str):
                yield token
            elif isinstance(token, list):
                yield "{"
                for t in flatten_nested_tokens(token):
                    yield t
                yield "}"
            else:
                for t in token.toTokens():
                    yield t


class ASMetodBody(FromTokens):
    def __init__(self, tokens):
        super(ASMetodBody, self).__init__()
        self.setTokens(tokens)


class ASVirtualMethod(ASMethod):
    """ActionScript Virtual Method Definition"""

    def __init__(self, name='', return_type='void'):
        super(ASVirtualMethod, self).__init__(name, return_type)
        self.name = name
        self.type_ = 'virtual function'
        self.visibility = 'public'

    def __repr__(self):
        return '<ASVirtualMethod: {0}>'.format(self.name)


class ASClass(ASType, Visible, MetaTagable, FromTokens):
    """ActionScript Class Definition"""

    def __init__(self, name):
        super(ASClass, self).__init__(name, 'class')
        self.full_name = self.name
        self.variables = {}
        self.methods = {}
        self.getter_methods = {}
        self.setter_methods = {}
        self.extends = ''
        self.implements = []
        self.isDynamic = False
        self.isFinal = False
        self.isInterface = False

    def __repr__(self):
        return '<ASClass: {0}>'.format(self.name)

    def toTokens(self):
        for token in self.raw_tokens:
            if isinstance(token, str):
                yield token
            elif isinstance(token, list):
                continue
            else:
                for t in token.toTokens():
                    yield t


class ASPackage(ASType, Visible, MetaTagable, FromTokens):
    """ActionScript Package Definition"""

    def __init__(self, name):
        super(ASPackage, self).__init__(name, 'package')
        self.classes = {}
        self.interfaces = {}
        self.imports = []
        self.use_namespace = []

    def __repr__(self):
        return '<ASPackage: {0}>'.format(self.name)

    def toTokens(self):
        for token in self.raw_tokens:
            if isinstance(token, str):
                yield token
            elif isinstance(token, list):
                continue
            else:
                for t in token.toTokens():
                    yield t
