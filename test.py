#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import pyvtt
import sys

import re
import string

import pafy

reload(sys)
sys.setdefaultencoding('utf-8')


yt_video_id = "ypEPe5Ii3Aw"






def get_timed_words(yt_video_id):
        # download subtitles
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/" + yt_video_id + "/")

    print 'video data directory: ' + video_data_path

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

   

    subs_path_pre = os.path.join(video_data_path, "autosubs.vtt")
    subs_path = os.path.join(video_data_path, "autosubs.ru.vtt")

    if not os.path.exists(subs_path):    
        print 'downloading subtitles to ' + subs_path

        p = subprocess.Popen(["youtube-dl",  "--write-auto-sub", "--sub-lang", "ru",
                          "--skip-download",
                          "-o", subs_path_pre,
                          yt_video_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            raise Exception("error_auto_downloading_subtitles")

        if not os.path.exists(subs_path):
            raise Exception("auto_subtitles_not_available")

    subs = pyvtt.WebVTTFile.open(subs_path)
  

    timed_words = []

    for i in range(0, len(subs)):
        s = subs[i]

        timecodes = [pyvtt.WebVTTTime.from_string(x).ordinal for x in re.findall(r'<(\d+:\d+:\d+.\d+)>', s.text)]

        end_time = s.end.ordinal
        if i < len(subs) - 1:
            if subs[i+1].start.ordinal < end_time:
                end_time = subs[i+1].start.ordinal

        timecodes = [s.start.ordinal] + timecodes + [end_time]
       
        words_str = re.sub(r'<[^>]*>', '', s.text)
        
        regex = re.compile(r'[\s]+')
        words = regex.split(words_str)

        for i in range(0, len(words)):
            word = words[i]

            timed_words.append({
                'word': words[i],
                'start': timecodes[i],
                'end': timecodes[i+1]
                })

    return timed_words


    
def find_string_timing(timed_words, target_str, seq_start_time, offset):
    target_str = target_str.decode('utf-8').lower()
    #print target_str 
    target_str = re.sub(u'[^a-zа-я ]+', '', target_str)
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


def download_yt_audio(yt_video_id):

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/" + yt_video_id + "/")

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

    video = pafy.new(yt_video_id)
    # download audio
    audio_lowest_size = sorted(
        video.audiostreams, key=lambda x: x.get_filesize())[0]
    print 'audio lowest download size: ' + str(audio_lowest_size.get_filesize())
    if audio_lowest_size.get_filesize() > 500000000:
        raise Exception("audio_file_is_too_big")

    audio_path = os.path.join(
        video_data_path, "audio." + audio_lowest_size.extension)

    if not os.path.exists(audio_path):
        print 'downloading audio ' + audio_path
        audio_lowest_size.download(filepath=audio_path, quiet=True)

    if not os.path.exists(audio_path):
        raise Exception("audio_download_failed")

    return audio_path

def cut_audio_piece_to_wav(in_audio_path, out_audio_path, start_sec, end_sec):
    p = subprocess.Popen(["ffmpeg", "-y",
         "-i", in_audio_path,
         "-ss", str(start_sec),
         "-to", str(end_sec),
         "-ac", "1",
         "-ab", "16",
         "-ar", "16000",         
         out_audio_path
         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    if p.returncode != 0:
        print("failed_ffmpeg_conversion "+str(err))
        return False
    return True


audio_path = download_yt_audio(yt_video_id)

timed_words = get_timed_words(yt_video_id)

piece_time = find_string_timing(timed_words, 'прекрасно справляться с задачей', 262000, 1500000)

if piece_time:
    cut_audio_piece_to_wav(audio_path, "/Users/gosha/Desktop/piece.wav",
                             float(piece_time['start'])/1000,
                            float(piece_time['end'])/1000+0.3)
else:
    print('ERROR! - phrase not found')

