# -*- coding: utf-8 -*-

import subprocess
import wave

import numpy as np
import webrtcvad


# Checks if audio+transcript sample is compatible with DeepSpeech ASR training
def is_bad_piece(audio_duration, transcript):   

    MAX_SECS = 20
    MIN_SECS = 3    
    
    MIN_SEC_PER_SYMBOL = 0.03
    #MIN_SEC_PER_SYMBOL = 0

    # remove audios that are shorter than 0.5s and longer than 20s.
    # remove audios that are too short for transcript.
    if audio_duration > MIN_SECS and audio_duration < MAX_SECS and transcript!="" and audio_duration/len(transcript) > MIN_SEC_PER_SYMBOL:
        return False
    return True


### FILTERS ###

def loud_norm(in_path, out_path):
    # ffmpeg-normalize audio.wav -o out.wav
    # ffmpeg -i audio.wav -filter:a loudnorm loudnorm.wav
    p = subprocess.Popen(["ffmpeg", "-y",
        "-i", in_path,
        "-af", "loudnorm",
        out_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    if p.returncode != 0:
        raise Exception("Failed to loudnorm: %s" % str(err))


def apply_bandpass_filter(in_path, out_path, lowpass=8000, highpass=50):
    # ffmpeg -i input.wav -acodec pcm_s16le -ac 1 -ar 16000 -af lowpass=3000,highpass=200 output.wav
    p = subprocess.Popen(["ffmpeg", "-y",
        "-acodec", "pcm_s16le",
         "-i", in_path,    
         "-acodec", "pcm_s16le",
         "-ac", "1",
         "-af", "lowpass=%i,highpass=%i" % (lowpass, highpass),
         "-ar", "16000",         
         out_path
         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    if p.returncode != 0:
        raise Exception("Failed to apply bandpass filter: %s" % str(err))

def correct_volume(in_path, out_path, db=-2):
    # ffmpeg -i audio.wav -filter:a "volume=-2dB" loudnorm_vol_set.wav
    p = subprocess.Popen(["ffmpeg", "-y",        
         "-i", in_path,
         "-filter:a", "volume=%idB" % (db),
         out_path
         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    if p.returncode != 0:
        raise Exception("Failed to correct volume: %s" % str(err))

# def correct_volume(in_path, out_path, db=-8):
#     # sox input.wav output.wav gain -n -10
#     p = subprocess.Popen(["sox",
#          in_path,             
#          out_path,
#          "gain",
#          "-n", str(db)
#          ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     out, err = p.communicate()

#     if p.returncode != 0:
#         raise Exception("Failed to correct volume: %s" % str(err))

def cut_wave(wave_obj, outfilename, start_ms, end_ms):
    width = wave_obj.getsampwidth()
    rate = wave_obj.getframerate()
    fpms = rate / 1000 # frames per ms
    length = (end_ms - start_ms) * fpms
    start_index = start_ms * fpms

    out = wave.open(outfilename, "w")
    out.setparams((wave_obj.getnchannels(), width, rate, length, wave_obj.getcomptype(), wave_obj.getcompname()))
    
    wave_obj.rewind()
    anchor = wave_obj.tell()
    wave_obj.setpos(anchor + start_index)
    out.writeframes(wave_obj.readframes(length))

def save_wave_samples_to_file(wave_samples, n_channels, byte_width, sample_rate, file_path):
    out = wave.open(file_path, "w")
    length = len(wave_samples)
    out.setparams((n_channels, byte_width, sample_rate, length, 'NONE', 'not compressed'))    
    out.writeframes(wave_samples)
    out.close()

def convert_to_wav(in_audio_path, out_audio_path):
    print 'converting %s to wav' % in_audio_path
    p = subprocess.Popen(["ffmpeg", "-y",
         "-i", in_audio_path,         
         "-ac", "1",
         "-ab", "16",
         "-ar", "16000",         
         out_audio_path
         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    try:
        p.kill()
    except:
        pass

    if p.returncode != 0:
        print("failed_ffmpeg_conversion "+str(err))
        return False
    return True

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

    try:
        p.kill()
    except:
        pass

    if p.returncode != 0:
        print("failed_ffmpeg_conversion "+str(err))
        return False
    return True



