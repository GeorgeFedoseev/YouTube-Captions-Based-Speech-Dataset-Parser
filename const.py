import os

curr_dir_path = os.path.dirname(os.path.realpath(__file__))

VIDEO_DATA_DIR = os.path.join(curr_dir_path, "data/")

csv_data_path = os.path.join(curr_dir_path, "csv_data/")

VID_TO_PROCESS_CSV_FILE = os.path.join(csv_data_path, "videos_to_process.csv")
VID_PROCESSING_CSV_FILE = os.path.join(csv_data_path, "videos_processing.csv")
VID_PROCESSED_CSV_FILE = os.path.join(csv_data_path, "videos_processed.csv")
VID_FAILED_CSV_FILE = os.path.join(csv_data_path, "videos_failed_to_process.csv")

KWDS_TO_SEARCH = os.path.join(csv_data_path, "keywords_to_search.csv")
KWDS_SEARCHED = os.path.join(csv_data_path, "keywords_done.csv")
