import argparse
import auth
import os.path
import process_videos
import resources
import thumbnails
import video

parser = argparse.ArgumentParser(description='Generate YouTube thumbnails.')
parser.add_argument(
    '--videos', metavar='video_id,...', type=str,
    help='force processing for a list of videos')
args = parser.parse_args()

def process_video(client, video):
  if not os.path.exists(video.output_path):
    print '  Generating...'
    with open(video.bg_image_path) as bg_image_file:
      with open(video.output_path, 'w') as out_file:
        thumbnails.generate_thumbnail(
            bg_image_file, video.title, video.subtitle, out_file)
    print '  done.'

    print '  Uploading...'
    client.thumbnails().set(
        videoId=video.video_id, media_body=video.output_path).execute()
    print '  done.'

  if not video.published:
    print '  Publishing...'
    resource = resources.build_resource(
        {'id': video.video_id, 'status.privacyStatus': 'public'})
    client.videos().update(body=resource, part='status').execute()
    print '  done.'

def main():
  client = auth.get_authenticated_client()

  if args.videos:
    videos = video.list_videos(client, args.videos.split(','))
  else:
    videos = [v for v in video.search_videos(client)
              if v.subtitle and not v.published]

  processor = process_videos.VideoProcessor()
  processor.process(client, videos, process_video)
  processor.print_summary()

if __name__ == '__main__':
  main()
