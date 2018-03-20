#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import pyvtt
import sys

import re
import string

import pafy

import io
import csv

import numpy as np
from scipy.io import wavfile




reload(sys)
sys.setdefaultencoding('utf-8')






def get_subs(yt_video_id, auto_subs=False):

    subs_name = "autosubs" if auto_subs else "subs"

    # download subtitles
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/" + yt_video_id + "/")

 

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
                          yt_video_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            raise Exception(subs_name+"_error_downloading_subtitles")

        if not os.path.exists(subs_path):
            raise Exception(subs_name+"_subtitles_not_available")

    subs = pyvtt.WebVTTFile.open(subs_path)

    return subs

def get_timed_words(yt_video_id):
    
    subs = get_subs(yt_video_id, auto_subs = True)
  

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

def is_bad_piece(wav_path, transcript):
    SAMPLE_RATE = 16000
    MAX_SECS = 10

    frames = int(subprocess.check_output(['soxi', '-s', wav_path], stderr=subprocess.STDOUT))
    

    if int(frames/SAMPLE_RATE*1000/10/2) < len(transcript):
        # Excluding samples that are too short to fit the transcript
        return True
    elif frames/SAMPLE_RATE > MAX_SECS:
        # Excluding very long samples to keep a reasonable batch-size
        return True

def is_bad_subs(subs_text):
    bad = False

    if subs_text.strip() == "":
        bad = True

    if len(re.findall(r'[0-9]+', subs_text)) > 0:
        bad = True
    if len(re.findall(r'[A-Za-z]+', subs_text)) > 0:
        bad = True

    return bad

def write_stats(video_folder, stats_header, stats):
    stats_path = os.path.join(video_folder, "stats.csv")
    csv_writer = csv.writer(open(stats_path, "w"))
    csv_writer.writerow(stats_header)
    csv_writer.writerow(stats)

def get_average_value_from_array_around_pos(array, pos, offset):
    start = max(0, pos-offset)
    end = min(pos+offset, len(array))
    s = 0
    for i in range(start, end):
        s += array[i]
    return s/(end-start)



def starts_or_ends_during_speech(path):

    sampl_rate, data = wavfile.read(path)
    data = np.absolute(data)   

    duration = (float(len(data))/sampl_rate)
    average_val =  np.sum(data)/len(data)

    min_val = 99999999
    max_val = 0
    sum_val = 0
    for v in data:
        if v < min_val:
            min_val = v
        if v > max_val:
            max_val = v        

     
    med_val = (max_val-min_val)/2

    print 'average_val %f' % average_val
    print 'med_val %f' % med_val

    offset_samples = int(sampl_rate*0.1)   

    #start = 0.756

    def get_val_at_time(t):
        return get_average_value_from_array_around_pos(data, int(t*sampl_rate), offset_samples)

    def is_silence(val):
        print 'check val %f' % val
        return val < med_val*0.75

    if not is_silence(get_val_at_time(0)):
        print 'starts with speech'
        return True

    if not is_silence(get_val_at_time(duration)):
        print 'ends with speech'
        return True

    return False


    


