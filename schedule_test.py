import schedule

import datetime
import unittest

class TestScheduler(unittest.TestCase):

  def test_same_day(self):
    # Start from a Monday
    s = schedule.Scheduler(
        datetime.datetime(2000, 1, 3, 10, 0), datetime.time(12), [0, 2, 4])
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 3, 12, 0))

  def test_midweek(self):
    # Start from a Tuesday
    s = schedule.Scheduler(
        datetime.datetime(2000, 1, 4, 10, 0), datetime.time(12), [0, 2, 4])
    
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 5, 12, 0))

  def test_over_weekend(self):
    # Start from a Saturday
    s = schedule.Scheduler(
        datetime.datetime(2000, 1, 8, 10, 0), datetime.time(12), [0, 2, 4])
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 10, 12, 0))

  def test_sequence(self):
    # Start from a Monday
    s = schedule.Scheduler(
        datetime.datetime(2000, 1, 3, 10, 0), datetime.time(12), [0, 2, 4])
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 3, 12, 0))
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 5, 12, 0))
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 7, 12, 0))
    self.assertEqual(s.get_next(), datetime.datetime(2000, 1, 10, 12, 0))

if __name__ == '__main__':
  unittest.main()
