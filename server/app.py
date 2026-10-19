"""
Flask REST API for Workout Application Backend.

Provides endpoints for managing Workouts, Exercises, and WorkoutExercises
with Marshmallow serialization/deserialization and error handling.
"""

import os
import sys
from datetime import date
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError

# Ensure server module path resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema,
    exercises_schema,
    exercise_with_workouts_schema,
    workout_schema,
    workouts_schema,
    workout_exercise_schema,
    workout_exercises_schema
)


def create_app(database_uri=None):
    """Application factory for Flask app."""
    app = Flask(__name__)

    # Default to sqlite database in server directory
    if database_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    else:
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False

    db.init_app(app)
    Migrate(app, db)

    # -------------------------------------------------------------
    # Welcome / Documentation Route
    # -------------------------------------------------------------
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "message": "Welcome to the Workout Application Backend API",
            "version": "1.0.0",
            "endpoints": {
                "GET /workouts": "List all logged workouts",
                "GET /workouts/<id>": "Show a workout and its associated exercises (with reps/sets/duration)",
                "POST /workouts": "Create a new workout",
                "DELETE /workouts/<id>": "Delete a workout and cascade remove associated workout exercises",
                "GET /exercises": "List all reusable exercises",
                "GET /exercises/<id>": "Show an exercise and associated workouts",
                "POST /exercises": "Create a new exercise",
                "DELETE /exercises/<id>": "Delete an exercise and cascade remove associated workout exercises",
                "POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises": "Add an exercise to a workout with performance metrics",
                "POST /workout_exercises": "Add workout exercise join record directly",
                "GET /workout_exercises": "List all workout exercise records"
            }
        }), 200

    # -------------------------------------------------------------
    # Workouts Endpoints
    # -------------------------------------------------------------
    @app.route('/workouts', methods=['GET'])
    def get_workouts():
        """List all workouts."""
        workouts = Workout.query.order_by(Workout.date.desc()).all()
        return jsonify(workouts_schema.dump(workouts)), 200

    @app.route('/workouts/<int:id>', methods=['GET'])
    def get_workout_by_id(id):
        """Show a single workout with its associated exercises (including reps/sets/duration)."""
        workout = db.session.get(Workout, id)
        if not workout:
            return jsonify({
                "error": "Not Found",
                "message": f"Workout with ID {id} does not exist."
            }), 404
        return jsonify(workout_schema.dump(workout)), 200

    @app.route('/workouts', methods=['POST'])
    def create_workout():
        """Create a new workout."""
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Bad Request",
                "message": "Request body must contain valid JSON."
            }), 400

        # Schema deserialization and validation
        try:
            validated_data = workout_schema.load(data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation Error",
                "messages": err.messages
            }), 400

        # Model creation & persistence
        try:
            new_workout = Workout(
                date=validated_data.get('date', date.today()),
                duration_minutes=validated_data['duration_minutes'],
                notes=validated_data.get('notes')
            )
            db.session.add(new_workout)
            db.session.commit()
            return jsonify(workout_schema.dump(new_workout)), 201
        except ValueError as val_err:
            db.session.rollback()
            return jsonify({"error": "Bad Request", "message": str(val_err)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server Error", "message": str(e)}), 500

    @app.route('/workouts/<int:id>', methods=['DELETE'])
    def delete_workout(id):
        """Delete a workout and cascade remove associated WorkoutExercises."""
        workout = db.session.get(Workout, id)
        if not workout:
            return jsonify({
                "error": "Not Found",
                "message": f"Workout with ID {id} does not exist."
            }), 404

        try:
            db.session.delete(workout)
            db.session.commit()
            return jsonify({
                "message": f"Workout with ID {id} and its associated exercises were successfully deleted."
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server Error", "message": str(e)}), 500

    # -------------------------------------------------------------
    # Exercises Endpoints
    # -------------------------------------------------------------
    @app.route('/exercises', methods=['GET'])
    def get_exercises():
        """List all exercises."""
        exercises = Exercise.query.order_by(Exercise.name.asc()).all()
        return jsonify(exercises_schema.dump(exercises)), 200

    @app.route('/exercises/<int:id>', methods=['GET'])
    def get_exercise_by_id(id):
        """Show an exercise and its associated workouts."""
        exercise = db.session.get(Exercise, id)
        if not exercise:
            return jsonify({
                "error": "Not Found",
                "message": f"Exercise with ID {id} does not exist."
            }), 404
        return jsonify(exercise_with_workouts_schema.dump(exercise)), 200

    @app.route('/exercises', methods=['POST'])
    def create_exercise():
        """Create a new exercise."""
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Bad Request",
                "message": "Request body must contain valid JSON."
            }), 400

        # Schema deserialization and validation
        try:
            validated_data = exercise_schema.load(data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation Error",
                "messages": err.messages
            }), 400

        # Check uniqueness constraint
        existing = Exercise.query.filter_by(name=validated_data['name']).first()
        if existing:
            return jsonify({
                "error": "Conflict",
                "message": f"An exercise with name '{validated_data['name']}' already exists."
            }), 409

        # Model creation & persistence
        try:
            new_exercise = Exercise(
                name=validated_data['name'],
                category=validated_data['category'],
                equipment_needed=validated_data.get('equipment_needed', False)
            )
            db.session.add(new_exercise)
            db.session.commit()
            return jsonify(exercise_schema.dump(new_exercise)), 201
        except ValueError as val_err:
            db.session.rollback()
            return jsonify({"error": "Bad Request", "message": str(val_err)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server Error", "message": str(e)}), 500

    @app.route('/exercises/<int:id>', methods=['DELETE'])
    def delete_exercise(id):
        """Delete an exercise and cascade remove associated WorkoutExercises."""
        exercise = db.session.get(Exercise, id)
        if not exercise:
            return jsonify({
                "error": "Not Found",
                "message": f"Exercise with ID {id} does not exist."
            }), 404

        try:
            db.session.delete(exercise)
            db.session.commit()
            return jsonify({
                "message": f"Exercise with ID {id} and its associated workout associations were successfully deleted."
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server Error", "message": str(e)}), 500

    # -------------------------------------------------------------
    # WorkoutExercise Join Endpoints
    # -------------------------------------------------------------
    @app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
    def add_exercise_to_workout(workout_id, exercise_id):
        """
        Add an exercise to a workout with performance metrics (sets, reps, duration_seconds).
        Matches the path explicitly requested in the lab spec.
        """
        workout = db.session.get(Workout, workout_id)
        if not workout:
            return jsonify({
                "error": "Not Found",
                "message": f"Workout with ID {workout_id} does not exist."
            }), 404

        exercise = db.session.get(Exercise, exercise_id)
        if not exercise:
            return jsonify({
                "error": "Not Found",
                "message": f"Exercise with ID {exercise_id} does not exist."
            }), 404

        data = request.get_json() or {}
        payload = {
            "workout_id": workout_id,
            "exercise_id": exercise_id,
            "reps": data.get("reps"),
            "sets": data.get("sets"),
            "duration_seconds": data.get("duration_seconds")
        }

        try:
            validated_data = workout_exercise_schema.load(payload)
        except ValidationError as err:
            return jsonify({
                "error": "Validation Error",
                "messages": err.messages
            }), 400

        try:
            we = WorkoutExercise(
                workout_id=workout_id,
                exercise_id=exercise_id,
                reps=validated_data.get("reps"),
                sets=validated_data.get("sets"),
                duration_seconds=validated_data.get("duration_seconds")
            )
            db.session.add(we)
            db.session.commit()
            return jsonify(workout_exercise_schema.dump(we)), 201
        except ValueError as val_err:
            db.session.rollback()
            return jsonify({"error": "Bad Request", "message": str(val_err)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server Error", "message": str(e)}), 500

    @app.route('/workout_exercises', methods=['POST'])
    def create_workout_exercise():
        """Standard REST endpoint to create a WorkoutExercise join record."""
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Bad Request",
                "message": "Request body must contain valid JSON."
            }), 400

        try:
            validated_data = workout_exercise_schema.load(data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation Error",
                "messages": err.messages
            }), 400

        workout = db.session.get(Workout, validated_data['workout_id'])
        if not workout:
            return jsonify({
                "error": "Not Found",
                "message": f"Workout with ID {validated_data['workout_id']} does not exist."
            }), 404

        exercise = db.session.get(Exercise, validated_data['exercise_id'])
        if not exercise:
            return jsonify({
                "error": "Not Found",
                "message": f"Exercise with ID {validated_data['exercise_id']} does not exist."
            }), 404

        try:
            we = WorkoutExercise(
                workout_id=validated_data['workout_id'],
                exercise_id=validated_data['exercise_id'],
                reps=validated_data.get('reps'),
                sets=validated_data.get('sets'),
                duration_seconds=validated_data.get('duration_seconds')
            )
            db.session.add(we)
            db.session.commit()
            return jsonify(workout_exercise_schema.dump(we)), 201
        except ValueError as val_err:
            db.session.rollback()
            return jsonify({"error": "Bad Request", "message": str(val_err)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server Error", "message": str(e)}), 500

    @app.route('/workout_exercises', methods=['GET'])
    def get_workout_exercises():
        """List all workout exercises."""
        items = WorkoutExercise.query.all()
        return jsonify(workout_exercises_schema.dump(items)), 200

    # -------------------------------------------------------------
    # Error Handlers
    # -------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": "The requested resource was not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method Not Allowed", "message": "The HTTP method is not allowed on this endpoint."}), 405

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)
