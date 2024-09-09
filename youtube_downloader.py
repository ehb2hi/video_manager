#youtube_downloader.py
from pytube import YouTube
from pytube.cli import on_progress
import os

def get_video_info(url):
    yt = YouTube(url)
    print(f"Title: {yt.title}")
    print(f"Author: {yt.author}")
    print(f"Length: {yt.length} seconds")
    print(f"Views: {yt.views}")
    print(f"Rating: {yt.rating}")
    
    description = yt.description if yt.description else "No description available"
    print(f"Description: {description[:200]}...")

    print(f"Published Date: {yt.publish_date}")
    print("Available Streams:")
    for stream in yt.streams.filter(progressive=True):
        print(f"Resolution: {stream.resolution}, Size: {round(stream.filesize / (1024 * 1024), 2)} MB")

    if yt.captions:
        print("Available Captions:")
        for caption in yt.captions:
            print(f"Language: {caption.code}")

def download_video(url, resolution, download_path):
    yt = YouTube(url, on_progress_callback=on_progress)
    stream = yt.streams.filter(res=resolution, progressive=True).first()
    if stream:
        print(f"Downloading {yt.title} at {resolution} to {download_path}...")
        stream.download(output_path=download_path)
        print("Download complete!")
    else:
        print("The requested resolution is not available.")

def main():
    url = input("Enter the YouTube video URL: ")
    get_video_info(url)

    choice = input("Do you want to download the video in a specific resolution? (yes/no): ").strip().lower()
    if choice == 'yes':
        resolution = input("Enter the resolution (e.g., 720p): ").strip()
        download_path = input("Enter the download location (leave empty for default ./Download): ").strip()
        
        if not download_path:
            download_path = './Download'
            
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        download_video(url, resolution, download_path)
    else:
        print("Exiting without download.")
