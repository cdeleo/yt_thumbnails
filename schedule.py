import bisect

from datetime import datetime
from datetime import timedelta

class Scheduler(object):

  def __init__(self, start_time, publish_time, publish_days):
    self.publish_days = sorted(publish_days)

    snapped_time = datetime.combine(start_time.date(), publish_time)
    if snapped_time < start_time:
      snapped_time += timedelta(days=1)
    self._next_time = self._skip_days(snapped_time)

  def _skip_days(self, time):
    pos = bisect.bisect_left(self.publish_days, time.weekday())
    if pos < len(self.publish_days):
      n_days_to_skip = self.publish_days[pos] - time.weekday()
    else:
      n_days_to_skip = (6 - time.weekday()) + self.publish_days[0] + 1
    return time + timedelta(days=n_days_to_skip)

  def get_next(self):
    next_time = self._next_time
    self._next_time = self._skip_days(next_time + timedelta(days=1))
    return next_time
