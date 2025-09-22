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
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout
from youtube_downloader import YouTubeDownloaderWindow
from video_splitter import VideoSplitterWindow
from video_editor import VideoEditorWindow
from youtube_uploader import YouTubeUploaderWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Tools")
        self.resize(1100, 700)
        self.setMinimumSize(800, 600)
        try:
            self.setWindowIcon(QIcon("icons/icon.png"))
        except Exception:
            pass

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.tool_tabs = QTabWidget(self)
        self.tool_tabs.setTabPosition(QTabWidget.East)
        self.tool_tabs.setMovable(False)
        self.tool_tabs.setDocumentMode(True)
        self.tool_tabs.setTabBarAutoHide(False)
        self.tool_tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #b0b0b0;
                border-radius: 10px;
                background: #ffffff;
            }
            QTabBar::tab {
                background-color: #FFC107;
                color: black;
                padding: 12px 16px;
                margin: 6px;
                border-radius: 12px;
                min-width: 150px;
            }
            QTabBar::tab:hover {
                background-color: #FFB300;
            }
            QTabBar::tab:selected {
                background-color: #FF9800;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                margin-right: 6px;
            }
            """
        )
        layout.addWidget(self.tool_tabs)

        # Instantiate each tool once and register it as a tab.
        self.youtube_downloader_tab = YouTubeDownloaderWindow(self)
        self.video_splitter_tab = VideoSplitterWindow(self)
        self.video_editor_tab = VideoEditorWindow(self)
        self.youtube_uploader_tab = YouTubeUploaderWindow(self)

        self.tool_tabs.addTab(self.youtube_downloader_tab, "YouTube Downloader")
        self.tool_tabs.addTab(self.video_splitter_tab, "Video Splitter")
        self.tool_tabs.addTab(self.video_editor_tab, "Basic Video Editor")
        self.tool_tabs.addTab(self.youtube_uploader_tab, "YouTube Uploader")

        # Ensure the first tool is displayed when the application launches.
        self.tool_tabs.setCurrentIndex(0)



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
