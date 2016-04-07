#!/usr/bin/env python
# encoding=utf-8
import logging

LOG_FILENAME = 'run.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)5s] %(filename)s@line:%(lineno)3s %(message)s',
    filename=LOG_FILENAME,
    filemode='w'
)
LOGGER_NAME = 'AS3Obfuscator'
logger = logging.getLogger(LOGGER_NAME)
