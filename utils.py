#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import re

def clear_subtitle_text(text):
	cleared_text = text

	cleared_text = cleared_text.replace("\n", " ")
	cleared_text = re.sub(u'[^a-zA-Zа-яА-Я ]+', '', cleared_text, re.UNICODE)
	cleared_text = cleared_text.strip()
	cleared_text = re.sub(' +', ' ', cleared_text)

	return cleared_text