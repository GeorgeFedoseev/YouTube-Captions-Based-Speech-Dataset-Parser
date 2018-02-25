#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import re
s = u'as32{ vd"s k!+ fg ddf gdfg ds выа'
print re.sub(u'[^a-zA-ZА-Яа-я ]+', '', s, re.U)