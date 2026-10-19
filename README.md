# Flask SQLAlchemy Workout Application Backend

A robust, enterprise-grade backend API for a personal trainer workout tracking application, built with **Python**, **Flask**, **SQLAlchemy**, **Flask-Migrate**, and **Marshmallow**.

This system models workouts, reusable exercises, and their associative relationships (tracking sets, reps, and duration metrics), complete with 3-tier validation (Table Constraints, Model Validations, Schema Validations) and full RESTful serialization.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Database Entities & Relationships](#database-entities--relationships)
3. [Three-Tier Validation Architecture](#three-tier-validation-architecture)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Database Migration & Seeding](#database-migration--seeding)
7. [Running the Application](#running-the-application)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Running Unit Tests](#running-unit-tests)
10. [Git Workflow & History](#git-workflow--history)

---

## Project Overview

Personal trainers need a reliable, normalized system to log custom workouts while reusing exercise definitions across clients and routines.

This API fulfills this need by:
- Managing **Workouts** (date, duration, notes).
- Managing reusable **Exercises** (name, category, equipment requirements).
- Joining them through **WorkoutExercises** with specific sets, reps, and duration seconds.
- Automatically cascading deletions so removing a workout or exercise safely cleans up orphaned join records.
- Enforcing rigorous constraints at the database, model, and serialization layer.

---

## Database Entities & Relationships

```
+--------------------+              +--------------------+              +--------------------+
|     Workouts       | 1          * |  WorkoutExercises  | *          1 |     Exercises      |
+--------------------+--------------+--------------------+--------------+--------------------+
| id (PK)            |              | id (PK)            |              | id (PK)            |
| date               |              | workout_id (FK)    |              | name (Unique)      |
| duration_minutes   |              | exercise_id (FK)   |              | category           |
| notes              |              | sets               |              | equipment_needed   |
+--------------------+              | reps               |              +--------------------+
                                    | duration_seconds   |
                                    +--------------------+
```

### Entity Relationships
- A `Workout` **has many** `WorkoutExercises` (with cascade delete).
- An `Exercise` **has many** `WorkoutExercises` (with cascade delete).
- A `WorkoutExercise` **belongs to** a `Workout` and **belongs to** an `Exercise`.
- A `Workout` **has many** `Exercises` through `WorkoutExercises`.
- An `Exercise` **has many** `Workouts` through `WorkoutExercises`.

---

## Three-Tier Validation Architecture

The application implements defense-in-depth data integrity across three distinct tiers:

| Tier | Implementation | Validations Enforced |
| :--- | :--- | :--- |
| **1. Table Constraints** | SQLite DDL via SQLAlchemy | • `nullable=False` on critical fields<br>• `unique=True` on `Exercise.name`<br>• `CheckConstraint('length(name) >= 2')`<br>• `CheckConstraint('duration_minutes > 0')`<br>• `CheckConstraint('reps >= 0')`<br>• `CheckConstraint('sets >= 0')`<br>• `CheckConstraint('duration_seconds >= 0')` |
| **2. Model Validations** | `@validates` decorators in `models.py` | • `validate_name`: non-empty string with minimum 2 characters<br>• `validate_category`: non-empty string<br>• `validate_duration_minutes`: must be positive integer (> 0)<br>• `validate_date`: valid date object or YYYY-MM-DD format<br>• `validate_sets` / `validate_reps` / `validate_duration`: non-negative integers |
| **3. Schema Validations** | Marshmallow fields & `validate` rules | • `validate.Length(min=2, max=100)` on exercise name<br>• `validate.Length(min=2, max=50)` on category<br>• `validate.Range(min=1, max=1440)` on workout duration<br>• `validate.Range(min=0, max=1000)` on reps<br>• `validate.Range(min=0, max=100)` on sets<br>• Custom `@validates` methods rejecting blank or whitespace-only inputs |

---

## Project Structure

```
flask-sqlalchemy-workout-app-backend/
├── Pipfile                   # Pipenv package manifest
├── requirements.txt          # Python pip dependencies
├── .gitignore                # Ignored environments, databases, and caches
├── README.md                 # Complete documentation
├── server/
│   ├── app.py                # Flask application factory, routes, and error handlers
│   ├── models.py             # SQLAlchemy entities, relationships, constraints, and validations
│   ├── schemas.py            # Marshmallow serialization schemas and schema validations
│   ├── seed.py               # Database reset and initial sample data seeding script
│   └── migrations/           # Alembic database migration versions
└── tests/
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures and isolated in-memory test database
    ├── test_models.py        # Model, constraint, validation, and cascade delete tests
    ├── test_schemas.py       # Marshmallow serialization and schema validation tests
    └── test_routes.py        # Complete API endpoint and status code test suite
```

---

## Installation & Setup

### Prerequisites

- **Python 3.8+**
- **pip** or **pipenv**
- **git**

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd flask-sqlalchemy-workout-app-backend
```

### 2. Install Dependencies

Using `pip`:
```bash
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Using `pipenv`:
```bash
pipenv install
pipenv shell
```

---

## Database Migration & Seeding

Navigate into the `server/` directory:

```bash
cd server
```

### 1. Initialize and Run Migrations

```bash
flask db init
flask db migrate -m "initial migration: create exercises, workouts, and workout_exercises tables"
flask db upgrade head
```

### 2. Seed Initial Data

```bash
python seed.py
```

This populates:
- **10 Exercises** (Bench Press, Squat, Deadlift, Pull-Ups, Push-Ups, Sprints, etc.)
- **4 Workouts** (Upper Body, Lower Body, HIIT Cardio, Full Body)
- **12 WorkoutExercise associations** linking workouts to exercises with sets, reps, and duration metrics.

---

## Running the Application

From the `server/` directory:

```bash
python app.py
```

Or using Flask CLI:
```bash
export FLASK_APP=app.py
flask run --port=5555
```

The server will be available at: **`http://127.0.0.1:5555/`**

---

## API Endpoints Reference

### Base URL: `http://127.0.0.1:5555`

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Welcome & Endpoint Documentation Index | `200 OK` |
| `GET` | `/workouts` | List all logged workouts | `200 OK` |
| `GET` | `/workouts/<id>` | View single workout with associated exercises, reps, sets, and duration | `200 OK` / `404 Not Found` |
| `POST` | `/workouts` | Create a new workout session | `201 Created` / `400 Bad Request` |
| `DELETE`| `/workouts/<id>` | Delete workout and cascade remove associated join records | `200 OK` / `404 Not Found` |
| `GET` | `/exercises` | List all reusable exercises | `200 OK` |
| `GET` | `/exercises/<id>` | View single exercise and its associated workout history | `200 OK` / `404 Not Found` |
| `POST` | `/exercises` | Create a new exercise | `201 Created` / `400 Bad Request` / `409 Conflict` |
| `DELETE`| `/exercises/<id>` | Delete exercise and cascade remove associated join records | `200 OK` / `404 Not Found` |
| `POST` | `/workouts/<w_id>/exercises/<e_id>/workout_exercises` | Add an exercise to a workout with sets, reps, duration | `201 Created` / `400 Bad Request` / `404 Not Found` |
| `POST` | `/workout_exercises` | Standard REST endpoint to create join record | `201 Created` / `400 Bad Request` / `404 Not Found` |
| `GET` | `/workout_exercises` | List all workout exercise records | `200 OK` |

### Example Payloads

#### Create Workout (`POST /workouts`)
```json
{
  "date": "2026-10-20",
  "duration_minutes": 60,
  "notes": "Chest & Triceps Focus"
}
```

#### Create Exercise (`POST /exercises`)
```json
{
  "name": "Dumbbell Lateral Raise",
  "category": "Strength",
  "equipment_needed": true
}
```

#### Add Exercise to Workout (`POST /workouts/1/exercises/2/workout_exercises`)
```json
{
  "sets": 4,
  "reps": 12,
  "duration_seconds": null
}
```

---

## Running Unit Tests

A comprehensive suite of **30 automated tests** validates models, schema serialization, validations, cascading deletes, and API endpoints against an isolated in-memory SQLite database.

From the repository root:

```bash
pytest -v
```

Expected output:
```
============================= test session starts ==============================
collected 30 items

tests/test_models.py::test_exercise_creation_valid PASSED                [  3%]
tests/test_models.py::test_exercise_name_validation PASSED               [  6%]
tests/test_models.py::test_exercise_category_validation PASSED           [ 10%]
tests/test_models.py::test_exercise_unique_name_constraint PASSED        [ 13%]
tests/test_models.py::test_workout_creation_valid PASSED                 [ 16%]
tests/test_models.py::test_workout_duration_validation PASSED            [ 20%]
tests/test_models.py::test_workout_exercise_creation_and_relationships PASSED [ 23%]
tests/test_models.py::test_cascade_delete_workout_deletes_workout_exercises PASSED [ 26%]
tests/test_models.py::test_cascade_delete_exercise_deletes_workout_exercises PASSED [ 30%]
tests/test_routes.py::test_index_route PASSED                            [ 33%]
...
tests/test_schemas.py::test_workout_exercise_schema_validation PASSED    [100%]

============================== 30 passed in 0.26s ==============================
```

---

## Git Workflow & History

This project was built following a strict Git feature-branching workflow:

1. `main`: Stable release branch.
2. `feature/models-relationships-constraints`: Defined Exercise, Workout, and WorkoutExercise models with relationships, table constraints, and model validations.
3. `feature/marshmallow-schemas`: Built Marshmallow serialization schemas and schema-level validation rules.
4. `feature/api-endpoints`: Implemented RESTful endpoints and error handlers.
5. `feature/database-migrations-seed`: Ran Flask-Migrate migrations and implemented `seed.py`.
6. `feature/test-suite`: Added 30 unit tests with isolated database fixtures.
7. `feature/documentation`: Created complete documentation and setup guides.

All branches were merged using `--no-ff` (non-fast-forward) to preserve a clean and legible commit graph.
