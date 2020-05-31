from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .views_main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .views_deal import deal as deal_blueprint
    app.register_blueprint(deal_blueprint)

    from .views_stats import stats as stats_blueprint
    app.register_blueprint(stats_blueprint)

    return app
