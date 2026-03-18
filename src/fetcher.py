"""
Fetches viral YouTube videos using the YouTube Data API v3.
Filters by views, recency, and category.
"""
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

def get_viral_videos(query: str, max_results: int = 10, min_views: int = 500_000) -> list[dict]:
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)

    published_after = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="viewCount",
        publishedAfter=published_after,
        maxResults=max_results * 2,
        videoDuration="medium",
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

    stats_response = youtube.videos().list(
        part="statistics,snippet,contentDetails",
        id=",".join(video_ids),
    ).execute()

    viral_videos = []
    for video in stats_response.get("items", []):
        views = int(video["statistics"].get("viewCount", 0))
        if views >= min_views:
            viral_videos.append({
                "id": video["id"],
                "title": video["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={video['id']}",
                "views": views,
                "duration": video["contentDetails"]["duration"],
                "channel": video["snippet"]["channelTitle"],
            })

    return sorted(viral_videos, key=lambda x: x["views"], reverse=True)[:max_results]