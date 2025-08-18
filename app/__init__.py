from flask import Flask, render_template
from whitenoise import WhiteNoise

from .extensions import cache, compress
from .views import bp as views_bp


class Config:
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60 * 60  # 1 hour


def page_not_found(_):
    return render_template("404.html"), 404


def internal_server_error(_):
    return render_template("500.html"), 500


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(views_bp)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.wsgi_app = WhiteNoise(app.wsgi_app, root="app/static/", prefix="static/")
    cache.init_app(app)
    compress.init_app(app)
    return app
