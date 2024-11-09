import pymysql
from flask import Flask
from flask_cors import CORS
import config
from patlytics.database import db, migrate


pymysql.install_as_MySQLdb()


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(config)

    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql+pymysql://{config.DB_USER}:{config.DB_PWD}@"
            f"{config.DB_HOST}:{config.DB_PORT}/{config.TEST_DB_NAME}?"
            f"{config.SQLALCHEMY_CHARSET_SYNTAX}"
        )
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from patlytics.database.models import Product, Company

    return app
