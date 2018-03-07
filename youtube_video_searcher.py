#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import urllib
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')



query_string = urllib.urlencode({"search_query" : 'яблоко', 'sp': 'EgIoAQ%3D%3D'})
html_content = urllib.urlopen("http://www.youtube.com/results?" + query_string)
search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())

print 'found '+str(len(search_results)) + ' videos'

for sr in search_results:
    print("http://www.youtube.com/watch?v=" + sr)
#