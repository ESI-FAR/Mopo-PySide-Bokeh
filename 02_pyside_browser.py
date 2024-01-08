#!/usr/bin/env python3

# Source: https://www.pythonguis.com/faq/qwebengineview-open-links-new-window/

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://duckduckgo.com"))
        self.setCentralWidget(self.browser)


app = QApplication()
window = MainWindow()
window.show()

app.exec()
