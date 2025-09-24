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
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QApplication,
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        # Custom font
        font = QFont("Arial", 11)

        # Compact form layout to keep labels close to fields
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # URL row (input + Paste button)
        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube video URL...")
        self.url_input.setFont(font)
        self.url_input.textChanged.connect(self._on_url_changed)
        url_row.addWidget(self.url_input, 1)
        self.paste_button = QPushButton('Paste', self)
        self.paste_button.setFont(font)
        self.paste_button.clicked.connect(self._paste_from_clipboard)
        url_row.addWidget(self.paste_button)
        form.addRow(QLabel('YouTube URL:'), url_row)

        # Resolution selection (label + combo)
        self.resolution_label = QLabel('Resolution:')
        self.resolution_label.setFont(font)
        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItems(["144", "240", "360", "480", "720", "1080"])
        self.resolution_combo.setFont(font)
        form.addRow(self.resolution_label, self.resolution_combo)

        # Download path row (readonly field + Browse)
        row_path = QHBoxLayout()
        row_path.setSpacing(8)
        self.path_display = QLineEdit(self)
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText('No folder selected')
        self.path_display.setFont(font)
        row_path.addWidget(self.path_display, 1)
        self.path_button = QPushButton('Browse', self)
        self.path_button.setFont(font)
        self.path_button.clicked.connect(self.select_path)
        row_path.addWidget(self.path_button)
        form.addRow(QLabel('Download Path:'), row_path)

        # Place form at top
        layout.addLayout(form)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # Status label
        self.status_label = QLabel('Waiting for URL...')
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)

        # Download / Cancel controls
        controls = QHBoxLayout()
        self.download_button = QPushButton('⬇️ Download', self)
        self.download_button.setFont(font)
        self.download_button.clicked.connect(self.start_download)
        controls.addWidget(self.download_button)

        self.cancel_button = QPushButton('✖ Cancel', self)
        self.cancel_button.setFont(font)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)
        controls.addWidget(self.cancel_button)
        layout.addLayout(controls)

        # Style cancel subtly as secondary (theme-aware)
        self._style_secondary_button()

        self.setLayout(layout)

        # Internal state and settings
        self.download_path = ""
        self.settings = QSettings()
        # Restore settings
        saved_dir = self.settings.value('downloader/download_path', '')
        if saved_dir:
            self.download_path = saved_dir
            self.path_display.setText(self.download_path)
        saved_res = self.settings.value('downloader/resolution', '')
        if saved_res:
            idx = self.resolution_combo.findText(str(saved_res))
            if idx >= 0:
                self.resolution_combo.setCurrentIndex(idx)
        self.resolution_combo.currentTextChanged.connect(self._save_resolution)
        # initial button state based on current fields
        self._on_url_changed(self.url_input.text())

        
    def closeEvent(self, event):
        #self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close event
        
    def select_path(self):
        self.download_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if self.download_path:
            self.path_display.setText(self.download_path)
            self.settings.setValue('downloader/download_path', self.download_path)
        else:
            self.path_display.clear()
        # recompute enabled state
        self._on_url_changed(self.url_input.text())

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
        self.status_label.setText("Downloading...")
        self._set_progress_color(None)
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
        self.progress.setFormat("%p%")
        self.status_label.setText("Downloading...")

        self.thread.start()

    def cancel_download(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.cancel()
            self.status_label.setText("Cancelling…")

    def _on_finished(self):
        self.progress.setValue(100)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._set_progress_color('success')
        self.status_label.setText("Download complete")

    def _on_error(self, msg: str):
        QMessageBox.critical(self, "Download Error", msg)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._set_progress_color('error')
        self.status_label.setText("Error")

    def _save_resolution(self, value: str):
        self.settings.setValue('downloader/resolution', value)

    def _on_url_changed(self, text: str):
        # Enable Download only with a valid http(s) URL and selected path
        is_valid = bool(re.match(r"^https?://", (text or '').strip()))
        self.download_button.setEnabled(is_valid and bool(self.download_path))
        if not (text or '').strip():
            self.status_label.setText("Waiting for URL...")

    def _paste_from_clipboard(self):
        cb = QApplication.clipboard()
        if not cb:
            return
        txt = cb.text() or ''
        if txt:
            self.url_input.setText(txt)

    def _style_secondary_button(self):
        # Light/dark aware neutral look for cancel button
        pal = self.palette()
        base = pal.color(pal.Button)
        text = pal.color(pal.ButtonText)
        self.cancel_button.setStyleSheet(
            f"QPushButton {{ background-color: {base.name()}; color: {text.name()}; border-radius: 10px; padding: 8px 14px; }}\n"
            f"QPushButton:hover {{ opacity: 0.95; }}\n"
            f"QPushButton:pressed {{ opacity: 0.9; }}"
        )

    def _set_progress_color(self, mode: str):
        # None: reset to theme accent, success: green, error: red
        if mode == 'success':
            color = '#10b981'
        elif mode == 'error':
            color = '#ef4444'
        else:
            self.progress.setStyleSheet("")
            return
        self.progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 8px; }}")

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
        pct = int(downloaded * 100 / max(1, total)) if total else 0
        self.progress.setFormat(f"{pct}%")
        # Keep detailed info as tooltip
        text = f"{_fmt_size(downloaded)} / { _fmt_size(total) }  |  {_fmt_speed(speed)}  |  ETA: {_fmt_eta(eta)}"
        self.progress.setToolTip(text)


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
        base_opts = {
            'outtmpl': os.path.join(self.out_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._hook],
            'noplaylist': True,
            'noprogress': False,
            # Prefer mp4 merge when possible
            'merge_output_format': 'mp4',
            'retries': 3,
        }
        # Tolerant format selector with fallbacks by height, then best
        fmt_pref = (
            f"bestvideo*[height<={self.max_height}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo*[height<={self.max_height}]+bestaudio/"
            f"best[height<={self.max_height}][ext=mp4]/"
            f"best[height<={self.max_height}]/best"
        )

        attempted_msgs = []
        # Try multiple player clients; yt-dlp expects a list value
        for client in ['android', 'mweb', 'web', 'ios', 'tv']:
            try:
                opts = dict(base_opts)
                opts['format'] = fmt_pref
                opts['extractor_args'] = {'youtube': {'player_client': [client]}}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([self.url])
                self.finished.emit()
                return
            except Exception as e1:
                try:
                    opts = dict(base_opts)
                    opts['format'] = 'best'
                    opts['extractor_args'] = {'youtube': {'player_client': [client]}}
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        ydl.download([self.url])
                    self.finished.emit()
                    return
                except Exception as e2:
                    attempted_msgs.append(f"{client}: {str(e2) or str(e1)}")

        # If all failed, try to provide helpful info about available formats
        msg = "Requested format is not available.\n" + "\n".join(attempted_msgs)
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'extractor_args': {'youtube': {'player_client': ['android']}}}) as ydl:
                info = ydl.extract_info(self.url, download=False)
            formats = info.get('formats') or []
            heights = sorted({f.get('height') for f in formats if f.get('url') and (f.get('vcodec') or '') != 'none'})
            if heights:
                msg += f"\nAvailable heights: {', '.join(str(h) for h in heights if h)}"
            else:
                msg += "\nNo downloadable video streams were found (YouTube may be restricting this content for this client)."
        except Exception:
            pass
        self.error.emit(msg)
        self.finished.emit()
