import googleapiclient.discovery
import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = 'client_id.json'
CREDENTIALS_FILE = 'credentials.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def _get_credentials():
  if not os.path.exists(CREDENTIALS_FILE):
    return None
  with open(CREDENTIALS_FILE) as f:
    return pickle.load(f)

def _put_credentials(credentials):
  with open(CREDENTIALS_FILE, 'w') as f:
    pickle.dump(credentials, f)

def get_authenticated_client():
  credentials = _get_credentials()
  if not credentials:
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    _put_credentials(credentials)
  return googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
