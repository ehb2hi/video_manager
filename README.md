 Video Manager

**Video Manager** is a Python application that allows users to download YouTube videos and split videos into chapters. The application is built using PyQt5 for the UI and uses external libraries such as `yt-dlp` for downloading videos and `moviepy` for video splitting.

## Features

- **YouTube Video Downloader**: Download videos from YouTube in various resolutions using the `yt-dlp` backend.
- **Video Splitter**: Split videos into chapters based on time stamps using `moviepy`.
- Simple and easy-to-use graphical interface built with PyQt5.

## Installation

### Prerequisites

Make sure you have Python 3.10+ installed on your system.

Install the necessary dependencies using `pip`:

```bash
pip install -r requirements.txt

How to Install from the .deb Package

    Build the .deb package by running the create_deb_package.sh script:

    bash

./create_deb_package.sh

Install the .deb package:

bash

    sudo apt install ./dist/video-manager_<version>_amd64.deb

Running the Application

Once the application is installed, you can run it using the command:

bash

video_manager

Alternatively, if you are running from the source, you can use the following command:

bash

python video_manager.py

Usage
YouTube Downloader

    Input: Enter a YouTube URL in the input field and choose the resolution.
    Output: Choose the destination path for the downloaded video.
    Progress: A progress bar will show the download progress.

Video Splitter

    Input Video: Select the video file to split.
    Chapters File: Provide a text file containing timestamps and titles for each chapter.
    Destination: Choose the output path for the split video segments.

Chapters File Format

The chapters file should be formatted as follows:

txt

00:00:00 Chapter 1
00:05:30 Chapter 2
00:10:00 Chapter 3
00:15:30 End

Each line consists of the timestamp (HH:MM
) and the chapter title.
Project Structure

bash

video_manager/
├── build/                      # Build files for the .deb package
├── config/                     # Configuration files
├── icons/                      # Icons for the application
├── __init__.py                 # Package initialization file
├── __version__.py              # Version information
├── create_deb_package.sh       # Script to create .deb package
├── README.md                   # This file
├── setup.py                    # Setup script for packaging
├── video_manager.py            # Main script (entry point)
├── video_splitter.py           # Video splitting functionality
└── youtube_downloader.py       # YouTube downloader functionality

License

This project is licensed under the MIT License - see the LICENSE file for details.
Contributing

Feel free to submit issues and pull requests. Contributions, whether in the form of bug reports, suggestions, or code contributions, are greatly appreciated.
Acknowledgments

    yt-dlp: The library used for downloading YouTube videos.
    moviepy: The library used for video manipulation and splitting.
    PyQt5: The framework used to create the graphical user interface.

markdown


### Steps to Implement:

1. **Create a `README.md` file** in the root of your project directory (if it doesn't already exist).
   
   ```bash
   touch README.md

    Paste the content provided above into the README.md file.

    Push to GitHub: Commit your changes and push the updated README.md file to your GitHub repository:

    bash

git add README.md
git commit -m "Add README"
git push origin main