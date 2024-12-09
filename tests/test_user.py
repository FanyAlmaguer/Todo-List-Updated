import sys
import os
from unittest.mock import patch
from app import google, User, db
from werkzeug.security import generate_password_hash, check_password_hash

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Prueba existente: Crear un usuario
def test_create_user(client):
    try:
        # Crear un usuario
        user = User(username="test_user", password=generate_password_hash("secure_password"))
        db.session.add(user)
        db.session.commit()

        # Verificar que se guardó correctamente
        assert user.id is not None
        assert user.username == "test_user"
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        assert False

# Prueba existente: Verificar hash de contraseña
def test_password_hashing():
    password = "secure_password"
    hashed_password = generate_password_hash(password)
    assert not check_password_hash(hashed_password, "wrong_password")
    assert check_password_hash(hashed_password, password)

# Nueva prueba: Login exitoso
def test_login_success(client):
    user = User(username="test_login", password=generate_password_hash("secure_password"))
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={
        'username': 'test_login',
        'password': 'secure_password'
    })
    assert response.status_code == 302  # Redirección a /tasks

# Nueva prueba: Login fallido
def test_login_fail(client):
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_password'
    })
    assert response.status_code == 200
    assert b"Login failed" in response.data

# Nueva prueba: Registro de usuario
def test_register_user(client):
    response = client.post('/register', data={
        'username': 'new_user',
        'password': 'secure_password'
    })
    assert response.status_code == 302  # Redirección a /login

    user = User.query.filter_by(username='new_user').first()
    assert user is not None

# Nueva prueba: Login con campos vacíos
def test_login_empty_fields(client):
    response = client.post('/login', data={
        'username': '',
        'password': ''
    })
    assert response.status_code == 200
    assert b"Login failed" in response.data

# Nueva prueba: Registro de usuario con campos vacíos
def test_register_empty_fields(client):
    response = client.post('/register', data={
        'username': '',
        'password': ''
    })
    assert response.status_code == 200
    assert b"Register" in response.data

# Nueva prueba: Login con usuario inexistente
def test_login_nonexistent_user(client):
    response = client.post('/login', data={
        'username': 'nonexistent_user',
        'password': 'password'
    })
    assert response.status_code == 200
    assert b"Login failed" in response.data

# Nueva prueba: Google OAuth login
@patch('app.google.authorize_redirect')
def test_google_login_redirect(mock_authorize_redirect, client):
    mock_authorize_redirect.return_value = "mock_redirect_url"

    response = client.get('/google_login')
    assert response.status_code == 200
    mock_authorize_redirect.assert_called_once()


@patch('app.google.authorize_access_token')
@patch('app.google.get')
def test_google_authorize(mock_google_get, mock_authorize_access_token, client):
    # Simular respuesta de authorize_access_token
    mock_authorize_access_token.return_value = {"id_token": "mock_id_token"}
    
    # Simular respuesta de Google para información del usuario
    mock_google_get.return_value.json.return_value = {
        "sub": "1234567890",
        "email": "new_user@gmail.com"
    }

    # Llamar a la ruta de autorización
    with client.session_transaction() as session:
        session['oauth_state'] = 'mock_state'  # Establecer un estado simulado en la sesión

    response = client.get('/google_authorize?state=mock_state&code=mock_code')
    
    # Verificar que el usuario fue creado
    user = User.query.filter_by(google_id="1234567890").first()
    assert user is not None
    assert user.username == "new_user@gmail.com"
    assert response.status_code == 302  # Redirección esperada
    assert response.headers['Location'] == '/tasks'