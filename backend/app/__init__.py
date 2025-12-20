from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    # 'user' here is the dictionary we passed to create_access_token
    return user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    # Import models here to avoid circular dependency
    from app.models import AdminUser, Business
    if identity['role'] == 'admin':
        return AdminUser.query.get(identity['id'])
    elif identity['role'] == 'business':
        return Business.query.get(identity['id'])
    return None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app) # Initialize CORS

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        from app import routes, models
        app.register_blueprint(routes.bp)

    return app
