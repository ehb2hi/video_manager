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
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QHBoxLayout,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QSettings
import yt_dlp
import os
import re

# Button styling is handled globally via the app theme (QSS)

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
        self.resolution_combo.addItems(["144", "240", "360", "480", "720", "1080"])
        self.resolution_combo.setFont(font)
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combo)

        # Destination folder
        self.path_button = QPushButton('Select Download Path', self)
        self.path_button.setFont(font)
        self.path_button.clicked.connect(self.select_path)
        layout.addWidget(self.path_button)

        # Label to display selected download path
        self.path_label = QLabel('No path selected')
        self.path_label.setFont(font)
        layout.addWidget(self.path_label)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Stats label
        self.stats_label = QLabel('')
        self.stats_label.setFont(font)
        layout.addWidget(self.stats_label)

        # Download / Cancel controls
        controls = QHBoxLayout()
        self.download_button = QPushButton('Download', self)
        self.download_button.setFont(font)
        self.download_button.clicked.connect(self.start_download)
        controls.addWidget(self.download_button)

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.setFont(font)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)
        controls.addWidget(self.cancel_button)
        layout.addLayout(controls)

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Internal state and settings
        self.download_path = ""
        self.settings = QSettings()
        # Restore settings
        saved_dir = self.settings.value('downloader/download_path', '')
        if saved_dir:
            self.download_path = saved_dir
            self.path_label.setText(f"Download Path: {self.download_path}")
        saved_res = self.settings.value('downloader/resolution', '')
        if saved_res:
            idx = self.resolution_combo.findText(str(saved_res))
            if idx >= 0:
                self.resolution_combo.setCurrentIndex(idx)
        self.resolution_combo.currentTextChanged.connect(self._save_resolution)

        
    def closeEvent(self, event):
        #self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close event
        
    def select_path(self):
        self.download_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if self.download_path:
            self.path_label.setText(f"Download Path: {self.download_path}")
            self.settings.setValue('downloader/download_path', self.download_path)
        else:
            self.path_label.setText("No path selected")

    def start_download(self):
        url = self.url_input.text().strip()
        resolution = self.resolution_combo.currentText()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter a YouTube URL.")
            return
        if not self.download_path:
            QMessageBox.warning(self, "Select Folder", "Please choose a download folder.")
            return
        if not re.match(r"^https?://", url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid http(s) URL.")
            return
        self.start_worker(url, resolution)

    def start_worker(self, url, resolution):
        # Prepare worker and thread
        self.thread = QThread()
        self.worker = _YTDLPWorker(
            url=url,
            out_dir=self.download_path,
            max_height=resolution,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.stats.connect(self._on_stats)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Toggle buttons
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress.setValue(0)
        self.stats_label.setText('')

        self.thread.start()

    def cancel_download(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.cancel()

    def _on_finished(self):
        self.progress.setValue(100)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _on_error(self, msg: str):
        QMessageBox.critical(self, "Download Error", msg)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _save_resolution(self, value: str):
        self.settings.setValue('downloader/resolution', value)

    def _on_stats(self, stats: dict):
        # Human-readable figures
        def _fmt_size(b):
            if not b:
                return '0B'
            for unit in ['B', 'KB', 'MB', 'GB']:
                if b < 1024.0:
                    return f"{b:.1f}{unit}"
                b /= 1024.0
            return f"{b:.1f}TB"

        def _fmt_speed(bps):
            if not bps:
                return '--'
            for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
                if bps < 1024.0:
                    return f"{bps:.1f} {unit}"
                bps /= 1024.0
            return f"{bps:.1f} TB/s"

        def _fmt_eta(sec):
            if not isinstance(sec, (int, float)):
                return '--'
            m, s = divmod(int(sec), 60)
            h, m = divmod(m, 60)
            if h:
                return f"{h:d}h {m:02d}m {s:02d}s"
            if m:
                return f"{m:d}m {s:02d}s"
            return f"{s:d}s"

        downloaded = stats.get('downloaded') or 0
        total = stats.get('total') or 0
        speed = stats.get('speed')
        eta = stats.get('eta')
        text = f"{_fmt_size(downloaded)} / { _fmt_size(total) }  |  {_fmt_speed(speed)}  |  ETA: {_fmt_eta(eta)}"
        self.stats_label.setText(text)


class _YTDLPWorker(QObject):
    progress = pyqtSignal(int)
    stats = pyqtSignal(object)  # dict with speed, eta, size
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str, out_dir: str, max_height: str):
        super().__init__()
        self.url = url
        self.out_dir = out_dir
        self.max_height = max_height
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _hook(self, d):
        if self._cancel:
            raise Exception("Cancelled by user")
        if d.get('status') == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total and total > 0:
                self.progress.emit(int(downloaded * 100 / total))
            # Emit stats
            speed = d.get('speed')  # bytes/s
            eta = d.get('eta')  # seconds
            self.stats.emit({
                'downloaded': downloaded,
                'total': total,
                'speed': speed,
                'eta': eta,
            })
        elif d.get('status') == 'finished':
            self.progress.emit(100)

    def run(self):
        ydl_opts = {
            'format': f'bestvideo[height<={self.max_height}]+bestaudio/best',
            'outtmpl': os.path.join(self.out_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._hook],
            'noprogress': False,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()
