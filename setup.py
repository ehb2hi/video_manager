# MIT License
# Copyright (c) 2024-2025 Brahim El Hamdaoui
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

from setuptools import setup


def get_version():
    version_ns = {}
    with open("__version__.py") as f:
        exec(f.read(), version_ns)
    return version_ns["__version__"]


setup(
    name="video_manager",
    version=get_version(),
    description="Download YouTube videos and split videos into chapters.",
    author="Brahim El Hamdaoui",
    author_email="",
    python_requires=">=3.10",
    # Flat-layout modules
    py_modules=[
        "video_manager",
        "youtube_downloader",
        "video_splitter",
        "video_editor",
        "youtube_uploader",
    ],
    install_requires=[
        "yt-dlp",
        "moviepy",
        "PyQt5",
        "PyQtWebEngine",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
    ],
    entry_points={
        "console_scripts": [
            "video_manager=video_manager:main",
        ]
    },
)
