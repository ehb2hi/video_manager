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
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, QComboBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import yt_dlp
import os
import re

class YouTubeDownloaderWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 500, 300)  # Set window size

        layout = QVBoxLayout()

        # Custom font
        font = QFont("Arial", 11)

        # URL input
        self.url_label = QLabel('YouTube URL:')
        self.url_label.setFont(font)
        self.url_input = QLineEdit(self)
        self.url_input.setFont(font)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Resolution selection
        self.resolution_label = QLabel('Select resolution:')
        self.resolution_label.setFont(font)
        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItems(['144','240','360','720', '1080', '480'])
        self.resolution_combo.setFont(font)
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combo)

        # Destination folder
        self.path_button = QPushButton('Select Download Path', self)
        self.path_button.setFont(font)
        self.path_button.setStyleSheet("background-color: #FFC107; color: black; padding: 8px;")
        self.path_button.clicked.connect(self.select_path)
        layout.addWidget(self.path_button)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Download button
        self.download_button = QPushButton('Download', self)
        self.download_button.setFont(font)
        self.download_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close event
        
    def select_path(self):
        self.download_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if self.download_path:
            print(f"Selected path: {self.download_path}")

    def start_download(self):
        url = self.url_input.text()
        resolution = self.resolution_combo.currentText()

        if url and self.download_path:
            self.download_video(url, resolution)

    def download_video(self, url, resolution):
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'noprogress': False  # Ensure progress is shown
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Calculate progress as percentage
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0)
            if total > 0:
                progress_percentage = (downloaded / total) * 100
                self.progress.setValue(int(progress_percentage))
            else:
                self.progress.setValue(0)

        elif d['status'] == 'finished':
            # Download finished, reset the progress bar
            self.progress.setValue(100)
            print("Download completed.")

