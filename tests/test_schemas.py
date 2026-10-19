"""
Unit tests for Marshmallow Schemas and Schema Validations.
"""

import pytest
from datetime import date
from marshmallow import ValidationError

from schemas import (
    exercise_schema,
    workout_schema,
    workout_exercise_schema
)


def test_exercise_schema_valid_dump_and_load():
    """Test ExerciseSchema serialization and deserialization."""
    payload = {
        "name": "Bicep Curl",
        "category": "Strength",
        "equipment_needed": True
    }
    loaded = exercise_schema.load(payload)
    assert loaded["name"] == "Bicep Curl"
    assert loaded["category"] == "Strength"
    assert loaded["equipment_needed"] is True


def test_exercise_schema_validation_length():
    """Test ExerciseSchema validation error on short name."""
    with pytest.raises(ValidationError) as exc:
        exercise_schema.load({"name": "A", "category": "Strength"})
    assert "name" in exc.value.messages


def test_workout_schema_valid_load():
    """Test WorkoutSchema loading valid data."""
    payload = {
        "date": "2026-10-19",
        "duration_minutes": 60,
        "notes": "Good pump"
    }
    loaded = workout_schema.load(payload)
    assert loaded["duration_minutes"] == 60
    assert loaded["date"] == date(2026, 10, 19)


def test_workout_schema_invalid_duration():
    """Test WorkoutSchema validation on duration range."""
    # Zero duration
    with pytest.raises(ValidationError) as exc:
        workout_schema.load({"date": "2026-10-19", "duration_minutes": 0})
    assert "duration_minutes" in exc.value.messages

    # Exceeding 24 hours
    with pytest.raises(ValidationError) as exc:
        workout_schema.load({"date": "2026-10-19", "duration_minutes": 1500})
    assert "duration_minutes" in exc.value.messages


def test_workout_exercise_schema_validation():
    """Test WorkoutExerciseSchema sets and reps validation."""
    # Negative reps
    with pytest.raises(ValidationError) as exc:
        workout_exercise_schema.load({
            "workout_id": 1,
            "exercise_id": 1,
            "sets": 3,
            "reps": -5
        })
    assert "reps" in exc.value.messages

    # Negative sets
    with pytest.raises(ValidationError) as exc:
        workout_exercise_schema.load({
            "workout_id": 1,
            "exercise_id": 1,
            "sets": -1,
            "reps": 10
        })
    assert "sets" in exc.value.messages
