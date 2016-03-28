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

import re
import os
import fnmatch

import pyparsing
import lxml
from lxml import etree

import asGrammar
import asModel


class TidySourceFile(object):
    def __init__(self):
        pass

    @staticmethod
    def trim_bomflag(source):
        if source[:3] == '\xEF\xBB\xBF':
            source = source[3:]
        return source

    @staticmethod
    def trim_comments(source):
        comments_positions = []
        asGrammar.COMMENTS.parseWithTabs()  # 设置Tab不扩展, 否则下面的字符串位置不符
        for _, begin, end in asGrammar.COMMENTS.scanString(source):
            comments_positions.append((begin, end))
        # 从后往前去除注释块
        for begin, end in reversed(comments_positions):
            # print('clearing:')
            # print(source[begin:end])
            source = source[:begin] + source[end:]
        return source

    @staticmethod
    def tidy(source):
        # 删除多余的分号
        source = re.sub(r'^\s*;\s*\n', '', source, flags=re.MULTILINE)
        # 去除行尾多余空白符
        source = re.sub(r'\s+$', '', source, flags=re.MULTILINE)
        # 删除多余的空行
        source = re.sub(r'^\s*\n', '', source, flags=re.MULTILINE)
        # 删除return语句多余的()
        source = re.sub(
            r'\breturn\s+\((.*)\)\s*;',
            r'return \1;',
            source
        )
        return source


class Builder(object):
    """ActionScript Source Builder"""

    sources = []
    packages = {}

    def __init__(self):
        self.sources = []
        self.packages = {}

    def addSource(self, source, pattern="*.as"):
        try:
            try:
                # If 'source' is a file object read it.
                self.parseSource(source.read())
            except AttributeError:
                # If 'source' is a filename open and read file.
                self.parseSource(open(source, 'rb').read())
        except IOError:
            # If 'source' is a directory read all files matching the
            # specified pattern.
            if os.path.isdir(source):
                for filename in self.locate(pattern, source):
                    self.parseSource(open(filename, 'rb').read())
            else:
                # If 'source' is a string append to source list
                self.parseSource(source)

    def addMXMLSource(self, filename, pkgname):
        filepath, name = os.path.split(filename)
        classname, ext = os.path.splitext(name)
        cls = asModel.ASClass(classname)
        if pkgname:
            cls.full_name = pkgname + '.' + classname
        else:
            cls.full_name = classname
        tree = etree.parse(filename)
        root = tree.getroot()
        for subroot in root:
            if isinstance(subroot, lxml.etree._Comment):
                continue
            if subroot.tag.endswith('Script'):
                try:
                    tokens = asGrammar.MXML_SCRIPT_BLOCK.parseString(subroot.text)
                    if tokens.variables:
                        for var in [_[0] for _ in tokens.variables.asList()]:
                            cls.variables[var.name] = var
                except pyparsing.ParseBaseException as exc:
                    print('Caught Exception @({0}, {1})!\n{2}'.format(
                        exc.lineno, exc.col, exc.line
                    ))
                    from IPython import embed;embed()

        if self.packages.get(pkgname) is None:
            pkg = asModel.ASPackage(pkgname)
            pkg.classes[cls.name] = cls
            self.packages[pkg.name] = pkg
        else:
            self.packages[pkgname].classes[cls.name] = cls

    def parseSource(self, src):
        # 清理注释
        src = TidySourceFile.tidy(TidySourceFile.trim_comments(src))

        # self.sources.append(src)
        # 开始解析
        try:
            root = asGrammar.PROGRAM.parseString(src)
            pkg = root.package
            # 融合多个文件
            if self.packages.get(pkg.name) is None:
                self.packages[pkg.name] = pkg
            else:
                for imp in pkg.imports:
                    if imp.name not in list(map(
                        lambda imp: imp.name, self.packages[pkg.name].imports
                    )):
                        self.packages[pkg.name].imports.append(imp)
                for cls in pkg.classes.values():
                    self.packages[pkg.name].classes[cls.name] = cls
                for interface in pkg.interfaces.values():
                    self.packages[pkg.name].interfaces[interface.name] = interface
        except pyparsing.ParseBaseException as exc:
            print('Caught Exception @({0}, {1})!\n{2}'.format(
                exc.lineno, exc.col, exc.line
            ))
            from IPython import embed;embed()

    def locate(self, pattern, root=os.getcwd()):
        for path, dirs, files in os.walk(root):
            matched_filenames = [
                os.path.abspath(os.path.join(path, filename))
                for filename in files if fnmatch.fnmatch(filename, pattern)
            ]
            for filename in matched_filenames:
                yield filename
