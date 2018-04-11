import sys
sys.path.insert(0,os.getcwd()) 

import os
import csv

import const



import shutil

import subprocess

from glob import glob

def remove_extra_data():
    curr_dir_path = os.getcwd()
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    total_scanned = 0
    removed = 0

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue        

        total_scanned += 1

        stats_path = os.path.join(item_path, "stats.csv")

        # remove extra files if found stats file        
        
        if os.path.exists(stats_path):
            for path in glob(os.path.join(item_path, "*.lock")):
                os.remove(path)
                removed += 1
            for path in glob(os.path.join(item_path, "audio.*")):
                os.remove(path)
                removed += 1
            for path in glob(os.path.join(item_path, "*.vtt")):
                os.remove(path)
                removed += 1

            
            
            

    
    print 'Removed %i extra files from %i folders' % (removed, total_scanned)


if __name__ == '__main__':
    remove_extra_data()
        