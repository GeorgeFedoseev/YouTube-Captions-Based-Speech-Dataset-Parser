from csv_utils import *
import const

import shutil

def setup():
    #print('csv utils setup - start')
    open(const.VID_TO_PROCESS_CSV_FILE, 'a').close()
    open(const.VID_PROCESSING_CSV_FILE, 'a').close()
    open(const.VID_PROCESSED_CSV_FILE, 'a').close()
    open(const.VID_FAILED_CSV_FILE, 'a').close()

    open(const.KWDS_TO_SEARCH, 'a').close()
    open(const.KWDS_SEARCHED, 'a').close()    

    # restore not processed and clear processing
    not_fully_processed_last_time = get_column_csv(const.VID_PROCESSING_CSV_FILE, 0)

    # remove folders
    for yt_id in not_fully_processed_last_time:
        maybe_remove_video_dir(yt_id)

    #print("restore not fully processed: %i" % len(not_fully_processed_last_time))    
    clear_csv(const.VID_PROCESSING_CSV_FILE)
    #print('csv utils setup 1')
    prepend_column_to_csv(const.VID_TO_PROCESS_CSV_FILE, not_fully_processed_last_time)


def maybe_remove_video_dir(yt_id):
    dir_path = os.path.join(const.VIDEO_DATA_DIR, yt_id)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


# VIDEO SEARCHING
def get_keywords_to_process():
    row = pop_first_row_in_csv(const.KWDS_TO_SEARCH)
    if row != None and len(row) > 0:
        return row[0]
    return None

def put_keywords_to_processed(query):
    remove_keywords_from_all(query)
    add_row_to_csv(const.KWDS_SEARCHED, [query])

def is_query_processed(query):
    return is_item_in_csv(const.KWDS_SEARCHED, 0)

def remove_keywords_from_all(query):
    remove_row_by_first_val(const.KWDS_TO_SEARCH, query)
    remove_row_by_first_val(const.KWDS_SEARCHED, query)

# VIDEO PROCESSING

def put_video_to_pending(video_id):
    #print("put_video_to_pending")
    if is_video_processed_or_failed(video_id):
        return
    remove_video_from_processing(video_id)
    add_row_to_csv(const.VID_TO_PROCESS_CSV_FILE, [video_id])

def put_videos_to_pending(video_ids):    
    #print("put_videos_to_pending %i" %len(video_ids))
    append_column_to_csv(const.VID_TO_PROCESS_CSV_FILE, video_ids)

def put_video_to_processing(video_id):
    remove_video_from_pending(video_id)
    add_row_to_csv(const.VID_PROCESSING_CSV_FILE, [video_id])

def put_video_to_failed(video_id, reason):
    remove_video_from_processing(video_id)
    add_row_to_csv(const.VID_FAILED_CSV_FILE, [video_id, reason])


def put_video_to_processed(video_id):
    remove_video_from_processing(video_id)
    add_row_to_csv(const.VID_PROCESSED_CSV_FILE, [video_id])

def remove_video_from_pending(video_id):
    remove_row_by_first_val(const.VID_TO_PROCESS_CSV_FILE, video_id)

def remove_video_from_processing(video_id):
    remove_row_by_first_val(const.VID_PROCESSING_CSV_FILE, video_id)


def is_video_processed_or_failed(video_id):
    return is_item_in_csv(const.VID_PROCESSED_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_FAILED_CSV_FILE, 0)

def is_video_in_any_list(video_id):
    #print("check is_video_in_any_list %s" % video_id)
    return is_item_in_csv(const.VID_TO_PROCESS_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_PROCESSING_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_PROCESSED_CSV_FILE, 0) \
    or is_item_in_csv(const.VID_FAILED_CSV_FILE, 0)

def get_video_to_process():
    row = pop_first_row_in_csv(const.VID_TO_PROCESS_CSV_FILE)
    if row != None and len(row) > 0:
        return row[0]
    return None

