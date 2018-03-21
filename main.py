import sys
import os

import video_parser

import stats_util

import subprocess


import csv_utils

from threading import Thread
import time

import traceback

import youtube_video_searcher



reload(sys)
sys.setdefaultencoding('utf8')

def check_dependencies_installed():
    try:
        subprocess.check_output(['soxi'], stderr=subprocess.STDOUT)
        subprocess.check_output(['youtube-dl', '--help'], stderr=subprocess.STDOUT)
        subprocess.check_output(['ffmpeg', '--help'], stderr=subprocess.STDOUT)
    except Exception as ex:
        print 'ERROR: some of dependencies are not installed: youtube-dl, ffmpeg or sox: '+str(ex)
        return False

    return True

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
            video_parser.process_video(video_id)

            csv_utils.put_video_to_processed(video_id)
        except Exception as e:
            print('failed to process video ' + video_id + ': ' + str(e))

            video_parser.remove_video_dir(video_id)

            #traceback.print_exc()
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
    for i in range(0, 12):
        print 'start parsing thread ' + str(i)
        thr = Thread(target=video_parser_thread_loop)
        thr.daemon = True
        thr.start()
        video_parser_threads.append(thr)



    # wait for threads
    for thr in video_parser_threads:
        thr.join()

    stats_util.show_global_stats()

if __name__ == "__main__":
    if check_dependencies_installed():
        start_parsing()
