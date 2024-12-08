from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys


class Browser(QWebEngineView):
    def __init__(self):
        super().__init__()

        # Initial settings for the browser
        self.setUrl(QUrl("https://duckduckgo.com/"))
        self.setup_settings()
        self.setup_signals()

    def setup_settings(self):
        """Enable settings for smoother performance"""
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)

    def setup_signals(self):
        """Connect signals for URL and page load status"""
        self.urlChanged.connect(self.update_urlbar)
        self.loadFinished.connect(self.update_title)

    def update_title(self):
        """Update window title with the current page title"""
        title = self.page().title()
        self.window().setWindowTitle(f"{title} - Easy Browser")

    def update_urlbar(self, q):
        """Update the URL bar with the current URL"""
        self.window().urlbar.setText(q.toString())
        self.window().urlbar.setCursorPosition(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Enable closing tabs
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Add the first tab
        self.add_new_tab()

        # Set up status bar and toolbar
        self.setup_status_bar()
        self.setup_toolbar()

        # Download progress bar
        self.download_progress = QProgressBar(self)
        self.download_progress.setRange(0, 100)
        self.statusBar().addPermanentWidget(self.download_progress)

        # Connect download requests to handlers
        self.tabs.currentWidget().page().profile().downloadRequested.connect(self.on_download_requested)

        self.show()

    def setup_status_bar(self):
        """Set up the status bar"""
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def setup_toolbar(self):
        """Set up the toolbar with navigation actions"""
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        # Add navigation actions
        actions = [
            ("<--", "Back to previous page", self.tabs.currentWidget().back),
            ("-->", "Forward to next page", self.tabs.currentWidget().forward),
            ("Reload", "Reload page", self.tabs.currentWidget().reload),
            ("Home", "Go home", self.navigate_home),
            ("Stop", "Stop loading current page", self.tabs.currentWidget().stop)
        ]
        for text, tip, action in actions:
            btn = QAction(text, self)
            btn.setStatusTip(tip)
            btn.triggered.connect(action)
            navtb.addAction(btn)

        navtb.addSeparator()

        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        # Add "New Tab" action
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.add_new_tab)
        navtb.addAction(new_tab_action)

    def add_new_tab(self):
        """Add a new tab to the browser"""
        new_browser = Browser()
        self.tabs.addTab(new_browser, "New Tab")
        self.tabs.setCurrentWidget(new_browser)

        # Connect the page's signals to download handling in the new tab
        new_browser.page().profile().downloadRequested.connect(self.on_download_requested)

    def close_tab(self, index):
        """Close the selected tab"""
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def navigate_home(self):
        """Navigate to the homepage"""
        self.tabs.currentWidget().setUrl(QUrl("https://duckduckgo.com/"))

    def navigate_to_url(self):
        """Navigate to the URL in the URL bar"""
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def on_download_requested(self, download):
        """Handle download requests"""
        downloads_folder = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        file_name = download.url().fileName()
        download_path = os.path.join(downloads_folder, file_name)

        download.setPath(download_path)
        download.finished.connect(self.on_download_finished)
        download.downloadProgress.connect(self.on_download_progress)
        download.accept()

    def on_download_progress(self, received, total):
        """Update the download progress bar"""
        if total > 0:
            progress = int((received / total) * 100)
            self.download_progress.setValue(progress)

    def on_download_finished(self):
        """Reset the progress bar once download is finished"""
        self.download_progress.reset()


# Creating the PyQt5 application
app = QApplication(sys.argv)
app.setApplicationName("Easy Browser")

# Creating the main window object
window = MainWindow()

# Start the application's event loop
sys.exit(app.exec_())
