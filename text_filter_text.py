# *= coding: utf-8 *=

import re

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

def filter_not_in_alphabet_chars(text):
    text = re.sub(u'[^а-яё\- ]+', '', text.decode("utf-8").lower())
    return text

text = "подошёл из-за угла"
print filter_not_in_alphabet_chars(text)