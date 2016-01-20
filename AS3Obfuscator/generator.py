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

FUCKUP_PUNCTUATIONS = '{|}!#$%()*+;='


class FuzzyModulenameGenerator(object):
    FUZZY_LENGTH = 1
    NAME_SET = string.ascii_letters + FUCKUP_PUNCTUATIONS

    @property
    def names_map(self):
        return self._names_map

    def __init__(self, root_paths):
        self.root_paths = root_paths
        self._names_map = {}
        self._names_map_r = {}

    def collect_old_meta(self, src_path, old_module_name):
        # 收集旧module信息
        old_module_meta = {
            'name': old_module_name,
            'full_path': os.path.relpath(
                os.path.join(src_path, old_module_name),
                self.root_paths['src']
            ),
            'full_name': None,
        }
        old_module_meta['full_name'] = filepath2module(old_module_meta['full_path'])
        return old_module_meta

    def generate(self, src_path, old_module_name, dst_path):
        # 收集旧module信息
        old_meta = self.collect_old_meta(src_path, old_module_name)
        # 生成新module信息
        new_meta = {}
        while True:
            new_meta['name'] = ''.join([
                random.choice(FuzzyModulenameGenerator.NAME_SET)
                for _ in range(FuzzyModulenameGenerator.FUZZY_LENGTH)
            ])
            new_meta['full_path'] = os.path.relpath(
                os.path.join(dst_path, new_meta['name']),
                self.root_paths['dst']
            )
            new_meta['full_name'] = filepath2module(new_meta['full_path'])
            if new_meta['full_path'] not in self._names_map_r:
                break
        # 标记此module已经被使用
        self.set_name_map(old_meta['full_path'], new_meta['full_path'])
        return new_meta, old_meta

    def set_name_map(self, old_full_path, new_full_path):
        assert old_full_path not in self._names_map
        self._names_map[old_full_path] = new_full_path
        self._names_map_r[new_full_path] = old_full_path
        print('[Module] {0} -> {1}'.format(
            filepath2module(old_full_path), filepath2module(new_full_path)
        ))


class FuzzyClassnameGenerator(object):
    FUZZY_LENGTH = 4
    NAME_FIRST_CH_SET = string.ascii_uppercase
    NAME_SET = string.ascii_letters + string.digits + FUCKUP_PUNCTUATIONS

    @property
    def names_map(self):
        return self._names_map

    def __init__(self, root_paths):
        self.root_paths = root_paths
        self._names_map = {}
        self._names_map_r = {}

    def collect_old_meta(self, src_path, old_filename):
        # 收集旧类文件信息
        # noinspection PyDictCreation
        old_class_meta = {}
        old_class_meta['name'], old_class_meta['ext'] = os.path.splitext(old_filename)
        relative_path = os.path.relpath(src_path, self.root_paths['src'])
        if relative_path == '.':
            old_class_meta['full_path'] = old_class_meta['name']
            old_class_meta['full_name'] = old_class_meta['name']
        else:
            old_class_meta['full_path'] = os.path.join(
                relative_path,
                old_class_meta['name']
            )
            old_class_meta['full_name'] = filepath2module(old_class_meta['full_path'])
        return old_class_meta

    def generate(self, src_path, old_filename, dst_path):
        # 收集旧类文件信息
        old_class_meta = self.collect_old_meta(src_path, old_filename)
        # 生成新类名信息
        new_class_meta = {}
        relative_path = os.path.relpath(dst_path, self.root_paths['dst'])
        while True:
            new_class_meta['name'] = (
                random.choice(FuzzyClassnameGenerator.NAME_FIRST_CH_SET)
                + ''.join(
                    random.choice(FuzzyClassnameGenerator.NAME_SET)
                    for _ in range(FuzzyClassnameGenerator.FUZZY_LENGTH - 1))
            )
            if relative_path == '.':
                new_class_meta['full_path'] = new_class_meta['name']
                new_class_meta['full_name'] = new_class_meta['name']
            else:
                new_class_meta['full_path'] = os.path.join(
                    relative_path, new_class_meta['name']
                )
                new_class_meta['full_name'] = filepath2module(new_class_meta['full_path'])
            if new_class_meta['full_path'] not in self._names_map_r:
                break
        # 标记此classname已经被使用
        self.set_name_map(old_class_meta['full_path'], new_class_meta['full_path'])
        return new_class_meta, old_class_meta

    def set_name_map(self, old_full_path, new_full_path):
        assert old_full_path not in self._names_map
        self._names_map[old_full_path] = new_full_path
        self._names_map_r[new_full_path] = old_full_path
        print('[Class] {0} -> {1}'.format(
            filepath2module(old_full_path), filepath2module(new_full_path)
        ))


class FuzzyClassGenerator(object):

    FUZZY_LENGTH = {
        'method': 3,
        'variable': 5,
    }

    NAME_SET = {
        'method': (
            string.ascii_letters
            + FUCKUP_PUNCTUATIONS
        ),
        'variable': (
            string.ascii_letters
            + FUCKUP_PUNCTUATIONS
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
                # print('override function ', method.name)
                used_fuzzy_method_names.add(method.name)
                continue
            # 构造函数, 重命名为跟混淆后的类名一致
            if method.name == original_cls.name:
                method.name = fuzzy.name
                used_fuzzy_method_names.add(method.name)
                continue
            if method.visibility == 'private':
                # 私有函数
                name = cls._generate_fuzzy_method_name(used_fuzzy_method_names)
                print(u'private method {0} -> {1}'.format(method.name, name))
                method.name = name
            # TODO 公有函数

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
                # 私有变量
                var.name = cls._generate_fuzzy_var_name(used_fuzzy_variable_names)
            elif var.isConstant and var.isStatic:
                # 公有静态常量
                var.name = cls._generate_fuzzy_var_name(used_fuzzy_variable_names)
            # TODO 公有成员变量/常量
        return fuzzy

    @staticmethod
    def _generate_fuzzy_method_name(used_fuzzy_method_names):
        while True:
            name = ''.join([
                random.choice(FuzzyClassGenerator.NAME_SET['method'])
                for _ in range(FuzzyClassGenerator.FUZZY_LENGTH['method'])
            ])
            if name not in used_fuzzy_method_names:
                used_fuzzy_method_names.add(name)
                return name

    @staticmethod
    def _generate_fuzzy_var_name(used_fuzzy_variable_names):
        while True:
            name = ''.join([
                random.choice(FuzzyClassGenerator.NAME_SET['variable'])
                for _ in range(FuzzyClassGenerator.FUZZY_LENGTH['variable'])
            ])
            if name not in used_fuzzy_variable_names:
                used_fuzzy_variable_names.add(name)
                return name
