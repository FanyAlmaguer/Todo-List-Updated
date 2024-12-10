# Setup Guide

## Local Development Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-folder>

2. Set up a virtual environment:
python3 -m venv venv
source venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Create a .env file with the following:
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
FLASK_SECRET_KEY=<your-secret-key>
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
OPENWEATHER_API_KEY=<your-weather-api-key>


## Local Development Setup
1. Build the Docker image:
docker build -t todo-app .

2. Run the Docker container:
docker run -p 5000:5000 --env-file .env todo-app

## CI/CD Pipeline Configuration

GitHub Actions is used for CI/CD.
The pipeline includes:
Testing with pytest.
Building and pushing a Docker image to Docker Hub.
Triggering deployment on Render.


## Troubleshooting
Database Errors: Ensure the SQLALCHEMY_DATABASE_URI is correctly configured.
OAuth Issues: Verify your Google OAuth credentials.

Database Errors: Ensure the SQLALCHEMY_DATABASE_URI is correctly configured.
OAuth Issues: Verify your Google OAuth credentials.


#### 3. Testing Guide (`Testing_Guide.md`)
```markdown
# Testing Guide

## Test Plan and Strategy
- **Unit Tests**: Cover individual functions.
- **Integration Tests**: Validate interactions between components.
- **End-to-End Tests**: Test complete user workflows.

---

## Running Tests
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate

2. Run all tests:
pytest --disable-warnings

3. Generate a coverage report:
pytest --cov=./ --cov-report=term-missing


----

## Test Cases
Example: User Registration
Input: Username and password
Expected Result: Redirect to login page.
Test File: test_user.py


## Performance Tests
Stress tests are located in stress_test.py. To execute:
python stress_test.py


## Security Audit Reports
Use bandit and safety:
bandit -r .
safety check

