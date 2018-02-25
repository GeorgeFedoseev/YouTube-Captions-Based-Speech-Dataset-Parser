import pafy
from subprocess import call

import pyvtt


video_url = "https://www.youtube.com/watch?v=ypEPe5Ii3Aw"

video = pafy.new(video_url)
print video.title





audio = sorted(video.audiostreams, key=lambda x: x.get_filesize())[0]



audio_path = ".data/audio."+audio.extension

#audio.download(filepath=audio_path)


call(["youtube-dl", "--write-sub", "--sub-lang", "ru",
 "--skip-download",
 "-o", "./subs.vtt",
  video_url])


subs_path = "./data/subs.ru.vtt"




subs = pyvtt.WebVTTFile.open(subs_path)

sub = subs[0]
print sub.start.ordinal



# audio convert

# ffmpeg -i audio.m4a -ac 1 -ab 16 -ar 16000 audio.wav

call(["ffmpeg", "-y",
 "-i",  audio_path,
 "-ac", "1",
 "-ab", "16",
 "-ar", "16000",
 "audio.wav"
 ])