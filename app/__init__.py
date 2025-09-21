from flask import Flask
from whitenoise import WhiteNoise

from .config import STATIC_DIR, STATIC_PREFIX
from .extensions import cache, compress
from .services.ansi import get_ansi_content
from .services.html import get_content
from .views.routes import bp as views_bp
from .views.routes import internal_server_error, page_not_found


class Config:
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60 * 60  # 1 hour


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(views_bp)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.wsgi_app = WhiteNoise(
        app.wsgi_app,
        root=STATIC_DIR,
        prefix=STATIC_PREFIX,
    )
    cache.init_app(app)
    compress.init_app(app)
    # Load and cache the contents of Markdown files
    get_content()
    get_ansi_content()
    return app
