# coding:utf-8

import os

import sys
curr_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(curr_dir_path, os.path.pardir))


import re
import const


def is_bad_subs(subs_text):
    bad = False

    if subs_text.strip() == "":
        bad = True

    if len(re.findall(r'[0-9]+', subs_text)) > 0:
        bad = True
    if len(re.findall(r'[A-Za-z]+', subs_text)) > 0:
        bad = True

    return bad


def clean_transcript_text(transcript):
    transcript = transcript.decode("utf-8")

    if const.LANGUAGE == "ru":
        transcript = re.sub(r'<[^>]*>', '', transcript)
        transcript = re.sub(r'\[[^\]]*\]', '', transcript)
        transcript = transcript.replace("\n", " ")
        transcript = re.sub(u'[^0-9a-zа-яё\- ]', '',
                            transcript.strip().lower()).strip()
        # transcript = transcript.replace("ё", "е")
    else:
        raise Exception(
            "clean_transcript_text is not implemented for language %s" % (const.LANGUAGE))

    return transcript
