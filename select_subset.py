#!/usr/bin/env python3

import sys
from typing import cast

from bokeh.models import ColumnDataSource
from bokeh.sampledata.autompg2 import autompg2 as mpg
from bokeh.server.server import Server

from PySide6.QtCore import QUrl, QObject, Signal, QRunnable, Slot, QThreadPool
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QSlider,
    QMainWindow,
    QRadioButton,
    QLabel,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

from model import DF
from viz import mileage_tbl


class WorkerSignals(QObject):
    """A collection of communication queues."""

    radio_signal = Signal(str)


class Worker(QRunnable):
    """This class will run in a separate PySide thread."""

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Why is this necessary?

        self.signals = WorkerSignals()
        self.model = model
        self.source = ColumnDataSource(data=self.model.df)

        self.doc = None  # Bokeh canvas
        self.subset = "all"

        # If `slider_value` changes, call the function `slider_changed`.
        self.signals.radio_signal.connect(self.update)

    def visualization(self, doc):
        """Attach Bokeh plot to canvas (doc)."""
        self.doc = doc
        plot = mileage_tbl(self.model, self.source)
        doc.add_root(plot)

    def update(self, subset: str):
        self.subset = subset

        # Communicating with Bokeh: queue `update_view` for the next iteration
        # of the Tornado server event loop.
        self.doc.add_next_tick_callback(self.update_view)

    async def update_view(self):
        """Update Bokeh plot."""
        if self.subset == "all":
            data = self.model.df
        else:
            data = self.model.df.query(f"manufacturer == '{self.subset}'")
        self.source.data = ColumnDataSource.from_df(data)

    def run(self):
        """Executed when Worker is started."""
        self.server = Server({"/visualization": self.visualization}, num_procs=1)
        self.server.start()
        self.server.io_loop.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = DF(mpg)

        widget = QWidget()

        wcols = QHBoxLayout()

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Manufacturers"))

        # reset to all
        button = QRadioButton("all", widget)
        button.toggled.connect(self.update)
        vbox.addWidget(button)

        for man in self.model.manufacturers:
            button = QRadioButton(man, widget)
            button.toggled.connect(self.update)
            vbox.addWidget(button)

        vbox.addStretch()  # flexible spacing at the bottom (can be 0)
        wcols.addLayout(vbox, 1)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:5006/visualization"))
        wcols.addWidget(self.browser, 4)

        widget.setLayout(wcols)
        self.setCentralWidget(widget)

        self.setWindowTitle("PoC: WebView based visualisation")
        self.resize(800, 300)

        self.show()

        # run worker (bokeh viz and server) in background
        self.threadpool = QThreadPool()
        self.worker = Worker(self.model)
        self.threadpool.start(self.worker)

    def update(self):
        sender = cast(QRadioButton, self.sender())
        if sender.isChecked():
            self.worker.signals.radio_signal.emit(sender.text())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()
    window.worker.server.io_loop.stop()
    sys.exit()


if __name__ == "__main__":
    main()
