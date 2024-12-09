from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '123AD0'

# Configuración de SQLite con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición de modelos para las tablas
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=3)  # 1: Alta, 2: Media, 3: Baja

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/tasks')
        else:
            return "Login failed"
    return render_template('login.html')

# Página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

# Página de la To Do List
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        task = request.form['task']
        priority = int(request.form['priority'])  # Obtener la prioridad del formulario
        new_task = Task(user_id=session['user_id'], task=task, priority=priority)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/tasks')

    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template('tasks.html', tasks=tasks)

# Editar una tarea
@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    new_task = request.form['task']
    new_priority = int(request.form['priority'])  # Obtener la nueva prioridad
    task = Task.query.get(task_id)
    if task and task.user_id == session['user_id']:
        task.task = new_task
        task.priority = new_priority
        db.session.commit()
    return redirect('/tasks')

# Eliminar una tarea
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()
    return redirect('/tasks')

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

