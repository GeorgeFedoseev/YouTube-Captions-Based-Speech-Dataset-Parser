#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

import csv
import csv_utils
import time
import datetime

from threading import Thread

import sys
reload(sys)
sys.setdefaultencoding('utf8')


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAKWy4ewu5VraFIFvKcIgl1lWDSa51Ksnk"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MAX_PAGES = 3

is_searching = False


def start_searcher_thread():
    print 'starting searcher thread'
    thr = Thread(target=searcher_thread_loop)
    thr.daemon = True
    thr.start()

    return thr

def searcher_thread_loop():
    global is_searching

    while True:
        with FileLock(const.VID_TO_PROCESS_CSV_FILE+".lock"):
            stats_pending_videos_count = len(list(csv.reader(open(const.VID_TO_PROCESS_CSV_FILE, "r"))))

            if stats_pending_videos_count > 100:
                # if have enough videos - dont search
                is_searching = False
                time.sleep(15)
                continue



        print('GETTING KEYWORDS... ')
        start_time = time.time()

        query = csv_utils.get_keywords_to_process()

        print("GOT KEYWORDS, took %s" % datetime.timedelta(seconds=round(time.time() - start_time)))



        if query == None:
            #print 'all search queries processed. waiting 5 seconds to check again...'
            is_searching = False
            time.sleep(5)
            continue

        is_searching = True

        if csv_utils.is_query_processed(query):
            print 'query "%s" is already processed' % query
            continue

        print 'searching query '+query
        video_ids = youtube_search(query)
        print 'found '+str(len(video_ids))+' videos'

        videos_put = 0

        videos_to_add = []
        # add only video ids that dont exist in video csvs
        for video_id in video_ids:
            if not csv_utils.is_video_in_any_list(video_id):
                print 'put video %s' % video_id
                videos_to_add.append(video_id)
                videos_put += 1

        csv_utils.put_videos_to_pending(videos_to_add)
        print ('added %i videos to pending' % videos_put)


        print('mark query as processed')
        # mark processed
        csv_utils.put_keywords_to_processed(query)

        print('sleep before next query')
        # sleep
        time.sleep(5)


def youtube_search(query, pageToken=None, page=0):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.

    print 'GETTING PAGE %i of query %s' % (page, query)

    #if pageToken != None:
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=50,
        type="video",
        videoCaption="closedCaption",
        pageToken=pageToken,
        relevanceLanguage='ru'
    ).execute()
    

    videos = []
    

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result["id"]["videoId"])
        

    print "Videos:\n", "\n".join(videos), "\n"

    if "nextPageToken" in search_response and page < MAX_PAGES:
        print search_response['nextPageToken']
        videos = videos + youtube_search(query, search_response['nextPageToken'], page+1)



    return videos


#youtube_search("арбуз")
