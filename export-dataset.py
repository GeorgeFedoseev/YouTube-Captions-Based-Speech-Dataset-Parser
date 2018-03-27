import os
import csv
import csv_utils

import random

import subs_utils

import shutil

from multiprocessing.pool import ThreadPool

import sys

from tqdm import tqdm # progressbar

NUM_THREADS = 8
DATASET_NAME = "yt-subs"

def export(target_folder):

    target_folder = os.path.abspath(os.path.expanduser(target_folder))

    print 'exporting to dir %s ' % target_folder

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    export_all_csv_path = os.path.join(target_folder, DATASET_NAME+"-all.csv")
    export_train_csv_path = os.path.join(target_folder, DATASET_NAME+"-train.csv")
    export_dev_csv_path = os.path.join(target_folder, DATASET_NAME+"-dev.csv")
    export_test_csv_path = os.path.join(target_folder, DATASET_NAME+"-test.csv")

    export_vocabulary_txt_path = os.path.join(target_folder, DATASET_NAME+"-vocabulary.txt")

    # make folders for audio
    export_train_dir_path = os.path.join(target_folder, DATASET_NAME+"-train")
    if not os.path.exists(export_train_dir_path):
        os.makedirs(export_train_dir_path)

    export_dev_dir_path = os.path.join(target_folder, DATASET_NAME+"-dev")
    if not os.path.exists(export_dev_dir_path):
        os.makedirs(export_dev_dir_path)

    export_test_dir_path = os.path.join(target_folder, DATASET_NAME+"-test")
    if not os.path.exists(export_test_dir_path):
        os.makedirs(export_test_dir_path)


    all_rows = []

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue

        # check if folder finished processing
        stats_path = os.path.join(item_path, "stats.csv")        
        if not os.path.exists(stats_path):
            continue

        parts_csv_path = os.path.join(item_path, "parts.csv")

        if not os.path.exists(parts_csv_path):
            continue

        parts = csv_utils.read_all(parts_csv_path)

        all_rows.extend(parts)





    csv_utils.write_rows_to_csv(export_all_csv_path, all_rows)


    all_count = len(all_rows)

    if all_count < 20:
        raise Exception('too small dataset < 20')

    # shuffle 

    random.shuffle(all_rows)

    # split in 3 groups train:dev:test 80:10:10
    train_rows = []
    dev_rows = []
    test_rows = []

    train_count = int(all_count*0.8)
    dev_count = int(all_count*0.1)


    all_rest = list(all_rows)
    train_rows = all_rest[:train_count]
    del all_rest[:train_count]
    dev_rows = all_rest[:dev_count]
    del all_rest[:dev_count]
    test_rows = all_rest

    print 'devided train:dev:test = '+str(len(train_rows))+':'+str(len(dev_rows))+':'+str(len(test_rows))


    def get_audio_rel_path(abs_path):
        return '/'.join(abs_path.split('/')[-4:])

    copy_jobs = []

    # rename audio files paths
    for row in train_rows:
        old_path = get_audio_rel_path(row[0])
        print old_path
        filename = os.path.basename(old_path)
        new_path =  os.path.join(export_train_dir_path, filename)       
        copy_jobs.append((old_path, new_path))

        row[0] = new_path


    for row in dev_rows:
        old_path = get_audio_rel_path(row[0])
        filename = os.path.basename(old_path)
        new_path =  os.path.join(export_dev_dir_path, filename)       
        copy_jobs.append((old_path, new_path))

        row[0] =  os.path.join(export_dev_dir_path, filename)        

    for row in test_rows:
        old_path = get_audio_rel_path(row[0])
        filename = os.path.basename(old_path)
        new_path =  os.path.join(export_test_dir_path, filename)       
        copy_jobs.append((old_path, new_path))

        row[0] =  os.path.join(export_test_dir_path, filename)        


    pbar = tqdm(total=len(copy_jobs))

    def copy_audio_file(job):
        #print 'copy %s -> %s' % job
        shutil.copyfile(job[0], job[1])
        pbar.update(1)


    pool = ThreadPool(NUM_THREADS)
    pool.map(copy_audio_file, copy_jobs)

    pbar.close()

    # write sets csvs
    header = ['wav_filename', 'wav_filesize', 'transcript']

    csv_utils.write_rows_to_csv(export_train_csv_path, [header])
    csv_utils.write_rows_to_csv(export_dev_csv_path, [header])
    csv_utils.write_rows_to_csv(export_test_csv_path, [header])

    csv_utils.append_rows_to_csv(export_train_csv_path, train_rows)
    csv_utils.append_rows_to_csv(export_dev_csv_path, dev_rows)
    csv_utils.append_rows_to_csv(export_test_csv_path, test_rows)


    # export vocabulary
    vocabulary = open(export_vocabulary_txt_path, "w")   
    vocabulary.writelines([x[2]+"\n" for x in all_rows])
    vocabulary.close()



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('USAGE: python export-dataset.py <export_dir_path>')
    else:    
        export(sys.argv[1])



        

