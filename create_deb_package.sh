#!/bin/bash

# Set variables
APP_NAME="video-manager"  # Changed to hyphen for debian package naming rules
MAIN_FILE="video_manager.py"
ICON_PATH="./icons/icon.png"
CONFIG_DIR="config"  # Adjust based on your project structure.
VERSION=$(grep -oP '(?<=__version__ = ")[^"]+' __version__.py)
ARCH="amd64"  # Change this based on system architecture (e.g., i386 for 32-bit)
OUTPUT_EXEC="video_manager"  # Explicitly set the output executable name

# Ensure we're in the script directory
cd "$(dirname "$0")"

# Check if VERSION was successfully extracted
if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from __version__.py."
    exit 1
fi

# Step 1: Install necessary Python dependencies
echo "Installing necessary Python dependencies..."
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install pyinstaller yt-dlp moviepy PyQt5 PyQtWebEngine

# Step 2: Run PyInstaller to create a standalone executable
echo "Running PyInstaller to build the application..."
pyinstaller --onefile --name "$OUTPUT_EXEC" \
            --add-data "$CONFIG_DIR:$CONFIG_DIR" \
            --add-data "youtube_downloader.py:." \
            --add-data "video_splitter.py:." \
            --add-data "video_editor.py:." \
            --add-data "youtube_uploader.py:." \
            --hidden-import yt_dlp \
            --hidden-import moviepy \
            --hidden-import moviepy.video \
            --hidden-import moviepy.video.io \
            --hidden-import moviepy.video.io.ffmpeg_tools \
            --hidden-import PyQt5.QtWebEngineWidgets \
            --hidden-import googleapiclient.discovery \
            --hidden-import googleapiclient.http \
            --hidden-import googleapiclient.errors \
            --hidden-import google.oauth2.credentials \
            --hidden-import google_auth_oauthlib.flow \
            "$MAIN_FILE"

# Check if the build was successful
if [ -f "dist/$OUTPUT_EXEC" ]; then
    echo "Build successful. Executable created at dist/$OUTPUT_EXEC"
else
    echo "PyInstaller failed to create the executable. Aborting."
    exit 1
fi

# Step 3: Prepare the directory structure for the .deb package
PACKAGE_DIR="./dist/${APP_NAME}_${VERSION}_${ARCH}"
DEBIAN_DIR="$PACKAGE_DIR/DEBIAN"
BIN_DIR="$PACKAGE_DIR/usr/local/bin"
ICON_DIR="$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$PACKAGE_DIR/usr/share/applications"

mkdir -p "$DEBIAN_DIR" "$BIN_DIR" "$ICON_DIR" "$DESKTOP_DIR"

# Step 4: Copy executable and icon
cp "dist/$OUTPUT_EXEC" "$BIN_DIR/$APP_NAME"
chmod +x "$BIN_DIR/$APP_NAME"

cp "$ICON_PATH" "$ICON_DIR/$APP_NAME.png"  # Convert .webp to .png for compatibility if needed.

# Step 5: Create the control file for the package metadata
CONTROL_FILE="$DEBIAN_DIR/control"
cat <<EOL > "$CONTROL_FILE"
Package: $APP_NAME
Version: $VERSION
Section: base
Priority: optional
Architecture: $ARCH
Depends: python3, python3-pyqt5, python3-moviepy
Maintainer: Your Name brahim.elhamdaoui@yahoo.de
Description: A tool for downloading YouTube videos and splitting videos.
EOL

# Step 6: Create a .desktop entry for the application menu
DESKTOP_FILE="$DESKTOP_DIR/$APP_NAME.desktop"
cat <<EOL > "$DESKTOP_FILE"
[Desktop Entry]
Version=$VERSION
Name=Video Manager
Comment=A tool for downloading YouTube videos and splitting videos
Exec=/usr/local/bin/$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Utility;
EOL

# Step 7: Build the .deb package
echo "Building the .deb package..."
dpkg-deb --build "$PACKAGE_DIR"

# Step 8: Clean up
echo "Cleaning up..."
rm -rf "$PACKAGE_DIR"

echo "Deployment complete. You can find the .deb package as ${PACKAGE_DIR}.deb."
