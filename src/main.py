"""
Main pipeline: fetch -> download -> clip -> upload to all platforms.
"""
import os
import yaml
from dotenv import load_dotenv
from fetcher import get_viral_videos
from downloader import download_video
from clipper import process_video
from uploader import upload_to_youtube_shorts, upload_to_tiktok, upload_to_instagram_reels

load_dotenv()

def run_pipeline(query: str = "viral moments 2026", max_videos: int = 3):
    with open("config/accounts.yaml") as f:
        accounts = yaml.safe_load(f)

    print(f"Fetching viral YouTube videos for: '{query}'")
    videos = get_viral_videos(query, max_results=max_videos)

    for video in videos:
        print(f"\nProcessing: {video['title']} ({video['views']:,} views)")

        try:
            video_path = download_video(video["url"])
            clip_path = process_video(video_path)

            title = f"{video['title'][:80]} #shorts #viral"
            caption = f"{video['title']} #viral #trending #reels"

            for account in accounts.get("youtube", []):
                upload_to_youtube_shorts(clip_path, title, caption,
                                          credentials_file=account["credentials"])

            for account in accounts.get("tiktok", []):
                upload_to_tiktok(clip_path, title, access_token=account["access_token"])

            for account in accounts.get("instagram", []):
                upload_to_instagram_reels(clip_path, caption,
                                           instagram_user_id=account["user_id"],
                                           access_token=account["access_token"])

        except Exception as e:
            print(f"Error processing '{video['title']}': {e}")
            continue

    print("\nPipeline complete!")

if __name__ == "__main__":
    run_pipeline()