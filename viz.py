from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    DataTable,
    HoverTool,
    IntEditor,
    NumberEditor,
    NumberFormatter,
    SelectEditor,
    StringEditor,
    StringFormatter,
    TableColumn,
)
from bokeh.plotting import figure

from model import DF


def mileage_tbl(model: DF, source: ColumnDataSource):
    columns = [
        TableColumn(
            field="manufacturer",
            title="Manufacturer",
            editor=SelectEditor(options=model.manufacturers),
            formatter=StringFormatter(font_style="bold"),
        ),
        TableColumn(
            field="model",
            title="Model",
            editor=StringEditor(completions=model.models),
        ),
        TableColumn(
            field="displ",
            title="Displacement",
            editor=NumberEditor(step=0.1),
            formatter=NumberFormatter(format="0.0"),
        ),
        TableColumn(field="year", title="Year", editor=IntEditor()),
        TableColumn(field="cyl", title="Cylinders", editor=IntEditor()),
        TableColumn(
            field="trans",
            title="Transmission",
            editor=SelectEditor(options=model.transmissions),
        ),
        TableColumn(
            field="drv",
            title="Drive",
            editor=SelectEditor(options=model.drives),
        ),
        TableColumn(
            field="class",
            title="Class",
            editor=SelectEditor(options=model.classes),
        ),
        TableColumn(field="cty", title="City MPG", editor=IntEditor()),
        TableColumn(field="hwy", title="Highway MPG", editor=IntEditor()),
    ]
    data_table = DataTable(
        source=source,
        columns=columns,
        editable=True,
        width=800,
        index_position=-1,
        index_header="row index",
        index_width=60,
    )

    plot = figure(
        width=800,
        height=300,
        tools="pan,wheel_zoom,xbox_select,reset",
        active_drag="xbox_select",
    )

    cty = plot.circle(
        x="index",
        y="cty",
        fill_color="#396285",
        size=8,
        alpha=0.5,
        source=source,
    )
    hwy = plot.circle(
        x="index",
        y="hwy",
        fill_color="#CE603D",
        size=8,
        alpha=0.5,
        source=source,
    )

    tooltips = [
        ("Manufacturer", "@manufacturer"),
        ("Model", "@model"),
        ("Displacement", "@displ"),
        ("Year", "@year"),
        ("Cylinders", "@cyl"),
        ("Transmission", "@trans"),
        ("Drive", "@drv"),
        ("Class", "@class"),
    ]
    cty_hover_tool = HoverTool(
        renderers=[cty], tooltips=[*tooltips, ("City MPG", "@cty")]
    )
    hwy_hover_tool = HoverTool(
        renderers=[hwy], tooltips=[*tooltips, ("Highway MPG", "@hwy")]
    )

    plot.add_tools(cty_hover_tool, hwy_hover_tool)
    return column(plot, data_table)
