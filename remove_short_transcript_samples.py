import os
import csv

import const

import sys

from filelock import Timeout, FileLock

def remove_short_transcripts(csv_path):
   
    if csv_path.split(".")[-1] != "csv":
        print 'ERROR please specify path to csv'
        return        


    

    f = open(csv_path, "r")
    parts = list(csv.reader(f))
    f.close()

    f = open(csv_path, "w")
    writer = csv.writer(f)

    total_count = 0
    removed_count = 0
    for i, row in enumerate(parts):        
        if i == 0:
            writer.writerow(row)
            continue

        total_count+=1
        print len(row[2])
        if len(row[2]) > 70: 
            writer.writerow(row)
        else:
            removed_count+=1
        
    f.close()

    print 'removed '+str(removed_count)+' samples ('+str(float(removed_count)/total_count*100)+'%)'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        remove_short_transcripts(sys.argv[1])
    else:
        print 'USAGE: script.py <path_to_csv>'
        