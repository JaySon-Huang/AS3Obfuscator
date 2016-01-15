#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import os
import os.path
import copy
import random
random.seed('0362')
import string

from utils import filepath2module, module2filepath


class FuzzyClassGenerator(object):

    NAMESET = {
        'method': (
            string.ascii_letters
            + '{|}!"#$%&\'()*+;<=>'
        ),
        'variable': (
            string.ascii_letters
            + '{|}!"#$%&\'()*+;<=>'
        ),
    }

    @classmethod
    def generate(cls, modulepath, original_cls, cls_names_map):
        fuzzy = copy.deepcopy(original_cls)
        fuzzy.full_name = cls_names_map[
            module2filepath(original_cls.full_name)
        ]
        fuzzy.name = os.path.split(fuzzy.full_name)[-1]
        
        
        # 方法名进行混淆
        used_fuzzy_method_names = set([])
        for method in fuzzy.methods.values():
            # 覆盖函数不再重命名
            if method.isOverride:
                print('override function ', method.name)
                continue
            if method.name == original_cls.name:
                # 构造函数
                method.name = fuzzy.name
            elif method.visibility == 'private':
                # 私有函数
                while True:
                    name = ''.join([
                        random.choice(cls.NAMESET['method'])
                        for _ in range(3)
                    ])
                    if name not in used_fuzzy_method_names:
                        used_fuzzy_method_names.add(name)
                        break
                print(u'private method {0} -> {1}'.format(method.name, name))
                method.name = name
            # TODO 公有函数
            # 参数名进行混淆(SUPPRESS, 在swf文件结构中消除相关信息)
        
        '''
        # getter/setter # FIXME: 默认getter/setter成对出现
        for method_name, method in fuzzy.getter_methods.items():
            while True:
                name = ''.join([
                    random.choice(cls.NAMESET['method'])
                    for _ in range(3)
                ])
                if name not in used_fuzzy_method_names:
                    used_fuzzy_method_names.add(name)
                    break
            method.name = name
            # 对 setter 设置为一样的名称
            fuzzy.setter_methods[method_name].name = name
        '''

        # 成员变量名进行混淆
        used_fuzzy_variable_names = set([])
        for var in fuzzy.variables.values():
            if var.visibility == 'private':
                while True:
                    name = ''.join([
                        random.choice(cls.NAMESET['variable'])
                        for _ in range(5)
                    ])
                    if name not in used_fuzzy_variable_names:
                        used_fuzzy_variable_names.add(name)
                        break
                var.name = name
            # TODO 公有成员变量/常量
        return fuzzy
