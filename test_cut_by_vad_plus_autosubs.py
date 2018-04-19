import re
import os
import webrtcvad
import datetime

from utils import yt_subs_utils
from utils.yt_utils import download_yt_audio
from utils import audio_utils

import wave

import const

from utils import csv_utils

from video_parser import is_bad_piece, is_bad_subs

curr_dir_path = os.getcwd()

def slice_audio_by_silence(wave_obj, min_audio_length=5, max_audio_length=20, vad_silence_volume_param=1):
    SPEECH_FRAME_SEC = 0.01

    vad = webrtcvad.Vad(vad_silence_volume_param)

    samples_per_second = wave_obj.getframerate()    
    samples_per_frame = int(SPEECH_FRAME_SEC*samples_per_second)
    total_samples = wave_obj.getnframes()    
    
    wave_obj.setpos(0)

    out_pieces = []

    current_piece_start_sec = 0    
    current_piece_length_sec = 0

    current_piece_samples = ""

    total_length = 0

    
    while wave_obj.tell() < total_samples:       
        
        wav_samples = wave_obj.readframes(samples_per_frame)
        current_frame_length_sec = float(samples_per_frame)/samples_per_second       

        
        try:
            is_speech = vad.is_speech(wav_samples, samples_per_second)
        except Exception as ex:
            print("VAD Exception: %s" % str(ex))
            continue

        current_piece_length_sec += current_frame_length_sec
        current_piece_samples += wav_samples

        if (current_piece_length_sec > min_audio_length):
            if not is_speech:
                # push current piece to out
                out_pieces.append({
                    "start": current_piece_start_sec,
                    "end": current_piece_start_sec+current_piece_length_sec,
                    "samples": current_piece_samples
                    })
                total_length += current_piece_length_sec
                # and reset current piece
                current_piece_samples = ""
                current_piece_start_sec += current_piece_length_sec
                current_piece_length_sec = 0
            else:
                if current_piece_length_sec > max_audio_length:
                    print("WARNING: forced cut not at silence but at max_audio_length = %f sec" % max_audio_length)
                    # push current piece to out
                    out_pieces.append({
                        "start": current_piece_start_sec,
                        "end": current_piece_start_sec+current_piece_length_sec,
                        "samples": current_piece_samples
                        })
                    total_length += current_piece_length_sec
                    # and reset current piece
                    current_piece_samples = ""
                    current_piece_start_sec += current_piece_length_sec
                    current_piece_length_sec = 0



    return out_pieces, total_length/len(out_pieces)

yt_video_id = "HBdK8Kac_zU"

autosubs = yt_subs_utils.get_subs(yt_video_id, auto_subs=True)
# for s in autosubs:
#     words_str = re.sub(r'<[^>]*>', '', s.text)
#     print words_str

timed_words = yt_subs_utils.get_timed_words(yt_video_id)
# for tw in timed_words:
#     print("%s-%s %s" % (
#         str(datetime.timedelta(seconds=float(tw["start"])/1000)),
#          str(datetime.timedelta(seconds=float(tw["end"])/1000)),
#           tw["word"]))

# download audio
audio_original_path = download_yt_audio(yt_video_id)

video_dir_path = os.path.join(const.VIDEO_DATA_DIR, yt_video_id);
if not os.path.exists(video_dir_path):
    os.makedirs(video_dir_path)

# convert to wav
audio_wav_path = os.path.join(const.VIDEO_DATA_DIR, yt_video_id+"/audio.wav")

if not os.path.exists(audio_wav_path):
    audio_utils.convert_to_wav(audio_original_path, audio_wav_path)

# load wave object
wave_obj = wave.open(audio_wav_path, "r")

# slice by VAD silence
sliced_pieces, avg_len_sec = slice_audio_by_silence(wave_obj)

print("sliced into %i pieces with average length of %f seconds" % (len(sliced_pieces), avg_len_sec))


parts_folder_path = os.path.join(video_dir_path, "parts/");
if not os.path.exists(parts_folder_path):
    os.makedirs(parts_folder_path)

csv_rows = []

for i, piece in enumerate(sliced_pieces):
    START_PREC_SEC = 0.5
    END_PREC_SEC = 0.2

    # for each piece find words that are inside it
    words = [w for w in timed_words if float(w["start"])/1000 >= piece["start"]-START_PREC_SEC and float(w["end"])/1000 <= piece["end"]+END_PREC_SEC]

    if len(words) == 0:
        continue

    words = sorted(words, key=lambda w: w["start"])

    if abs(piece["start"] - float(words[0]["start"])/1000) > 0.5 or abs(piece["end"] - float(words[-1]["end"])/1000) > 0.5:
        print("skip not precise bounds %i" % i)
        continue

    words_str = " ".join([w["word"] for w in words])

    # print("%s-%s %s" % (
    #     str(datetime.timedelta(seconds=piece["start"])),
    #     str(datetime.timedelta(seconds=piece["end"])),
    #     words_str
    #                     )
    # )

    if is_bad_subs(words_str):
        print("bad subs %i: %s" % (i, words_str))
        continue

    part_wav_path = os.path.join(parts_folder_path, "%s_%i.wav" % (yt_video_id, i))
    audio_utils.save_wave_samples_to_file(piece["samples"], 1, 2, 16000, part_wav_path)
    filesize = os.path.getsize(part_wav_path)

    if is_bad_piece(filesize, words_str):
        print("is_bad_piece %i" % i)
        # remove file
        os.remove(part_wav_path)
        continue



    

    csv_rows.append([part_wav_path, filesize, words_str])


print("added %i pieces" % len(csv_rows))

csv_path = os.path.join(video_dir_path, "parts.csv")

csv_utils.write_rows_to_csv(csv_path, csv_rows)








