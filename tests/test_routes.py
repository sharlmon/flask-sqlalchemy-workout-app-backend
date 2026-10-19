"""
Unit tests for API Endpoints, HTTP Status Codes, and Route Behaviors.
"""

import pytest


def test_index_route(client):
    """GET / returns API index and documentation."""
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert "endpoints" in data
    assert "GET /workouts" in data["endpoints"]


def test_get_workouts(client, sample_data):
    """GET /workouts lists all workouts."""
    res = client.get('/workouts')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["duration_minutes"] == 45


def test_get_workout_by_id_success(client, sample_data):
    """GET /workouts/<id> returns single workout with associated exercises (stretch goal)."""
    w_id = sample_data["workout_id"]
    res = client.get(f'/workouts/{w_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == w_id
    assert "workout_exercises" in data
    assert len(data["workout_exercises"]) == 1
    we = data["workout_exercises"][0]
    assert we["sets"] == 3
    assert we["reps"] == 10
    assert we["exercise"]["name"] == "Bench Press"


def test_get_workout_by_id_not_found(client):
    """GET /workouts/<id> returns 404 for nonexistent workout."""
    res = client.get('/workouts/999')
    assert res.status_code == 404
    assert res.get_json()["error"] == "Not Found"


def test_create_workout_success(client):
    """POST /workouts creates a new workout with 201 Created."""
    payload = {
        "date": "2026-10-20",
        "duration_minutes": 50,
        "notes": "Leg Day testing"
    }
    res = client.post('/workouts', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] is not None
    assert data["duration_minutes"] == 50


def test_create_workout_validation_failure(client):
    """POST /workouts returns 400 when duration is invalid."""
    payload = {
        "date": "2026-10-20",
        "duration_minutes": -10
    }
    res = client.post('/workouts', json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_delete_workout_success_and_cascade(client, sample_data):
    """DELETE /workouts/<id> removes workout and its associations."""
    w_id = sample_data["workout_id"]
    res = client.delete(f'/workouts/{w_id}')
    assert res.status_code == 200

    # Ensure workout no longer exists
    check = client.get(f'/workouts/{w_id}')
    assert check.status_code == 404


def test_delete_workout_not_found(client):
    """DELETE /workouts/<id> returns 404 when ID is missing."""
    res = client.delete('/workouts/9999')
    assert res.status_code == 404


def test_get_exercises(client, sample_data):
    """GET /exercises lists all exercises."""
    res = client.get('/exercises')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2


def test_get_exercise_by_id_success(client, sample_data):
    """GET /exercises/<id> returns exercise with associated workouts."""
    ex_id = sample_data["exercise1_id"]
    res = client.get(f'/exercises/{ex_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "Bench Press"
    assert "workout_exercises" in data


def test_create_exercise_success(client):
    """POST /exercises creates an exercise with 201 Created."""
    payload = {
        "name": "Barbell Incline Press",
        "category": "Strength",
        "equipment_needed": True
    }
    res = client.post('/exercises', json=payload)
    assert res.status_code == 201
    assert res.get_json()["name"] == "Barbell Incline Press"


def test_create_exercise_duplicate_conflict(client, sample_data):
    """POST /exercises returns 409 Conflict if name already exists."""
    payload = {
        "name": "Bench Press",
        "category": "Strength"
    }
    res = client.post('/exercises', json=payload)
    assert res.status_code == 409


def test_delete_exercise_success(client, sample_data):
    """DELETE /exercises/<id> deletes exercise."""
    ex_id = sample_data["exercise2_id"]
    res = client.delete(f'/exercises/{ex_id}')
    assert res.status_code == 200


def test_post_workout_exercise_nested_route(client, sample_data):
    """POST /workouts/<w_id>/exercises/<e_id>/workout_exercises adds exercise to workout."""
    w_id = sample_data["workout_id"]
    ex_id = sample_data["exercise2_id"]
    payload = {
        "sets": 4,
        "reps": 15,
        "duration_seconds": None
    }
    res = client.post(f'/workouts/{w_id}/exercises/{ex_id}/workout_exercises', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["workout_id"] == w_id
    assert data["exercise_id"] == ex_id
    assert data["sets"] == 4
    assert data["reps"] == 15


def test_post_workout_exercise_standard_route(client, sample_data):
    """POST /workout_exercises creates join record directly."""
    payload = {
        "workout_id": sample_data["workout_id"],
        "exercise_id": sample_data["exercise2_id"],
        "sets": 3,
        "reps": 12
    }
    res = client.post('/workout_exercises', json=payload)
    assert res.status_code == 201
    assert res.get_json()["sets"] == 3


def test_get_workout_exercises_list(client, sample_data):
    """GET /workout_exercises lists all associations."""
    res = client.get('/workout_exercises')
    assert res.status_code == 200
    assert len(res.get_json()) >= 1
