# -*- coding: utf-8 -*-

import os
import subprocess
import re

import pyvtt

import sys
curr_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,os.path.join(curr_dir_path, os.path.pardir))

import const


def get_subs(yt_video_id, auto_subs=False):

    subs_name = "autosubs" if auto_subs else "subs"

    # download subtitles
    video_data_path = os.path.join(const.VIDEO_DATA_DIR, yt_video_id)

 

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

   

    subs_path_pre = os.path.join(video_data_path, subs_name+".vtt")
    subs_path = os.path.join(video_data_path, subs_name+".ru.vtt")

    if not os.path.exists(subs_path):    
        print 'downloading subtitles to ' + subs_path

        p = subprocess.Popen(["youtube-dl",  "--write-auto-sub" if auto_subs else "--write-sub",                          
                          "--sub-lang", "ru",
                          "--skip-download",
                          "-o", subs_path_pre,
                          'https://www.youtube.com/watch?v='+yt_video_id],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        try:
            p.kill()
        except:
            pass

        if p.returncode != 0:
            print 'ERROR: %s'+err
            raise Exception(subs_name+"_error_downloading_subtitles")

        

        if not os.path.exists(subs_path):
            raise Exception(subs_name+"_subtitles_not_available")

    subs = pyvtt.WebVTTFile.open(subs_path)

    

    # fix yt autosubs
    if auto_subs:
        fixed_subs = []

        for s in subs:           
            #print "--> "+s.text     
            rows = s.text.split('\n')            

            # take last row (bugfix)
            s.text = rows[-1]

            timecodes = [pyvtt.WebVTTTime.from_string(x).ordinal for x in re.findall(r'<(\d+:\d+:\d+.\d+)>', s.text)]

            words_str = re.sub(r'<[^>]*>', '', s.text)
            words = re.compile(r'[\s]+').split(words_str)

            if len(rows) < 2 and len(timecodes) == 0:
                continue

            if len(words) > 1 and len(timecodes) == 0:
                #s.text = "[BAD] "+s.text
                continue

            fixed_subs.append(s)

        subs = fixed_subs

    return subs

def get_timed_words(yt_video_id):
    
    subs = get_subs(yt_video_id, auto_subs = True)

    #print 'number of auto-subs: %i' % len(subs)
  

    timed_words = []

    auto_time_codes_found = 0

    for i in range(0, len(subs)):
        s = subs[i]

        #print '---'
        #print s.text

        timecodes = [pyvtt.WebVTTTime.from_string(x).ordinal for x in re.findall(r'<(\d+:\d+:\d+.\d+)>', s.text)]
        auto_time_codes_found += len(timecodes)

        end_time = s.end.ordinal
        if i < len(subs) - 1:
            if subs[i+1].start.ordinal < end_time:
                end_time = subs[i+1].start.ordinal

        timecodes = [s.start.ordinal] + timecodes + [end_time]


       
        words_str = re.sub(r'<[^>]*>', '', s.text)
        
        

        rows = words_str.split('\n')

        #print 'rows: %i ' % len(rows)

        # take last row (bugfix)
        words_str = rows[-1]

        #print '***'
        #print words_str

        

        regex = re.compile(r'[\s]+')
        words = regex.split(words_str)

        if len(words)+1 != len(timecodes):
            #raise Exception('video_doesnt_have_auto_subtitles')
            continue
            
        #print 'USE'

        for i in range(0, len(words)):
            word = words[i]

            timed_words.append({
                'word': words[i],
                'start': timecodes[i],
                'end': timecodes[i+1]
                })

    if auto_time_codes_found == 0:
        raise Exception('video_doesnt_have_auto_subtitles')

    return timed_words


    
def find_string_timing(timed_words, target_str, seq_start_time, offset):
    target_str = target_str.decode('utf-8').lower()    
    #print target_str 
    target_str = re.sub(u'[^a-zа-яё ]+', '', target_str)
    #print target_str 
    regex = re.compile(r'[\s]+')
    words = regex.split(target_str)

    if len(words) == 0:
        return None

    for i in range(0, len(timed_words)):

        if timed_words[i]['start'] > seq_start_time - offset \
            and timed_words[i]['end'] < seq_start_time + offset \
            and timed_words[i]['word'] == words[0]:
            
            start_timing = timed_words[i]['start']
            end_timing = timed_words[i]['end']            

            matching_sequence = True
            for j in range(1, len(words)):
                if i+j >= len(timed_words):
                    matching_sequence = False
                    break
                if timed_words[i+j]['word'] != words[j]:
                    matching_sequence = False
                    break
                end_timing = timed_words[i+j]['end']

            if matching_sequence:
                return {'start': start_timing, 'end': end_timing}

    return None