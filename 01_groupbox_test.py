#!/usr/bin/env python3

""" Exploring how PySide6 groupboxes work."""

# Source: https://pythonprogramminglanguage.com/pyqt5-groupbox/
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)  # Why is this necessary?

        # Create grid
        grid = QGridLayout()
        grid.addWidget(self.createExampleGroup(), 0, 0)
        grid.addWidget(self.createExampleGroup(), 0, 1)
        self.setLayout(grid)

        self.setWindowTitle("PySide Group Box Example")
        self.resize(800, 300)

    def createExampleGroup(self):
        groupBox = QGroupBox("Select Your Favorite Food")

        radio1 = QRadioButton("&Pizza")
        radio2 = QRadioButton("&Taco")
        radio3 = QRadioButton("&Burrito")

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox


if __name__ == "__main__":
    app = QApplication(sys.argv)
    windowInstance = Window()
    windowInstance.show()
    sys.exit(app.exec())
