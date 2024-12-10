# Testing Guide for Todo-List Application

## Introduction
This document provides a comprehensive guide to testing the Todo-List application. The testing framework used is `pytest` with additional tools like `pytest-cov` for code coverage and `bandit` for security checks.

---

## Types of Tests

### 1. Unit Tests
- Focus on individual functions and methods.
- Located in the `tests/` directory.

### 2. Integration Tests
- Test the interaction between different modules of the application.

### 3. End-to-End (E2E) Tests
- Simulate user behavior to validate the entire application workflow.

---

## Running Tests

### 1. Prerequisites
Ensure the following are installed:
- `pytest`
- `pytest-cov`
- `bandit`

Install them via pip:
```bash
pip install pytest pytest-cov bandit
```

### 2. Run All Tests
```bash
pytest
```

### 3. Run Specific Test Files
To run a specific test file, use:
```bash
pytest tests/test_<filename>.py
```

### 4. Run Tests with Coverage
To generate a code coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

### 5. Run Security Checks
Use `bandit` to scan for security vulnerabilities:
```bash
bandit -r .
```

---

## Test Coverage

### Generate Coverage Report
To generate an HTML report:
```bash
pytest --cov=app --cov-report=html
```
The report will be available in the `htmlcov/` directory.

---

## Test Files Overview

### 1. `test_e2e.py`
- **Purpose**: End-to-end tests for user workflows like login, task management, and weather API.
- **Example Command**:
  ```bash
  pytest tests/test_e2e.py
  ```

### 2. `test_integration.py`
- **Purpose**: Tests for database operations and session management.
- **Example Command**:
  ```bash
  pytest tests/test_integration.py
  ```

### 3. `test_task.py`
- **Purpose**: Unit tests for task-related operations (CRUD).
- **Example Command**:
  ```bash
  pytest tests/test_task.py
  ```

### 4. `test_user.py`
- **Purpose**: Unit tests for user-related operations (login, registration).
- **Example Command**:
  ```bash
  pytest tests/test_user.py
  ```

---

## Test Environment Setup

### 1. Configure Test Database
Update the `.env` file with the test database URI:
```env
TEST_DATABASE_URI=sqlite:///:memory:
```

### 2. Use Fixtures in `conftest.py`
- The `conftest.py` file provides reusable fixtures for setting up the test environment.

### Example Fixture for Database
```python
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
```

---

## Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError`
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

#### Issue: `Database Not Initialized`
**Solution**: Run the database setup commands:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### Issue: `Tests Fail with Flask Context Errors`
**Solution**: Use the `@pytest.fixture` to set up the app context properly.

---

## Best Practices

1. **Use Descriptive Test Names**
   - Name your tests to clearly indicate their purpose.

2. **Keep Tests Independent**
   - Ensure tests do not depend on the state created by other tests.

3. **Use Assertions Effectively**
   - Validate both expected outcomes and edge cases.

4. **Run Tests Frequently**
   - Integrate testing into your development workflow to catch issues early.



