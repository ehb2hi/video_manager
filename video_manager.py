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
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QDockWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMdiArea,
    QMdiSubWindow,
    QAction,
    QStyle,
    QColorDialog,
)
try:
    from PyQt5.QtSvg import QSvgRenderer
except Exception:  # QtSvg not always present
    QSvgRenderer = None
from youtube_downloader import YouTubeDownloaderWindow
from video_splitter import VideoSplitterWindow
from video_editor import VideoEditorWindow
from youtube_uploader import YouTubeUploaderWindow


# Resolve resource paths (works in source and PyInstaller one-file)
def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Tools")
        self.resize(1100, 700)
        self.setMinimumSize(800, 600)
        try:
            self.setWindowIcon(QIcon(resource_path("icons/icon.png")))
        except Exception:
            pass

        # Global style: Fusion for consistency
        QApplication.setStyle("Fusion")

        # Central MDI area where tools open as subwindows
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        # Left dock: Tools panel with horizontal button labels
        self.tools_dock = QDockWidget("Tools", self)
        self.tools_dock.setObjectName("tools_dock")
        self.tools_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.tools_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )

        tools_container = QWidget(self.tools_dock)
        tools_layout = QVBoxLayout()
        tools_layout.setContentsMargins(8, 8, 8, 8)
        tools_layout.setSpacing(8)
        tools_container.setLayout(tools_layout)

        def _icon(name: str, fallback_sp=None, path: str = None):
            # Try themed icon first
            if path:
                p = resource_path(path)
                if QSvgRenderer is not None and p.lower().endswith('.svg'):
                    try:
                        sizes = [16, 22, 24, 32]
                        icon = QIcon()
                        for sz in sizes:
                            pm = QtCore.QPixmap(sz, sz)
                            pm.fill(Qt.transparent)
                            r = QSvgRenderer(p)
                            if r.isValid():
                                painter = QtGui.QPainter(pm)
                                r.render(painter)
                                painter.end()
                                icon.addPixmap(pm)
                        if not icon.isNull():
                            return icon
                    except Exception:
                        pass
                # fallback: load whatever Qt can from file
                ico = QIcon(p)
                if not ico.isNull():
                    return ico
            ico = QIcon.fromTheme(name)
            if not ico.isNull():
                return ico
            # Try style standard pixmap
            if fallback_sp is not None:
                return self.style().standardIcon(fallback_sp)
            # Fallback to app icon
            try:
                return QIcon("icons/icon.png")
            except Exception:
                return QIcon()

        def make_button(text, handler, icon_name=None, sp=None, icon_path=None):
            btn = QPushButton(text)
            btn.setMinimumHeight(36)
            btn.clicked.connect(handler)
            if icon_name or sp is not None or icon_path:
                btn.setIcon(_icon(icon_name or "", sp, icon_path))
                btn.setIconSize(QtCore.QSize(18, 18))
            # Use global theme styles; avoid per-button overrides
            # subtle shadow for depth
            try:
                effect = QtWidgets.QGraphicsDropShadowEffect(self)
            except Exception:
                effect = None
            if effect:
                effect.setBlurRadius(16)
                effect.setOffset(0, 2)
                effect.setColor(QColor(0, 0, 0, 40))
                btn.setGraphicsEffect(effect)
                btn.installEventFilter(self)
            return btn

        self._subwindows = {}
        # expose icon helper for reuse in open_tool
        self._icon = _icon

        self._tool_buttons = []
        b = make_button(
                "YouTube Downloader",
                lambda: self.open_tool("downloader"),
                icon_name="download",
                sp=QStyle.SP_ArrowDown,
                icon_path="icons/downloader.svg",
            )
        self._tool_buttons.append(b)
        tools_layout.addWidget(b)
        b = make_button(
                "Video Splitter",
                lambda: self.open_tool("splitter"),
                icon_name="edit-cut",
                sp=QStyle.SP_TrashIcon,
                icon_path="icons/splitter.svg",
            )
        self._tool_buttons.append(b)
        tools_layout.addWidget(b)
        b = make_button(
                "Basic Video Editor",
                lambda: self.open_tool("editor"),
                icon_name="document-edit",
                sp=QStyle.SP_FileDialogDetailedView,
                icon_path="icons/editor.svg",
            )
        self._tool_buttons.append(b)
        tools_layout.addWidget(b)
        b = make_button(
                "YouTube Uploader",
                lambda: self.open_tool("uploader"),
                icon_name="document-send",
                sp=QStyle.SP_ArrowUp,
                icon_path="icons/uploader.svg",
            )
        self._tool_buttons.append(b)
        tools_layout.addWidget(b)
        tools_layout.addStretch(1)

        self.tools_dock.setWidget(tools_container)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tools_dock)

        # View menu with toggle for Tools panel
        view_menu = self.menuBar().addMenu("&View")
        self.toggle_tools_act = QAction(_icon("view-pane-show", QStyle.SP_DirOpenIcon, "icons/editor.svg"), "Tools Panel", self)
        self.toggle_tools_act.setCheckable(True)
        self.toggle_tools_act.setChecked(True)
        self.toggle_tools_act.setShortcut("Ctrl+T")
        self.toggle_tools_act.toggled.connect(self.tools_dock.setVisible)
        self.tools_dock.visibilityChanged.connect(self.toggle_tools_act.setChecked)
        view_menu.addAction(self.toggle_tools_act)

        # Toggle between SubWindow and Tabbed MDI modes
        self.toggle_tabbed_act = QAction(_icon("tab-new", QStyle.SP_FileDialogListView, "icons/downloader.svg"), "Tabbed MDI", self)
        self.toggle_tabbed_act.setCheckable(True)
        self.toggle_tabbed_act.setChecked(False)
        self.toggle_tabbed_act.setShortcut("Ctrl+Shift+T")
        def _toggle_tabbed(on: bool):
            if on:
                self.mdi.setViewMode(QMdiArea.TabbedView)
                self.mdi.setTabsClosable(True)
                self.mdi.setTabsMovable(True)
            else:
                self.mdi.setViewMode(QMdiArea.SubWindowView)
        self.toggle_tabbed_act.toggled.connect(_toggle_tabbed)
        view_menu.addAction(self.toggle_tabbed_act)

        # Theme menu
        theme_menu = self.menuBar().addMenu("&Theme")
        self.theme_light_act = QAction("Light", self, checkable=True)
        self.theme_dark_act = QAction("Dark", self, checkable=True)
        theme_menu.addAction(self.theme_light_act)
        theme_menu.addAction(self.theme_dark_act)

        theme_menu.addSeparator()
        self.accent_act = QAction("Accent Color…", self)
        theme_menu.addAction(self.accent_act)

        self.theme_light_act.triggered.connect(lambda: self.apply_theme("light"))
        self.theme_dark_act.triggered.connect(lambda: self.apply_theme("dark"))
        self.accent_act.triggered.connect(self.pick_accent_color)

        # Accent presets
        presets_menu = theme_menu.addMenu("Accent Presets")
        def preset(name, hex_):
            act = QAction(name, self)
            act.triggered.connect(lambda _, h=hex_: self.set_accent(h))
            presets_menu.addAction(act)
        preset("Amber", "#ffc107")
        preset("Indigo", "#6366f1")
        preset("Emerald", "#10b981")
        preset("Rose", "#f43f5e")

        # Load theme from settings (default: light)
        settings = QtCore.QSettings()
        theme = settings.value("ui/theme", "light")
        self.apply_theme(theme)

        # Density menu
        density_menu = self.menuBar().addMenu("&Density")
        self.density_comfy_act = QAction("Comfortable", self, checkable=True)
        self.density_compact_act = QAction("Compact", self, checkable=True)
        density_menu.addAction(self.density_comfy_act)
        density_menu.addAction(self.density_compact_act)
        self.density_comfy_act.triggered.connect(lambda: self.apply_density("comfortable"))
        self.density_compact_act.triggered.connect(lambda: self.apply_density("compact"))
        self.apply_density(settings.value("ui/density", "comfortable"))

        # Open first tool by default
        self.open_tool("downloader")

    def open_tool(self, key: str):
        # Reuse existing subwindow if open
        if key in self._subwindows:
            sub = self._subwindows[key]
            self.mdi.setActiveSubWindow(sub)
            sub.widget().setFocus()
            return

        # Create the tool widget
        if key == "downloader":
            widget = YouTubeDownloaderWindow(self)
            title = "YouTube Downloader"
            icon_path = "icons/downloader.svg"
            theme = "download"; sp = QStyle.SP_ArrowDown
        elif key == "splitter":
            widget = VideoSplitterWindow(self)
            title = "Video Splitter"
            icon_path = "icons/splitter.svg"
            theme = "edit-cut"; sp = QStyle.SP_TrashIcon
        elif key == "editor":
            widget = VideoEditorWindow(self)
            title = "Basic Video Editor"
            icon_path = "icons/editor.svg"
            theme = "document-edit"; sp = QStyle.SP_FileDialogDetailedView
        elif key == "uploader":
            widget = YouTubeUploaderWindow(self)
            title = "YouTube Uploader"
            icon_path = "icons/uploader.svg"
            theme = "document-send"; sp = QStyle.SP_ArrowUp
        else:
            return

        sub = QMdiSubWindow()
        sub.setWidget(widget)
        sub.setWindowTitle(title)
        # Set icon with fallbacks so tabs match the tool buttons
        try:
            ico = self._icon(theme, sp, icon_path)
            if not ico.isNull():
                widget.setWindowIcon(ico)
                sub.setWindowIcon(ico)
        except Exception:
            pass
        sub.setAttribute(Qt.WA_DeleteOnClose)
        sub.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        )
        # Subtle shadow for subwindow content (visible in SubWindowView)
        try:
            se = QtWidgets.QGraphicsDropShadowEffect(self)
            se.setBlurRadius(24)
            se.setOffset(0, 3)
            se.setColor(QColor(0, 0, 0, 60))
            widget.setGraphicsEffect(se)
        except Exception:
            pass
        self.mdi.addSubWindow(sub)
        sub.resize(900, 600)
        sub.show()
        self._subwindows[key] = sub
        # Clean up dict when closed
        sub.destroyed.connect(lambda: self._subwindows.pop(key, None))

    def apply_theme(self, name: str):
        name = (name or "light").lower()
        # mark menu state
        self.theme_light_act.setChecked(name == "light")
        self.theme_dark_act.setChecked(name == "dark")

        # load qss
        path = f"styles/theme_{name}.qss"
        try:
            with open(resource_path(path), "r", encoding="utf-8") as f:
                qss = f.read()
            # Accent colors (with defaults)
            s = QtCore.QSettings()
            accent = s.value("ui/accent", "#ffc107")
            accent_hover = s.value("ui/accent_hover", "#ffb300")
            accent_active = s.value("ui/accent_active", "#ff9800")
            qss = (
                qss.replace("${ACCENT}", accent)
                   .replace("${ACCENT_HOVER}", accent_hover)
                   .replace("${ACCENT_ACTIVE}", accent_active)
            )
            # Append density overrides if compact
            if QtCore.QSettings().value("ui/density", "comfortable") == "compact":
                try:
                    with open(resource_path("styles/density_compact.qss"), "r", encoding="utf-8") as df:
                        qss += "\n" + df.read()
                except Exception:
                    pass
            QApplication.instance().setStyleSheet(qss)
        except Exception:
            QApplication.instance().setStyleSheet("")

        # palette tweak for dark
        if name == "dark":
            pal = QPalette()
            pal.setColor(QPalette.Window, QColor(18,20,23))
            pal.setColor(QPalette.WindowText, QColor(229,231,235))
            pal.setColor(QPalette.Base, QColor(15,18,22))
            pal.setColor(QPalette.AlternateBase, QColor(27,31,36))
            pal.setColor(QPalette.ToolTipBase, QColor(27,31,36))
            pal.setColor(QPalette.ToolTipText, QColor(229,231,235))
            pal.setColor(QPalette.Text, QColor(229,231,235))
            pal.setColor(QPalette.Button, QColor(27,31,36))
            pal.setColor(QPalette.ButtonText, QColor(229,231,235))
            pal.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 124, 130))
            pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 124, 130))
            QApplication.instance().setPalette(pal)
        else:
            QApplication.instance().setPalette(QApplication.style().standardPalette())

        # persist
        settings = QtCore.QSettings()
        settings.setValue("ui/theme", name)

    def pick_accent_color(self):
        s = QtCore.QSettings()
        current = QColor(s.value("ui/accent", "#ffc107"))
        col = QColorDialog.getColor(current, self, "Choose Accent Color")
        if not col.isValid():
            return
        # derive hover and active (slightly darker)
        def darker(c: QColor, pct):
            d = QColor(c)
            d = d.darker(pct)
            return d.name()
        accent = col.name()
        accent_hover = darker(col, 110)  # 10% darker
        accent_active = darker(col, 125)  # 25% darker
        s.setValue("ui/accent", accent)
        s.setValue("ui/accent_hover", accent_hover)
        s.setValue("ui/accent_active", accent_active)
        self.apply_theme(QtCore.QSettings().value("ui/theme", "light"))

    def set_accent(self, hex_color: str):
        col = QColor(hex_color)
        if not col.isValid():
            return
        s = QtCore.QSettings()
        def darker(c: QColor, pct):
            d = QColor(c)
            d = d.darker(pct)
            return d.name()
        s.setValue("ui/accent", col.name())
        s.setValue("ui/accent_hover", darker(col, 110))
        s.setValue("ui/accent_active", darker(col, 125))
        self.apply_theme(QtCore.QSettings().value("ui/theme", "light"))

    def apply_density(self, density: str):
        density = (density or "comfortable").lower()
        self.density_comfy_act.setChecked(density == "comfortable")
        self.density_compact_act.setChecked(density == "compact")
        QtCore.QSettings().setValue("ui/density", density)
        # Reapply theme to include density overrides
        self.apply_theme(QtCore.QSettings().value("ui/theme", "light"))

    # Hover elevation for tool buttons
    def eventFilter(self, obj, event):
        if hasattr(self, "_tool_buttons") and obj in self._tool_buttons:
            eff = obj.graphicsEffect()
            if isinstance(eff, QtWidgets.QGraphicsDropShadowEffect):
                if event.type() == QtCore.QEvent.Enter:
                    eff.setBlurRadius(22)
                    eff.setOffset(0, 4)
                    eff.setColor(QColor(0, 0, 0, 70))
                elif event.type() == QtCore.QEvent.Leave:
                    eff.setBlurRadius(16)
                    eff.setOffset(0, 2)
                    eff.setColor(QColor(0, 0, 0, 40))
        return super().eventFilter(obj, event)



def main():
    # Suppress specific noisy Qt warnings (harmless on Wayland/threads)
    try:
        rules = os.environ.get("QT_LOGGING_RULES", "")
        rule = "qt.qpa.wayland.warning=false"
        if rule not in rules:
            os.environ["QT_LOGGING_RULES"] = (rules + (";" if rules else "") + rule)
    except Exception:
        pass

    # Filter out a known benign runtime warning from Qt
    try:
        def _qt_msg_handler(mode, context, msg):
            s = str(msg)
            if (
                "QSocketNotifier: Can only be used with threads started with QThread" in s
                or "Wayland does not support QWindow::requestActivate()" in s
            ):
                return  # ignore these warnings
            # Fallback to default behavior
            sys.stderr.write(s + "\n")
        QtCore.qInstallMessageHandler(_qt_msg_handler)
    except Exception:
        pass

    app = QApplication(sys.argv)
    # Configure QSettings scope
    QtCore.QCoreApplication.setOrganizationName("BrahimElHamdaoui")
    QtCore.QCoreApplication.setApplicationName("Video Manager")
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
