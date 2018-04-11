
import sys
sys.path.insert(0,os.getcwd()) 

import os
import csv

import const



import shutil

from tqdm import tqdm # progressbar

def remove_failed_data():
    curr_dir_path = os.getcwd()
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    total_scanned = 0
    bad = 0


    dir_items = os.listdir(videos_data_dir)

    pbar = tqdm(total=len(dir_items))

    for item in dir_items:
        item_path = os.path.join(videos_data_dir, item)

        pbar.update(1)

        if not os.path.isdir(item_path):
            continue        

        stats_path = os.path.join(item_path, "stats.csv")

        total_scanned += 1
        if not os.path.exists(stats_path):
            bad += 1
            #print 'No stats in %s' % item
            shutil.rmtree(item_path)

    
    print 'Removed %i folders from %i total' % (bad, total_scanned)


if __name__ == '__main__':
    remove_failed_data()
        