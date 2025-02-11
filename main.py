import os
import subprocess
import shutil
import yt_dlp
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Instagram Reels Downloader API"}

# Ensure FFmpeg is installed
def install_ffmpeg():
    if not shutil.which("ffmpeg"):
        os.system("apt update && apt install -y ffmpeg")  # Install FFmpeg
install_ffmpeg()

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
    try:
        os.makedirs("downloads", exist_ok=True)
        file_path = "downloads/video.mp4"
        encoded_file = "downloads/encoded_video.mp4"

        ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 'outtmpl': file_path}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        reencode_video(file_path, encoded_file)
        
        return {"download_url": f"https://instagram-reels-downloader-b12x.onrender.com/video/encoded_video.mp4"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video/{filename}")
def serve_video(filename: str):
    file_path = f"downloads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)
