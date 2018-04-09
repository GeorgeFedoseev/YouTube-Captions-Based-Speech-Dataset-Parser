#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pafy
import subprocess


import os
import io
import re

import shutil

import wave
import csv



import time

from utils import audio_utils
from utils import yt_subs_utils



import sys 

import const

reload(sys)
sys.setdefaultencoding('utf8')



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



# CHECK audio piece

def is_bad_piece(wav_path, transcript):
    SAMPLE_RATE = 16000
    MAX_SECS = 10
    MIN_SECS = 1

    frames = int(subprocess.check_output(['soxi', '-s', wav_path], stderr=subprocess.STDOUT))
    

    if int(frames/SAMPLE_RATE*1000/10/2) < len(transcript):
        # Excluding samples that are too short to fit the transcript
        return True
    elif frames/SAMPLE_RATE > MAX_SECS:
        # Excluding very long samples to keep a reasonable batch-size
        return True
    elif frames/SAMPLE_RATE < MIN_SECS:
        # Excluding too small
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
    f = open(stats_path, "w")
    csv_writer = csv.writer(f)
    csv_writer.writerow(stats_header)
    csv_writer.writerow(stats)
    f.close()

def process_video(yt_video_id):
    

    print 'Processing video '+yt_video_id

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/" + yt_video_id + "/")

    # check additionally if processed
    # if os.path.exists(video_data_path):
    #     print 'video %s is ALREADY PARSED' % yt_video_id
    #     raise Exception('video_already_parsed')

    timed_words = yt_subs_utils.get_timed_words(yt_video_id)
    subs = yt_subs_utils.get_subs(yt_video_id)
    

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

    parts_dir_path = os.path.join(video_data_path, "parts/")

    if os.path.exists(parts_dir_path):
        shutil.rmtree(parts_dir_path)

    if not os.path.exists(parts_dir_path):
        os.makedirs(parts_dir_path)  


    audio_path = download_yt_audio(yt_video_id)

    # get wav audio object
    audio_path_wav = os.path.join(video_data_path, "audio.wav")
    if not os.path.exists(audio_path_wav):
        if not audio_utils.convert_to_wav(audio_path, audio_path_wav):
            raise Exception('ERROR: failed to convert to wav')
    wave_obj = wave.open(audio_path_wav, 'r')

    # create csv
    csv_path = os.path.join(video_data_path, "parts.csv")
    csv_f = io.open(csv_path, "w+", encoding="utf-8")

    good_pieces_count = 0
    found_timing_count = 0
    processed_subs_count = 0
    total_speech_duration = 0.0

    print "subs count: %i" % len(subs)

    current_video_time = 0

    try:
        for i, s in enumerate(subs):
            words_str = re.sub(r'<[^>]*>', '', s.text)

            if is_bad_subs(words_str):
                continue

            processed_subs_count+=1
            transcript = words_str.replace("\n", " ")
            transcript = re.sub(u'[^а-яё ]', '', transcript.strip().lower()).strip()
            #print transcript
            piece_time = yt_subs_utils.find_string_timing(timed_words, transcript, s.start.ordinal, 15000)
            if not piece_time:
                continue

            found_timing_count+=1

            #print "process sub %i" % i

            

            cut_global_time_start = float(piece_time['start'])/1000
            cut_global_time_end = float(piece_time['end'])/1000+0.3



            # cut_global_time_start = float(s.start.ordinal)/1000
            # cut_global_time_end = float(s.end.ordinal)/1000 + 0.3

          
            # CHECK CUT (if starts or ends on speech) and try to correct
            good_cut = False
            corrected_cut = False
            #print_speech_frames(wave_obj, cut_global_time_start, cut_global_time_end)


            
            if not audio_utils.starts_or_ends_during_speech(wave_obj, cut_global_time_start, cut_global_time_end):                        
                good_cut = True
            else:            
                good_cut = False
                corrected_cut = audio_utils.try_correct_cut(wave_obj, cut_global_time_start, cut_global_time_end)
                if corrected_cut:                    
                    cut_global_time_start, cut_global_time_end = corrected_cut
                    good_cut = True

            if not audio_utils.has_speech(wave_obj, cut_global_time_start, cut_global_time_end):
                good_cut = False

            audio_piece_path = os.path.join(
                    parts_dir_path, yt_video_id + "-" + str(int(cut_global_time_start*1000)) 
                    + "-" + str(int(cut_global_time_end*1000)) + ("_corr" if corrected_cut else "") + ".wav")

            # good_cut = True


            

            if cut_global_time_start < current_video_time:
                continue



            if good_cut:               
         
                print '----------------'
                print audio_piece_path
                
                print 'GOOD CUT'

                audio_utils.cut_wave(wave_obj, audio_piece_path,
                                int(cut_global_time_start*1000),
                                int(cut_global_time_end*1000))  
            else:
                #print 'BAD CUT'
                if os.path.exists(audio_piece_path):
                    os.remove(audio_piece_path)
                continue
            

            # if not bad piece - write to csv
            if is_bad_piece(audio_piece_path, transcript):
                # remove file
                if os.path.exists(audio_piece_path):
                    os.remove(audio_piece_path)
                continue


            current_video_time = cut_global_time_end

            good_pieces_count += 1

            file_size = os.path.getsize(audio_piece_path)

            total_speech_duration += cut_global_time_end - cut_global_time_start

            # write to csv
            csv_f.write(audio_piece_path + ", " +
                        str(file_size) + ", " + transcript + "\n")
    except Exception as ex:
        raise ex
    finally:
        csv_f.close()
        wave_obj.close()

    print 'found timed audio for '+str(float(found_timing_count)/processed_subs_count*100)+'% ('+str(found_timing_count)+'/'+str(processed_subs_count)+')'
    print 'good pieces: '+str(float(good_pieces_count)/processed_subs_count*100)+'% ('+str(good_pieces_count)+')'

    if good_pieces_count == 0:
        raise Exception('no_audio_parsed')

    # stats
    write_stats(video_data_path, ["speech_duration", "subs_quality", "good_samples", "total_samples"], [
                total_speech_duration, float(found_timing_count)/processed_subs_count, good_pieces_count, processed_subs_count])

#yt_video_id = "cMtaWP3KtTU"
#process_video(yt_video_id)
