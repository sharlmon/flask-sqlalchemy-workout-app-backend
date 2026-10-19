"""
Shared pytest fixtures for Workout Application test suite.
"""

import os
import sys
import pytest
from datetime import date

# Add server directory to path
server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server'))
sys.path.insert(0, server_dir)

from app import create_app
from models import db, Exercise, Workout, WorkoutExercise


@pytest.fixture
def app():
    """Create a test application instance with an isolated in-memory SQLite database."""
    test_app = create_app(database_uri="sqlite:///:memory:")
    test_app.config['TESTING'] = True

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """Seed initial sample data into the in-memory database and return stable IDs."""
    with app.app_context():
        ex1 = Exercise(name="Bench Press", category="Strength", equipment_needed=True)
        ex2 = Exercise(name="Push-Ups", category="Bodyweight", equipment_needed=False)
        db.session.add_all([ex1, ex2])
        db.session.commit()

        w1 = Workout(date=date.today(), duration_minutes=45, notes="Upper body workout")
        db.session.add(w1)
        db.session.commit()

        we1 = WorkoutExercise(workout_id=w1.id, exercise_id=ex1.id, sets=3, reps=10)
        db.session.add(we1)
        db.session.commit()

        return {
            "workout_id": w1.id,
            "exercise1_id": ex1.id,
            "exercise2_id": ex2.id,
            "workout_exercise_id": we1.id
        }
