import os
import subprocess
import shutil
import yt_dlp
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# Ensure the downloads directory exists
os.makedirs("downloads", exist_ok=True)

# Ensure FFmpeg is installed
def install_ffmpeg():
    if not shutil.which("ffmpeg"):
        os.system("apt update && apt install -y ffmpeg")

install_ffmpeg()

# Get FFmpeg path
FFMPEG_PATH = shutil.which("ffmpeg")
if not FFMPEG_PATH:
    raise RuntimeError("FFmpeg is not installed. Install it manually.")

# Function to encode video
def reencode_video(input_file, output_file):
    try:
        command = [
            FFMPEG_PATH, "-i", input_file,
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            output_file
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg encoding failed: {str(e)}")

# Root Route
@app.get("/")
def home():
    return {"message": "Welcome to the Instagram Reels Downloader API"}

# Route for downloading and encoding
@app.post("/download/")
def download_reel(url: str = Form(...)):
    file_path = "downloads/video.mp4"
    encoded_file = "downloads/encoded_video.mp4"

    try:
        # Download video
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': file_path
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Re-encode video
        reencode_video(file_path, encoded_file)

        return {"download_url": f"/video/encoded_video.mp4"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download or encoding error: {str(e)}")

# Serve video file
@app.get("/video/{filename}")
def serve_video(filename: str):
    file_path = f"downloads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="video/mp4", filename=filename)
