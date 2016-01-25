#!/usr/bin/env python
# encoding=utf-8

import os


def filepath2module(filepath):
    return '.'.join(filepath.split(os.sep))


def module2filepath(modulepath):
    return os.sep.join(modulepath.split('.'))


def splitABCName(abcName):
    package, classname = os.path.split(abcName)
    package = '.'.join(package.split('/'))
    return package, classname


def joinPackageClassName(package, classname):
    if package == '':
        return classname
    return '{0}:{1}'.format(package, classname)
