import os
import sys
import time
from typing import Optional, List
import mimetypes

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QSettings, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QProgressBar,
    QMessageBox,
)

# Google API imports (runtime deps)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# Button styling is handled globally via the app theme (QSS)


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploaderWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("YouTube Uploader")
        self.setGeometry(100, 100, 640, 600)

        layout = QVBoxLayout()

        # Video file
        self.video_label = QLabel("Video file:")
        self.video_path = QLineEdit()
        btn_browse_video = QPushButton("Browse")
        btn_browse_video.clicked.connect(self._choose_video)
        row1 = QHBoxLayout()
        row1.addWidget(self.video_label)
        row1.addWidget(self.video_path)
        row1.addWidget(btn_browse_video)
        layout.addLayout(row1)

        # Title
        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Description
        self.desc_label = QLabel("Description:")
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(120)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)

        # Tags
        self.tags_label = QLabel("Tags (comma-separated):")
        self.tags_input = QLineEdit()
        layout.addWidget(self.tags_label)
        layout.addWidget(self.tags_input)

        # Category and Privacy
        row2 = QHBoxLayout()
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        # Common categories; users can edit later if needed
        categories = [
            (1, "Film & Animation"), (2, "Autos & Vehicles"), (10, "Music"),
            (15, "Pets & Animals"), (17, "Sports"), (19, "Travel & Events"),
            (20, "Gaming"), (22, "People & Blogs"), (23, "Comedy"),
            (24, "Entertainment"), (25, "News & Politics"), (26, "Howto & Style"),
            (27, "Education"), (28, "Science & Technology"), (29, "Nonprofits & Activism"),
        ]
        for cid, name in categories:
            self.category_combo.addItem(name, cid)

        self.privacy_label = QLabel("Privacy:")
        self.privacy_combo = QComboBox()
        self.privacy_combo.addItems(["public", "unlisted", "private"])

        row2.addWidget(self.category_label)
        row2.addWidget(self.category_combo)
        row2.addSpacing(16)
        row2.addWidget(self.privacy_label)
        row2.addWidget(self.privacy_combo)
        layout.addLayout(row2)

        # Credentials path
        self.creds_label = QLabel("Google credentials.json:")
        self.creds_path = QLineEdit()
        btn_browse_creds = QPushButton("Browse")
        btn_browse_creds.clicked.connect(self._choose_creds)
        row3 = QHBoxLayout()
        row3.addWidget(self.creds_label)
        row3.addWidget(self.creds_path)
        row3.addWidget(btn_browse_creds)
        layout.addLayout(row3)

        # Thumbnail (optional)
        self.thumb_label = QLabel("Thumbnail (optional):")
        self.thumb_path = QLineEdit()
        btn_browse_thumb = QPushButton("Browse")
        btn_browse_thumb.clicked.connect(self._choose_thumbnail)
        row4 = QHBoxLayout()
        row4.addWidget(self.thumb_label)
        row4.addWidget(self.thumb_path)
        row4.addWidget(btn_browse_thumb)
        layout.addLayout(row4)

        # Progress + Buttons
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        controls = QHBoxLayout()
        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self._start_upload)
        controls.addWidget(self.upload_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_upload)
        controls.addWidget(self.cancel_button)

        layout.addLayout(controls)
        self.setLayout(layout)

        # Restore settings
        self._restore_settings()

    def _restore_settings(self):
        vp = self.settings.value('uploader/video_path', '')
        if vp:
            self.video_path.setText(vp)
        tp = self.settings.value('uploader/title', '')
        if tp:
            self.title_input.setText(tp)
        cp = self.settings.value('uploader/creds_path', '')
        if cp:
            self.creds_path.setText(cp)
        pr = self.settings.value('uploader/privacy', 'unlisted')
        idx = self.privacy_combo.findText(pr) if pr else -1
        if idx >= 0:
            self.privacy_combo.setCurrentIndex(idx)
        cat_id = int(self.settings.value('uploader/category', 27))
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == cat_id:
                self.category_combo.setCurrentIndex(i)
                break

    def _choose_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Video File')
        if file_path:
            self.video_path.setText(file_path)
            self.settings.setValue('uploader/video_path', file_path)

    def _choose_creds(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select credentials.json', filter="JSON files (*.json)")
        if file_path:
            self.creds_path.setText(file_path)
            self.settings.setValue('uploader/creds_path', file_path)

    def _choose_thumbnail(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Thumbnail Image', filter="Images (*.jpg *.jpeg *.png *.gif)")
        if file_path:
            self.thumb_path.setText(file_path)

    def _start_upload(self):
        video = self.video_path.text().strip()
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText()
        tags = [t.strip() for t in self.tags_input.text().split(',') if t.strip()]
        category_id = int(self.category_combo.currentData())
        privacy = self.privacy_combo.currentText()
        creds_file = self.creds_path.text().strip()

        if not os.path.isfile(video):
            QMessageBox.warning(self, "Missing Video", "Please select a valid video file.")
            return
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a title.")
            return
        if not os.path.isfile(creds_file):
            QMessageBox.warning(self, "Missing Credentials", "Please provide a valid Google API credentials.json file.")
            return

        # Persist fields
        self.settings.setValue('uploader/title', title)
        self.settings.setValue('uploader/privacy', privacy)
        self.settings.setValue('uploader/category', category_id)

        # Start worker thread
        self.thread = QThread()
        self.worker = _YouTubeUploadWorker(
            video_path=video,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy,
            creds_file=creds_file,
            thumbnail_path=self.thumb_path.text().strip() or None,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.upload_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress.setValue(0)

        self.thread.start()

    def _cancel_upload(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.cancel()

    def _on_progress(self, percent: int):
        self.progress.setValue(percent)

    def _on_finished(self):
        self.progress.setValue(100)
        self.upload_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.information(self, "Upload", "Upload completed.")

    def _on_error(self, msg: str):
        self.upload_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.critical(self, "Upload Error", msg)


class _YouTubeUploadWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        category_id: int,
        privacy_status: str,
        creds_file: str,
        thumbnail_path: Optional[str] = None,
    ):
        super().__init__()
        self.video_path = video_path
        self.title = title
        self.description = description
        self.tags = tags
        self.category_id = category_id
        self.privacy_status = privacy_status
        self.creds_file = creds_file
        self.thumbnail_path = thumbnail_path
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _get_credentials(self) -> Credentials:
        token_path = os.path.join(os.path.expanduser("~"), ".video_manager", "youtube_token.json")
        os.makedirs(os.path.dirname(token_path), exist_ok=True)

        creds: Optional[Credentials] = None
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception:
                creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # type: ignore[name-defined]
                except Exception:
                    creds = None
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def run(self):
        try:
            creds = self._get_credentials()
            youtube = build('youtube', 'v3', credentials=creds)

            body = {
                'snippet': {
                    'title': self.title,
                    'description': self.description,
                    'tags': self.tags,
                    'categoryId': str(self.category_id),
                },
                'status': {
                    'privacyStatus': self.privacy_status,
                },
            }

            media = MediaFileUpload(self.video_path, chunksize=5 * 1024 * 1024, resumable=True)
            request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)

            response = None
            last_percent = -1
            while response is None:
                if self._cancel:
                    raise Exception('Cancelled by user')
                status, response = request.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    if pct != last_percent:
                        last_percent = pct
                        self.progress.emit(pct)
                time.sleep(0.05)

            # Optionally set thumbnail
            try:
                if self.thumbnail_path and os.path.isfile(self.thumbnail_path):
                    video_id = response.get('id') if isinstance(response, dict) else None
                    if video_id:
                        mime, _ = mimetypes.guess_type(self.thumbnail_path)
                        thumb_media = MediaFileUpload(self.thumbnail_path, mimetype=mime, resumable=False)
                        youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
            except Exception:
                # Non-fatal: continue even if thumbnail set fails
                pass

            self.progress.emit(100)
            self.finished.emit()
        except HttpError as e:
            self.error.emit(f"YouTube API error: {e}")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()
