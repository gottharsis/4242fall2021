# from flask import Flask, render_template
# from flask_cors import CORS

# def create_app():
#     app = Flask(__name__, static_folder='../client/build/static', template_folder='../client/build')
#     CORS(app)

#     @app.route("/", defaults = {'path': ''})
#     @app.route("/<path:path>")
#     def index(path):
#         """
#         Default route: returns the React app
#         """
#         return render_template('index.html')

#     @app.route("/route2")
#     def test():
#         """
#         Test route to contrast with server route
#         """
#         return "Route 2"
#     return app


"""
    Embed bokeh server session into a flask framework
    Adapted from bokeh-master/examples/howto/serve_embed/flask_gunicorn_embed.py
"""

import asyncio
import logging
from threading import Thread
import time

from bokeh import __version__ as ver
from bokeh.embed import server_document
from flask import Flask, render_template, request
from flask.wrappers import Response
from flask_cors import CORS, cross_origin
import requests
from tornado.ioloop import IOLoop
from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer

from server.bkapp import bokeh_cdn_resources
from server.config import (
    BOKEH_PATH,
    BOKEH_URL,
    BOKEH_WS_PATH,
    FLASK_PATH,
    FLASK_PORT,
    FLASK_URL,
    get_bokeh_port,
)
from server.wsproxy import WebSocketProxy


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


app = Flask(__name__, static_folder='templates/static')
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SECRET_KEY"] = "secret!"


@app.route("/", defaults = {'path': ''})
@app.route("/<path:path>")
def index(path):
    """
    Default route: returns the React app
    """
    return render_template('index.html')

@app.route("/route2")
def test():
    """
    Test route to contrast with server route
    """
    return "Route 2"



@app.route("/seagraph", methods=["GET"])
def seagraph_test():
    """Index"""
    resources = bokeh_cdn_resources()
    script = server_document(FLASK_URL + BOKEH_PATH, resources=None)
    return render_template("embed.html", script=script, resources=resources)


@app.route("/bokeh/<path:path>", methods=["GET"])
@cross_origin(origins="*")
def proxy(path):
    """HTTP Proxy"""
    # print(request.__dict__)
    path = "bokeh/" + path
    print("path", path)
    query = ""
    if request.query_string is not None:
        query = "?" + request.query_string.decode("utf-8")

    bokeh_url = BOKEH_URL.replace("$PORT", get_bokeh_port())
    request_url = f"{bokeh_url}/{path}{query}"
    resp = requests.get(request_url)
    excluded_headers = ["content-length", "connection"]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    response = Response(resp.content, resp.status_code, headers)
    return response


def start_tornado():
    """Start Tornado server to run a flask app in a Tornado
    WSGI container.
    """
    asyncio.set_event_loop(asyncio.new_event_loop())
    container = WSGIContainer(app)
    server = Application(
        [
            (BOKEH_WS_PATH, WebSocketProxy),
            (r".*", FallbackHandler, dict(fallback=container)),
        ],
        **{"use_xheaders": True},
    )
    server.listen(port=FLASK_PORT)
    IOLoop.instance().start()


if __name__ == "__main__":
    t = Thread(target=start_tornado, daemon=True)
    t.start()
    log.info("Flask + Bokeh Server App Running at %s", FLASK_URL + FLASK_PATH)
    while True:
        time.sleep(0.05)
