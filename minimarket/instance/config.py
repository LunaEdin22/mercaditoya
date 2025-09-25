import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-muy-segura'
    
    # Configuración de SQL Server
    SQLSERVER_SERVER = os.environ.get('SQLSERVER_SERVER') or 'localhost'
    SQLSERVER_DATABASE = os.environ.get('SQLSERVER_DATABASE') or 'minimarket'
    SQLSERVER_USERNAME = os.environ.get('SQLSERVER_USERNAME') or 'sa'
    SQLSERVER_PASSWORD = os.environ.get('SQLSERVER_PASSWORD') or '123456'
    SQLSERVER_DRIVER = os.environ.get('SQLSERVER_DRIVER') or 'ODBC Driver 17 for SQL Server'
    
    # URL de conexión para SQLAlchemy con SQL Server
    connection_string = f'DRIVER={{{SQLSERVER_DRIVER}}};SERVER={SQLSERVER_SERVER};DATABASE={SQLSERVER_DATABASE};UID={SQLSERVER_USERNAME};PWD={SQLSERVER_PASSWORD};TrustServerCertificate=yes;'
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API de imgbb
    IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY') or 'tu-api-key-de-imgbb'
    IMGBB_API_URL = 'https://api.imgbb.com/1/upload'
    
    # Configuración de uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']