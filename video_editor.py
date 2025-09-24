import sys
import os
import re
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QFileDialog, QMessageBox, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class VideoEditorWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Basic Video Editor")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(QtCore.Qt.AlignTop)

        # Compact form for source selection
        form = QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setFormAlignment(QtCore.Qt.AlignTop)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        top = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube URL or MP4 path/URL")
        top.addWidget(self.url_input, 1)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        top.addWidget(self.browse_btn)
        form.addRow(QLabel("Source:"), top)
        layout.addLayout(form)

        # Load Video Button
        self.load_button = QPushButton('Load Video', self)
        self.load_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_button)

        # Video player for MP4 streams
        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.player.error.connect(self._on_player_error)
        layout.addWidget(self.video_widget)

        # Web view fallback (YouTube embed or general URLs)
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.video_widget.hide()
        self.browser.hide()
        self._shown_gst_help = False

        self.setLayout(layout)

    def load_video(self):
        text = self.url_input.text().strip()
        if not text:
            return
        # If local mp4 path
        if self.is_local_mp4(text):
            url = QUrl.fromLocalFile(os.path.abspath(text))
            self._play_mp4(url)
            return
        # If MP4 over HTTP(S)
        if re.match(r"^https?://", text) and text.lower().endswith(".mp4"):
            self._play_mp4(QUrl(text))
            return
        # If YouTube URL → try to fetch a progressive MP4 and play via QMediaPlayer
        vid = self.extract_video_id(text)
        if vid:
            self._load_youtube_progressive(text)
            return
        # Fallback: try to treat as URL
        if re.match(r"^https?://", text):
            self.browser.setUrl(QUrl(text))

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select MP4 File", filter="MP4 files (*.mp4)")
        if path:
            self.url_input.setText(path)
            self._play_mp4(QUrl.fromLocalFile(path))

    def extract_video_id(self, url):
        # Regular expression to extract the video ID from YouTube URL
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return None

    def is_local_mp4(self, path: str) -> bool:
        try:
            return os.path.isfile(path) and path.lower().endswith('.mp4')
        except Exception:
            return False

    def _play_mp4(self, url: QUrl):
        try:
            self.browser.hide()
            self.video_widget.show()
            self.player.stop()
            self.player.setMedia(QMediaContent(url))
            self.player.play()
        except Exception:
            # Fallback to web HTML5 if multimedia fails
            src = url.toString()
            html = f"""
            <!doctype html>
            <html><body style='margin:0;background:#000'>
            <video controls autoplay style='width:100%;height:100%'>
                <source src="{src}" type="video/mp4">
            </video>
            </body></html>
            """
            base = QUrl.fromLocalFile(os.path.dirname(url.toLocalFile()) + "/") if url.isLocalFile() else url
            self.video_widget.hide()
            self.browser.show()
            self.browser.setHtml(html, base)

    def _load_youtube_progressive(self, yt_url: str):
        # Run yt-dlp in a worker thread to avoid blocking UI
        try:
            self._yt_thread = QThread()
            self._yt_worker = _YTDLWorker(yt_url)
            self._yt_worker.moveToThread(self._yt_thread)
            self._yt_thread.started.connect(self._yt_worker.run)
            self._yt_worker.result.connect(self._on_ytdl_result)
            self._yt_worker.finished.connect(self._yt_thread.quit)
            self._yt_worker.finished.connect(self._yt_worker.deleteLater)
            self._yt_thread.finished.connect(self._yt_thread.deleteLater)
            self._yt_thread.start()
        except Exception:
            # Fallback to embed if threading fails
            vid = self.extract_video_id(yt_url)
            if vid:
                self.browser.show()
                self.video_widget.hide()
                self.browser.setUrl(QUrl(f"https://www.youtube.com/embed/{vid}"))

    def _on_ytdl_result(self, direct_url: str, error: str):
        if direct_url:
            self._play_mp4(QUrl(direct_url))
        else:
            # Fallback to YouTube embed (do not show codec dialog for yt-dlp issues)
            vid = self.extract_video_id(self.url_input.text().strip())
            if vid:
                self.video_widget.hide()
                self.browser.show()
                self.browser.setUrl(QUrl(f"https://www.youtube.com/embed/{vid}"))

    def closeEvent(self, event):
        # self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close event

    # Friendly guidance when multimedia backends/codecs are missing
    def _on_player_error(self):
        err = self.player.errorString() or ""
        if not self._shown_gst_help:
            self._show_gst_help(extra_detail=err)

    def _show_gst_help(self, extra_detail: str = ""):
        self._shown_gst_help = True
        msg = (
            "Video playback backend is missing codecs.\n\n"
            "Install GStreamer codecs for H.264/AAC:\n\n"
            "Debian/Ubuntu:\n  sudo apt install gstreamer1.0-libav gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libqt5multimedia5-plugins\n\n"
            "Fedora/RHEL:\n  sudo dnf install gstreamer1-plugins-\{good,bad-free,ugly-free\} gstreamer1-libav qt5-qtmultimedia\n\n"
            "Arch/Manjaro:\n  sudo pacman -S gstreamer gst-plugins-\{base,good,bad,ugly\} gst-libav qt5-multimedia\n\n"
            "openSUSE:\n  sudo zypper install gstreamer-plugins-\{base,good,bad,ugly\} gstreamer-libav libqt5-qtmultimedia\n"
        )
        if extra_detail:
            msg += f"\nDetails: {extra_detail}"
        QMessageBox.warning(self, "Missing Codecs", msg)


class _YTDLWorker(QObject):
    result = pyqtSignal(str, str)  # (direct_url, error)
    finished = pyqtSignal()

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            import yt_dlp
            errors = []
            for client in ['android', 'mweb', 'web', 'ios', 'tv']:
                try:
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'skip_download': True,
                        'extractor_args': {'youtube': {'player_client': [client]}},
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.url, download=False)
                    direct = self._pick_progressive(info)
                    if direct:
                        self.result.emit(direct, '')
                        return
                except Exception as e:
                    errors.append(f"{client}: {e}")
            # No progressive found → report first error string
            self.result.emit('', "; ".join(errors) if errors else 'no-progressive-found')
        except Exception as e:
            self.result.emit('', str(e))
        finally:
            self.finished.emit()

    def _pick_progressive(self, info) -> str:
        formats = info.get('formats') or []
        best = None
        for f in formats:
            if f.get('vcodec') == 'none' or f.get('acodec') == 'none':
                continue  # require progressive
            if not str(f.get('protocol', '')).startswith('http'):
                continue
            # prefer mp4 and <= 1080p
            score = 0
            if (f.get('ext') or '').lower() == 'mp4':
                score += 10
            height = f.get('height') or 0
            score += min(height, 1080) / 100.0
            if not best or score > best[0]:
                best = (score, f.get('url'))
        return best[1] if best else ''
