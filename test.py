#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import cyrtranslit
from num2words import num2words
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def cvt_num(num_str):
    return num2words(int(num_str), lang='ru')

s = '1 perspective операционка 2'

print cyrtranslit.to_cyrillic(s, 'ru')

print re.sub(r'\d+', lambda m: cvt_num(m.group()), s)

