import os

curr_dir_path = os.path.dirname(os.path.realpath(__file__))

TO_PROCESS_CSV_FILE = os.path.join(curr_dir_path, "videos_to_process.csv")
PROCESSING_CSV_FILE = os.path.join(curr_dir_path, "videos_processing.csv")
PROCESSED_CSV_FILE = os.path.join(curr_dir_path, "videos_processed.csv")
FAILED_CSV_FILE = os.path.join(curr_dir_path, "videos_failed_to_process.csv")
