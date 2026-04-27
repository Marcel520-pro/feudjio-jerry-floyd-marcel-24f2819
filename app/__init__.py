import os
from flask import Flask
from app.models.database import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'camgame-pulse-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app
