from flask import Flask, render_template
from whitenoise import WhiteNoise

from .views import bp as views_bp


def page_not_found(_):
    return render_template("404.html"), 404


def internal_server_error(_):
    return render_template("500.html"), 500


def create_app():
    app = Flask(__name__)
    app.register_blueprint(views_bp)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.wsgi_app = WhiteNoise(app.wsgi_app, root="app/static/", prefix="static/")
    return app
