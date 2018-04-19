#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime

# yt api
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# csv processing
import const
from utils import csv_utils
from utils import queue_utils

# threading
from threading import Thread

from pprint import pprint


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

MAX_PAGES = 9999999999999999



def youtube_search(query, pageToken=None, page=0):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.

    #print 'GETTING PAGE %i of query %s' % (page, query)

    #if pageToken != None:
    # search_response = youtube.search().list(
    #     q=query,
    #     part="id,snippet",
    #     maxResults=50,
    #     type="video",
    #     #videoCaption="closedCaption",
    #     pageToken=pageToken,
    #     relevanceLanguage='ru'
    # ).execute()

    search_response = youtube.playlistItems().list(
        playlistId="PLSfXKSO5IqoSDOqBFwKB3AkU55xUWyJPm",
        maxResults=50,
        pageToken=pageToken,
        part='snippet,contentDetails'
    ).execute()
    

    videos = []
    
    for search_result in search_response.get("items", []):
        #pprint(search_result)
        #continue        
        videos.append(search_result["contentDetails"]["videoId"])
                

    print "found %i videos on page %i" % (len(videos), page)
    

    #print "Videos:\n", "\n".join(videos), "\n"

    if "nextPageToken" in search_response and page < MAX_PAGES and len(videos) > 0:
        #print search_response['nextPageToken']
        videos = videos + youtube_search(query, search_response['nextPageToken'], page+1)



    return videos


video_ids = youtube_search("особое мнение эхо москвы")
print "\n".join(video_ids)
#print "%i total videos" % len(video_ids)
