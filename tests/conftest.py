import pytest
import sys
import os

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app import app, db, User, Task

@pytest.fixture
def client():
    # Configuración del modo de prueba
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():  # Activar el contexto de la aplicación
        db.create_all()  # Crear tablas para las pruebas
        yield app.test_client()  # Proveer el cliente de pruebas
        db.session.remove()
        db.drop_all()  # Limpiar las tablas después de las pruebas

