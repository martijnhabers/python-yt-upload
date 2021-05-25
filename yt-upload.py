import os
import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = 'client_secret.json'

credentials = None

# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token..')
        credentials.refresh(Request)
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes= SCOPES)
        flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message= 'Redirecting to Auth Link')
        credentials = flow.credentials
        with open('token.pickle', 'wb') as file:
            print('Saving credentials for Future use...')
            pickle.dump(credentials, file)

youtube = build('youtube', 'v3', credentials=credentials)

request_body = {
    'snippet': {
        'categoryI': 20,
        'title': 'Upload Testing This is Private Video ',
        'description': 'Upload Testing This is Private Video',
        'tags': ['Test', 'Youtube API', 'Python']
    },
    'status': {
        'privacyStatus': 'private',
        # 'publishAt': upload_date_time,
        'selfDeclaredMadeForKids': False, 
    },
    'notifySubscribers': False
}

mediaFile = MediaFileUpload('upload-tester.MP4')
response_upload = youtube.videos().insert(part='snippet,status', body=request_body, media_body=mediaFile).execute()
