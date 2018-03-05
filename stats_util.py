import os
import csv

import const

from filelock import Timeout, FileLock

def show_global_stats():

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")


    stats_total_duration = 0.0
    stats_videos_folders_count = 0
    
    stats_processed_videos_count = 0
    stats_failed_videos_count = 0
    stats_pending_videos_count = 0

    # get queue stats
    with FileLock(const.PROCESSED_CSV_FILE+".lock"):
        stats_processed_videos_count = len(list(csv.reader(open(const.PROCESSED_CSV_FILE, "r"))))
    with FileLock(const.FAILED_CSV_FILE+".lock"):
        stats_failed_videos_count = len(list(csv.reader(open(const.FAILED_CSV_FILE, "r"))))
    with FileLock(const.TO_PROCESS_CSV_FILE+".lock"):
        stats_pending_videos_count = len(list(csv.reader(open(const.TO_PROCESS_CSV_FILE, "r"))))

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue

        stats_path = os.path.join(item_path, "stats.csv")

        if not os.path.exists(stats_path):
            print 'WARNING: no stats for video '+item
            continue

        with FileLock(const.PROCESSED_CSV_FILE+".lock"):
            stats_csv = list(csv.reader(open(stats_path, "r")))            
            stats = stats_csv[1]
            stats_total_duration += float(stats[0])


    # print stats

    print '[PARSING STATS]'
    print "stats_failed_videos_count: "+str(stats_failed_videos_count)
    print "stats_processed_videos_count: " + str(stats_processed_videos_count)
    print "stats_pending_videos_count: " + str(stats_pending_videos_count)

    print "stats_total_duration: " + format(stats_total_duration/3600, '.2f')+" hours"

if __name__ == '__main__':
    show_global_stats()
        
