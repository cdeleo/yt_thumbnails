import os
import sys
sys.path.insert(0, os.getcwd())

import auth
import descriptions
import process_videos
import video

def filter_video(video):
  return video.subtitle and video.is_published() and not video.description

def process_video(client, video):
  snippet = video.get_part('snippet')
  snippet['description'] = descriptions.get(video.bg_image_mid)
  client.videos().update(
      part='snippet',
      body={'id': video.video_id, 'snippet': snippet}).execute()

def main():
  client = auth.get_authenticated_client()
  processor = process_videos.VideoProcessor()

  page_token = None
  while True:
    videos, page_token = video.search_videos(client, page_token)
    stop = processor.process(
        client, videos, process_video, filter_video=filter_video)
    if stop or not page_token:
      break
  processor.print_summary()

if __name__ == '__main__':
  main()
