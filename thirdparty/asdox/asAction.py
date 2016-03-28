#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

from pyparsing import ParseResults
from asModel import (
    ASClass, ASPackage, ASMetaTag,
    ASVirtualMethod, ASMethod, ASMetodBody,
    ASType, ASVariable,
    ASImport,
)

_isTracing = False
# _isTracing = True


def parseASPackage(s, location, tokens):
    if _isTracing:
        print('parseASPackage[{0}] @ loc({1})'.format(tokens.name, location))
    pkg = ASPackage(tokens.name)
    if tokens.imports:
        tokens.imports = tokens.imports.asList()
        pkg.imports += tokens.imports
    if tokens.use_namespace:
        pkg.use_namespace += tokens.use_namespace.asList()
    # 定义的类
    if tokens.class_:
        cls = tokens.class_[0]
        if pkg.name:
            cls.full_name = pkg.name + '.' + cls.name
        pkg.classes[cls.name] = cls
        # 把成员变量类名替换为全名
        for var in cls.variables.values():
            for imported_cls in tokens.imports:
                imported_cls_name = imported_cls.name.split('.')[-1]
                if var.type_ == imported_cls_name:
                    var.type_ = imported_cls
                    break
    # 定义的接口
    if tokens.interface:
        interface = tokens.interface[0]
        if pkg.name:
            interface.full_name = pkg.name + '.' + interface.name
        pkg.interfaces[interface.name] = interface
    # tokens
    pkg.setTokens(tokens)
    return pkg


def parseASClass(s, location, tokens):
    if _isTracing:
        print('parseASClass[{0}] @ loc({1})'.format(tokens.name, location))
    cls = ASClass(tokens.name)
    # 基类 & 接口
    cls.extends = tokens.extends
    if tokens.implements:
        cls.implements = tokens.implements.asList()
    # 可见性
    if tokens.visibility == '':
        cls.visibility = 'internal'
    else:
        cls.visibility = tokens.visibility
    # 其他属性
    if tokens.dynamic == 'dynamic':
        cls.isDynamic = True
    if tokens.final == 'final':
        cls.isFinal = True
    # metatag
    if tokens.metatag:
        cls.metadata.append(tokens.metatag[0])
    for variable in tokens.variables:
        variable = variable[0]
        cls.variables[variable.name] = variable
    # methods
    for method in tokens.methods:
        method = method[0]
        if not method.accessor:
            cls.methods[method.name] = method
        else:
            # getter/setter 对相关变量属性进行设置
            # if method.name not in cls.variables:
            #     cls.variables[method.name] = ASVariable(method.name)
            # v = cls.variables[method.name]
            if method.accessor == 'get':
                cls.getter_methods[method.name] = method
                # v.readable = True
                # v.type_ = method.return_type
            elif method.accessor == 'set':
                cls.setter_methods[method.name] = method
                # v.writable = True
                # v.type_ = method.arguments.values()[0].type_
            # v.visibility = method.visibility
            # v.isProperty = True
    cls.setTokens(tokens)
    return ParseResults(cls)


def parseASInterface(s, location, tokens):
    if _isTracing:
        print('parseASInterface[{0}] @ loc({1})'.format(tokens.name, location))
    cls = ASClass(tokens.name)
    cls.isInterface = True
    # methods
    for method in tokens.methods:
        method = method[0]
        cls.methods[method.name] = method
    cls.setTokens(tokens)
    return ParseResults(cls)


def parseImports(s, location, tokens):
    if _isTracing:
        print('parseImports[{0}] @ loc({1})'.format(tokens.name, location))
    imp = ASImport(tokens.name)
    imp.setTokens(tokens)
    return imp


def parseASMetaTag(s, location, tokens):
    if _isTracing:
        print('parseASMetaTag[{0}] @ loc({1})'.format(tokens.name, location))
    metatag = ASMetaTag(tokens.name)
    index = 0
    for attr in tokens.attributes:
        if attr.key == '':
            metatag.params[index] = attr.value
        else:
            metatag.params[attr.key] = attr.value
        index += 1
    metatag.setTokens(tokens)
    return ParseResults(metatag)


def parseASArg(s, location, tokens):
    if _isTracing:
        print('parseASArg[{0}] @ loc({1})'.format(tokens.name, location))
    arg = ASType(tokens.name, tokens.type_)
    arg.setTokens(tokens)
    return arg


def parseASMethod(s, location, tokens):
    if _isTracing:
        print('parseASMethod[{0}] @ loc({1})'.format(tokens.name, location))
    # 返回类型
    if tokens.type_:
        method = ASMethod(tokens.name, tokens.type_)
    else:
        method = ASMethod(tokens.name)
    # 可见域
    if tokens.visibility:
        method.visibility = tokens.visibility
    else:
        method.visibility = 'internal'
    # method 属性
    if tokens.override:
        method.isOverride = True
    if tokens.final:
        method.isFinal = True
    if tokens.static:
        method.isStatic = True
    if tokens.accessor:
        method.accessor = tokens.accessor
    # method 传入参数
    for arg in tokens.arguments:
        method.arguments[arg.name] = arg
    # 方法体
    method.body = tokens.body[0]
    method.setTokens(tokens)
    return ParseResults(method)


def parseASVirtualMethod(s, location, tokens):
    if _isTracing:
        print('parseASVirtualMethod[{0}] @ loc({1})'.format(tokens.name, location))
    if tokens.type_:
        method = ASVirtualMethod(tokens.name, tokens.type_)
    else:
        method = ASVirtualMethod(tokens.name)
    # method 传入参数
    for arg in tokens.arguments:
        method.arguments[arg.name] = arg
    method.setTokens(tokens)
    return ParseResults(method)


def parseASMethodBody(s, location, tokens):
    if _isTracing:
        print('parseASMethodBody @ loc({1})').format(location)
    return ParseResults(ASMetodBody(tokens))


def parseASVariable(s, location, tokens):
    if _isTracing:
        print('parseASVariable[{0}] @ loc({1})'.format(tokens.name, location))
    var = ASVariable(tokens.name, tokens.type_)
    if tokens.visibility:
        var.visibility = tokens.visibility
    # 静态量
    if tokens.static == 'static':
        var.isStatic = True
    # 常量/变量
    if tokens.kind == 'const':
        var.isConstant = True
        var.readable = True
        var.writable = False
    else:
        var.readable = True
        var.writable = True
    # metatag
    if tokens.metatag:
        var.metadata = tokens.metatag.asList()
    var.setTokens(tokens)
    return ParseResults(var)
