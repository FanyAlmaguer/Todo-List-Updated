import pytest
import os
from app import app, db, User, Task
from werkzeug.security import generate_password_hash
from selenium import webdriver
from selenium.webdriver.common.by import By

@pytest.mark.parametrize("browser", ["chrome", "edge"])
def test_cross_browser_compatibility(browser):
    driver = None
    try:
        if browser == "chrome":
            driver = webdriver.Chrome()
        elif browser == "edge":
            driver = webdriver.Edge()

        # Verificar que la página de login carga correctamente
        driver.get("http://127.0.0.1:5000/login")
        assert "LOGIN" in driver.page_source  # Busca texto presente en login.html
    finally:
        if driver:
            driver.quit()


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    with app.app_context():
        db.session.query(Task).delete()
        db.session.query(User).delete()
        db.session.commit()

def test_user_registration():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:5000/register")

        # Llenar el formulario de registro
        username_field = driver.find_element(By.ID, "register-username")
        password_field = driver.find_element(By.ID, "register-password")
        register_button = driver.find_element(By.ID, "register-button")

        username_field.send_keys("test_user")
        password_field.send_keys(os.getenv("TEST_USER_PASSWORD", "secure_password"))
        register_button.click()

        assert "Login" in driver.title
    finally:
        driver.quit()


def test_user_login():
    driver = webdriver.Chrome()
    try:
        # Crear usuario si no existe
        with app.app_context():
            if not User.query.filter_by(username="test_user").first():
                user = User(username="test_user", password=generate_password_hash(os.getenv("TEST_USER_PASSWORD", "secure_password")))
                db.session.add(user)
                db.session.commit()

        driver.get("http://localhost:5000/login")

        # Intentar iniciar sesión
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login-button")

        username_field.send_keys("test_user")
        password_field.send_keys(os.getenv("TEST_USER_PASSWORD", "secure_password"))
        login_button.click()

        # Verificar redirección a la página de tareas
        assert "To Do List" in driver.page_source
    finally:
        driver.quit()


def test_task_management():
    driver = webdriver.Chrome()
    try:
        # Crear usuario si no existe
        with app.app_context():
            if not User.query.filter_by(username="test_user").first():
                user = User(username="test_user", password=generate_password_hash(os.getenv("TEST_USER_PASSWORD", "secure_password")))
                db.session.add(user)
                db.session.commit()

        driver.get("http://localhost:5000/login")

        # Login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login-button")
        username_field.send_keys("test_user")
        password_field.send_keys(os.getenv("TEST_USER_PASSWORD", "secure_password"))
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
    finally:
        driver.quit()


def test_google_oauth_login():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:5000/google_login")
        assert "accounts.google.com" in driver.current_url
    finally:
        driver.quit()


def test_responsive_design():
    driver = webdriver.Chrome()
    try:
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
    finally:
        driver.quit()






