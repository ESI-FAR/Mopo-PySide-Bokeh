#!/usr/bin/env python3

import threading

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.themes import Theme

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView


def bkapp(doc):
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(
        x_axis_type="datetime",
        y_range=(0, 25),
        y_axis_label="Temperature (Celsius)",
        title="Sea Surface Temperature at 43.18, -70.43",
    )
    plot.line("time", "temperature", source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling(f"{new}D").mean()
        source.data = ColumnDataSource.from_df(data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    doc.add_root(column(slider, plot))


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:5006/bkapp"))
        self.setCentralWidget(self.browser)


def show_window(QApplication, MainWindow):
    app = QApplication()
    window = MainWindow()
    window.show()

    app.exec()


def start_server(server):
    server.io_loop.start()


server = Server({"/bkapp": bkapp}, num_procs=1)
server.start()

server_thread = threading.Thread(target=start_server, args=(server,))
pyside_thread = threading.Thread(target=show_window, args=(QApplication, MainWindow))

server_thread.start()
pyside_thread.start()
