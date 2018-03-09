#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import re

def remove_latin_chars():
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    count = 0
    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue        

        parts_path = os.path.join(item_path, "parts.csv")

        if not os.path.exists(parts_path):
            continue

        f = open(parts_path, "r")
        parts = list(csv.reader(f))
        f.close()

        f = open(parts_path, "w")
        writer = csv.writer(f)

        
        for row in parts:
            if len(row) < 3:
                continue

            cleared_text = re.sub(u'[^а-яА-Я ]+', '', row[2], re.UNICODE)
            row[2] = cleared_text
            count+=1
                     
            writer.writerow(row)
        f.close()

    print 'processed '+str(count)+' samples'

if __name__ == '__main__':
    remove_latin_chars()