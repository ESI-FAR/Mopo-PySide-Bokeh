# Run Bokeh Visualization with PySide6 Controls

## Scripts

### [01_pyside_browser.py](./01_pyside_browser.py)

Learn about
- PySide6 basics
- PySide6 browser

Based on this [example](https://www.pythonguis.com/faq/qwebengineview-open-links-new-window/) by [Martin Fitzpatrick](https://www.pythonguis.com/authors/martin-fitzpatrick/) under [MIT license](https://mit-license.org/).

### [02_bokeh_viz_with_pyside_controls.py](./02_bokeh_viz_with_pyside_controls.py)

Open a Bokeh visualization in a PySide6 browser window and control it with a separate PySide6 `QSlider`.

Learn about
- `groupbox`es
- Multithreading with `QThreadpool`
- PySide6 Signals: `emit` (send) and `connect` (receive)

Based on this [example](https://github.com/bokeh/bokeh/blob/3.3.2/examples/server/api/standalone_embed.py) by [Bokeh](http://bokeh.org/) under [MIT license](https://mit-license.org/).

#### Caveats

- The GUI itself does not run in a background thread
- The application sometimes takes a while to exit, I don't understand the exact reason. It might have to do with the QThreadpool.
- I'm not sure if we can control the viewport/content sizes appropriately, e.g. stretch content to fill the viewport without scrollbars.
