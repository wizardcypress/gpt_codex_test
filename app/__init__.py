from flask import Flask

from .database import init_db
from .scheduler import init_scheduler


def create_app() -> Flask:
    app = Flask(__name__)

    init_db()
    from .routes import bp as main_blueprint

    app.register_blueprint(main_blueprint)

    init_scheduler(app)

    return app
