import sys
import os

import video_parser

import stats_util


import csv_utils

from threading import Thread
import time

import traceback

import youtube_video_searcher



reload(sys)
sys.setdefaultencoding('utf8')


def setup():
    csv_utils.setup()

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    if not os.path.exists(videos_data_dir):
        os.makedirs(videos_data_dir)



def video_parser_thread_loop():

    while True:
        video_id = csv_utils.get_video_to_process()

        if not video_id:
            print 'no videos to parse - wait 5 seconds...'
            time.sleep(5)
            continue

        # start video processing
        csv_utils.put_video_to_processing(video_id)

        try:
            video_parser.parse_video(video_id)

            csv_utils.put_video_to_processed(video_id)
        except Exception as e:
            print('failed to process video ' + video_id + ': ' + str(e))

            traceback.print_exc()
            #trace = traceback.format_exc().replace('\n', '  ')

            error_type = str(e)
            
            # put id to failed csv with reason
            csv_utils.put_video_to_failed(video_id, error_type)


def start_parsing():
    setup()


    # start searching thread
    youtube_video_searcher.start_searcher_thread()

    video_parser_threads = []
    # start parsing threads
    for i in range(0, 8):
        print 'start parsing thread ' + str(i)
        thr = Thread(target=video_parser_thread_loop)
        thr.start()
        video_parser_threads.append(thr)



    # wait for threads
    for thr in video_parser_threads:
        thr.join()

    stats_util.show_global_stats()


start_parsing()