def correct_cut_by_waveform(path, start, end):
    sampl_rate, data = wavfile.read(path)

    data = np.absolute(data)

    
    #print path
    duration = (float(len(data))/sampl_rate)
    print 'duration: %f' % duration
    print 'initial cut: %.2f - %.2f' % (start, end)

    sum_val = 0
    for v in data:
        sum_val += v
        

    average_val =  sum_val/len(data)


    offset_samples = int(sampl_rate*0.05)   

    #start = 0.756

    def get_val_at_time(t):
        return get_average_value_from_array_around_pos(data, int(t*sampl_rate), offset_samples)    
    def is_silence(val):
        return val < average_val/1.3
    

    # find SILENT START
    start_later = start    

    while True:       
        # reached silence or end
        if is_silence(get_val_at_time(start_later)) or start_later >= end:
            break
        start_later += 0.05

    start_earlier = start    

    # while True:       
    #     # reached silence or 0
    #     if is_silence(get_val_at_time(start_earlier)) or start_earlier <= 0:
    #         break
    #     start_earlier -= 0.05

    # select closest to current pos
    #if abs(start - start_earlier) > abs(start - start_later):
    start = start_later
    # else:
    #     start = start_earlier

    # find SILENT END
    end_later = end

    while True:       
        # reached silence or end
        if is_silence(get_val_at_time(end_later)) or end_later >= duration:
            break
        end_later += 0.05

    end_earlier = end

    while True:       
        # reached silence or start
        if is_silence(get_val_at_time(end_earlier)) or end_earlier <= start:
            break
        end_earlier -= 0.05

    # select closest to current pos
    if abs(end - end_earlier) > abs(end - end_later):
        end = end_later
    else:
        end = end_earlier
        

    print 'new cut %f - %f' % (start, end)

    print "average val: %f (from %i samples)" % (average_val, len(data))
    
    return (start, end)

    




def process_video(yt_video_id):
    print 'Processing video '+yt_video_id

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/" + yt_video_id + "/")

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

    parts_dir_path = os.path.join(video_data_path, "parts/")

    if not os.path.exists(parts_dir_path):
        os.makedirs(parts_dir_path)



    timed_words = get_timed_words(yt_video_id)

    subs = get_subs(yt_video_id)

    audio_path = download_yt_audio(yt_video_id)



    good_pieces_count = 0
    found_timing_count = 0
    processed_subs_count = 0
    total_speech_duration = 0.0


    for i, s in enumerate(subs):
        if is_bad_subs(s.text):
            continue

        processed_subs_count+=1
        transcript = s.text.replace("\n", " ")
        transcript = re.sub(u'[^а-яё ]', '', transcript.strip().lower())
        #print transcript
        piece_time = find_string_timing(timed_words, transcript, s.start.ordinal, 15000)
        if not piece_time:
            continue

        found_timing_count+=1

        # cut audio
        audio_piece_path = os.path.join(
            parts_dir_path, yt_video_id + "-" + str(piece_time['start']) + "-" + str(piece_time['end']) + ".wav")

        cut_global_time_start = float(piece_time['start'])/1000
        cut_global_time_end = float(piece_time['end'])/1000+0.3

        # cut_extended_global_time_start = max(cut_global_time_start - 1.0, 0)
        # cut_extended_global_time_end = cut_global_time_end + 1.0


        

        #if not os.path.exists(audio_piece_path):
        cut_audio_piece_to_wav(audio_path, audio_piece_path,
                        cut_global_time_start,
                        cut_global_time_end)

        

        # corrected_start, corrected_end = correct_cut_by_waveform(audio_piece_path,
        #      cut_global_time_start - cut_extended_global_time_start,
        #      cut_global_time_end - cut_extended_global_time_start)

        # cut_audio_piece_to_wav(audio_piece_path, audio_piece_path,
        #                 corrected_start,
        #                 corrected_end)        

        # if not bad piece - write to csv
        if is_bad_piece(audio_piece_path, transcript):
            continue

        if "Y53gG0ZauaE-18130-20449" in audio_piece_path:
            if not starts_or_ends_during_speech(audio_piece_path):            
                print 'OK: '+audio_piece_path
            else:
                print 'BAD: '+audio_piece_path

        good_pieces_count += 1

        file_size = os.path.getsize(audio_piece_path)

        total_speech_duration += float(piece_time['end'] - piece_time['start'])/1000

        


    print 'found timed audio for '+str(float(found_timing_count)/processed_subs_count*100)+'%'
    print 'good pieces: '+str(float(good_pieces_count)/processed_subs_count*100)+'% ('+str(good_pieces_count)+')'

   
# yQPbqSfPoJw-21990-23430
yt_video_id = "Y53gG0ZauaE"

process_video(yt_video_id)



