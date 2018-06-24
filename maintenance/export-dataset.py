# *= coding: utf-8 *=
import os
import csv

import sys
curr_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(curr_dir_path, os.path.pardir))

reload(sys)
sys.setdefaultencoding("utf-8")

from utils import csv_utils
import random
import shutil
from multiprocessing.pool import ThreadPool, Pool


from utils.text_utils import clean_transcript_text
from utils.cli_dependency_check import is_ffmpeg_installed

# progressbar
from tqdm import tqdm

import time
import signal


pbar = None


def export(target_folder, skip_audio=False, minimum_words_count=1, DATASET_NAME = "yt-subs", NUM_THREADS = 8, RANDOM_SEED=42):
    global pbar

    is_ffmpeg_installed()

    print 'exporting to dir %s ' % target_folder
       
    print "skip_audio: %s" % str(skip_audio)
    print "minimum_words_count: %s" % str(minimum_words_count)
    print "num_threads: %i" % NUM_THREADS
    print "dataset_name: %s" % DATASET_NAME
    print "random_seed: %i" % RANDOM_SEED

    curr_dir_path = os.getcwd()
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

        # remove duplicates
        parts = reduce(lambda x,y: x+[y] if not y in x else x, parts,[])

        # filter not in alphabet symbols        
        parts = [[p[0], p[1], clean_transcript_text(p[2], full=True)] for p in parts]

        # filter transcripts less than minimum_words_count words
        parts = [p for p in parts if len(str(p[2]).split()) >= minimum_words_count]



        all_rows.extend(parts)





    csv_utils.write_rows_to_csv(export_all_csv_path, all_rows)


    all_count = len(all_rows)

    if all_count < 20:
        raise Exception('too small dataset < 20')

    # shuffle 
    random.seed(RANDOM_SEED)
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

    print 'total: %i samples' % len(all_rows)
    print 'devided train:dev:test = '+str(len(train_rows))+':'+str(len(dev_rows))+':'+str(len(test_rows))


    def get_audio_rel_path(abs_path):
        return '/'.join(abs_path.split('/')[-4:])

    copy_jobs = []

    # rename audio files paths
    for row in train_rows:
        old_path = get_audio_rel_path(row[0])
        #print old_path
        filename = os.path.basename(old_path)
        new_path =  os.path.join(export_train_dir_path, filename)       
        if (not os.path.exists(new_path)) or os.path.getsize(new_path) != int(row[1]):
            copy_jobs.append((old_path, new_path))

        row[0] = new_path


    for row in dev_rows:
        old_path = get_audio_rel_path(row[0])
        filename = os.path.basename(old_path)
        new_path =  os.path.join(export_dev_dir_path, filename)       
        if (not os.path.exists(new_path)) or os.path.getsize(new_path) != int(row[1]):
            copy_jobs.append((old_path, new_path))

        row[0] =  os.path.join(export_dev_dir_path, filename)        

    for row in test_rows:
        old_path = get_audio_rel_path(row[0])
        filename = os.path.basename(old_path)
        new_path =  os.path.join(export_test_dir_path, filename)       
        if (not os.path.exists(new_path)) or os.path.getsize(new_path) != int(row[1]):
            copy_jobs.append((old_path, new_path))

        row[0] =  os.path.join(export_test_dir_path, filename)        


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


    if not skip_audio:
        # write audio files
        pbar = tqdm(total=len(copy_jobs))
        

        
        pool = Pool(NUM_THREADS)
        pool.map_async(process_audio_file, copy_jobs).get(99999999999999999999999999)
        

        # check if all jobs has been copied
        check_errors = 0
        for job in copy_jobs:
            if not os.path.exists(job[1]):
                check_errors += 1
                print("Bad copy, file wasnt copied: %s -> %s " % (job[0], job[1]))
            if os.path.getsize(job[0]) != os.path.getsize(job[1]):
                check_errors += 1
                print("Bad copy, filesize doesnt match: %s -> %s " % (job[0], job[1]))
        if check_errors > 0:
            print("ERROR: not all (%i) files were copied to destination correctly!" % check_errors)
        else:
            print("All files copied correctly")

    

def process_audio_file(job):
    global pbar

    from_path = job[0]
    to_path = job[1]
    shutil.copyfile(from_path, to_path)    
    pbar.update(1)
    time.sleep(0.05)

if __name__ == '__main__':
    # defaults
    minimum_words_count = 1
    dataset_name = "yt-subs"
    num_threads = 10
    random_seed = 42

    if len(sys.argv) < 2:
        print('USAGE: python export-dataset.py <export_dir_path> [--skip-audio] [--min-words <int:%i>] \
[--name <string:%s>] [--num_threads <int:%i>] [--random-seed <int:%i>]' % (minimum_words_count, dataset_name, num_threads, random_seed))
    else:            
        try:
            minimum_words_count = int(sys.argv[sys.argv.index("--min-words")+1])
        except:
            pass        
        try:
            dataset_name = str(sys.argv[sys.argv.index("--name")+1])
        except:
            pass        
        try:
            num_threads = int(sys.argv[sys.argv.index("--num-threads")+1])
        except:
            pass        
        try:
            random_seed = int(sys.argv[sys.argv.index("--random-seed")+1])
        except:
            pass

        export(sys.argv[1],
               skip_audio=("--skip-audio" in str(sys.argv)),
               minimum_words_count = minimum_words_count,
               DATASET_NAME=dataset_name,
               NUM_THREADS=num_threads,
               RANDOM_SEED=random_seed
               )



        

