import os
import praw
import ffmpeg
import json
import pprint
import pickle
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
from urllib.parse import urlparse
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload


current_dir = os.getcwd()
REDDITSECRETS = json.load(open('reddit-secrets.json', 'r'))

# -------- REDDIT DOWNLOAD PART --------

# Create reddit instance

reddit = praw.Reddit(
    client_id = REDDITSECRETS['client_id'],
    client_secret =REDDITSECRETS['client_secret'],
    user_agent = REDDITSECRETS['user_agent'],
    username = REDDITSECRETS['username'],
    password = REDDITSECRETS['password']
)


# Select subreddit to be used for downloading
subred = reddit.subreddit('rocketleague')
hot = subred.hot(limit = 20)


video = []      # generate empty list for video link dictionaries
vidstop = 10    # amount of vids to scrape
k = 0           # initalize constant number of vids scraped

for i in hot:
    submission = reddit.submission(id=i)
    if i.is_video == True:
        # print(submission.title) # Prints all submissions in hot
        vid_url = submission.media['reddit_video']['fallback_url']
        audio_url = vid_url[:vid_url.rfind('/')] + '/DASH_audio.mp4?source=fallback'
        video.append({'id': i.id, 'video': vid_url, 'audio': audio_url, 'url': i.url, 'title': i.title})
        k += 1

        if k == vidstop: 
            break



# --- YOUTUBE UPLOAD PART --- 

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


vidTitle = ''
vidDesc = ''

request_body = {
    'snippet': {
        'categoryI': 20,
        'title': vidTitle,
        'description': vidDesc,
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
