from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import os

def split_video(input_file, start_time, end_time, output_file):
    ffmpeg_extract_subclip(input_file, start_time, end_time, targetname=output_file)

def convert_time_to_seconds(time_str):
    parts = time_str.split(':')
    parts = [0] * (3 - len(parts)) + parts  # Pad with zeros if format is mm:ss or ss
    h, m, s = map(int, parts)
    return h * 3600 + m * 60 + s

def main():
    input_file = input("Enter the path to the input video file: ").strip().strip('"')
    chapters_file = input("Enter the path to the chapters file: ").strip().strip('"')

    # Get the duration of the video
    video = VideoFileClip(input_file)
    video_duration = video.duration
    video.close()

    with open(chapters_file, 'r') as file:
        chapters = [line.strip() for line in file.readlines() if line.strip()]

    for i in range(len(chapters) - 1):
        start_time_str, title = chapters[i].split(' ', 1)
        next_title = chapters[i + 1].split(' ', 1)[1]
        
        start_time = convert_time_to_seconds(start_time_str)
        
        if next_title.lower() == "end":
            end_time = convert_time_to_seconds(chapters[i + 1].split(' ')[0])
        else:
            end_time_str = chapters[i + 1].split(' ', 1)[0]
            end_time = convert_time_to_seconds(end_time_str)
        
        if title.lower() == "end":
            continue
        
        output_path = os.path.join(
            os.path.dirname(input_file),
            f"{title.strip().replace(' ', '_').replace(':', '-')}.mp4"
        )
        
        print(f"Splitting: {title.strip()} from {start_time_str} to {end_time_str if next_title.lower() != 'end' else 'end of video'}")
        
        try:
            split_video(input_file, start_time, end_time, output_path)
            print(f"Video chapter '{title.strip()}' has been split and saved to {output_path}")
        except OSError as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
