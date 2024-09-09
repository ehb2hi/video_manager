from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit)
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import os

class VideoSplitterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Splitter")

        layout = QVBoxLayout()

        # Input video file
        self.video_label = QLabel('Select video file:')
        self.video_button = QPushButton('Browse', self)
        self.video_button.clicked.connect(self.select_video)
        self.video_path = QLineEdit(self)
        layout.addWidget(self.video_label)
        layout.addWidget(self.video_path)
        layout.addWidget(self.video_button)

        # Chapters file
        self.chapters_label = QLabel('Select chapters file:')
        self.chapters_button = QPushButton('Browse', self)
        self.chapters_button.clicked.connect(self.select_chapters)
        self.chapters_path = QLineEdit(self)
        layout.addWidget(self.chapters_label)
        layout.addWidget(self.chapters_path)
        layout.addWidget(self.chapters_button)

        # Destination path
        self.destination_button = QPushButton('Select Destination', self)
        self.destination_button.clicked.connect(self.select_destination)
        layout.addWidget(self.destination_button)

        # Split button
        self.split_button = QPushButton('Split Video', self)
        self.split_button.clicked.connect(self.split_video)
        layout.addWidget(self.split_button)

        self.setLayout(layout)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Video File')
        if file_path:
            self.video_path.setText(file_path)

    def select_chapters(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Chapters File')
        if file_path:
            self.chapters_path.setText(file_path)

    def select_destination(self):
        self.destination_path = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if self.destination_path:
            print(f"Selected destination path: {self.destination_path}")

    def split_video(self):
        video_file = self.video_path.text()
        chapters_file = self.chapters_path.text()

        if video_file and chapters_file and self.destination_path:
            with open(chapters_file, 'r') as file:
                chapters = [line.strip() for line in file.readlines() if line.strip()]

            for i in range(len(chapters) - 1):
                start_time_str, title = chapters[i].split(' ', 1)
                start_time = self.convert_time_to_seconds(start_time_str)

                next_time_str, _ = chapters[i + 1].split(' ', 1)
                end_time = self.convert_time_to_seconds(next_time_str)

                output_path = os.path.join(self.destination_path, f"{title}.mp4")
                ffmpeg_extract_subclip(video_file, start_time, end_time, targetname=output_path)
                print(f"Saved {title} to {output_path}")

    def convert_time_to_seconds(self, time_str):
        parts = time_str.split(':')
        parts = [0] * (3 - len(parts)) + parts
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
