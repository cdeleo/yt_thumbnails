import os
import os.path
import re

BG_IMAGE_DIR = 'bg_images'
OUTPUT_DIR = 'output'

class Video(object):

  def __init__(self, video_id):
    self.video_id = video_id
    self.name = None
    self.title = None
    self.subtitle = None
    self.published = None

    # Derived data
    self.bg_image_path = None
    self.bg_image_mid = None
    self.output_path = None

  @classmethod
  def from_item(cls, item):
    video = cls(item['id']['videoId'])
    video.update(item)
    return video

  def update(self, item):
    if 'snippet' in item:
      self.name, self.title, self.subtitle = self._parse_video_title(
          item['snippet']['title'])
      self._load_derived_data()
    if 'status' in item:
      self.published = item['status']['privacyStatus'] == 'public'

  @staticmethod
  def _parse_video_title(raw_title):
    title, _, subtitle = raw_title.partition(' - ')
    if not subtitle:
      subtitle = None
    name = re.sub('[^a-zA-Z0-9 ]', '', title).lower().replace(' ', '_')
    return name, title, subtitle

  @staticmethod
  def _get_bg_image_data(name):
    simple_bg_image_path = os.path.join(BG_IMAGE_DIR, name + '.png')
    if os.path.exists(simple_bg_image_path):
      return simple_bg_image_path, None
    else:
      pattern = re.compile('%s_(\d+)\.png' % name)
      for filename in os.listdir(BG_IMAGE_DIR):
        match = pattern.match(filename)
        if match:
          return os.path.join(BG_IMAGE_DIR, match.group(0)), int(match.group(1))
    return None, None

  def _load_derived_data(self):
    self.bg_image_path, self.bg_image_mid = self._get_bg_image_data(self.name)
    self.output_path = os.path.join(OUTPUT_DIR, self.name + '.png')

  def __str__(self):
    return str(
        {'video_id': self.video_id,
         'name': self.name,
         'title': self.title,
         'subtitle': self.subtitle,
         'published': self.published})

def _finish_loading_videos(client, needed_parts, videos):
  video_map = {v.video_id: v for v in videos}
  video_ids = ','.join(v.video_id for v in videos)
  list_response = client.videos().list(
      id=video_ids, part=needed_parts).execute()
  for item in list_response['items']:
    video = video_map[item['id']]
    video.update(item)

def search_videos(client):  
  search_response = client.search().list(
      type='video', forMine=True, part='snippet', maxResults=25).execute()
  videos = []
  for item in search_response['items']:
    video = Video.from_item(item)
    if video.name:
      videos.append(video)
  _finish_loading_videos(client, 'status', videos)
  return videos

def list_videos(client, video_ids):
  videos = [Video(video_id) for video_id in video_ids]
  _finish_loading_videos(client, 'snippet,status', videos)
  return videos
