import os
import csv

import const

import sys

import shutil

def remove_failed_data():
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    total_scanned = 0
    bad = 0

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue        

        stats_path = os.path.join(item_path, "stats.csv")

        total_scanned += 1
        if not os.path.exists(stats_path):
            bad += 1
            print 'No stats in %s' % item
            shutil.rmtree(item_path)

    
    print 'Removed %i folders from %i total' % (bad, total_scanned)


if __name__ == '__main__':
    remove_failed_data()
        