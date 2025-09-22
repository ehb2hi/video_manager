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
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont, QIcon
from youtube_downloader import YouTubeDownloaderWindow
from video_splitter import VideoSplitterWindow
from video_editor import VideoEditorWindow


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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Tools")
        self.setGeometry(100, 100, 400, 200)  # Set window size
        try:
            self.setWindowIcon(QIcon("icons/icon.png"))
        except Exception:
            pass

        layout = QVBoxLayout()

        # Custom font
        font = QFont("Arial", 12, QFont.Bold)

        # YouTube Downloader button
        self.yt_button = QPushButton('YouTube Downloader', self)
        self.yt_button.setFont(font)
        self.yt_button.setStyleSheet(button_style)
        self.yt_button.clicked.connect(self.open_youtube_downloader)
        layout.addWidget(self.yt_button)

        # Video Splitter button
        self.splitter_button = QPushButton('Video Splitter', self)
        self.splitter_button.setFont(font)
        self.splitter_button.setStyleSheet(button_style)
        self.splitter_button.clicked.connect(self.open_video_splitter)
        layout.addWidget(self.splitter_button)
        
        # Basic Video Editor button
        self.editor_button = QPushButton('Basic Video Editor', self)
        self.editor_button.setFont(font)
        self.editor_button.setStyleSheet(button_style)
        self.editor_button.clicked.connect(self.open_video_editor)
        layout.addWidget(self.editor_button)

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

    def open_youtube_downloader(self):
        self.youtube_window = YouTubeDownloaderWindow(self)
        self.youtube_window.show()
        # self.hide()  # Hide the main window when the YouTube downloader window opens

    def open_video_splitter(self):
        self.splitter_window = VideoSplitterWindow(self)
        self.splitter_window.show()
        # self.hide()  # Hide the main window when the video splitter window opens
        
    def open_video_editor(self):
        self.editor_window = VideoEditorWindow(self)
        self.editor_window.show()
        # self.hide()  # Hide the main window when the video editor opens
        


def main():
    app = QApplication(sys.argv)
    # Configure QSettings scope
    QtCore.QCoreApplication.setOrganizationName("BrahimElHamdaoui")
    QtCore.QCoreApplication.setApplicationName("Video Manager")
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
