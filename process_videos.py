import traceback

def _render_number_string(base_str, n, overrides=None):
  if overrides:
    for override_n, override_str in overrides:
      if n == override_n:
        return override_str % n
  return base_str % n

class VideoProcessor(object):

  def __init__(self):
    self.n_successes = 0
    self.failures = {}

  def process(
      self, client, videos, process_video, filter_video=None,
      stop_on_error=False):
    for video in videos:
      if filter_video and not filter_video(video):
        continue
      stop = False
      print 'Processing %s...' % video.name
      try:
        stop = process_video(client, video)
      except:
        print 'failed!'
        self.failures[video.name] = traceback.format_exc()
        if stop_on_error:
          stop = True
      else:
        self.n_successes += 1
      print 'done.'
      if stop:
        return True
    return False

  def print_summary(self):
    print
    print _render_number_string(
        '%d successes.', self.n_successes, [(1, '%d success.')])
    print _render_number_string(
        '%d failures:', len(self.failures),
        [(0, '%d failures.'), (1, '%d failure:')])
    for name, e in self.failures.iteritems():
      print '%s:' % name
      print '  %s' % e
      print
