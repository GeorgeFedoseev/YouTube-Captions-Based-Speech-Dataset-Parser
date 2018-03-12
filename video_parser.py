#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pafy
import subprocess

import pyvtt
import os
import io
import re


import subs_utils

import shutil

import contextlib
import wave
import speech_utils

import csv

from remove_source_lower_than_target_fix import source_lower_than_target_bad_condition

def remove_video_dir(video_id):
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/" + video_id + "/")
    if os.path.exists(video_data_path):
        shutil.rmtree(video_data_path)


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

        if len(words)+1 != len(timecodes):
            raise Exception('video_doesnt_have_auto_subtitles')
            

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
    #print 'audio lowest download size: ' + str(audio_lowest_size.get_filesize())
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

    if len(subs) < 30:
        raise Exception('too_little_nuber_of_subtitles_in_video')

    audio_path = download_yt_audio(yt_video_id)


    # create csv
    csv_path = os.path.join(video_data_path, "parts.csv")
    csv_f = io.open(csv_path, "w+", encoding="utf-8")

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

        if not os.path.exists(audio_piece_path):
            cut_audio_piece_to_wav(audio_path, audio_piece_path,
                            float(piece_time['start'])/1000,
                            float(piece_time['end'])/1000+0.3)

        # if not bad piece - write to csv
        if is_bad_piece(audio_piece_path, transcript):
            continue

        good_pieces_count += 1

        file_size = os.path.getsize(audio_piece_path)

        total_speech_duration += float(piece_time['end'] - piece_time['start'])/1000

        # write to csv
        csv_f.write(audio_piece_path + ", " +
                    str(file_size) + ", " + transcript + "\n")


    print 'found timed audio for '+str(float(found_timing_count)/processed_subs_count*100)+'%'
    print 'good pieces: '+str(float(good_pieces_count)/processed_subs_count*100)+'% ('+str(good_pieces_count)+')'

    # stats
    write_stats(video_data_path, ["speech_duration", "subs_quality", "good_samples", "total_samples"], [
                total_speech_duration, float(found_timing_count)/processed_subs_count, good_pieces_count, processed_subs_count])
