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



def remove_video_dir(video_id):
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/"+video_id+"/")

    shutil.rmtree(video_data_path)

def parse_video(yt_video_id):

    stats_total_speech_duration = 0
    stats_speech_correspondance_to_subs_quality = 0

    print 'PARSE VIDEO '+yt_video_id

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/"+yt_video_id+"/")

    print 'video data directory: ' + video_data_path

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

    video = pafy.new(yt_video_id)
    print "video title" + video.title



    # download subtitles
    subs_path_pre = os.path.join(video_data_path, "subs.vtt")
    subs_path = os.path.join(video_data_path, "subs.ru.vtt")

    print 'downloading subtitles to '+subs_path

    p = subprocess.Popen(["youtube-dl", "--write-sub", "--sub-lang", "ru",
     "--skip-download",
     "-o", subs_path_pre,
      yt_video_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if p.returncode != 0:
        remove_video_dir(yt_video_id)
        raise Exception("error_downloading_subtitles")

    if not os.path.exists(subs_path):
        remove_video_dir(yt_video_id)
        raise Exception("subtitles_not_available")



    # download audio
    audio_lowest_size = sorted(video.audiostreams, key=lambda x: x.get_filesize())[0]
    print 'audio lowest download size: '+str(audio_lowest_size.get_filesize())
    if audio_lowest_size.get_filesize() > 500000000:
        remove_video_dir(yt_video_id)
        raise Exception("audio_file_is_too_big")

    audio_path = os.path.join(video_data_path, "audio."+audio_lowest_size.extension) 

    if not os.path.exists(audio_path):
        print 'downloading audio '+audio_path
        audio_lowest_size.download(filepath=audio_path, quiet=True)

    if not os.path.exists(audio_path):
        remove_video_dir(yt_video_id)
        raise Exception("audio_download_failed")


    # cut by subs

    # create csv
    csv_path = os.path.join(video_data_path, "parts.csv")
    parts_dir_path = os.path.join(video_data_path, "parts/")

    if not os.path.exists(parts_dir_path):
        os.makedirs(parts_dir_path)

    csv_f = io.open(csv_path, "w+", encoding="utf-8")



    # audio, text -> csv

    subs_audio_added_count = 0
    subs_cleared_count = 0

    subs = pyvtt.WebVTTFile.open(subs_path)
    for s in subs:
        cleared_text =  subs_utils.clear_subtitle_text(s.text)
        
        if cleared_text == "":
            continue

        subs_cleared_count += 1

        audio_fragment_path = os.path.join(parts_dir_path, yt_video_id+"-"+str(s.start.ordinal)+"-"+str(s.end.ordinal)+".wav")

        
        if not os.path.exists(audio_fragment_path):
            if not speech_utils.cut_speech_from_audio(audio_path, s.start, s.end, audio_fragment_path):
                continue

        '''
        if not os.path.exists(audio_fragment_path):
            call(["ffmpeg", "-y",
             "-i", audio_path,

             "-ss", str(s.start),
             "-to", str(s.end),
             "-ac", "1",
             "-ab", "16",
             "-ar", "16000",

             
             audio_fragment_path
             ])
        '''

        fragment_duration = 0

        with contextlib.closing(wave.open(audio_fragment_path,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            fragment_duration = frames / float(rate)

        if fragment_duration < 1 or fragment_duration > 10:
            continue


        stats_total_speech_duration += fragment_duration

        filesize = os.path.getsize(audio_fragment_path)

        # add to csv

        csv_f.write(audio_fragment_path+", "+str(filesize)+", "+cleared_text+"\n")
        subs_audio_added_count += 1

    if subs_cleared_count > 0:
        stats_speech_correspondance_to_subs_quality = float(subs_audio_added_count)/subs_cleared_count

    csv_f.close()

    if subs_audio_added_count < 20:
        remove_video_dir(yt_video_id)
        raise Exception("too_little_speech")

    # stats
    write_stats(video_data_path, ["speech_duration", "speech_correspondance_to_subs_quality"], [stats_total_speech_duration, stats_speech_correspondance_to_subs_quality])



def write_stats(video_folder, stats_header, stats):
    stats_path = os.path.join(video_folder, "stats.csv")
    csv_writer = csv.writer(open(stats_path, "w"))
    csv_writer.writerow(stats_header)
    csv_writer.writerow(stats)

