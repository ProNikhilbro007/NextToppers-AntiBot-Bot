import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from google.auth.transport.requests import Request  # <-- Missing import added

# Set up OAuth 2.0 client ID and secret
CLIENT_SECRET_FILE = 'client_secret.json'  # Path to your client secret file
API_NAME = 'youtube'
API_VERSION = 'v3'

# The scopes required by the API
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/youtube.force-ssl']

# Function to authenticate and build the YouTube API client
def get_authenticated_service():
    credentials = None
    
    # Check if there are existing credentials in the token.pickle file
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If no valid credentials are available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())  # <-- Refresh the token
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    
    # Build the YouTube API client
    youtube = build(API_NAME, API_VERSION, credentials=credentials)
    return youtube

# Function to get live chat messages
def get_live_chat_messages(youtube, channel_id):
    try:
        live_chat_id = get_live_chat_id(youtube, channel_id)
    
        if live_chat_id:
            response = youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet,authorDetails"
            ).execute()

            for item in response['items']:
                user_id = item['authorDetails']['channelId']
                message = item['snippet']['displayMessage']
                profile_image = item['authorDetails'].get('profileImageUrl', None)
                
                # Check for bots (new user, no profile image, or spammy behavior)
                if not profile_image or is_spammy(message):
                    print(f"Potential bot detected: {user_id}, Message: {message}")
                    block_user(user_id)  # Block the bot
    except HttpError as error:
        print(f"An error occurred: {error}")

# Function to get live chat ID (based on current live stream)
def get_live_chat_id(youtube, channel_id):
    try:
        response = youtube.search().list(
            channelId=channel_id,
            eventType="live",
            type="video",
            part="snippet"
        ).execute()

        if response['items']:
            video_id = response['items'][0]['id']['videoId']
            video_response = youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            ).execute()

            live_chat_id = video_response['items'][0]['liveStreamingDetails']['activeLiveChatId']
            return live_chat_id
    except HttpError as error:
        print(f"An error occurred: {error}")
    return None

# Function to check if message is spammy
def is_spammy(message):
    spam_keywords = ['http', 'www', 'buy', 'free', 'click', 'promo']
    return any(keyword in message.lower() for keyword in spam_keywords)

# Function to block user (simulated - depends on available YouTube API functionality)
def block_user(user_id):
    print(f"Blocking user {user_id}...")

# Start checking messages
if __name__ == "__main__":
    channel_id = 'UCtgHR0fSfJfg2Flu5Wx85sw'  # This is the actual Channel ID
    youtube = get_authenticated_service()
    get_live_chat_messages(youtube, channel_id)


