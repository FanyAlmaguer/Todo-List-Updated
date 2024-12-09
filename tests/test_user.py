import sys
import os
from unittest.mock import patch
from app import google, User, db
from flask.testing import FlaskClient

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app import Task, User, db
from werkzeug.security import generate_password_hash, check_password_hash

# Prueba existente: Crear un usuario
def test_create_user(client):
    # Crear un usuario
    user = User(username="test_user", password=generate_password_hash("secure_password"))
    db.session.add(user)
    db.session.commit()

    # Verificar que se guardó correctamente
    assert user.id is not None
    assert user.username == "test_user"

# Prueba existente: Verificar hash de contraseña
def test_password_hashing(client):
    # Probar hashing y verificación de contraseñas
    password = "secure_password"
    hashed_password = generate_password_hash(password)
    assert not check_password_hash(hashed_password, "wrong_password")
    assert check_password_hash(hashed_password, password)

# Nueva prueba: Login exitoso
def test_login_success(client):
    # Crear un usuario
    user = User(username="test_login", password=generate_password_hash("password"))
    db.session.add(user)
    db.session.commit()

    # Intentar iniciar sesión
    response = client.post('/login', data={
        'username': 'test_login',
        'password': 'password'
    })
    assert response.status_code == 302  # Redirección a /tasks

# Nueva prueba: Login fallido
def test_login_fail(client):
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_password'
    })
    assert response.status_code == 200  # Quedarse en /login
    assert b"Login failed" in response.data

# Nueva prueba: Registro de usuario
def test_register_user(client):
    response = client.post('/register', data={
        'username': 'new_user',
        'password': 'new_password'
    })
    assert response.status_code == 302  # Redirección a /login

    # Verificar que el usuario se guardó
    user = User.query.filter_by(username='new_user').first()
    assert user is not None


def test_login_empty_fields(client):
    response = client.post('/login', data={
        'username': '',
        'password': ''
    })
    assert response.status_code == 200  # No redirige
    assert b"Login failed" in response.data


def test_login_nonexistent_user(client):
    response = client.post('/login', data={
        'username': 'nonexistent_user',
        'password': 'password'
    })
    assert response.status_code == 200  # No redirige
    assert b"Login failed" in response.data


def test_register_empty_fields(client):
    response = client.post('/register', data={
        'username': '',
        'password': ''
    })
    assert response.status_code == 200  # No redirige
    assert b"Register" in response.data  # Se queda en la página de registro


def test_register_existing_user(client):
    # Crear un usuario
    user = User(username="existing_user", password=generate_password_hash("password"))
    db.session.add(user)
    db.session.commit()

    # Intentar registrar con el mismo username
    response = client.post('/register', data={
        'username': 'existing_user',
        'password': 'new_password'
    })
    assert response.status_code == 200  # No redirige
    assert b"Register" in response.data


def test_render_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data  # Verificar que el texto 'Login' esté presente


def test_render_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data  # Verificar que el texto 'Register' esté presente


def test_google_login_redirect(client):
    # Simular la URL de redirección generada por Google OAuth
    with patch.object(google, "authorize_redirect") as mock_authorize_redirect:
        mock_authorize_redirect.return_value = "mock_redirect_url"

        # Realizar la solicitud a /google_login
        response = client.get('/google_login')
        assert response.status_code == 200
        mock_authorize_redirect.assert_called_once()


def test_google_authorize_new_user(client: FlaskClient):
    # Datos simulados de un nuevo usuario de Google
    mock_user_info = {
        "sub": "1234567890",
        "email": "new_user@gmail.com"
    }

    # Simular respuestas de Google OAuth
    with patch.object(google, "authorize_access_token") as mock_authorize_access_token, \
         patch.object(google, "get") as mock_google_get:
        mock_authorize_access_token.return_value = {"id_token": "mock_token"}
        mock_google_get.return_value = type('MockResponse', (object,), {'json': lambda self: mock_user_info})()

        # Realizar la solicitud a /google_authorize
        response = client.get('/google_authorize')

        # Verificar que el usuario fue creado en la base de datos
        user = User.query.filter_by(google_id=mock_user_info['sub']).first()
        assert user is not None
        assert user.username == mock_user_info['email']
        assert response.status_code == 302  # Redirección a /tasks


def test_google_authorize_existing_user(client: FlaskClient):
    # Crear un usuario en la base de datos con Google ID
    existing_user = User(username="existing_user@gmail.com", google_id="1234567890")
    db.session.add(existing_user)
    db.session.commit()

    # Datos simulados del usuario de Google
    mock_user_info = {
        "sub": "1234567890",
        "email": "existing_user@gmail.com"
    }

    # Simular respuestas de Google OAuth
    with patch.object(google, "authorize_access_token") as mock_authorize_access_token, \
         patch.object(google, "get") as mock_google_get:
        mock_authorize_access_token.return_value = {"id_token": "mock_token"}
        mock_google_get.return_value = type('MockResponse', (object,), {'json': lambda self: mock_user_info})()

        # Realizar la solicitud a /google_authorize
        response = client.get('/google_authorize')

        # Verificar que no se creó un usuario nuevo
        user_count = User.query.filter_by(google_id=mock_user_info['sub']).count()
        assert user_count == 1
        assert response.status_code == 302  # Redirección a /tasks
