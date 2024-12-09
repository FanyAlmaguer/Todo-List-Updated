import pytest
from app import app, db, User, Task
from werkzeug.security import generate_password_hash  # Importar para hashing de contraseñas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.parametrize("browser", ["chrome", "edge"])
def test_cross_browser_compatibility(browser):
    if browser == "chrome":
        driver = webdriver.Chrome()
    elif browser == "edge":
        driver = webdriver.Edge()

    # Cambiar la ruta a '/login' y buscar texto existente
    driver.get("http://127.0.0.1:5000/login")
    assert "LOGIN" in driver.page_source  # Busca texto presente en login.html
    driver.quit()



@pytest.fixture(scope="function", autouse=True)
def clean_database():
    # Activar el contexto de la aplicación
    with app.app_context():
        db.session.query(Task).delete()  # Eliminar todas las tareas
        db.session.query(User).delete()  # Eliminar todos los usuarios
        db.session.commit()

def test_user_registration():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000/register")

    # Llenar el formulario de registro
    username_field = driver.find_element(By.ID, "register-username")
    password_field = driver.find_element(By.ID, "register-password")
    register_button = driver.find_element(By.ID, "register-button")

    username_field.send_keys("test_user")
    password_field.send_keys("secure_password")
    register_button.click()

    assert "Login" in driver.title
    driver.quit()


def test_user_login():
    driver = webdriver.Chrome()

    # Crear usuario si no existe
    with app.app_context():
        if not User.query.filter_by(username="test_user").first():
            user = User(username="test_user", password=generate_password_hash("secure_password"))
            db.session.add(user)
            db.session.commit()

    driver.get("http://localhost:5000/login")

    # Intentar iniciar sesión
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.ID, "login-button")

    username_field.send_keys("test_user")
    password_field.send_keys("secure_password")
    login_button.click()

    # Verificar redirección a la página de tareas
    assert "To Do List" in driver.page_source
    driver.quit()




def test_task_management():
    driver = webdriver.Chrome()

    # Crear usuario si no existe
    with app.app_context():
        if not User.query.filter_by(username="test_user").first():
            user = User(username="test_user", password=generate_password_hash("secure_password"))
            db.session.add(user)
            db.session.commit()

    driver.get("http://localhost:5000/login")

    # Login
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.ID, "login-button")
    username_field.send_keys("test_user")
    password_field.send_keys("secure_password")
    login_button.click()

    # Crear una nueva tarea
    task_field = driver.find_element(By.ID, "task-input")
    priority_field = driver.find_element(By.ID, "priority-select")
    add_task_button = driver.find_element(By.ID, "add-task-button")
    task_field.send_keys("Test Task")
    priority_field.send_keys("1")
    add_task_button.click()

    # Verificar que la tarea se haya creado
    assert "Test Task" in driver.page_source

    driver.quit()



def test_google_oauth_login():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000/google_login")

    # Verificar redirección a Google OAuth
    assert "accounts.google.com" in driver.current_url

    # Simular el flujo de OAuth completado (esto requeriría un entorno de prueba más avanzado como Selenium Grid o un mock para OAuth)
    # Aquí solo verificamos que la redirección inicial es correcta
    driver.quit()


def test_responsive_design():
    driver = webdriver.Chrome()

    # Tamaño de escritorio
    driver.set_window_size(1920, 1080)
    driver.get("http://localhost:5000/login")
    assert "LOGIN" in driver.page_source

    # Tamaño de tableta
    driver.set_window_size(768, 1024)
    assert "LOGIN" in driver.page_source

    # Tamaño de móvil
    driver.set_window_size(375, 812)
    assert "LOGIN" in driver.page_source

    driver.quit()





