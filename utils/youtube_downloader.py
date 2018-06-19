import os

import sys
curr_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(curr_dir_path, os.path.pardir))

import const

import pafy  # yt audio downloading
import pyvtt  # VTT subtitles parsing

from cli_dependency_check import is_ytdownloader_installed

def maybe_download_audio_track(yt_video_id):

    curr_dir_path = const.curr_dir_path
    video_data_path = os.path.join(curr_dir_path, "data/" + yt_video_id + "/")

    if not os.path.exists(video_data_path):
        os.makedirs(video_data_path)


    video = pafy.new(yt_video_id)
    # download audio
    audio_lowest_size = sorted(
        video.audiostreams, key=lambda x: x.get_filesize())[0]
    #print 'audio lowest download size: ' + str(audio_lowest_size.get_filesize())
    if audio_lowest_size.get_filesize() > 500000000:
        raise Exception("audio_file_is_too_big")

    audio_path = os.path.join(
        video_data_path, "audio." + audio_lowest_size.extension)

    if not os.path.exists(audio_path):
        print 'downloading audio ' + audio_path
        audio_lowest_size.download(filepath=audio_path, quiet=True)

    if not os.path.exists(audio_path):
        raise Exception("audio_download_failed")

    return audio_path




def maybe_download_subtitiles(yt_video_id, auto_subs=False):
    if not is_ytdownloader_installed():
        return

    subs_name = "autosubs" if auto_subs else "subs"

    # download subtitles
    video_data_path = os.path.join(const.VIDEO_DATA_DIR, yt_video_id)

    ensure_dir(video_data_path)

    _subs_path_tmp = os.path.join(video_data_path, subs_name + ".vtt")
    subs_path = os.path.join(video_data_path, "%s.%s.vtt" %
                             (subs_name, const.LANGUAGE))

    if not os.path.exists(subs_path):
        print 'downloading subtitles to ' + subs_path

        p = subprocess.Popen(["youtube-dl", "--write-auto-sub" if auto_subs else "--write-sub",
                              "--sub-lang", const.LANGUAGE,
                              "--skip-download",
                              "-o", _subs_path_tmp,
                              'https://www.youtube.com/watch?v=' + yt_video_id],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        try:
            p.kill()
        except:
            pass

        if p.returncode != 0:
            print 'ERROR: %s' + err
            raise Exception(subs_name + "_error_downloading_subtitles")

        if not os.path.exists(subs_path):
            raise Exception(subs_name + "_subtitles_not_available")

    subs = pyvtt.WebVTTFile.open(subs_path)

    # fix youtube autosubs
    if auto_subs:
        fixed_subs = []

        for s in subs:
            # print "--> "+s.text
            rows = s.text.split('\n')

            # take last row (bugfix)
            s.text = rows[-1]

            timecodes = [pyvtt.WebVTTTime.from_string(
                x).ordinal for x in re.findall(r'<(\d+:\d+:\d+.\d+)>', s.text)]

            words_str = re.sub(r'<[^>]*>', '', s.text)
            words = re.compile(r'[\s]+').split(words_str)

            if len(rows) < 2 and len(timecodes) == 0:
                continue

            if len(words) > 1 and len(timecodes) == 0:
                #s.text = "[BAD] "+s.text
                continue

            fixed_subs.append(s)

        subs = fixed_subs

    return subs