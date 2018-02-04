import json

from datetime import datetime

CARD_DATA_FILE = 'data/AllSets.json'
COMPANY_NAME = 'Wizards of the Coast LLC, a subsidiary of Hasbro, Inc.'
RELEASE_DATE_FORMAT = '%Y-%m-%d'

class Card(object):

  def __init__(self, card_data, release_date):
    self.mid = card_data.get('multiverseid')
    self.name = card_data.get('name')
    self.artist = card_data.get('artist')
    self.release_date = release_date

class _CardData(object):

  def __init__(self):
    self._cards = None

  def _load_cards(self):
    with open(CARD_DATA_FILE) as card_data_file:
      json_data = json.load(card_data_file)
    self._cards = {}
    for set_data in json_data.itervalues():
      release_date = None
      if 'releaseDate' in set_data:
        try:
          release_date = datetime.strptime(
              set_data['releaseDate'], RELEASE_DATE_FORMAT).date()
        except ValueError:
          pass
      for card_data in set_data['cards']:
        card = Card(card_data, release_date)
        if card.mid is not None:
          self._cards[card.mid] = card

  def get(self, mid):
    if self._cards is None:
      self._load_cards()
    return self._cards[mid]

_CARD_DATA = _CardData()

def get(mid):
  card = _CARD_DATA.get(mid)
  lines = []
  lines.append(u'Thumbnail from %s by %s' % (card.name, card.artist))
  if card.release_date:
    year_str = str(card.release_date.year)
  else:
    year_str = '1995 - %d' % datetime.now().year
  lines.append(u'\u00A9 %s %s' % (year_str, COMPANY_NAME))
  return '\n'.join(lines)
