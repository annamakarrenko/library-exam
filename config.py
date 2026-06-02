import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # MySQL конфигурация (для хостинга)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'std-mysql.ist.mospolytech.ru')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'std_XXXX_exam')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'std_XXXX_exam')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}