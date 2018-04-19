

from utils import yt_subs_utils
import re

yt_video_id = "i2csYREI2g0"

subs = yt_subs_utils.get_subs(yt_video_id, auto_subs=True)

for s in subs:
    words_str = re.sub(r'<[^>]*>', '', s.text)
    print words_str