# viral-clip-bot

Automatically finds viral YouTube videos, creates short-form clips using AI, and uploads them to TikTok, Instagram Reels, and YouTube Shorts.

## Pipeline

1. **Fetch** – Finds viral YouTube videos via YouTube Data API
2. **Download** – Downloads the video using yt-dlp
3. **Clip** – Transcribes with Whisper, picks the best segment with GPT-4o, exports vertical 9:16 via FFmpeg
4. **Upload** – Posts to YouTube Shorts, TikTok, and Instagram Reels

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Install FFmpeg
- macOS: brew install ffmpeg
- Ubuntu: sudo apt install ffmpeg
- Windows: https://ffmpeg.org/download.html

### 3. Configure environment
cp .env.example .env
Fill in your API keys in .env

### 4. Configure accounts
Edit config/accounts.yaml with your platform tokens and credentials.

### 5. Run
cd src
python main.py

## API Keys Required

| Platform | What you need |
|---|---|
| YouTube (download) | YouTube Data API v3 key |
| YouTube Shorts (upload) | Google OAuth2 app + youtube.upload scope |
| TikTok | TikTok Developer App with Content Posting API |
| Instagram Reels | Meta Developer App + instagram_content_publish permission |
| OpenAI | OpenAI API key (GPT-4o + Whisper) |

## Notes
- Respect copyright and platform Terms of Service
- For multiple accounts, consider using residential proxies
- Instagram Reels upload requires a publicly accessible video URL (e.g., S3)