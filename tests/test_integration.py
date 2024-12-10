import pytest
import os
from app import app, db, User, Task
from werkzeug.security import generate_password_hash
from unittest.mock import patch
from flask import redirect

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        try:
            db.create_all()
            yield app.test_client()
        finally:
            db.session.remove()
            db.drop_all()

def test_database_operations(client):
    # Crear usuario
    user = User(username="test_user", password=generate_password_hash(os.getenv("TEST_USER_PASSWORD", "secure_password")))
    db.session.add(user)
    db.session.commit()
    assert user.id is not None

    # Crear tareas asociadas al usuario
    task = Task(user_id=user.id, task="Test Task", priority=1)
    db.session.add(task)
    db.session.commit()
    assert task.id is not None

    # Consultar tareas
    tasks = Task.query.filter_by(user_id=user.id).all()
    assert len(tasks) == 1
    assert tasks[0].task == "Test Task"

def test_session_management(client):
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Simular acceso a una ruta protegida
    response = client.get('/tasks')
    assert response.status_code == 200

    # Cerrar sesión
    response = client.get('/logout')
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert 'user_id' not in session

def test_user_authentication_flow(client):
    # Registro de usuario
    response = client.post('/register', data={
        'username': 'test_user',
        'password': os.getenv("TEST_USER_PASSWORD", "test_password")
    })
    assert response.status_code == 302

    # Inicio de sesión con el usuario registrado
    response = client.post('/login', data={
        'username': 'test_user',
        'password': os.getenv("TEST_USER_PASSWORD", "test_password")
    })
    assert response.status_code == 302

def test_task_management_workflow(client):
    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Crear una nueva tarea
    response = client.post('/tasks', data={
        'task': 'New Task',
        'priority': 2
    })
    assert response.status_code == 302

    # Verificar que la tarea se creó
    task = Task.query.filter_by(task='New Task').first()
    assert task is not None

    # Editar la tarea
    response = client.post(f'/edit_task/{task.id}', data={
        'task': 'Updated Task',
        'priority': 1
    })
    assert response.status_code == 302

    # Verificar cambios
    edited_task = db.session.get(Task, task.id)
    assert edited_task.task == 'Updated Task'
    assert edited_task.priority == 1

    # Eliminar la tarea
    response = client.get(f'/delete_task/{task.id}')
    assert response.status_code == 302

    # Verificar eliminación
    deleted_task = db.session.get(Task, task.id)
    assert deleted_task is None

@patch('app.google.authorize_redirect')
def test_google_login(mock_authorize_redirect, client):
    # Simular la redirección de autorización
    mock_authorize_redirect.return_value = redirect('/tasks')  # Simular redirección a una página válida

    # Realizar la solicitud a la ruta /google_login
    response = client.get('/google_login')

    # Verificar que la redirección se intentó
    mock_authorize_redirect.assert_called_once()
    assert response.status_code == 302  # Código de redirección
    assert response.location == '/tasks'  # Verificar la ubicación de la redirección



from unittest.mock import patch

@patch('app.google.authorize_access_token')
@patch('app.google.get')
def test_google_authorize(mock_get, mock_authorize, client):
    mock_authorize.return_value = {'userinfo': {'sub': '12345', 'email': 'testuser@gmail.com'}}
    mock_get.return_value.json.return_value = {'sub': '12345', 'email': 'testuser@gmail.com'}

    response = client.get('/google_authorize')
    assert response.status_code == 302
    assert response.headers['Location'] == '/tasks'

    user = User.query.filter_by(google_id='12345').first()
    assert user is not None
    assert user.username == 'testuser@gmail.com'

def test_server_running(client):
    response = client.get('/login')
    assert response.status_code == 200
