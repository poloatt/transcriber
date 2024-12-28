import os
import sys
import logging
from app import create_app
from app.config import Config
import subprocess
from app.routes import transcriber_bp  # Ensure this is the only import

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 5002
DEBUG = True

app = create_app()
logger = logging.getLogger(__name__)

def setup_ssl():
    """Configura los certificados SSL para desarrollo"""
    cert_file = os.path.join(Config.SSL_DIR, 'cert.pem')
    key_file = os.path.join(Config.SSL_DIR, 'key.pem')
    
    try:
        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            # Crear archivo de configuración de OpenSSL
            ssl_conf = os.path.join(Config.SSL_DIR, 'openssl.cnf')
            with open(ssl_conf, 'w') as f:
                f.write("""[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = IT
ST = Development
L = Local
O = Development
OU = Development
CN = localhost

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 172.22.191.182
""")
            
            # Generar certificados usando la configuración
            openssl_cmd = [
                'openssl', 'req', '-x509',
                '-newkey', 'rsa:4096',
                '-keyout', key_file,
                '-out', cert_file,
                '-days', '365',
                '-nodes',
                '-config', ssl_conf
            ]
            
            subprocess.run(openssl_cmd, check=True)
            print(f"Generated SSL certificates in {Config.SSL_DIR}")
            
            # Limpiar archivo de configuración
            os.remove(ssl_conf)
            
        return cert_file, key_file
    except Exception as e:
        print(f"Error setting up SSL: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    cert_file, key_file = setup_ssl()
    
    print(f"Using certificates:\n  Cert: {cert_file}\n  Key: {key_file}")
    print(f"Starting server on {HOST}:{PORT}")
    
    app.run(
        host=HOST,
        port=PORT,
        ssl_context=(cert_file, key_file),
        debug=DEBUG
    )