#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import cyrtranslit
from num2words import num2words


def cvt_num(num_str):
    return num2words(int(num_str), lang='ru')

def clear_subtitle_text(text):
    cleared_text = text


    cleared_text = cyrtranslit.to_cyrillic(cleared_text, 'ru')

    # convert latin
    cleared_text = cyrtranslit.to_cyrillic(cleared_text, 'ru')

    #convert numbers 
    cleared_text = re.sub(r'\d+', lambda m: cvt_num(m.group()), cleared_text)


    cleared_text = cleared_text.replace("\n", " ")
    cleared_text = re.sub(u'[^a-zA-Zа-яА-Я ]+', '', cleared_text, re.UNICODE)
    cleared_text = cleared_text.strip()
    cleared_text = re.sub(' +', ' ', cleared_text)
    cleared_text = cleared_text.lower()



    return cleared_text
