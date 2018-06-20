import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import time
from utils import stats_util
from utils import queue_utils
from threading import Thread
from vad_first_parser import process_video

import const

from utils.file_utils import ensure_dir
from utils import cli_dependency_check


#displayed_no_videos_to_process = False

def video_parser_thread_loop():
    #global displayed_no_videos_to_process

    while True:       

        #print "getting video id to parse..."
        video_id = queue_utils.get_video_to_process()

        #print 'got video id %s' % video_id
        if queue_utils.is_video_processed_or_failed(video_id):
            print("VIDEO %s is already processed" % video_id)

        if not video_id:
            #if not displayed_no_videos_to_process:
                #print 'no videos to parse - wait 5 seconds...'
                #displayed_no_videos_to_process = True
            #time.sleep(5)
            #continue
            return

        #displayed_no_videos_to_process = False

        # start video processing
        queue_utils.put_video_to_processing(video_id)

        try:
            process_video(video_id)
            queue_utils.put_video_to_processed(video_id)
        except Exception as e:
            print('failed to process video ' + video_id + ': ' + str(e))
            error_type = str(e)
            queue_utils.put_video_to_failed(video_id, error_type)

        time.sleep(0.2)

        

def start_parsing(threads_num):
    
    try:        

        ensure_dir(const.VIDEO_DATA_DIR)       

        video_parser_threads = []
        # start parsing threads

        for i in range(0, threads_num):
            #print 'start parsing thread ' + str(i)
            thr = Thread(target=video_parser_thread_loop)
            thr.daemon = True
            thr.start()
            video_parser_threads.append(thr)

        # wait for threads
        while True: 
            if not any([thr.isAlive() for thr in video_parser_threads]):
                break
            time.sleep(5)

    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting threads.\n'

    print "DONE"

    stats_util.show_global_stats()

if __name__ == "__main__":


    _threads_number = 20
    try:    
        _threads_number = int(sys.argv[sys.argv.index("--threads-num")+1])
    except:
        pass

    
    cli_dependency_check.is_ffmpeg_installed()
    cli_dependency_check.is_ytdownloader_installed()

    print("Start parsing with %i threads" % _threads_number)
    start_parsing(threads_num=_threads_number)
