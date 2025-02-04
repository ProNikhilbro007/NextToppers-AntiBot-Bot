import os
from googleapiclient.discovery import build

# Set up YouTube API
api_key = 'YOUR_YOUTUBE_API_KEY'  # Replace with your API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Define the channel and live stream details
channel_id = 'YOUR_CHANNEL_ID'  # Replace with your channel ID

# Function to get live chat messages
def get_live_chat_messages():
    live_chat_id = get_live_chat_id(channel_id)
    
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

# Function to get live chat ID (based on current live stream)
def get_live_chat_id(channel_id):
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
    get_live_chat_messages()
