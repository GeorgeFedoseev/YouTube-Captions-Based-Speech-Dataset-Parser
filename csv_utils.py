import csv
from filelock import Timeout, FileLock

import const


def setup():
    open(const.VID_TO_PROCESS_CSV_FILE, 'a').close()
    open(const.VID_PROCESSING_CSV_FILE, 'a').close()
    open(const.VID_PROCESSED_CSV_FILE, 'a').close()
    open(const.VID_FAILED_CSV_FILE, 'a').close()

    open(const.KWDS_TO_SEARCH, 'a').close()
    open(const.KWDS_SEARCHED, 'a').close()    

    # restore not processed and clear processing
    not_fully_processed_last_time = get_column_csv(const.VID_PROCESSING_CSV_FILE, 0)
    clear_csv(const.VID_PROCESSING_CSV_FILE)
    append_column_to_csv(const.VID_TO_PROCESS_CSV_FILE, not_fully_processed_last_time)

def clear_csv(csv_path):
    with FileLock(csv_path + ".lock"):
        csv_writer = csv.writer(open(csv_path, "w+"))


def get_column_csv(csv_path, column_index):
    column = []
    with FileLock(csv_path + ".lock"):
        csv_reader = csv.reader(open(csv_path, "r+"))
        data = list(csv_reader)

        for row in data:
            if len(row) > column_index:
                column.append(row[column_index])
    return column

def append_column_to_csv(csv_path, column):
    
    with FileLock(csv_path + ".lock"):
        csv_writer = csv.writer(open(csv_path, "a+"))
        for val in column:
            csv_writer.writerow([val])

def write_column_to_csv(csv_path, column):
    clear_csv(csv_path)
    append_column_to_csv(csv_path, column)

def get_item_in_csv(csv_path, row_first_cell_val):
    with FileLock(csv_path + ".lock"):
        csv_reader = csv.reader(open(csv_path, "r+"))
        data = list(csv_reader)

        for row in data:
            if len(row) > 0 and row[0] == row_first_cell_val:
                return row
    return None

def is_item_in_csv(csv_path, item):
    get_item_in_csv(csv_path, item) != None


def put_item_to_csv(csv_path, row_list):
    if not is_item_in_csv(csv_path, row_list[0]):
        with FileLock(csv_path + ".lock"):
            csv_writer = csv.writer(open(csv_path, "a+"))
            csv_writer.writerow(row_list)



def pop_first_row_in_csv(csv_path):
    with FileLock(csv_path + ".lock"):
        first_row = None

        csv_reader = csv.reader(open(csv_path, "r+"))

        data = list(csv_reader)
        if len(data) > 0:
            first_row = data.pop(0)

        csv_writer = csv.writer(open(csv_path, "wb"))

        # write without first row
        for row in data:
            csv_writer.writerow(row)

    return first_row

def remove_row_by_first_val(csv_path, val):
    with FileLock(csv_path + ".lock"):
        csv_reader = csv.reader(open(csv_path, "r+"))
        data = list(csv_reader)   

        csv_writer = csv.writer(open(csv_path, "w"))
        # write without this row
        for row in data:
            if not (len(row) > 0 and row[0] == val):
                csv_writer.writerow(row)



# VIDEO SEARCHING
def get_keywords_to_process():
    row = pop_first_row_in_csv(const.KWDS_TO_SEARCH)
    if row != None and len(row) > 0:
        return row[0]
    return None

def put_keywords_to_processed(query):

    remove_keywords_from_all(query)
    put_item_to_csv(const.KWDS_SEARCHED, [query])

def remove_keywords_from_all(query):
    remove_row_by_first_val(const.KWDS_TO_SEARCH)
    remove_row_by_first_val(const.KWDS_SEARCHED)

# VIDEO PROCESSING

def put_video_to_pending(video_id):
    remove_video_from_all(video_id)
    put_item_to_csv(const.VID_TO_PROCESS_CSV_FILE, [video_id])

def put_video_to_processing(video_id):
    remove_video_from_all(video_id)
    put_item_to_csv(const.VID_PROCESSING_CSV_FILE, [video_id])

def put_video_to_failed(video_id, reason):
    remove_video_from_all(video_id)
    put_item_to_csv(const.VID_FAILED_CSV_FILE, [video_id, reason])


def put_video_to_processed(video_id):
    remove_video_from_all(video_id)
    put_item_to_csv(const.VID_PROCESSED_CSV_FILE, [video_id])

def remove_video_from_all(video_id):
    remove_row_by_first_val(const.VID_TO_PROCESS_CSV_FILE, video_id)
    remove_row_by_first_val(const.VID_PROCESSING_CSV_FILE, video_id)
    remove_row_by_first_val(const.VID_PROCESSED_CSV_FILE, video_id)
    remove_row_by_first_val(const.VID_FAILED_CSV_FILE, video_id)

def is_video_in_any_list(video_id):
    return is_item_in_csv(const.VID_TO_PROCESS_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_PROCESSING_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_PROCESSED_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_FAILED_CSV_FILE, 0)

def get_video_to_process():
    row = pop_first_row_in_csv(const.VID_TO_PROCESS_CSV_FILE)
    if row != None and len(row) > 0:
        return row[0]
    return None
