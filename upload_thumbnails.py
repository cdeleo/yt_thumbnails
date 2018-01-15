import argparse
import googleapiclient.discovery
import os.path
import pickle
import re
import resources
import thumbnails
import traceback

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = 'client_id.json'
CREDENTIALS_FILE = 'credentials.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

parser = argparse.ArgumentParser(description='Generate YouTube thumbnails.')
parser.add_argument(
    '--videos', metavar='video_id,...', type=str,
    help='force processing for a list of videos')
args = parser.parse_args()

def get_bg_image_path(name):
  return os.path.join('bg_images', name + '.png')

def get_output_path(name):
  return os.path.join('output', name + '.png')

def get_credentials():
  if not os.path.exists(CREDENTIALS_FILE):
    return None
  with open(CREDENTIALS_FILE) as f:
    return pickle.load(f)

def put_credentials(credentials):
  with open(CREDENTIALS_FILE, 'w') as f:
    pickle.dump(credentials, f)

def get_authenticated_client():
  credentials = get_credentials()
  if not credentials:
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    put_credentials(credentials)
  return googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

class Video(object):

  def __init__(self, video_id):
    self.video_id = video_id
    self.name = None
    self.title = None
    self.subtitle = None
    self.published = None

  @classmethod
  def from_item(cls, item):
    video = cls(item['id']['videoId'])
    video.update(item)
    return video

  def update(self, item):
    if 'snippet' in item:
      self.name, self.title, self.subtitle = self._parse_video_title(
          item['snippet']['title'])
    if 'status' in item:
      self.published = item['status']['privacyStatus'] == 'public'

  @staticmethod
  def _parse_video_title(raw_title):
    title, _, subtitle = raw_title.partition(' - ')
    if not subtitle:
      subtitle = None
    name = re.sub('[^a-zA-Z0-9 ]', '', title).lower().replace(' ', '_')
    return name, title, subtitle

  def __str__(self):
    return str(
        {'video_id': self.video_id,
         'name': self.name,
         'title': self.title,
         'subtitle': self.subtitle,
         'published': self.published})

def list_videos(client, video_ids=None):
  if video_ids is None:
    # Search videos
    search_response = client.search().list(
        type='video', forMine=True, part='snippet', maxResults=25).execute()
    videos = {}
    for item in search_response['items']:
      video = Video.from_item(item)
      if video.name:
        videos[video.video_id] = video
    needed_parts = 'status'
  else:
    videos = {video_id: Video(video_id) for video_id in video_ids}
    needed_parts = 'snippet,status'

  # List videos
  video_ids = ','.join(v.video_id for v in videos.itervalues())
  list_response = client.videos().list(
      id=video_ids, part=needed_parts).execute()
  for item in list_response['items']:
    video = videos[item['id']]
    video.update(item)

  return videos.values()

def process_video(client, video):
  print 'Processing %s...' % video.name

  thumbnail_path = get_output_path(video.name)
  if not os.path.exists(thumbnail_path):
    print '  Generating...'
    with open(get_bg_image_path(video.name)) as bg_image_file:
      with open(get_output_path(video.name), 'w') as out_file:
        thumbnails.generate_thumbnail(
            bg_image_file, video.title, video.subtitle, out_file)
    print '  done.'

    print '  Uploading...'
    client.thumbnails().set(
        videoId=video.video_id, media_body=thumbnail_path).execute()
    print '  done.'

  if not video.published:
    print '  Publishing...'
    resource = resources.build_resource(
        {'id': video.video_id, 'status.privacyStatus': 'public'})
    client.videos().update(body=resource, part='status').execute()
    print '  done.'

  print 'done.'

def render_number_string(base_str, n, overrides=None):
  if overrides:
    for override_n, override_str in overrides:
      if n == override_n:
        return override_str % n
  return base_str % n

def main():
  client = get_authenticated_client()

  if args.videos:
    videos = list_videos(client, args.videos.split(','))
  else:
    videos = [v for v in list_videos(client) if v.subtitle and not v.published]

  successes = set()
  failures = {}
  for video in videos:
    try:
      process_video(client, video)
    except:
      print 'failed!'
      failures[video.name] = traceback.format_exc()
    else:
      successes.add(video.name)

  print
  print render_number_string(
      '%d successes.', len(successes), [(1, '%d success.')])
  print render_number_string(
      '%d failures:', len(failures), [(0, '%d failures.'), (1, '%d failure:')])
  for name, e in failures.iteritems():
    print '%s:' % name
    print '  %s' % e
    print

if __name__ == '__main__':
  main()
