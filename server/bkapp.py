"""
    Embed bokeh server session into a flask framework
    Adapted from bokeh-master/examples/howto/serve_embed/flask_gunicorn_embed.py
"""

import asyncio
import logging
import os
from threading import Thread
import time

from bokeh import __version__ as bokeh_release_ver
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.resources import get_sri_hashes_for_version
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from bokeh.themes import Theme
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from server.config import (
    BOKEH_ADDR,
    BOKEH_CDN,
    BOKEH_PATH,
    BOKEH_URL,
    FLASK_ADDR,
    FLASK_PORT,
    cwd,
    set_bokeh_port,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


BOKEH_BROWSER_LOGGING = """
    <script type="text/javascript">
      Bokeh.set_log_level("debug");
    </script>
"""


def bkapp(doc):
    """Bokeh App

    Arguments:
        doc {Bokeh Document} -- bokeh document

    Returns:
        Bokeh Document --bokeh document with plot and slider
    """
    dataframe = sea_surface_temperature.copy()
    source = ColumnDataSource(data=dataframe)

    plot = figure(
        x_axis_type="datetime",
        y_range=(0, 25),
        y_axis_label="Temperature (Celsius)",
        title="Sea Surface Temperature at 43.18, -70.43",
    )
    plot.line(x="time", y="temperature", source=source)

    def callback(_attr, _old, new):
        if new == 0:
            data = dataframe
        else:
            data = dataframe.rolling("{0}D".format(new)).mean()
        source.data = ColumnDataSource.from_df(data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    # doc.theme = Theme(filename=os.path.join(cwd(), "theme.yaml"))
    return doc.add_root(column(slider, plot))


def bokeh_cdn_resources():
    """Create script to load Bokeh resources from CDN based on
       installed bokeh version.

    Returns:
        script -- script to load resources from CDN
    """
    included_resources = [
        f"bokeh-{bokeh_release_ver}.min.js",
        f"bokeh-api-{bokeh_release_ver}.min.js",
        f"bokeh-tables-{bokeh_release_ver}.min.js",
        f"bokeh-widgets-{bokeh_release_ver}.min.js",
    ]

    resources = "\n    "
    for key, value in get_sri_hashes_for_version(bokeh_release_ver).items():
        if key in included_resources:
            resources += '<script type="text/javascript" '
            resources += f'src="{BOKEH_CDN}/{key}" '
            resources += f'integrity="sha384-{value}" '
            resources += 'crossorigin="anonymous"></script>\n    '

    resources += BOKEH_BROWSER_LOGGING
    return resources


def get_sockets():
    """bind to available socket in this system

    Returns:
        sockets, port -- sockets and port bind to
    """
    _sockets, _port = bind_sockets("0.0.0.0", 0)
    set_bokeh_port(_port)
    return _sockets, _port


def bk_worker(sockets, port):
    """Worker thread to  run Bokeh Server"""
    _bkapp = Application(FunctionHandler(bkapp))
    asyncio.set_event_loop(asyncio.new_event_loop())

    websocket_origins = [f"{BOKEH_ADDR}:{port}", f"{FLASK_ADDR}:{FLASK_PORT}"]
    bokeh_tornado = BokehTornado(
        {BOKEH_PATH: _bkapp},
        extra_websocket_origins=websocket_origins,
        **{"use_xheaders": True},
    )

    bokeh_http = HTTPServer(bokeh_tornado, xheaders=True)
    bokeh_http.add_sockets(sockets)
    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()


if __name__ == "__main__":
    bk_sockets, bk_port = get_sockets()
    t = Thread(target=bk_worker, args=[bk_sockets, bk_port], daemon=True)
    t.start()
    bokeh_url = BOKEH_URL.replace("$PORT", str(bk_port))
    log.info("Bokeh Server App Running at: %s", bokeh_url)
    while True:
        time.sleep(0.05)
