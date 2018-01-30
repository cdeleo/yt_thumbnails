import traceback

def _render_number_string(base_str, n, overrides=None):
  if overrides:
    for override_n, override_str in overrides:
      if n == override_n:
        return override_str % n
  return base_str % n

def process_videos(client, videos, process_video):
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
  print _render_number_string(
      '%d successes.', len(successes), [(1, '%d success.')])
  print _render_number_string(
      '%d failures:', len(failures), [(0, '%d failures.'), (1, '%d failure:')])
  for name, e in failures.iteritems():
    print '%s:' % name
    print '  %s' % e
    print
