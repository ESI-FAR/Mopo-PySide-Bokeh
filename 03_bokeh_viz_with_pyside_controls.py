#!/usr/bin/env python3

# Source: https://github.com/bokeh/bokeh/blob/3.3.2/examples/server/api/standalone_embed.py
import sys

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server

from PySide6.QtCore import Qt, QUrl, QObject, Signal, QRunnable, Slot, QThreadPool
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QVBoxLayout,
    QWidget,
    QSlider,
    QMainWindow,
)
from PySide6.QtWebEngineWidgets import QWebEngineView


MODEL = sea_surface_temperature.copy()


class WorkerSignals(QObject):
    """A collection of communication queues."""
    slider_signal = Signal(int)


class Worker(QRunnable):
    """This class will run in a separate PySide thread."""
    def __init__(self, model, *args, **kwargs):
        super(Worker, self).__init__()  # Why is this necessary?

        self.signals = WorkerSignals()
        self.df = model
        self.source = ColumnDataSource(data=self.df)

        self.doc = None  # Bokeh canvas
        self.slider_value = 0  # Starting position

        # If `slider_value` changes, call the function `slider_changed`.
        self.signals.slider_signal.connect(self.slider_changed)

    def visualization(self, doc):
        """Attach Bokeh plot to canvas (doc)."""
        self.doc = doc

        plot = figure(
            x_axis_type="datetime",
            y_range=(0, 25),
            y_axis_label="Temperature (Celsius)",
            title="Sea Surface Temperature at 43.18, -70.43",
        )
        plot.line("time", "temperature", source=self.source)

        doc.add_root(plot)

    def slider_changed(self, new_slider_position):
        self.slider_value = new_slider_position

        # Communicating with Bokeh: queue `update_view` for the next iteration
        # of the Tornado server event loop.
        self.doc.add_next_tick_callback(self.update_view)

    async def update_view(self):
        """Update Bokeh plot."""
        if self.slider_value == 0:
            self.data = self.df
        else:
            self.data = self.df.rolling(f"{self.slider_value}D").mean()
        self.source.data = ColumnDataSource.from_df(self.data)

    def run(self):
        """Executed when Worker is started."""
        self.server = Server({"/visualization": self.visualization}, num_procs=1)
        self.server.start()
        self.server.io_loop.start()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        # window
        super(MainWindow, self).__init__(*args, **kwargs)

        # define grid
        grid = QGridLayout()
        grid.addWidget(self.createControls(), 0, 0)
        grid.addWidget(self.createBrowser(), 0, 1)

        # create window content
        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        self.setWindowTitle("PySide Group Box Example")
        self.resize(800, 300)

        self.show()

        # run worker (bokeh viz and server) in background
        self.threadpool = QThreadPool()
        self.worker = Worker(MODEL)
        self.threadpool.start(self.worker)

    def slider_value_changed(self, value):
        """Send `slider_signal` when the slider value is changed."""
        self.worker.signals.slider_signal.emit(value)

    def createControls(self):
        """Create controls `groupbox`."""
        groupBox = QGroupBox("Controls")

        slider = QSlider(orientation=Qt.Horizontal)

        slider.setRange(0, 30)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.valueChanged.connect(self.slider_value_changed)

        vbox = QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def createBrowser(self):
        """Create browser `groupbox`."""
        groupBox = QGroupBox("Visualization")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:5006/visualization"))

        vbox = QVBoxLayout()
        vbox.addWidget(self.browser)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()
    window.worker.server.io_loop.stop()
    sys.exit()

if __name__ == "__main__":
    main()
