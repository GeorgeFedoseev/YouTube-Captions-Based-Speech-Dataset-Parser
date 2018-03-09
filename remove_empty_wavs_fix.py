import os
import csv

import const

from filelock import Timeout, FileLock

def remove_empty_wavs():
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

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
            if len(row) < 2:
                continue
            if int(row[1]) > 1000:
                writer.writerow(row)
            else:
                print('remove '+row[0])
        f.close()

if __name__ == '__main__':
    remove_empty_wavs()