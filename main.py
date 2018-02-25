import pafy
from subprocess import call

import pyvtt

'''
video_url = "https://www.youtube.com/watch?v=ypEPe5Ii3Aw"

video = pafy.new(video_url)
print video.title


for stream in video.audiostreams:
	print stream

video.audiostreams[0].download()


call(["youtube-dl", "--write-sub", "--sub-lang", "ru",
 "--skip-download",
 "-o", "./subs.vtt",
  video_url])
'''

subs_path = "./subs.ru.vtt"




subs = pyvtt.WebVTTFile.open(subs_path)

sub = subs[0]
print sub.start.ordinal