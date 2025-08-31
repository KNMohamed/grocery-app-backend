# Grocery List App

A RESTful API backend for the RideCo Grocery List application

## Overview

- Grocery list management for a family of 1
- Comprehensive test coverage

## Tech Stack

- **Framework**: Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate
- **Containerization**: Docker & Docker Compose
- **Python**: 3.10+

## Architecture

This project follows clean architecture principles using the **Service Layer Pattern** and **Repository Pattern** to maintain separation of concerns and testability.

### Directory Structure

```
├── adapters/
│   ├── __init__.py
│   ├── repository.py  # Database repository implementations
│   └── orm.py         # SQLAlchemy ORM mappings
├── domain/
│   ├── __init__.py
│   ├── models.py      # Domain entities
├── service_layer/
│   ├── __init__.py
│   ├── services.py    # Business logic
├── entrypoints/
│   ├── __init__.py
│   ├── flask_app.py   # Flask application and routes
├── tests/             # Test suite
│   ├── __init__.py
│   ├── unit/          # Unit tests for domain logic
│   ├── integration/   # Integration tests for adapters
│   └── e2e/          # End-to-end API tests
├── config.py          # Application configuration
├── ...
```

**Repository Pattern (`adapters/`)**
- Abstracts data access logic from business logic
- Provides a consistent interface for data operations
- Easy testing with mock repositories
- Isolates domain models from persistence concerns

**Service Layer Pattern (`service_layer/`)**
- Business operations and use cases
- Coordinates between domain models and repositories
- Handles transaction boundaries via Unit of Work (TODO)

**Domain Layer (`domain/`)**
- Represents the core business concepts
- Contains pure business logic and rules
- Defines entities, value objects

**Entrypoints (`entrypoints/`)**
- Handles HTTP requests
- Translates between external formats and domain models
- Delegates to service layer

## Getting Started
### Using Docker (Recommended)

```bash
# Start the application in detached mode
docker-compose up -d --build

# Stop the application
docker-compose down
```

### Local Development (Prefer Docker Instead)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/KNMohamed/grocery-app-backend.git
cd grocery-app-backend

# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
source .venv/bin/activate  

# Set environment variables
export FLASK_APP=entrypoints/flask_app.py
export FLASK_DEBUG=1

# Run the application
uv run flask run
```

## Testing

Run the test suite using pytest:

```bash
# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
source .venv/bin/activate  
# Run all tests
pytest

# Run specific test types
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only
```

## Linting
```bash
uv run ruff check
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade
```