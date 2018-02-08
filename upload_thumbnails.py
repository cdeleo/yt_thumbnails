import argparse
import auth
import descriptions
import os.path
import process_videos
import resources
import thumbnails
import video

parser = argparse.ArgumentParser(description='Generate YouTube thumbnails.')
parser.add_argument(
    '--videos', metavar='video_id,...', type=str,
    help='force processing for a list of videos')
parser.add_argument(
    '--nopublish', action='store_false',
    help='Only update videos, do not publish')
args = parser.parse_args()

def process_video(client, video):
  parts_to_update = []
  resource = {'id': video.video_id}

  if not os.path.exists(video.output_path):
    print '  Generating thumbnail...'
    with open(video.bg_image_path) as bg_image_file:
      with open(video.output_path, 'w') as out_file:
        thumbnails.generate_thumbnail(
            bg_image_file, video.title, video.subtitle, out_file)
    print '  done.'

    print '  Uploading...'
    client.thumbnails().set(
        videoId=video.video_id, media_body=video.output_path).execute()
    print '  done.'

    print '  Generating description...'
    snippet = video.get_part('snippet')
    snippet['description'] = descriptions.get(video.bg_image_mid)
    resource['snippet'] = snippet
    parts_to_update.append('snippet')
    print '  done.'

  if not args.nopublish and not video.is_published():
    print '  Setting publishing...'
    resource.update(
        resources.build_resource({'status.privacyStatus': 'public'}))
    parts_to_update.append('status')
    print '  done.'

  if parts_to_update:
    print '  Updating...'
    client.videos().update(
        body=resource, part=','.join(parts_to_update)).execute()
    print '  done.'

def main():
  client = auth.get_authenticated_client()

  if args.videos:
    videos = video.list_videos(client, args.videos.split(','))
  else:
    videos = [v for v in video.search_videos(client)[0]
              if v.subtitle and v.is_staged()]

  processor = process_videos.VideoProcessor()
  processor.process(client, videos, process_video)
  processor.print_summary()

if __name__ == '__main__':
  main()
