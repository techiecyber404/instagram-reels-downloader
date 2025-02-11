import os
import subprocess
import shutil
import yt_dlp
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# Ensure FFmpeg is installed
def install_ffmpeg():
    if not shutil.which("ffmpeg"):  # Check if FFmpeg is installed
        os.system("apt update && apt install -y ffmpeg")  # Install FFmpeg on startup
install_ffmpeg()

# FFmpeg path
FFMPEG_PATH = shutil.which("ffmpeg")

# Function to encode video
def reencode_video(input_file, output_file):
    command = [
        FFMPEG_PATH, "-i", input_file,
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_file
    ]
    subprocess.run(command, check=True)

# Route for downloading and encoding
@app.post("/download/")
def download_reel(url: str = Form(...)):
    file_path = "downloads/video.mp4"  # Path for the downloaded file
    encoded_file = "downloads/encoded_video.mp4"  # Output encoded file

    # Download video
    ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 'outtmpl': file_path}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Re-encode video
    reencode_video(file_path, encoded_file)
    
    return {"download_url": f"/video/{encoded_file}"}

@app.get("/video/{filename}")
def serve_video(filename: str):
    return FileResponse(f"downloads/{filename}", media_type="video/mp4", filename=filename)
