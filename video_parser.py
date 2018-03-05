import pafy
from subprocess import call

import pyvtt
import os
import io
import re



import subs_utils


def parse_video(yt_video_id):
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    video_data_path = os.path.join(curr_dir_path, "data/"+yt_video_id+"/")

    print 'video data directory: ' + video_data_path

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)

    video = pafy.new(yt_video_id)
    print video.title





    audio = sorted(video.audiostreams, key=lambda x: x.get_filesize())[0]



    audio_path = os.path.join(video_data_path, "audio."+audio.extension) 

    if not os.path.exists(audio_path):
        audio.download(filepath=audio_path)



    # download subtitles
    subs_path_pre = os.path.join(video_data_path, "subs.vtt")
    subs_path = os.path.join(video_data_path, "subs.ru.vtt")

    print 'downloading subtitles to '+subs_path

    call(["youtube-dl", "--write-sub", "--sub-lang", "ru",
     "--skip-download",
     "-o", subs_path_pre,
      yt_video_id])

    



    # cut by subs

    # create csv
    csv_path = os.path.join(video_data_path, "parts.csv")
    parts_dir_path = os.path.join(video_data_path, "parts/")

    if not os.path.exists(parts_dir_path):
        os.makedirs(parts_dir_path)

    csv_f = io.open(csv_path, "w+", encoding="utf-8")



    # create paths

    subs = pyvtt.WebVTTFile.open(subs_path)
    for s in subs:
        cleared_text =  subs_utils.clear_subtitle_text(s.text)
        
        

        audio_fragment_path = os.path.join(parts_dir_path, yt_video_id+"-"+str(s.start.ordinal)+"-"+str(s.end.ordinal)+".wav")

        


        call(["ffmpeg", "-y",
         "-i", audio_path,

         "-ss", str(s.start),
         "-to", str(s.end),
         "-ac", "1",
         "-ab", "16",
         "-ar", "16000",

         
         audio_fragment_path
         ])


        csv_f.write(audio_fragment_path+", "+cleared_text+"\n")


    csv_f.close()