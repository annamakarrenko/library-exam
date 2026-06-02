from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Регистрация blueprint'ов
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.books import bp as books_bp
    app.register_blueprint(books_bp)
    
    from app.reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp)
    
    from app.moderation import bp as moderation_bp
    app.register_blueprint(moderation_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Создание папки для загрузок
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app