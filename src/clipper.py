"""
Uses Whisper (transcription) + OpenAI GPT to find the best viral clip moments,
then uses FFmpeg to cut & reformat for Shorts/Reels/TikTok (vertical 9:16).
"""
import os
import json
import subprocess
import whisper
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_video(video_path: str) -> list[dict]:
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"],
        })
    return segments

def find_best_clip(segments: list[dict], target_duration: int = 55) -> tuple[float, float]:
    transcript_text = "\n".join(
        [f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}" for s in segments]
    )

    prompt = f"""
You are a viral content strategist. Analyze this YouTube video transcript and identify the SINGLE most engaging, surprising, or emotionally compelling segment that would perform best as a TikTok/Reel/Short.

The clip must be {target_duration} seconds or less.

Transcript:
{transcript_text}

Respond ONLY with valid JSON in this format:
{{"start": <start_seconds_float>, "end": <end_seconds_float>, "reason": "<brief reason>"}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    print(f"✂️  Best clip: {result['start']}s -> {result['end']}s | Reason: {result['reason']}")
    return result["start"], result["end"]

def create_vertical_clip(
    input_path: str,
    start: float,
    end: float,
    output_dir: str = "output/clips",
    title: str = "",
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_clip.mp4")
    duration = end - start

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),
        "-vf", (
            "split[original][blur];"
            "[blur]scale=1080:1920,gblur=sigma=20[bg];"
            "[original]scale=w=1080:h=1080:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2"
        ),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-r", "30",
        output_path,
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")

    print(f"Clip saved: {output_path}")
    return output_path

def process_video(video_path: str) -> str:
    print(f"Transcribing {video_path}...")
    segments = transcribe_video(video_path)

    print("Finding best viral clip with AI...")
    start, end = find_best_clip(segments)

    print("Creating vertical clip...")
    clip_path = create_vertical_clip(video_path, start, end)

    return clip_path