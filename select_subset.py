#!/usr/bin/env python3

import sys
import time
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
    resize_signal = Signal(list)
    viz_ready_signal = Signal()


class Worker(QRunnable):
    """This class will run in a separate PySide thread."""

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Why is this necessary?

        self.signals = WorkerSignals()
        self.model = model
        self.source = ColumnDataSource(data=self.model.df)

        self.doc = None  # Bokeh canvas
        self.subset = "all"

        self.plot = None
        self.plot_width = 0
        self.plot_height = 0

        self.signals.radio_signal.connect(self.update)
        self.signals.resize_signal.connect(self.update_size)

    def visualization(self, doc):
        """Attach Bokeh plot to canvas (doc)."""
        self.doc = doc
        self.plot = mileage_tbl(self.model, self.source)
        doc.add_root(self.plot)
        self.signals.viz_ready_signal.emit()

    def update(self, subset: str):
        self.subset = subset

        # Communicating with Bokeh: queue `update_view` for the next iteration
        # of the Tornado server event loop.
        if self.doc:
            self.doc.add_next_tick_callback(self.update_view)

    #def update_size(self, subset: str):
    #    # Communicating with Bokeh: queue `update_view` for the next iteration
    #    # of the Tornado server event loop.
    #    self.doc.add_next_tick_callback(self.update_canvas_size)

    def update_size(self, new_size: list[int]):
        width, height = new_size
        self.plot_width = width - 20  # TODO why is this needed?
        self.plot_height = height

        # Communicating with Bokeh: queue `update_canvas_size` for the next iteration
        # of the Tornado server event loop.
        if self.doc:
            self.doc.add_next_tick_callback(self.update_canvas_size)
        else:
            print("no doc yet")

    async def update_view(self):
        """Update Bokeh plot."""
        if self.subset == "all":
            data = self.model.df
        else:
            data = self.model.df.query(f"manufacturer == '{self.subset}'")
        self.source.data = ColumnDataSource.from_df(data)

    async def update_canvas_size(self):
        """Update Bokeh canvas size."""
        self.plot.width = self.plot_width
        self.plot.height = self.plot_height

    def run(self):
        """Executed when Worker is started."""
        self.server = Server({"/visualization": self.visualization}, num_procs=1)
        self.server.start()
        self.server.io_loop.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = DF(mpg)

        # run worker (bokeh viz and server) in background
        self.threadpool = QThreadPool()
        self.worker = Worker(self.model)
        self.signals = self.worker.signals
        self.signals.viz_ready_signal.connect(self.set_initial_size)
        self.threadpool.start(self.worker)

        widget = QWidget()

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(QLabel("Manufacturers"))

        self.wcols = QHBoxLayout()

        # reset to all
        button = QRadioButton("all", widget)
        button.toggled.connect(self.update)
        self.vbox.addWidget(button)

        for man in self.model.manufacturers:
            button = QRadioButton(man, widget)
            button.toggled.connect(self.update)
            self.vbox.addWidget(button)

        self.vbox.addStretch()  # flexible spacing at the bottom (can be 0)
        self.wcols.addLayout(self.vbox, 1)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:5006/visualization"))
        self.wcols.addWidget(self.browser, 4)

        widget.setLayout(self.wcols)
        self.setCentralWidget(widget)

        self.setWindowTitle("PoC: WebView based visualisation")
        self.resize(800, 300)

        self.show()

    def update(self):
        sender = cast(QRadioButton, self.sender())
        if sender.isChecked():
            self.worker.signals.radio_signal.emit(sender.text())

    def set_initial_size(self):
        self.worker.signals.resize_signal.emit([self.browser.geometry().width(), self.browser.geometry().height()])

    def resizeEvent(self, event):
        self.worker.signals.resize_signal.emit([self.browser.geometry().width(), self.browser.geometry().height()])
        QMainWindow.resizeEvent(self, event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()
    window.worker.server.io_loop.stop()
    sys.exit()


if __name__ == "__main__":
    main()
