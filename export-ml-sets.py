import os
import csv
import csv_utils

import random

import subs_utils

def export():

    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    export_sets_dir_path = os.path.join(curr_dir_path, "export-sets/")
    if not os.path.exists(export_sets_dir_path):
        os.makedirs(export_sets_dir_path)

    export_all_csv_path = os.path.join(export_sets_dir_path, "all.csv")
    export_train_csv_path = os.path.join(export_sets_dir_path, "yt-train.csv")
    export_dev_csv_path = os.path.join(export_sets_dir_path, "yt-dev.csv")
    export_test_csv_path = os.path.join(export_sets_dir_path, "yt-test.csv")

    export_vocabulary_txt_path = os.path.join(export_sets_dir_path, "vocabulary.txt")


    all_rows = []

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue

        parts_csv_path = os.path.join(item_path, "parts.csv")
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


    # write sets
    header = ['wav_filename', 'wav_filesize', 'transcript']

    csv_utils.write_rows_to_csv(export_train_csv_path, [header])
    csv_utils.write_rows_to_csv(export_dev_csv_path, [header])
    csv_utils.write_rows_to_csv(export_test_csv_path, [header])

    csv_utils.append_rows_to_csv(export_train_csv_path, train_rows)
    csv_utils.append_rows_to_csv(export_dev_csv_path, dev_rows)
    csv_utils.append_rows_to_csv(export_test_csv_path, test_rows)


    # export vocabulary
    vocabulary = open(export_vocabulary_txt_path, "w")   
    vocabulary.writelines([subs_utils.clear_subtitle_text(x[2])+"\n" for x in all_rows])
    vocabulary.close()

export()

        

