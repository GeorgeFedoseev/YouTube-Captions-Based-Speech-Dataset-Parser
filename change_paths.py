import os
import csv

import const

import sys

from filelock import Timeout, FileLock

def change_paths(find, replace):
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    export_csvs_dir = os.path.join(curr_dir_path, "export-sets/")

    for item in os.listdir(export_csvs_dir):
        csv_path = os.path.join(export_csvs_dir, item)

        #print 'process '+csv_path
        #print csv_path.split(".")[-1]
        if csv_path.split(".")[-1] != "csv":
            continue        


        

        f = open(csv_path, "r")
        parts = list(csv.reader(f))
        f.close()

        f = open(csv_path, "w")
        writer = csv.writer(f)
        for row in parts:
            row[0] = row[0].replace(find, replace)
            writer.writerow(row)
            
        f.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('USAGE: python change_paths.py <find_path> <replacement>')
    else:    
        change_paths(sys.argv[1], sys.argv[2])