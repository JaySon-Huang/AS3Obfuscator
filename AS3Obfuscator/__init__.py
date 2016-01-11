#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import re
import os
import os.path
import copy
import json
import random
random.seed('0362')
import string
import shutil

import asdox.asBuilder
from asdox.asBuilder import TidySourceFile


from utils import filepath2module, module2filepath

from replacer import SWFFileReplacer, SourceCodeReplacer
from generator import FuzzyClassGenerator


class AS3Obfuscator(object):

    NAMESET = {
        'module': string.ascii_uppercase,
        'class': string.ascii_letters + string.digits,
    }
    MAP_TYPE_CLASS = 0
    MAP_TYPE_MODULE = 1

    def __init__(self, srcDir, dstDir,
                 ignore_paths=None, ignore_classes=None,
                 keep_classname_classes=None):
        self._paths = {
            'src': srcDir,
            'dst': dstDir
        }
        self._names_map = {
            'module': {},
            'class': {},
        }
        self._names_map_r = {
            'module': {},
            'class': {},
        }
        if ignore_paths is not None:
            self._ignore_paths = [
                os.path.join(self._paths['src'], path)
                for path in ignore_paths
            ]
        if ignore_classes is not None:
            self._ignore_classes = ignore_classes
        if keep_classname_classes is not None:
            self._keep_classname_classes = keep_classname_classes
        else:
            self._keep_classname_classes = []

    def _markup_names_map(self, type_, old, new):
        if type_ == self.MAP_TYPE_CLASS:
            self._names_map['class'][old] = new
            self._names_map_r['class'][new] = old
        elif type_ == self.MAP_TYPE_MODULE:
            self._names_map['module'][old] = new
            self._names_map_r['module'][new] = old

    def _getOldModuleMeta(self, dir_path, dirname):
        '''
        _getOldModuleMeta('../samples/Bio_src/Teach/Item/', 'Biology')
        >> {
            'name': 'Biology',
            'full_name': 'Teach.Item.Biology',
            'full_path': 'Teach/Item/Biology',
        }
        '''
        meta = {}
        meta['name'] = dirname
        meta['full_path'] = os.path.relpath(
            os.path.join(dir_path, dirname),
            self._paths['src']
        )
        meta['full_name'] = filepath2module(meta['full_path'])
        return meta
    
    def _getNewModuleMeta(self, dir_path):
        meta = {}
        while True:
            meta['name'] = ''.join([
                random.choice(self.NAMESET['module']) for _ in range(1)
            ])
            meta['full_path'] = os.path.relpath(
                os.path.join(dir_path, meta['name']),
                self._paths['dst']
            )
            meta['full_name'] = filepath2module(meta['full_path'])
            if meta['full_path'] not in self._names_map['module'].values():
                break
        return meta

    def _getOldClassMeta(self, dir_path, filename):
        meta = {}
        meta['name'], meta['ext'] = os.path.splitext(filename)
        relative_path = os.path.relpath(dir_path, self._paths['src'])
        if relative_path == '.':
            meta['full_path'] = meta['name']
            meta['full_name'] = meta['name']
        else:
            meta['full_path'] = os.path.join(
                relative_path, meta['name']
            )
            meta['full_name'] = '.'.join(
                meta['full_path'].split(os.sep)
            )
        return meta

    def _getNewClassMeta(self, dir_path, filename):
        '''获得唯一的类名'''
        meta = {}
        relative_path = os.path.relpath(dir_path, self._paths['dst'])
        while True:
            if filename in self._keep_classname_classes:
                meta['name'] = os.path.splitext(filename)[0]
            else:
                meta['name'] = (
                    random.choice(string.ascii_uppercase) +
                    ''.join(random.choice(self.NAMESET['class'])
                        for _ in range(3))
                )
            if relative_path == '.':
                meta['full_path'] = meta['name']
                meta['full_name'] = meta['name']
            else:
                meta['full_path'] = os.path.join(
                    relative_path, meta['name']
                )
                meta['full_name'] = '.'.join(
                    meta['full_path'].split(os.sep)
                )
            if meta['full_path'] not in self._names_map['class'].values():
                break
        return meta

    def _reproduce_dir(self, src_root, dst_root):
        '''
        递归地处理目录
        '''
        # 对 src_root 下的目录/文件进行混淆
        for old_name in os.listdir(src_root):
            old_path = os.path.join(src_root, old_name)
            if os.path.isfile(old_path):
                self._reproduce_file(src_root, dst_root, old_name)
            elif os.path.isdir(old_path):
                if old_path in self._ignore_paths:
                    # 在忽略目录中, 直接拷贝到目标目录
                    shutil.copytree(
                        old_path,
                        os.path.join(dst_root, old_name)
                    )
                else:
                    # 不在忽略目录中, 修改目录名称
                    old_module_meta = self._getOldModuleMeta(src_root, old_name)
                    new_module_meta = self._getNewModuleMeta(dst_root)
                    # 记录映射关系
                    self._markup_names_map(
                        self.MAP_TYPE_MODULE,
                        old_module_meta['full_path'],
                        new_module_meta['full_path']
                    )
                    print('[Module] {0} -> {1}'.format(
                        old_module_meta['full_name'],
                        new_module_meta['full_name']
                    ))
                    # 创建目标目录
                    new_path = os.path.join(
                        dst_root, new_module_meta['name']
                    )
                    os.makedirs(new_path)
                    # 递归处理子目录
                    self._reproduce_dir(old_path, new_path)

    def _reproduce_file(self, src_root, dst_root, filename):
        '''
        对文件进行处理
        '''
        if filename in self._ignore_classes:
            # 忽略的类, 直接复制到目标文件夹下
            shutil.copy2(
                os.path.join(src_root, filename),
                dst_root
            )
            return
        old_cls_meta = self._getOldClassMeta(src_root, filename)
        if old_cls_meta['ext'].lower() not in ('.as', '.mxml'):
            # 非 .as .mxml, 直接复制文件到目标文件夹下
            shutil.copy2(
                os.path.join(src_root, filename),
                dst_root
            )
            return
        elif old_cls_meta['ext'].lower() == '.mxml':
            # mxml 文件
            self._builder.addMXMLSource(
                os.path.join(src_root, filename),
                pkgname=filepath2module(os.path.split(old_cls_meta['full_path'])[0])
            )
            self._markup_names_map(
                self.MAP_TYPE_CLASS,
                old_cls_meta['full_path'],
                old_cls_meta['full_path']
            )
            shutil.copy2(
                os.path.join(src_root, filename),
                dst_root
            )
            return
        else:
            # as 文件
            self._builder.addSource(os.path.join(src_root, filename))
            # 生成新的类名
            new_cls_meta = self._getNewClassMeta(dst_root, filename)
            self._markup_names_map(
                self.MAP_TYPE_CLASS,
                old_cls_meta['full_path'],
                new_cls_meta['full_path']
            )
            print('[Class] {0} -> {1}'.format(
                old_cls_meta['full_name'], new_cls_meta['full_name']
            ))
            # 拼接目标文件名称
            new_path_name = os.path.join(
                dst_root, new_cls_meta['name']+old_cls_meta['ext']
            )
            shutil.copy2(
                os.path.join(src_root, filename),
                new_path_name
            )
            return

    def _generate_new_packages(self, packages):
        for pkg in packages.values():
            for cls in pkg.classes.values():
                self._generate_new_cls(packages, pkg.name, cls)

    def _generate_new_cls(self, packages, modulepath, cls):
        print('handling class: {0} -> {1}'.format(
            cls.full_name,
            cls.fuzzy.full_name
        ))
        try:
            cls_full_path = os.path.join(
                self._paths['dst'],
                module2filepath(cls.fuzzy.full_name)+'.as'
            )
            with open(cls_full_path, 'r') as infile:
                source = infile.read()
            source = TidySourceFile.tidy(TidySourceFile.trim_comments(source))

            source = SourceCodeReplacer.replace(
                source, cls, packages, modulepath, self._names_map
            )
            # from IPython import embed;embed();
            with open(cls_full_path, 'w') as outfile:
                source = outfile.write(source)
        except IOError:
            # FIXME mxml文件
            pass

    def run(self, swf_filename):
        print('parsing original source files in {0} ...'.format(
                self._paths['src']
        ))
        self._builder = asdox.asBuilder.Builder()
        print('clean up {0} ...'.format(self._paths['dst']))
        if os.path.exists(self._paths['dst']):
            shutil.rmtree(self._paths['dst'])
        os.makedirs(self._paths['dst'])
        # 收集混淆包名, 类名
        self._reproduce_dir(self._paths['src'], self._paths['dst'])
        self._names_map['module'][''] = ''
        #
        self._packages = self._builder.packages
        del self._builder
        print(json.dumps(self._names_map, indent=4))
        with open('names_map.json', 'w') as outfile:
            print(json.dumps(self._names_map, indent=4), file=outfile)
        print('generating new infos ...')
        for pkg in self._packages.values():
            for i, cls in enumerate(pkg.classes.values()):
                cls.fuzzy = FuzzyClassGenerator.generate(
                    pkg.name, cls,
                    self._names_map['class']
                )
        
        import pickle
        with open('self.pydata', 'w') as outfile:
            pickle.dump(self, outfile)
            print('dumped `self` to `self.pydata`....')
        # self._generate_new_packages(self._packages)

        print('Analysing swf file:{0} ...'.format(swf_filename))
        replacer = SWFFileReplacer(self._packages, self._names_map)
        name, ext = os.path.splitext(swf_filename)
        out_filename = name + '.obfused' + ext
        replacer.replace(swf_filename,  out_filename)
        print('Replacing SWF file {0} -> {1}'.format(swf_filename, out_filename))
        return None

    def debug(self, swf_filename):
        print('>>debug<< restore self from {0}'.format('self.pydata'))
        import pickle
        with open('self.pydata', 'r') as infile:
            self = pickle.load(infile)

        # self._generate_new_packages(self._packages)

        print('Analysing swf file:{0} ...'.format(swf_filename))
        replacer = SWFFileReplacer(self._packages, self._names_map)
        name, ext = os.path.splitext(swf_filename)
        out_filename = name + '.obfused' + ext
        replacer.replace(swf_filename,  out_filename)
        print('Replacing SWF file {0} -> {1}'.format(swf_filename, out_filename))
        return None
