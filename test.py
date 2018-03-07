#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from vad import VoiceActivityDetector

from subprocess import call

wav_path = "/Users/gosha/Projects/youtube-audio-captions-parsing/data/blSz672ZarU/parts/blSz672ZarU-50160-56480.wav"
#wav_path = '/Users/gosha/Projects/youtube-audio-captions-parsing/data/h37C0iPGBRU/parts/h37C0iPGBRU-5530-7620.wav'
output_fragment_path = '/Users/gosha/Desktop/test.wav'


v = VoiceActivityDetector(wav_path)
raw_detection = v.detect_speech()
speech_intervals = v.convert_windows_to_readible_labels(raw_detection)
print speech_intervals
print speech_intervals[0]['speech_begin']

speech_start = speech_intervals[0]['speech_begin']-0.2
speech_end = speech_intervals[-1]['speech_end']+0.2

print 'cut '+str(speech_start)+'-'+str(speech_end)

# cut silence
call(["ffmpeg", "-y",
     "-i", wav_path,
     "-ss", str(speech_start),
     "-to", str(speech_end),
     "-ac", "1",
     "-ab", "16",
     "-ar", "16000",         
     output_fragment_path
     ])