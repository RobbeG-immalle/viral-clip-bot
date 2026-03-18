"""
Downloads YouTube videos using yt-dlp.
"""
import subprocess
import os

def download_video(url: str, output_dir: str = "output/downloads") -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

    result = subprocess.run(
        [
            "yt-dlp",
            url,
            "--output", output_template,
            "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "--no-playlist",
            "--print", "after_move:filepath",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")

    filepath = result.stdout.strip().splitlines()[-1]
    return filepath