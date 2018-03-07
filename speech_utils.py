#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import subprocess
from vad import VoiceActivityDetector


def cut_speech_from_audio(full_audio_path, subs_start, subs_end, output_fragment_path):

    print 'trimming speech -> '+output_fragment_path

    p = subprocess.Popen(["ffmpeg", "-y",
         "-i", full_audio_path,
         "-ss", str(subs_start),
         "-to", str(subs_end),
         "-ac", "1",
         "-ab", "16",
         "-ar", "16000",         
         output_fragment_path
         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    if p.returncode != 0:
        raise Exception("failed_ffmpeg_conversion")

    # detect speech borders
    v = VoiceActivityDetector(output_fragment_path)
    raw_detection = v.detect_speech()
    speech_intervals = v.convert_windows_to_readible_labels(raw_detection)

    if len(speech_intervals) == 0:
        return False

   
    
    speech_start = speech_intervals[0]['speech_begin'] - 0.2
    speech_end = speech_intervals[-1]['speech_end'] + 0.2


    # cut silence
    p = subprocess.Popen(["ffmpeg", "-y",
         "-i", output_fragment_path,
         "-ss", str(speech_start),
         "-to", str(speech_end),
         "-ac", "1",
         "-ab", "16",
         "-ar", "16000",         
         output_fragment_path
         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    if p.returncode != 0:
        raise Exception("failed_ffmpeg_conversion")

    return True






