import os
from flask import Flask
from app.models.database import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'camgame-pulse-secret-2024')

    # Sur Railway : utilise /data (volume persistant) si disponible
    # En local : utilise instance/data.db
    data_dir = '/data' if os.path.isdir('/data') else os.path.join(app.instance_path)
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app