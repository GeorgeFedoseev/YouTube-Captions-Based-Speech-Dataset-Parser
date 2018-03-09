#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import cyrtranslit
from num2words import num2words

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def cvt_num(num_str):
    return num2words(int(num_str), lang='ru')

def clear_subtitle_text(text):
    cleared_text = text

    cleared_text = cleared_text.replace("\n", " ")
    cleared_text = re.sub(u'[^a-zA-Zа-яА-Я ]+', '', cleared_text, re.UNICODE)


    # convert latin
    cleared_text = cyrtranslit.to_cyrillic(cleared_text, 'ru').decode('utf-8')

    #convert numbers to words
    cleared_text = re.sub(r'\d+', lambda m: cvt_num(m.group()), cleared_text)

    #leave only russian in the end
    cleared_text = re.sub(u'[^а-яА-Я ]+', '', cleared_text, re.UNICODE)
    
    cleared_text = cleared_text.strip()
    cleared_text = re.sub(' +', ' ', cleared_text)
    cleared_text = cleared_text.lower()


    #print cleared_text

    return cleared_text
