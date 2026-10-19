"""
Unit tests for SQLAlchemy Models, Table Constraints, Validations, and Relationships.
"""

import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise


def test_exercise_creation_valid(app):
    """Test creating an exercise with valid attributes."""
    with app.app_context():
        ex = Exercise(name="Squat", category="Strength", equipment_needed=True)
        db.session.add(ex)
        db.session.commit()

        assert ex.id is not None
        assert ex.name == "Squat"
        assert ex.category == "Strength"
        assert ex.equipment_needed is True


def test_exercise_name_validation(app):
    """Test model validation rejects invalid exercise names."""
    with app.app_context():
        # Name too short
        with pytest.raises(ValueError, match="at least 2 characters"):
            Exercise(name="A", category="Strength")

        # Name empty
        with pytest.raises(ValueError, match="at least 2 characters"):
            Exercise(name="   ", category="Strength")


def test_exercise_category_validation(app):
    """Test model validation rejects invalid category."""
    with app.app_context():
        with pytest.raises(ValueError, match="non-empty string"):
            Exercise(name="Deadlift", category=" ")


def test_exercise_unique_name_constraint(app):
    """Test unique table constraint on exercise name."""
    with app.app_context():
        ex1 = Exercise(name="Pull-Ups", category="Bodyweight")
        db.session.add(ex1)
        db.session.commit()

        ex2 = Exercise(name="Pull-Ups", category="Strength")
        db.session.add(ex2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_workout_creation_valid(app):
    """Test creating a workout with valid attributes."""
    with app.app_context():
        w = Workout(date=date.today(), duration_minutes=60, notes="Good session")
        db.session.add(w)
        db.session.commit()

        assert w.id is not None
        assert w.duration_minutes == 60
        assert w.notes == "Good session"


def test_workout_duration_validation(app):
    """Test model validation rejects non-positive workout duration."""
    with app.app_context():
        with pytest.raises(ValueError, match="positive integer greater than 0"):
            Workout(date=date.today(), duration_minutes=0)

        with pytest.raises(ValueError, match="positive integer greater than 0"):
            Workout(date=date.today(), duration_minutes=-15)


def test_workout_exercise_creation_and_relationships(app):
    """Test WorkoutExercise join table and relationships."""
    with app.app_context():
        ex = Exercise(name="Overhead Press", category="Strength")
        w = Workout(date=date.today(), duration_minutes=50)
        db.session.add_all([ex, w])
        db.session.commit()

        we = WorkoutExercise(workout=w, exercise=ex, sets=4, reps=8)
        db.session.add(we)
        db.session.commit()

        assert we.id is not None
        assert we.workout_id == w.id
        assert we.exercise_id == ex.id
        assert we.sets == 4
        assert we.reps == 8

        # Test relationship access
        assert we.exercise.name == "Overhead Press"
        assert we.workout.duration_minutes == 50
        assert len(w.workout_exercises) == 1
        assert len(ex.workout_exercises) == 1


def test_cascade_delete_workout_deletes_workout_exercises(app):
    """Test deleting a workout cascades and removes associated WorkoutExercise records."""
    with app.app_context():
        ex = Exercise(name="Plank", category="Core")
        w = Workout(date=date.today(), duration_minutes=30)
        db.session.add_all([ex, w])
        db.session.commit()

        we = WorkoutExercise(workout=w, exercise=ex, sets=3, duration_seconds=60)
        db.session.add(we)
        db.session.commit()
        we_id = we.id

        # Delete workout
        db.session.delete(w)
        db.session.commit()

        # WorkoutExercise should be gone
        assert db.session.get(WorkoutExercise, we_id) is None
        # Exercise itself should remain intact
        assert db.session.get(Exercise, ex.id) is not None


def test_cascade_delete_exercise_deletes_workout_exercises(app):
    """Test deleting an exercise cascades and removes associated WorkoutExercise records."""
    with app.app_context():
        ex = Exercise(name="Lunges", category="Strength")
        w = Workout(date=date.today(), duration_minutes=40)
        db.session.add_all([ex, w])
        db.session.commit()

        we = WorkoutExercise(workout=w, exercise=ex, sets=3, reps=12)
        db.session.add(we)
        db.session.commit()
        we_id = we.id

        # Delete exercise
        db.session.delete(ex)
        db.session.commit()

        # WorkoutExercise should be gone
        assert db.session.get(WorkoutExercise, we_id) is None
        # Workout itself should remain intact
        assert db.session.get(Workout, w.id) is not None
