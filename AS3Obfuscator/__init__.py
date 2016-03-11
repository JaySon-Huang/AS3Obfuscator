#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import os
import os.path
import json
import shutil

import asdox.asBuilder

from utils import filepath2module, module2filepath
from replacer import SWFFileReplacer
from generator import (
    FuzzyClassGenerator,
    FuzzyModulenameGenerator,
    FuzzyClassnameGenerator,
)
from logger import logger


def get_dummy_watcher_class(class_full_name):
    watcher_name = '_{0}WatcherSetupUtil'.format(
        '_'.join(class_full_name.split('.'))
    )
    from asdox.asModel import ASClass, ASMethod
    cls = ASClass(watcher_name)
    constructor = ASMethod(watcher_name)
    constructor.visibility = 'public'
    cls.methods[constructor.name] = constructor
    return cls


class AS3Obfuscator(object):

    def __init__(self, src_dir, dst_dir,
                 ignore_paths=None, ignore_classes=None,
                 keep_classname_classes=None,
                 keep_static_constant_name=None):
        # 是否保存混淆之后的 .as 文件.
        self.is_move_source_codes = False
        self._paths = {
            'src': src_dir,
            'dst': dst_dir
        }
        # 记录混淆前->混淆后的名字
        self._names_map = {
            'module': {},  # 模块名
            'class': {},   # 类名
            'method': {},  # 方法名
            'var': {},     # 变量名
        }
        self._module_generator = FuzzyModulenameGenerator(self._paths)
        self._classname_generator = FuzzyClassnameGenerator(self._paths)
        if ignore_paths is not None:
            self._ignore_paths = [
                os.path.join(self._paths['src'], path)
                for path in ignore_paths
            ]
        else:
            self._ignore_paths = []
        # 整个类进行例外, 不处理类内所有信息
        self._ignore_classes = ignore_classes if ignore_classes is not None else []
        # 保持不混淆的 类名
        self._keep_classname_classes = (
            keep_classname_classes if keep_classname_classes is not None else []
        )
        # 保持不混淆的 静态常量名
        self._keep_static_constant_name = (
            keep_static_constant_name if keep_static_constant_name is not None else []
        )

        # ActionScript3/MXML 语法解析器
        self._builder = asdox.asBuilder.Builder()
        # 解析出来的 ActionScript3类 信息
        self._packages = {}

    def _reproduce_module(self, src_root, dst_root, is_move_files=False):
        """
        递归地处理目录
        """
        # 对 src_root 下的目录/文件进行混淆
        for old_name in os.listdir(src_root):
            old_path = os.path.join(src_root, old_name)
            if os.path.isfile(old_path):
                self._reproduce_file(src_root, dst_root, old_name, is_move_files)
            elif os.path.isdir(old_path):
                if old_path in self._ignore_paths:
                    # 在忽略目录中, 直接拷贝到目标目录
                    if is_move_files:
                        shutil.copytree(
                            old_path,
                            os.path.join(dst_root, old_name)
                        )
                else:
                    # 不在忽略目录中, 修改目录名称
                    new_module_meta, old_module_meta = \
                        self._module_generator.generate(src_root, old_name, dst_root)
                    # 创建目标目录
                    new_path = os.path.join(
                        dst_root, new_module_meta['name']
                    )
                    if is_move_files:
                        os.makedirs(new_path)
                    # 递归处理子目录
                    self._reproduce_module(old_path, new_path)

    def _reproduce_file(self, src_root, dst_root, filename, is_move_files):
        """
        对文件进行处理
        """
        old_cls_meta = self._classname_generator.collect_old_meta(src_root, filename)
        if old_cls_meta['full_name'] in self._ignore_classes:
            logger.debug('ignore class: {0}'.format(os.path.join(src_root, filename)))
            # 忽略的类, 直接复制到目标文件夹下
            if is_move_files:
                shutil.copy2(
                    os.path.join(src_root, filename),
                    dst_root
                )
            return
        if old_cls_meta['ext'].lower() not in ('.as', '.mxml'):
            # 非 .as .mxml, 直接复制文件到目标文件夹下
            if is_move_files:
                shutil.copy2(
                    os.path.join(src_root, filename),
                    dst_root
                )
            return
        elif old_cls_meta['ext'].lower() == '.mxml':
            # mxml 文件
            self._builder.addMXMLSource(
                os.path.join(src_root, filename),
                pkgname=filepath2module(
                    os.path.split(old_cls_meta['full_path'])[0]
                )
            )
            # mxml 文件类名保持不变
            self._classname_generator.set_name_map(
                old_cls_meta['full_path'],
                old_cls_meta['full_path']
            )
            if src_root != self._paths['src']:
                # 框架生成的 WatcherSetupUtil 类, 把其加入swf文件中处理二进制中的包名/类名
                watcher_class = get_dummy_watcher_class(old_cls_meta['full_name'])
                logger.debug('[Generate Class] {}'.format(watcher_class.full_name))
                if watcher_class.full_name not in self._classname_generator.names_map:
                    # FIX bug: 有时候 ASPackage('') 未定义, 在这里创建一个空的 ASPackage('')
                    if self._builder.packages.get('') is None:
                        import asdox.asModel
                        self._builder.packages[''] = asdox.asModel.ASPackage('')
                    self._builder.packages[''].classes[watcher_class.name] = watcher_class
                    self._classname_generator.set_name_map(
                        watcher_class.full_name,
                        watcher_class.full_name
                    )
            if is_move_files:
                shutil.copy2(
                    os.path.join(src_root, filename),
                    dst_root
                )
            return
        else:
            # as 文件
            self._builder.addSource(os.path.join(src_root, filename))
            if (filename in self._keep_classname_classes
                or (old_cls_meta['full_name'].startswith('_')
                    and old_cls_meta['full_name'].endswith('WatcherSetupUtil'))):
                # 保持类名不变
                self._classname_generator.set_name_map(
                    old_cls_meta['full_path'],
                    old_cls_meta['full_path']
                )
                new_cls_meta = {'name': old_cls_meta['name']}
            else:
                # 生成新的类名
                new_cls_meta, _ = \
                    self._classname_generator.generate(src_root, filename, dst_root)
            if is_move_files:
                # 拼接目标文件名称
                new_path_name = os.path.join(
                    dst_root, new_cls_meta['name'] + old_cls_meta['ext']
                )
                shutil.copy2(
                    os.path.join(src_root, filename),
                    new_path_name
                )
            return

    def run(self, swf_filename):
        logger.info('Parsing original source files in {0} ...'.format(
            self._paths['src']
        ))
        if self.is_move_source_codes:
            logger.info('Clean up {0} ...'.format(self._paths['dst']))
            if os.path.exists(self._paths['dst']):
                shutil.rmtree(self._paths['dst'])
            os.makedirs(self._paths['dst'])
        # 收集混淆包名, 类名
        self._reproduce_module(self._paths['src'], self._paths['dst'])
        self._names_map['module'] = self._module_generator.names_map
        self._names_map['module'][''] = ''
        self._names_map['class'] = self._classname_generator.names_map
        # 收集源代码信息
        self._packages = self._builder.packages
        del self._builder

        logger.info('Generating new information ...')
        class_generator = FuzzyClassGenerator(self._keep_static_constant_name)
        for pkg in self._packages.values():
            for cls in pkg.classes.values():
                cls.fuzzy, method_names_map, var_names_map = class_generator.generate(
                    pkg.name, cls,
                    self._names_map['class']
                )
                self._names_map['method'][cls.full_name] = method_names_map
                self._names_map['var'][cls.full_name] = var_names_map
            for interface in pkg.interfaces.values():
                interface.fuzzy, method_names_map, var_names_map = class_generator.generate(
                    pkg.name, interface,
                    self._names_map['class']
                )
                self._names_map['method'][interface.full_name] = method_names_map
                self._names_map['var'][interface.full_name] = var_names_map

        # 记录映射关系
        names_map_filename = 'names_map.json'
        logger.info('Dumped NamesMap -> {0}'.format(names_map_filename))
        logger.debug('NamesMap: {0}'.format(json.dumps(self._names_map, indent=4)))
        with open(names_map_filename, 'w') as outfile:
            outfile.write(json.dumps(self._names_map, indent=4))

        pydata_filename = swf_filename.split(os.sep)[2]
        dump_filename = 'self.' + pydata_filename + '.pydata'
        import cPickle as pickle
        with open(dump_filename, 'w') as outfile:
            pickle.dump(self, outfile)
            logger.info('Dumped `self` to `{0}`....'.format(dump_filename))

        logger.info('Analysing swf file:{0} ...'.format(swf_filename))
        replacer = SWFFileReplacer(self._packages, self._names_map)
        name, ext = os.path.splitext(swf_filename)
        out_filename = name + '.obfused' + ext
        replacer.replace(swf_filename, out_filename)
        logger.info('[FINISHED] Replaced SWF file {0} -> {1}'.format(swf_filename, out_filename))
        return None

    def debug(self, swf_filename):
        pydata_filename = swf_filename.split(os.sep)[2]
        dump_filename = 'self.' + pydata_filename + '.pydata'
        print('>>debug<< restore self from {0}'.format(
            'self.' + pydata_filename + '.pydata'
        ))
        import cPickle as pickle
        with open(dump_filename, 'r') as infile:
            self = pickle.load(infile)

        print('Analysing swf file:{0} ...'.format(swf_filename))
        replacer = SWFFileReplacer(self._packages, self._names_map)
        name, ext = os.path.splitext(swf_filename)
        out_filename = name + '.obfused' + ext
        replacer.replace(swf_filename, out_filename)
        print('Replacing SWF file {0} -> {1}'.format(swf_filename, out_filename))
        return None
