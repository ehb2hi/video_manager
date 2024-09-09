import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QProgressBar, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt
import yt_dlp
import re

class YouTubeDownloaderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")

        layout = QVBoxLayout()

        # URL input
        self.url_label = QLabel('YouTube URL:')
        self.url_input = QLineEdit(self)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Resolution selection
        self.resolution_label = QLabel('Select resolution:')
        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItems(['720', '1080', '480'])
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combo)

        # Destination folder
        self.path_button = QPushButton('Select Download Path', self)
        self.path_button.clicked.connect(self.select_path)
        layout.addWidget(self.path_button)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Download button
        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

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
            'progress_hooks': [self.progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Extract percentage by removing non-numeric and non-decimal characters
            percentage_str = re.sub(r'[^\d.]', '', d['_percent_str'])
            try:
                progress = int(float(percentage_str))
                self.progress.setValue(progress)
            except ValueError:
                # Handle the case where the percentage string can't be converted
                print(f"Failed to parse progress percentage: {d['_percent_str']}")
