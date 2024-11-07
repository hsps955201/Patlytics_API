from flask import Blueprint
from patlytics.routes.auth_bp import auth_bp
from patlytics.routes.patent_bp import patent_bp

blueprints = [
    (auth_bp, '/api/auth'),
    (patent_bp, '/api/patent'),
]


def register_blueprints(app):
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
