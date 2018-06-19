# -*- coding: utf-8 -*-

import os
import subprocess
import re

import pyvtt

import sys
curr_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(curr_dir_path, os.path.pardir))

import const

from utils import ensure_dir





# def get_timed_words(yt_video_id):

#     subs = get_subs(yt_video_id, auto_subs=True)

#     # print 'number of auto-subs: %i' % len(subs)

#     timed_words = []

#     auto_time_codes_found = 0

#     for i in range(0, len(subs)):
#         s = subs[i]

#         timecodes = [pyvtt.WebVTTTime.from_string(
#             x).ordinal for x in re.findall(r'<(\d+:\d+:\d+.\d+)>', s.text)]
#         auto_time_codes_found += len(timecodes)

#         end_time = s.end.ordinal
#         if i < len(subs) - 1:
#             if subs[i + 1].start.ordinal < end_time:
#                 end_time = subs[i + 1].start.ordinal

#         timecodes = [s.start.ordinal] + timecodes + [end_time]

#         words_str = re.sub(r'<[^>]*>', '', s.text)

#         rows = words_str.split('\n')

#         # print 'rows: %i ' % len(rows)

#         # take last row (bugfix)
#         words_str = rows[-1]

#         # print '***'
#         # print words_str

#         regex = re.compile(r'[\s]+')
#         words = regex.split(words_str)

#         if len(words) + 1 != len(timecodes):
#             #raise Exception('video_doesnt_have_auto_subtitles')
#             continue

#         # print 'USE'

#         for i in range(0, len(words)):
#             word = words[i]

#             timed_words.append({
#                 'word': words[i],
#                 'start': timecodes[i],
#                 'end': timecodes[i + 1]
#             })

#     if auto_time_codes_found == 0:
#         raise Exception('video_doesnt_have_auto_subtitles')

#     return timed_words


# def find_string_timing(timed_words, target_str, seq_start_time, offset):
#     target_str = target_str.decode('utf-8').lower()
#     # print target_str
#     target_str = re.sub(u'[^a-zа-яё ]+', '', target_str)
#     # print target_str
#     regex = re.compile(r'[\s]+')
#     words = regex.split(target_str)

#     if len(words) == 0:
#         return None

#     for i in range(0, len(timed_words)):

#         if timed_words[i]['start'] > seq_start_time - offset \
#                 and timed_words[i]['end'] < seq_start_time + offset \
#                 and timed_words[i]['word'] == words[0]:

#             start_timing = timed_words[i]['start']
#             end_timing = timed_words[i]['end']

#             matching_sequence = True
#             for j in range(1, len(words)):
#                 if i + j >= len(timed_words):
#                     matching_sequence = False
#                     break
#                 if timed_words[i + j]['word'] != words[j]:
#                     matching_sequence = False
#                     break
#                 end_timing = timed_words[i + j]['end']

#             if matching_sequence:
#                 return {'start': start_timing, 'end': end_timing}

#     return None
