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
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QCheckBox,
    QProgressBar,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QSettings
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import subprocess
import re
import shutil


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

class VideoSplitterWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window 
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Splitter")
        self.setGeometry(100, 100, 500, 300)  # Set window size

        layout = QVBoxLayout()

        # Custom font
        font = QFont("Arial", 11)

        # Input video file
        self.video_label = QLabel('Select video file:')
        self.video_label.setFont(font)
        self.video_button = QPushButton('Browse', self)
        self.video_button.setFont(font)
        self.video_button.setStyleSheet(button_style)
        self.video_button.clicked.connect(self.select_video)
        self.video_path = QLineEdit(self)
        self.video_path.setFont(font)
        layout.addWidget(self.video_label)
        layout.addWidget(self.video_path)
        layout.addWidget(self.video_button)

        # Chapters file
        self.chapters_label = QLabel('Select chapters file:')
        self.chapters_label.setFont(font)
        self.chapters_button = QPushButton('Browse', self)
        self.chapters_button.setFont(font)
        self.chapters_button.setStyleSheet(button_style)
        self.chapters_button.clicked.connect(self.select_chapters)
        self.chapters_path = QLineEdit(self)
        self.chapters_path.setFont(font)
        layout.addWidget(self.chapters_label)
        layout.addWidget(self.chapters_path)
        layout.addWidget(self.chapters_button)

        # Destination path
        self.destination_button = QPushButton('Select Destination', self)
        self.destination_button.setFont(font)
        self.destination_button.setStyleSheet(button_style)
        self.destination_button.clicked.connect(self.select_destination)
        layout.addWidget(self.destination_button)

        # Label to display selected destination path
        self.destination_label = QLabel('No destination selected')
        self.destination_label.setFont(font)
        layout.addWidget(self.destination_label)

        # Options
        self.accurate_checkbox = QCheckBox('Accurate cut (re-encode)')
        self.accurate_checkbox.setFont(font)
        layout.addWidget(self.accurate_checkbox)

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Split button
        controls = QHBoxLayout()
        self.split_button = QPushButton('Split Video', self)
        self.split_button.setFont(font)
        self.split_button.setStyleSheet(button_style)
        self.split_button.clicked.connect(self.split_video)
        controls.addWidget(self.split_button)

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.setFont(font)
        self.cancel_button.setStyleSheet(button_style)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_split)
        controls.addWidget(self.cancel_button)
        layout.addLayout(controls)

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Internal state
        self.destination_path = ""
        self.settings = QSettings()
        # Restore saved values
        saved_video = self.settings.value('splitter/video_path', '')
        if saved_video:
            self.video_path.setText(saved_video)
        saved_chapters = self.settings.value('splitter/chapters_path', '')
        if saved_chapters:
            self.chapters_path.setText(saved_chapters)
        saved_dest = self.settings.value('splitter/destination_path', '')
        if saved_dest:
            self.destination_path = saved_dest
            self.destination_label.setText(f"Destination: {self.destination_path}")
        saved_accurate = self.settings.value('splitter/accurate', False, type=bool)
        self.accurate_checkbox.setChecked(bool(saved_accurate))
        self.accurate_checkbox.stateChanged.connect(lambda _: self.settings.setValue('splitter/accurate', self.accurate_checkbox.isChecked()))


    def closeEvent(self, event):
        #self.main_window.show()  # Show the main window again when this window is closed
        event.accept()  # Accept the close even

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Video File')
        if file_path:
            self.video_path.setText(file_path)
            self.settings.setValue('splitter/video_path', file_path)

    def select_chapters(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Chapters File')
        if file_path:
            self.chapters_path.setText(file_path)
            self.settings.setValue('splitter/chapters_path', file_path)

    def select_destination(self):
        self.destination_path = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if self.destination_path:
            self.destination_label.setText(f"Destination: {self.destination_path}")
            self.settings.setValue('splitter/destination_path', self.destination_path)
        else:
            self.destination_label.setText("No destination selected")

    def split_video(self):
        video_file = self.video_path.text().strip()
        chapters_file = self.chapters_path.text().strip()

        if not video_file:
            QMessageBox.warning(self, "Missing Video", "Please select an input video file.")
            return
        if not chapters_file:
            QMessageBox.warning(self, "Missing Chapters", "Please select a chapters text file.")
            return
        if not self.destination_path:
            QMessageBox.warning(self, "Select Destination", "Please choose an output folder.")
            return
        if shutil.which("ffmpeg") is None:
            QMessageBox.critical(self, "FFmpeg Not Found", "FFmpeg is required. Please install FFmpeg and ensure it is on your PATH.")
            return

        # Read and parse chapters
        with open(chapters_file, 'r', encoding='utf-8') as file:
            raw_lines = [line.strip() for line in file if line.strip()]

        chapters = []
        for line in raw_lines:
            m = re.match(r"^(\d{1,2}(:\d{2}){1,2})\s+(.+)$", line)
            if not m:
                continue
            ts = m.group(1)
            title = m.group(3)
            chapters.append((self.convert_time_to_seconds(ts), title))

        # Append end duration if needed
        chapters = self._ensure_final_segment(video_file, chapters)

        if len(chapters) < 2:
            QMessageBox.warning(self, "Invalid Chapters", "Need at least two timestamps to form a segment.")
            return

        # Prepare and start worker
        self.thread = QThread()
        self.worker = _SplitWorker(
            video_file=video_file,
            chapters=chapters,
            dest_dir=self.destination_path,
            accurate=self.accurate_checkbox.isChecked(),
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Toggle buttons
        self.split_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress.setValue(0)

        self.thread.start()

    def cancel_split(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.cancel()

    def convert_time_to_seconds(self, time_str):
        parts = time_str.split(':')
        parts = [0] * (3 - len(parts)) + parts
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s

    def _safe_filename(self, name: str) -> str:
        # Remove illegal filename characters and trim
        name = re.sub(r"[\\/:*?\"<>|]", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name[:200]

    def _on_progress(self, percent: int, current_title: str):
        self.progress.setValue(percent)
        # Optional: could update window title or label with current_title

    def _on_finished(self):
        self.progress.setValue(100)
        self.split_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _on_error(self, msg: str):
        QMessageBox.critical(self, "Split Error", msg)
        self.split_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _ensure_final_segment(self, video_file: str, chapters):
        # chapters: list of (start_seconds, title)
        if len(chapters) < 1:
            return chapters
        duration = self._get_video_duration(video_file)
        if not duration:
            return chapters
        last_start, last_title = chapters[-1]
        if last_start < int(duration) and (len(chapters) == 1 or chapters[-1][0] != int(duration)):
            # Append synthetic end marker title
            chapters = chapters + [(int(duration), f"End")]  # title not used for end
        return chapters

    def _get_video_duration(self, video_file: str):
        # Try ffprobe first
        if shutil.which('ffprobe') is not None:
            try:
                out = subprocess.check_output([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', video_file
                ])
                return float(out.decode('utf-8').strip())
            except Exception:
                pass
        # Fallback to moviepy
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(video_file) as clip:
                return float(clip.duration)
        except Exception:
            return None


class _SplitWorker(QObject):
    progress = pyqtSignal(int, str)  # percent, current title
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, video_file: str, chapters, dest_dir: str, accurate: bool):
        super().__init__()
        self.video_file = video_file
        self.chapters = chapters  # list of (start_seconds, title) plus final end marker
        self.dest_dir = dest_dir
        self.accurate = accurate
        self._cancel = False
        self._current_proc = None

    def cancel(self):
        self._cancel = True
        if self._current_proc and self._current_proc.poll() is None:
            try:
                self._current_proc.terminate()
            except Exception:
                pass

    def run(self):
        try:
            total_segments = max(0, len(self.chapters) - 1)
            for i in range(total_segments):
                if self._cancel:
                    raise Exception('Cancelled by user')
                start_time, title = self.chapters[i]
                end_time, _ = self.chapters[i + 1]
                safe_title = self._safe_filename(title) or f"part_{i+1:02d}"
                output_path = os.path.join(self.dest_dir, f"{safe_title}.mp4")

                cmd = self._build_ffmpeg_cmd(start_time, end_time, output_path)
                self.progress.emit(int(i * 100 / max(1, total_segments)), title)
                self._current_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True,
                )

                seg_duration = max(1e-6, float(end_time - start_time))
                current_percent = 0
                # Parse progress lines
                if self._current_proc.stdout:
                    for line in self._current_proc.stdout:
                        if self._cancel:
                            self._current_proc.terminate()
                            raise Exception('Cancelled by user')
                        line = line.strip()
                        if not line or '=' not in line:
                            continue
                        key, val = line.split('=', 1)
                        if key == 'out_time_ms':
                            try:
                                out_s = float(val) / 1_000_000.0
                            except Exception:
                                continue
                            seg_progress = min(1.0, out_s / seg_duration)
                            overall = int(((i + seg_progress) * 100) / max(1, total_segments))
                            if overall != current_percent:
                                current_percent = overall
                                self.progress.emit(current_percent, title)
                        elif key == 'out_time':
                            # Format HH:MM:SS.microseconds
                            parts = val.split(':')
                            try:
                                h = float(parts[0]); m = float(parts[1]); s = float(parts[2])
                                out_s = h*3600 + m*60 + s
                                seg_progress = min(1.0, out_s / seg_duration)
                                overall = int(((i + seg_progress) * 100) / max(1, total_segments))
                                if overall != current_percent:
                                    current_percent = overall
                                    self.progress.emit(current_percent, title)
                            except Exception:
                                pass
                _, err = self._current_proc.communicate()
                if self._current_proc.returncode != 0:
                    raise Exception(err.decode('utf-8', errors='ignore') or 'FFmpeg failed')
            self.progress.emit(100, '')
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()

    def _build_ffmpeg_cmd(self, start_time, end_time, output_path):
        base = ['ffmpeg', '-y']
        if self.accurate:
            cmd = base + [
                '-ss', str(start_time), '-to', str(end_time), '-i', self.video_file,
                '-c:v', 'libx264', '-preset', 'faster', '-crf', '22', '-c:a', 'aac', '-movflags', '+faststart',
            ]
        else:
            cmd = base + [
                '-i', self.video_file,
                '-ss', str(start_time), '-to', str(end_time),
                '-c', 'copy',
            ]
        # Add progress reporting
        cmd += ['-progress', 'pipe:1', '-nostats', output_path]
        return cmd

    def _safe_filename(self, name: str) -> str:
        name = re.sub(r"[\\/:*?\"<>|]", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name[:200]
