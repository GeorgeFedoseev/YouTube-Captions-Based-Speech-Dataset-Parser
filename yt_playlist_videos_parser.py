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



def get_videos(playlistId, pageToken=None, page=0):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    search_response = youtube.playlistItems().list(
        playlistId=playlistId,
        maxResults=50,
        pageToken=pageToken,
        part='snippet,contentDetails'
    ).execute()
    

    videos = []
    
    for search_result in search_response.get("items", []):
        #pprint(search_result)
        #print search_result["snippet"]["title"]
        #continue        
        videos.append((search_result["contentDetails"]["videoId"], search_result["snippet"]["title"]))
                

    print "found %i videos on page %i" % (len(videos), page)
    

    #print "Videos:\n", "\n".join(videos), "\n"

    if "nextPageToken" in search_response and page < MAX_PAGES and len(videos) > 0:
        #print search_response['nextPageToken']
        videos = videos + get_videos(playlistId, search_response['nextPageToken'], page+1)


    return videos


if __name__ == "__main__":
    if len(sys.argv) > 1:        
        videos = get_videos(sys.argv[1])
        for v in videos:
            print '"%s", "%s"' % (v[0], v[1]) 
    else:
        print "Usage: yt_playlist_videos_parser.py <playlistId>"



