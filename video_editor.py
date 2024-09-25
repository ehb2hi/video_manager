import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QLineEdit
import re

class VideoEditorWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Basic Video Editor")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # URL input field for YouTube video
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube Video URL")
        layout.addWidget(self.url_input)

        # Load Video Button
        self.load_button = QPushButton('Load Video', self)
        self.load_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_button)

        # Web view to display the YouTube video
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.setLayout(layout)

    def load_video(self):
        video_url = self.url_input.text()
        if video_url:
            # Extract the video ID from the standard YouTube URL
            video_id = self.extract_video_id(video_url)
            if video_id:
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                self.browser.setUrl(QtCore.QUrl(embed_url))

    def extract_video_id(self, url):
        # Regular expression to extract the video ID from YouTube URL
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return None

    def closeEvent(self, event):
        # self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close event