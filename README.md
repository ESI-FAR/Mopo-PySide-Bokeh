# Run Bokeh Visualization with PySide6 Controls

## Files

### ./01_groupbox_test.py

Learn about
- PySide6 basics
- `groupbox`es

### ./02_pyside_browser.py

Learn about
- PySide6 browser

### ./03_bokeh_viz_with_pyside_controls.py

Open a Bokeh visualization in a PySide6 browser window and control it with a separate PySide6 `QSlider`.

Learn about
- PySide6 multithreading with `QThreadpool`
- PySide6 Signals: `emit` (send) and `connect` (receive)

#### Caveats

- The GUI itself does not run in a background thread
- The application sometimes takes a while to exit, I don't understand the exact reason. It might have to do with the QThreadpool.
