from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def load_login_page(self):
        self.client.get("/login")

    @task(2)
    def user_login(self):
        self.client.post("/login", data={"username": "test_user", "password": "secure_password"})

    @task(2)
    def task_management(self):
        self.client.post("/tasks", data={"task": "Stress Task", "priority": "1"})
        self.client.get("/tasks")

    @task(1)
    def oauth_login(self):
        self.client.get("/google_login")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)  # Simula espera entre tareas
