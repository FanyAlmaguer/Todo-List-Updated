import sys
import os
from sqlalchemy.exc import SQLAlchemyError

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app import Task, User, db
from werkzeug.security import generate_password_hash

# Prueba existente: Crear una tarea
def test_create_task(client):
    try:
        # Crear una tarea
        task = Task(user_id=1, task="Sample Task", priority=1)
        db.session.add(task)
        db.session.commit()

        # Verificar que se guardó correctamente
        assert task.id is not None
        assert task.task == "Sample Task"
        assert task.priority == 1
    except SQLAlchemyError as e:
        print(f"Error en la base de datos: {e}")
        assert False

# Nueva prueba: Leer una tarea
def test_read_task(client):
    try:
        # Crear una tarea
        task = Task(user_id=1, task="Read Task Test", priority=2)
        db.session.add(task)
        db.session.commit()

        # Leer la tarea
        retrieved_task = Task.query.filter_by(task="Read Task Test").first()
        assert retrieved_task is not None
        assert retrieved_task.task == "Read Task Test"
        assert retrieved_task.priority == 2
    except SQLAlchemyError as e:
        print(f"Error en la base de datos: {e}")
        assert False

# Nueva prueba: Actualizar una tarea
def test_update_task(client):
    try:
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
    except SQLAlchemyError as e:
        print(f"Error en la base de datos: {e}")
        assert False

# Nueva prueba: Eliminar una tarea
def test_delete_task(client):
    try:
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
    except SQLAlchemyError as e:
        print(f"Error en la base de datos: {e}")
        assert False

# Nueva prueba: Relación entre User y Task
def test_task_user_relationship(client):
    try:
        # Crear un usuario
        user = User(username="test_user_rel", password=generate_password_hash("secure_password"))
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
    except SQLAlchemyError as e:
        print(f"Error en la base de datos: {e}")
        assert False
