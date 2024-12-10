# Code Documentation

## Overview
This project is a "To-Do List Application" that includes user authentication (via Google OAuth), task management, and a weather API integration. The application is built using Flask, with a PostgreSQL database and integration with Docker for deployment.

---

## Project Structure
app.py # Main application entry point
/templates # HTML templates for rendering UI
/static # CSS and JS files for styling and interactivity
/tests # Unit and integration tests
dockerfile # Docker configuration file
requirements.txt # Python dependencies
.env # Environment variables (not included in repo)


---

## Key Components
### Endpoints
- `/register`: User registration
- `/login`: User login
- `/google_login`: Login via Google OAuth
- `/tasks`: Task management
- `/weatherstack`: Weather API integration
- `/logout`: Logout

### Environment Variables
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `FLASK_SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI`
- `OPENWEATHER_API_KEY` (for WeatherStack API)

---

## Functions and Modules
### app.py
- `get_weatherstack()`: Fetches weather data using WeatherStack API.
- `register()`, `login()`, `logout()`: Handles user authentication.
- `tasks()`: Manages task CRUD operations.

### Testing
The `/tests` folder includes:
- End-to-End tests (`test_e2e.py`)
- Integration tests (`test_integration.py`)
- Unit tests (`test_task.py` and `test_user.py`)
