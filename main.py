import sys
import os

import video_parser

import stats_util
import const

import csv
from filelock import Timeout, FileLock

from threading import Thread
import time

import traceback

reload(sys)
sys.setdefaultencoding('utf8')

curr_dir_path = os.path.dirname(os.path.realpath(__file__))

const.TO_PROCESS_CSV_FILE = os.path.join(curr_dir_path, "videos_to_process.csv")
const.PROCESSED_CSV_FILE = os.path.join(curr_dir_path, "videos_processed.csv")
const.FAILED_CSV_FILE = os.path.join(curr_dir_path, "videos_failed_to_process.csv")


def setup():
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    if not os.path.exists(videos_data_dir):
        os.makedirs(videos_data_dir)
	
    
    open(const.TO_PROCESS_CSV_FILE, 'a').close()	
    open(const.PROCESSED_CSV_FILE, 'a').close()	
    open(const.FAILED_CSV_FILE, 'a').close()


def get_video_to_process():
    with FileLock(const.TO_PROCESS_CSV_FILE + ".lock"):
        video_id = None

        csv_reader = csv.reader(open(const.TO_PROCESS_CSV_FILE, "r+"))

        data = list(csv_reader)
        if len(data) > 0:
            video_id = data.pop(0)[0]

        csv_writer = csv.writer(open(const.TO_PROCESS_CSV_FILE, "wb"))

        # write without first row
        for row in data:
            csv_writer.writerow(row)

        return video_id


def is_video_in_csv(csv_path, video_id):
    with FileLock(csv_path + ".lock"):
        csv_reader = csv.reader(open(csv_path, "r+"))
        data = list(csv_reader)

        for row in data:
            if row[0] == video_id:
                return True
    return False


def put_video_to_failed(video_id, reason):
    if not is_video_in_csv(const.FAILED_CSV_FILE, video_id):
        with FileLock(const.FAILED_CSV_FILE + ".lock"):
            csv_writer = csv.writer(open(const.FAILED_CSV_FILE, "a+"))
            csv_writer.writerow([video_id, reason])


def put_video_to_processed(video_id):
    if not is_video_in_csv(const.PROCESSED_CSV_FILE, video_id):
        with FileLock(const.PROCESSED_CSV_FILE + ".lock"):
            csv_writer = csv.writer(open(const.PROCESSED_CSV_FILE, "a+"))
            csv_writer.writerow([video_id])


def video_parser_thread_loop():
    
    while True:
        video_id = get_video_to_process()
        
        if not video_id:
            print 'no videos to parse - wait 5 seconds...'
            time.sleep(5)
            continue

        try:
            video_parser.parse_video(video_id)

            put_video_to_processed(video_id)
        except Exception as e:
            print('failed to process video ' + video_id + ': ' + str(e))

            traceback.print_exc()

            # put id to failed csv with reason
            put_video_to_failed(video_id, str(e))

        


def start_parsing():
    setup()


    video_parser_threads = []
    # start parsing threads
    for i in range(0, 8):
        print 'start parsing thread '+str(i)
        thr = Thread(target=video_parser_thread_loop)
        thr.start()
        video_parser_threads.append(thr)

    # wait for threads
    for thr in video_parser_threads:
        thr.join()

    stats_util.show_global_stats()

start_parsing()



