import pafy
from subprocess import call

import pyvtt
import os

video_id = "ypEPe5Ii3Aw"
video_data_path = "./data/"+video_id+"/"
if not os.path.exists(video_data_path):
	os.mkdirs(video_data_path)

video = pafy.new(video_id)
print video.title





audio = sorted(video.audiostreams, key=lambda x: x.get_filesize())[0]



audio_path = os.path.join(video_data_path, "audio."+audio.extension) 



#audio.download(filepath=audio_path)


subs_path = os.path.join(video_data_path, "subs.ru.vtt")

call(["youtube-dl", "--write-sub", "--sub-lang", "ru",
 "--skip-download",
 "-o", subs_path,
  video_id])











# audio convert

# ffmpeg -i audio.m4a -ac 1 -ab 16 -ar 16000 audio.wav

audio_output_path = os.path.join(video_data_path, "audio.wav")

call(["ffmpeg", "-y",
 "-i",  audio_path,
 "-ac", "1",
 "-ab", "16",
 "-ar", "16000",
 audio_output_path
 ])


# split 