from flask import Flask, render_template

def create_app():
    app = Flask(__name__, static_folder='../client/build/static', template_folder='../client/build')

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
    return app
