#!/usr/bin/env python3

# Source: https://pythonprogramminglanguage.com/pyqt5-groupbox/
import sys

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.themes import Theme

from PySide6.QtCore import Qt, QUrl, QObject, Signal, QRunnable, Slot, QThreadPool
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QMenu,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QSlider,
    QMainWindow,
)
from PySide6.QtWebEngineWidgets import QWebEngineView


MODEL = sea_surface_temperature.copy()


class WorkerSignals(QObject):
    slider_position = Signal(int)


class Worker(QRunnable):
    def __init__(self, model, *args, **kwargs):
        super(Worker, self).__init__()

        self.signals = WorkerSignals()
        self.df = model
        self.source = ColumnDataSource(data=self.df)

        self.doc = None
        self.slider_position = 0
        self.signals.slider_position.connect(self.update_view_wrap)

    def visualization(self, doc):
        self.doc = doc

        plot = figure(
            x_axis_type="datetime",
            y_range=(0, 25),
            y_axis_label="Temperature (Celsius)",
            title="Sea Surface Temperature at 43.18, -70.43",
        )
        plot.line("time", "temperature", source=self.source)

        doc.add_root(plot)

    def update_view_wrap(self, new_slider_position):
        self.slider_position = new_slider_position
        self.doc.add_next_tick_callback(self.update_view)

    async def update_view(self):
        if self.slider_position == 0:
            self.data = self.df
        else:
            self.data = self.df.rolling(f"{self.slider_position}D").mean()
        self.source.data = ColumnDataSource.from_df(self.data)

    @Slot()
    def run(self):
        server = Server({"/visualization": self.visualization}, num_procs=1)
        server.start()
        server.io_loop.start()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        # window
        super(MainWindow, self).__init__(*args, **kwargs)

        grid = QGridLayout()
        grid.addWidget(self.createControls(), 0, 0)
        grid.addWidget(self.createBrowser(), 0, 1)

        widget = QWidget()
        widget.setLayout(grid)

        self.setCentralWidget(widget)

        self.setWindowTitle("PySide Group Box Example")
        self.resize(800, 300)

        self.threadpool = QThreadPool()

        self.worker = Worker(MODEL)

        self.threadpool.start(self.worker)

        self.show()

    def value_changed(self, value):
        self.worker.signals.slider_position.emit(value)

    def createControls(self):
        groupBox = QGroupBox("Controls")

        slider = QSlider(orientation=Qt.Horizontal)

        slider.setRange(0, 30)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.valueChanged.connect(self.value_changed)

        vbox = QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def createBrowser(self):
        groupBox = QGroupBox("Visualization")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:5006/visualization"))

        vbox = QVBoxLayout()
        vbox.addWidget(self.browser)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
