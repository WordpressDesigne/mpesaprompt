import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_admin_user(email, password):
    from app.models import AdminUser
    admin = AdminUser.query.filter_by(email=email).first()
    if not admin:
        new_admin = AdminUser(email=email)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()

def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    if test_config is None:
        app.config.from_object(config_class)
    else:
        app.config.from_mapping(test_config)
    CORS(app) # Initialize CORS

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        from app import routes, models
        app.register_blueprint(routes.bp)

    return app
