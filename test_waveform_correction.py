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

import webrtcvad
import wave


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


def convert_to_wav(in_audio_path, out_audio_path):
    p = subprocess.Popen(["ffmpeg", "-y",
         "-i", in_audio_path,         
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

def get_average_value_from_array_around_pos(array, pos, offset):
    start = max(0, pos-offset)
    end = min(pos+offset, len(array))
    s = 0
    for i in range(start, end):
        s += array[i]
    return s/(end-start)

SPEECH_FRAME_SEC = 0.02
CHECK_FRAMES_NUM = 3

def get_speech_int_array(wave, start, end):
    vad = webrtcvad.Vad(3)

    samples_per_second = wave.getframerate()


    samples_per_frame = int(SPEECH_FRAME_SEC*samples_per_second)

    
    wave.setpos(start*samples_per_second)

    wave_view_int = []
    while wave.tell() < end*samples_per_second:
        #wave_view_str += "1" if vad.is_speech(wave.readframes(samples_to_get), sample_rate) else "0"
        wave_view_int.append(1 if vad.is_speech(wave.readframes(samples_per_frame), samples_per_second) else 0)
        wave.setpos(wave.tell() + samples_per_frame)   

    return wave_view_int 

def has_speech(wave, start, end):
    speech_array = get_speech_int_array(wave, start, end)
    return np.sum(speech_array) > 0

def starts_with_speech(wave, start, end):
    speech_array = get_speech_int_array(wave, start, end)
    #print 'start2: '+(''.join([str(x) for x in speech_array]))
    return np.sum(speech_array[:CHECK_FRAMES_NUM]) > 0

def ends_with_speech(wave, start, end): 
    speech_array = get_speech_int_array(wave, start, end)
    #print 'end2: '+(''.join([str(x) for x in speech_array]))
    return np.sum(speech_array[-CHECK_FRAMES_NUM:]) > 0

def starts_or_ends_during_speech(wave, start, end):
    speech_array = get_speech_int_array(wave, start, end)

    return np.sum(speech_array[-CHECK_FRAMES_NUM:]) > 0 or np.sum(speech_array[:CHECK_FRAMES_NUM]) > 0


MAX_ALLOWED_CORRECTION_SEC = 0.2
CORRECTION_WINDOW_SEC = 0.1
def try_correct_cut(wave, start, end):

    print 'try correct cut'

    corrected_start = start   

    need_start_correction = starts_with_speech(wave, start, end)


    if need_start_correction:               
        # try go forward
        while need_start_correction and corrected_start <= start + MAX_ALLOWED_CORRECTION_SEC:            
            corrected_start += CORRECTION_WINDOW_SEC
            need_start_correction = starts_with_speech(wave, corrected_start, end)

        if need_start_correction:
            # try go backwards
            corrected_start = start
            while need_start_correction and corrected_start >= start - MAX_ALLOWED_CORRECTION_SEC:            
                corrected_start -= CORRECTION_WINDOW_SEC
                need_start_correction = starts_with_speech(wave, corrected_start, end)

    if need_start_correction:
        print 'FAILED to correct start'
        return None



    need_end_correction = ends_with_speech(wave, start, end)
    corrected_end = end

    if need_end_correction:
        # try go forward
        while need_end_correction and corrected_end <= end + MAX_ALLOWED_CORRECTION_SEC:            
            corrected_end += CORRECTION_WINDOW_SEC
            need_end_correction = ends_with_speech(wave, corrected_start, corrected_end)

        if need_end_correction:
            # try go backwards
            corrected_end = end
            while need_end_correction and corrected_end >= end - MAX_ALLOWED_CORRECTION_SEC:            
                corrected_end -= CORRECTION_WINDOW_SEC
                need_end_correction = ends_with_speech(wave, corrected_start, corrected_end)

    if need_end_correction:
        print 'FAILED to corrected_end'
        return None

    print 'SUCCESS corrected cut: %f-%f -> %f-%f' % (start, end, corrected_start, corrected_end)

    return (corrected_start, corrected_end)


def print_speech_int_array(speech_int_array):
    print ''.join([str(x) for x in speech_int_array])


def print_speech_frames(wave, start, end):

    wave_view_int = get_speech_int_array(wave, start, end)

    print_speech_int_array(wave_view_int)


    start_view = wave_view_int[:3]
    end_view = wave_view_int[-3:]

    print  'start: '+(''.join([str(x) for x in start_view]))
    print  'end: '+(''.join([str(x) for x in end_view]))

    is_speech_on_start = np.sum(start_view)  > 0
    is_speech_on_end = np.sum(end_view)  > 0

    

    print 'is_speech_on_start: '+str(is_speech_on_start) 
    print 'is_speech_on_end: '+str(is_speech_on_end)

    return is_speech_on_start or is_speech_on_end

#def try_move_start():






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

    audio_path_wav = os.path.join(video_data_path, "audio.wav")


    if not convert_to_wav(audio_path, audio_path_wav):
        print 'ERROR: failet to convert to wav'

    wave_obj = wave.open(audio_path_wav, 'r')





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

      

        good_cut = False

        print '----------------'
        print_speech_frames(wave_obj, cut_global_time_start, cut_global_time_end)
        if not starts_or_ends_during_speech(wave_obj, cut_global_time_start, cut_global_time_end):            
            print 'OK: '+audio_piece_path
            good_cut = True
        else:
            print 'BAD: '+audio_piece_path
            good_cut = False
            corrected_cut = try_correct_cut(wave_obj, cut_global_time_start, cut_global_time_end)
            if corrected_cut:
                cut_global_time_start, cut_global_time_end = corrected_cut
                good_cut = True

        if not has_speech(wave_obj, cut_global_time_start, cut_global_time_end):
            good_cut = False

        if good_cut:
            cut_audio_piece_to_wav(audio_path_wav, audio_piece_path,
                            cut_global_time_start,
                            cut_global_time_end)  
        else:
            if os.path.exists(audio_piece_path):
                os.remove(audio_piece_path)

        good_pieces_count += 1

        # file_size = os.path.getsize(audio_piece_path)

        # total_speech_duration += float(piece_time['end'] - piece_time['start'])/1000

        


    print 'found timed audio for '+str(float(found_timing_count)/processed_subs_count*100)+'%'
    print 'good pieces: '+str(float(good_pieces_count)/processed_subs_count*100)+'% ('+str(good_pieces_count)+')'

   
# yQPbqSfPoJw-21990-23430
yt_video_id = "tKZUGeBhL3M"

process_video(yt_video_id)



