"""
Uploads clips to YouTube Shorts, TikTok, and Instagram Reels.
"""
import os
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_youtube_shorts(
    clip_path: str,
    title: str,
    description: str,
    credentials_file: str = "config/youtube_credentials.json",
) -> str:
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=0)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": ["shorts", "viral", "trending"],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(clip_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"YouTube upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"YouTube Shorts uploaded: https://youtube.com/shorts/{video_id}")
    return video_id

def upload_to_tiktok(clip_path: str, title: str, access_token: str) -> dict:
    import requests

    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    file_size = os.path.getsize(clip_path)

    init_payload = {
        "post_info": {
            "title": title[:150],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1,
        },
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    init_resp = requests.post(init_url, json=init_payload, headers=headers).json()
    upload_url = init_resp["data"]["upload_url"]
    publish_id = init_resp["data"]["publish_id"]

    with open(clip_path, "rb") as f:
        video_data = f.read()

    upload_headers = {
        "Content-Type": "video/mp4",
        "Content-Length": str(file_size),
        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
    }
    requests.put(upload_url, data=video_data, headers=upload_headers)

    print(f"TikTok uploaded (publish_id: {publish_id})")
    return {"publish_id": publish_id}

def upload_to_instagram_reels(
    clip_path: str,
    caption: str,
    instagram_user_id: str,
    access_token: str,
) -> str:
    import requests

    video_url = upload_to_temp_hosting(clip_path)

    container_url = f"https://graph.instagram.com/v21.0/{instagram_user_id}/media"
    container_resp = requests.post(container_url, data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token,
    }).json()

    container_id = container_resp["id"]
    print(f"Instagram container created: {container_id}")

    time.sleep(15)

    publish_url = f"https://graph.instagram.com/v21.0/{instagram_user_id}/media_publish"
    publish_resp = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": access_token,
    }).json()

    media_id = publish_resp["id"]
    print(f"Instagram Reel published: {media_id}")
    return media_id

def upload_to_temp_hosting(clip_path: str) -> str:
    raise NotImplementedError("Implement temp hosting (e.g., S3, Cloudflare R2)")