import sys
import os

import video_parser


import csv
from filelock import Timeout, FileLock

reload(sys)
sys.setdefaultencoding('utf8')

curr_dir_path = os.path.dirname(os.path.realpath(__file__))

TO_PROCESS_CSV_FILE = os.path.join(curr_dir_path, "videos_to_process.csv")
PROCESSED_CSV_FILE = os.path.join(curr_dir_path, "videos_processed.csv")
FAILED_CSV_FILE = os.path.join(curr_dir_path, "videos_failed_to_process.csv")


def get_video_to_process():
    with FileLock(TO_PROCESS_CSV_FILE + ".lock"):
        video_id = None

        csv_reader = csv.reader(open(TO_PROCESS_CSV_FILE, "rb"))

        data = list(csv_reader)
        if len(data) > 0:
            video_id = data.pop(0)[0]

        csv_writer = csv.writer(open(TO_PROCESS_CSV_FILE, "wb"))

        # write without first row
        for row in data:
            csv_writer.writerow(row)

        return video_id


def is_video_in_csv(csv_path, video_id):
    with FileLock(csv_path + ".lock"):
        csv_reader = csv.reader(open(csv_path, "rb"))
        data = list(csv_reader)

        for row in data:
            if row[0] == video_id:
                return True
    return False


def put_video_to_failed(video_id, reason):
    if not is_video_in_csv(FAILED_CSV_FILE, video_id):
        with FileLock(FAILED_CSV_FILE + ".lock"):
            csv_writer = csv.writer(open(FAILED_CSV_FILE, "ab"))
            csv_writer.writerow([video_id, reason])


def put_video_to_processed(video_id, reason):
    if not is_video_in_csv(PROCESSED_CSV_FILE, video_id):
        with FileLock(PROCESSED_CSV_FILE + ".lock"):
            csv_writer = csv.writer(open(PROCESSED_CSV_FILE, "ab"))
            csv_writer.writerow([video_id, reason])


def video_parser_loop():

    video_id = get_video_to_process()
    while video_id:
        try:
            video_parser.parse_video(video_id)

            put_video_to_processed(video_id)
        except Exception as e:
            print('failed to process video ' + video_id + ': ' + str(e))

            # put id to failed csv with reason
            put_video_to_failed(video_id, str(e))

        video_id = get_video_to_process()


video_parser_loop()

# video_parser.parse_video("FNmZ3ldVlmc")
