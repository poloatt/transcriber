import os

class Config:
    # Root paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # App directories (inside /app)
    STATIC_DIR = os.path.join(APP_DIR, 'static')
    SSL_DIR = os.path.join(APP_DIR, 'ssl')
    TEMPLATES_DIR = os.path.join(APP_DIR, 'templates')
    UTILS_DIR = os.path.join(APP_DIR, 'utils')
    
    # Project directories (in root)
    UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    DOCKER_DIR = os.path.join(BASE_DIR, 'docker')
    TESTS_DIR = os.path.join(BASE_DIR, 'tests')
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = 5002
    DEBUG = True
    
    # File settings
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.webm', '.ogg']

# Create required directories
REQUIRED_DIRS = [
    Config.STATIC_DIR,   # /app/static
    Config.SSL_DIR,      # /app/ssl
    Config.TEMPLATES_DIR, # /app/templates
    Config.UTILS_DIR,    # /app/utils
    Config.UPLOADS_DIR,  # /uploads
    Config.LOGS_DIR,    # /logs
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)

# Make Config available for import
__all__ = ['Config']
