import pafy
from subprocess import call

video_url = "https://www.youtube.com/watch?v=j6TL7ufqoLc"

video = pafy.new(video_url)
print video.title

'''
for stream in video.audiostreams:
	print stream

video.audiostreams[0].download()
'''

call(["youtube-dl", "--write-sub", "--sub-lang", "ru", "--skip-download", video_url])
