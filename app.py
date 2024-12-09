from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
import os
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Configuración de SQLite con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuración de OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=GOOGLE_DISCOVERY_URL,
    client_kwargs={
        'scope': 'openid email profile',
    }
)

# Definición de modelos para las tablas
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)  # La contraseña será opcional para usuarios de Google
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Campo para almacenar el ID de Google

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=3)  # 1: Alta, 2: Media, 3: Baja

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Rutas de Google OAuth
@app.route('/google_login')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google_authorize')
def google_authorize():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')  # Obtener información del usuario desde el token
    if not user_info:
        user_info = google.get('userinfo').json()  # Si no está en el token, obtenerla del endpoint de Google

    # Buscar al usuario en la base de datos
    user = User.query.filter_by(google_id=user_info['sub']).first()
    if not user:
        # Si no existe, crearlo
        user = User(
            username=user_info['email'],
            google_id=user_info['sub']
        )
        db.session.add(user)
        db.session.commit()

    # Iniciar sesión
    session['user_id'] = user.id
    return redirect('/tasks')

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            return render_template('login.html', error="Login failed: Fields cannot be empty.")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/tasks')
        else:
            return render_template('login.html', error="Login failed: Invalid username or password.")

    return render_template('login.html')

# Página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            return render_template('register.html', error="Fields cannot be empty.")

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists.")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
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
        task_name = request.form['task'].strip()
        priority = request.form['priority'].strip()

        if not task_name or not priority or int(priority) not in [1, 2, 3]:
            return render_template('tasks.html', tasks=Task.query.filter_by(user_id=session['user_id']).all(), error="Invalid input.")

        new_task = Task(user_id=session['user_id'], task=task_name, priority=int(priority))
        db.session.add(new_task)
        db.session.commit()
        return redirect('/tasks')

    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template('tasks.html', tasks=tasks)

# Editar una tarea
@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = db.session.get(Task, task_id)

    if task and task.user_id == session['user_id']:
        new_task_name = request.form['task'].strip()
        new_priority = request.form['priority'].strip()

        if not new_task_name or not new_priority:
            tasks = Task.query.filter_by(user_id=session['user_id']).all()
            return render_template('tasks.html', tasks=tasks, error="Fields cannot be empty.")

        task.task = new_task_name
        task.priority = int(new_priority)
        db.session.commit()
    return redirect('/tasks')

# Eliminar una tarea
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = db.session.get(Task, task_id)
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
    app.run(debug=os.getenv("FLASK_DEBUG", "False") == "True")
