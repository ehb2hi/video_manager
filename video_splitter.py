# MIT License
# Copyright (c)  2024 Brahim El Hamdaoui
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import subprocess


button_style = """
    QPushButton {
        background-color: #FFC107;  /* Button color */
        color: black;
        padding: 10px;
        border-radius: 15px;  /* Rounded corners */
        font-size: 14px;
        min-height: 40px;  /* Set minimum height */
        min-width: 150px;   /* Set minimum width */
    }
    QPushButton:hover {
        background-color: #FFB300;  /* Hover effect */
    }
    QPushButton:pressed {
        background-color: #FF9800;  /* Pressed effect */
    }
"""

class VideoSplitterWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window 
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Splitter")
        self.setGeometry(100, 100, 500, 300)  # Set window size

        layout = QVBoxLayout()

        # Custom font
        font = QFont("Arial", 11)

        # Input video file
        self.video_label = QLabel('Select video file:')
        self.video_label.setFont(font)
        self.video_button = QPushButton('Browse', self)
        self.video_button.setFont(font)
        self.video_button.setStyleSheet(button_style)
        self.video_button.clicked.connect(self.select_video)
        self.video_path = QLineEdit(self)
        self.video_path.setFont(font)
        layout.addWidget(self.video_label)
        layout.addWidget(self.video_path)
        layout.addWidget(self.video_button)

        # Chapters file
        self.chapters_label = QLabel('Select chapters file:')
        self.chapters_label.setFont(font)
        self.chapters_button = QPushButton('Browse', self)
        self.chapters_button.setFont(font)
        self.chapters_button.setStyleSheet(button_style)
        self.chapters_button.clicked.connect(self.select_chapters)
        self.chapters_path = QLineEdit(self)
        self.chapters_path.setFont(font)
        layout.addWidget(self.chapters_label)
        layout.addWidget(self.chapters_path)
        layout.addWidget(self.chapters_button)

        # Destination path
        self.destination_button = QPushButton('Select Destination', self)
        self.destination_button.setFont(font)
        self.destination_button.setStyleSheet(button_style)
        self.destination_button.clicked.connect(self.select_destination)
        layout.addWidget(self.destination_button)

        # Label to display selected destination path
        self.destination_label = QLabel('No destination selected')
        self.destination_label.setFont(font)
        layout.addWidget(self.destination_label)

        # Split button
        self.split_button = QPushButton('Split Video', self)
        self.split_button.setFont(font)
        self.split_button.setStyleSheet(button_style)
        self.split_button.clicked.connect(self.split_video)
        layout.addWidget(self.split_button)

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        

    def closeEvent(self, event):
        #self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close even

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
            self.destination_label.setText(f"Destination: {self.destination_path}")
        else:
            self.destination_label.setText("No destination selected")

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

                # Run FFmpeg with the `-strict -2` option
                ffmpeg_command = [
                    'ffmpeg', '-i', video_file, '-ss', str(start_time), '-to', str(end_time),
                    '-c', 'copy', '-strict', '-2', output_path
                ]

                # Execute the command
                subprocess.run(ffmpeg_command)
                print(f"Saved {title} to {output_path}")

    def convert_time_to_seconds(self, time_str):
        parts = time_str.split(':')
        parts = [0] * (3 - len(parts)) + parts
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
