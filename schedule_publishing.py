import auth
import datetime
import process_videos
import schedule
import video

PUBLISH_TIME = datetime.time(21)
PUBLISH_DAYS = [0, 2, 4]

def find_staged_videos(client):
  staged_videos = []
  stop_video = None
  page_token = None
  while True:
    videos, page_token = video.search_videos(client, page_token)
    for v in videos:
      if not v.subtitle:
        continue
      elif v.is_staged():
        staged_videos.append(v)
      else:
        stop_video = v
        break
    if stop_video or not page_token:
      break
  return reversed(staged_videos), stop_video

def schedule_video(client, v, scheduler):
  status = v.get_part('status')
  status['privacyStatus'] = 'private'
  status['publishAt'] = scheduler.get_next().strftime(video.TIME_FORMAT)
  client.videos().update(
      body={'id': v.video_id, 'status': status}, part='status').execute()

def main():
  client = auth.get_authenticated_client()
  staged_videos, stop_video = find_staged_videos(client)
  staged_videos = list(staged_videos)
  staged_videos = [staged_videos[0]]

  if stop_video:
    start_time = stop_video.publish_time()
  else:
    start_time = datetime.datetime.utcnow()
  scheduler = schedule.Scheduler(start_time, PUBLISH_TIME, PUBLISH_DAYS)

  processor = process_videos.VideoProcessor()
  processor.process(
      client, staged_videos, lambda c, v, s=scheduler: schedule_video(c, v, s))
  processor.print_summary()

if __name__ == '__main__':
  main()
