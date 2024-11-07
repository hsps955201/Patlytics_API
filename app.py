from patlytics import create_app
from patlytics.routes import register_blueprints

app = create_app()
register_blueprints(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
