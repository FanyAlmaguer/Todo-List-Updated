import sys
import os

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app import Task, User, db

# Prueba existente: Crear una tarea
def test_create_task(client):
    # Crear una tarea
    task = Task(user_id=1, task="Sample Task", priority=1)
    db.session.add(task)
    db.session.commit()

    # Verificar que se guardó correctamente
    assert task.id is not None
    assert task.task == "Sample Task"
    assert task.priority == 1

# Nueva prueba: Leer una tarea
def test_read_task(client):
    # Crear una tarea
    task = Task(user_id=1, task="Read Task Test", priority=2)
    db.session.add(task)
    db.session.commit()

    # Leer la tarea
    retrieved_task = Task.query.filter_by(task="Read Task Test").first()
    assert retrieved_task is not None
    assert retrieved_task.task == "Read Task Test"
    assert retrieved_task.priority == 2

# Nueva prueba: Actualizar una tarea
def test_update_task(client):
    # Crear una tarea
    task = Task(user_id=1, task="Update Task Test", priority=3)
    db.session.add(task)
    db.session.commit()

    # Actualizar la tarea
    task.task = "Updated Task"
    task.priority = 1
    db.session.commit()

    # Verificar los cambios
    updated_task = Task.query.filter_by(id=task.id).first()
    assert updated_task.task == "Updated Task"
    assert updated_task.priority == 1

# Nueva prueba: Eliminar una tarea
def test_delete_task(client):
    # Crear una tarea
    task = Task(user_id=1, task="Delete Task Test", priority=3)
    db.session.add(task)
    db.session.commit()

    # Eliminar la tarea
    db.session.delete(task)
    db.session.commit()

    # Verificar que la tarea haya sido eliminada
    deleted_task = Task.query.filter_by(task="Delete Task Test").first()
    assert deleted_task is None

# Nueva prueba: Relación entre User y Task
def test_task_user_relationship(client):
    # Crear un usuario
    user = User(username="test_user_rel", password="password")
    db.session.add(user)
    db.session.commit()

    # Crear tareas asociadas al usuario
    task1 = Task(user_id=user.id, task="Task 1", priority=1)
    task2 = Task(user_id=user.id, task="Task 2", priority=2)
    db.session.add_all([task1, task2])
    db.session.commit()

    # Verificar la relación
    tasks = Task.query.filter_by(user_id=user.id).all()
    assert len(tasks) == 2
    assert tasks[0].task == "Task 1"
    assert tasks[1].task == "Task 2"

def test_tasks_view(client):
    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Verificar acceso a /tasks
    response = client.get('/tasks')
    assert response.status_code == 200

def test_add_task(client):
    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Añadir una nueva tarea
    response = client.post('/tasks', data={
        'task': 'New Task',
        'priority': 2
    })
    assert response.status_code == 302  # Redirección a /tasks

    # Verificar que la tarea fue creada
    task = Task.query.filter_by(task='New Task').first()
    assert task is not None

def test_edit_task(client):
    # Crear usuario y tarea
    user = User(username="edit_test_user", password="password")
    db.session.add(user)
    db.session.commit()
    task = Task(user_id=user.id, task="Edit Me", priority=2)
    db.session.add(task)
    db.session.commit()

    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Editar tarea
    response = client.post(f'/edit_task/{task.id}', data={
        'task': 'Edited Task',
        'priority': 1
    })
    assert response.status_code == 302  # Redirección a /tasks

    # Verificar cambios
    edited_task = db.session.get(Task, task.id)  # Cambiar Task.query.get() por Session.get()
    assert edited_task.task == 'Edited Task'
    assert edited_task.priority == 1

def test_delete_task(client):
    # Crear usuario y tarea
    user = User(username="delete_test_user", password="password")
    db.session.add(user)
    db.session.commit()
    task = Task(user_id=user.id, task="Delete Me", priority=3)
    db.session.add(task)
    db.session.commit()

    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Eliminar tarea
    response = client.get(f'/delete_task/{task.id}')
    assert response.status_code == 302  # Redirección a /tasks

    # Verificar eliminación
    deleted_task = db.session.get(Task, task.id)  # Cambiar Task.query.get() por Session.get()
    assert deleted_task is None

def test_logout(client):
    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Cerrar sesión
    response = client.get('/logout')
    assert response.status_code == 302  # Redirección a /login

    # Verificar que se eliminó la sesión
    with client.session_transaction() as session:
        assert 'user_id' not in session

def test_add_task_empty_field(client):
    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Intentar añadir una tarea con el campo vacío
    response = client.post('/tasks', data={
        'task': '',
        'priority': 2
    })
    assert response.status_code == 200  # No redirige
    assert b"To Do List" in response.data

def test_add_task_invalid_priority(client):
    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Intentar añadir una tarea con prioridad inválida
    response = client.post('/tasks', data={
        'task': 'Invalid Priority Task',
        'priority': 5  # Valor fuera del rango esperado
    })
    assert response.status_code == 200  # No redirige
    assert b"To Do List" in response.data

def test_edit_task_empty_fields(client):
    # Crear usuario y tarea
    user = User(username="edit_user", password="password")
    db.session.add(user)
    db.session.commit()
    task = Task(user_id=user.id, task="Edit Me", priority=2)
    db.session.add(task)
    db.session.commit()

    # Simular un usuario logueado
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Intentar editar la tarea con campos vacíos
    response = client.post(f'/edit_task/{task.id}', data={
        'task': '',
        'priority': ''
    })
    assert response.status_code == 200  # No redirige
    assert b"To Do List" in response.data

def test_tasks_redirect_if_not_logged_in(client):
    response = client.get('/tasks')
    assert response.status_code == 302  # Redirección esperada
    assert '/login' in response.headers['Location']
