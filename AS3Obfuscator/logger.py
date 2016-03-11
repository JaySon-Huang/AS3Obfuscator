#!/usr/bin/env python
# encoding=utf-8
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)5s] %(filename)s@line:%(lineno)3s %(message)s',
    filename='run.log',
    filemode='w'
)
LOGGER_NAME = 'AS3Obfuscator'
logger = logging.getLogger(LOGGER_NAME)
