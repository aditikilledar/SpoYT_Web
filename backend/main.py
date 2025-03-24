from typing import Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.errors import HttpError

import os
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Spotify API Credentials
SPOTIPY_CLIENT_ID = os.getenv('CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = os.getenv('SPOTIFY_SCOPE')

# Set up YouTube API credentials, forcing SSL (privacy and integrity)
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

app = FastAPI()

# Enable CORS globally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

class TransferRequest(BaseModel):
    spotify_url: str
    youtube_playlist_title: str

def auth_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))
    return sp

def auth_youtube():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", YOUTUBE_SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret_file.json", YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)
    return yt

def get_spotify_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])   
    return tracks

def create_yt_playlist(yt, title, descr):
    req = yt.playlists().insert(
        part="snippet, status",
        body={
            "snippet": {
                "title": title,
                "description": descr
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    res = req.execute()
    return res["id"]

def search_yt_video(yt, query):
    req = yt.search().list(
        part="snippet",
        maxResults=1,
        q=query
    )
    res = req.execute()
    if res["items"]:
        return res["items"][0]["id"]["videoId"]
    return None

def add_vid_to_playlist(yt, playlist_id, video_id):
    max_retries = 3
    delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            req = yt.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            response = req.execute()
            print("Video added successfully:", response)
            return response
        except HttpError as e:
            if e.resp.status == 409:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
            else:
                print(f"An unexpected error occurred: {e}")
                raise
    raise Exception("Max retries exceeded")

def parse_spotify_playlist_url(url):
    pattern = r"playlist/([^?]+)"
    match = re.search(pattern, url)
    if match:
        playlist_id = match.group(1)
        return playlist_id
    else:
        raise Exception("Oops! Enter a valid Spotify playlist URL.")

@app.post("/transfer")
def transfer_playlist(request: TransferRequest):

    if request.spotify_url == "":
        raise HTTPException(status_code=400, detail="Spotify URL is required")
    

    spotify_playlist_id = parse_spotify_playlist_url(request.spotify_url)
    
    sp = auth_spotify()
    yt = auth_youtube()

    tracks = get_spotify_playlist_tracks(sp, spotify_playlist_id)

    if request.youtube_playlist_title:
        youtube_playlist_title = request.youtube_playlist_title
    else: 
        # use same name as the playlist
        youtube_playlist_title = "Spotify Playlist"

    yt_playlist_id = create_yt_playlist(yt, youtube_playlist_title, "From Spotify")

    for track in tracks:
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        query = f"{track_name} by {artist_name} Official Audio"
        video_id = search_yt_video(yt, query)
        if video_id:
            add_vid_to_playlist(yt, yt_playlist_id, video_id)
            print(f"Added {track_name} by {artist_name} to YouTube playlist")
        else:
            print(f"Could not find {track_name} by {artist_name} on YouTube")

    return {"message": "Playlist transfer completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)