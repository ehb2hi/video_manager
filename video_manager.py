import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

from youtube_downloader import YouTubeDownloaderWindow
from video_splitter import VideoSplitterWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Tools")

        layout = QVBoxLayout()

        # YouTube Downloader button
        self.yt_button = QPushButton('YouTube Downloader', self)
        self.yt_button.clicked.connect(self.open_youtube_downloader)
        layout.addWidget(self.yt_button)

        # Video Splitter button
        self.splitter_button = QPushButton('Video Splitter', self)
        self.splitter_button.clicked.connect(self.open_video_splitter)
        layout.addWidget(self.splitter_button)

        self.setLayout(layout)

    def open_youtube_downloader(self):
        self.youtube_window = YouTubeDownloaderWindow()
        self.youtube_window.show()

    def open_video_splitter(self):
        self.splitter_window = VideoSplitterWindow()
        self.splitter_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
