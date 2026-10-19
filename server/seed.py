#!/usr/bin/env python3
"""
Seed script for Workout Application Backend.

Populates the database with realistic sample exercises, workouts,
and workout-exercise association records to demonstrate relationships.
"""

import os
import sys
from datetime import date, timedelta

# Ensure server directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app
from models import db, Exercise, Workout, WorkoutExercise


def seed_database():
    """Clear existing records and populate with comprehensive initial data."""
    with app.app_context():
        print("[*] Clearing existing database tables...")
        # Delete join table records first, then parents
        WorkoutExercise.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        db.session.commit()

        print("[*] Seeding Exercises...")
        exercises_data = [
            {
                "name": "Barbell Bench Press",
                "category": "Strength",
                "equipment_needed": True
            },
            {
                "name": "Barbell Back Squat",
                "category": "Strength",
                "equipment_needed": True
            },
            {
                "name": "Conventional Deadlift",
                "category": "Strength",
                "equipment_needed": True
            },
            {
                "name": "Pull-Ups",
                "category": "Bodyweight",
                "equipment_needed": True
            },
            {
                "name": "Push-Ups",
                "category": "Bodyweight",
                "equipment_needed": False
            },
            {
                "name": "Dumbbell Overhead Shoulder Press",
                "category": "Strength",
                "equipment_needed": True
            },
            {
                "name": "Treadmill Interval Sprint",
                "category": "Cardio",
                "equipment_needed": True
            },
            {
                "name": "Jump Rope",
                "category": "Cardio",
                "equipment_needed": True
            },
            {
                "name": "Standard Forearm Plank",
                "category": "Core",
                "equipment_needed": False
            },
            {
                "name": "Hanging Leg Raises",
                "category": "Core",
                "equipment_needed": True
            }
        ]

        exercise_objs = []
        for ex in exercises_data:
            exercise_objs.append(Exercise(**ex))

        db.session.add_all(exercise_objs)
        db.session.commit()
        print(f"[+] Added {len(exercise_objs)} exercises.")

        print("[*] Seeding Workouts...")
        today = date.today()
        workouts_data = [
            {
                "date": today - timedelta(days=6),
                "duration_minutes": 60,
                "notes": "Upper Body Heavy Strength session focusing on chest, triceps, and shoulders."
            },
            {
                "date": today - timedelta(days=4),
                "duration_minutes": 75,
                "notes": "Lower Body Leg Day. Squats felt strong, finished with core work."
            },
            {
                "date": today - timedelta(days=2),
                "duration_minutes": 45,
                "notes": "HIIT Conditioning and Cardio Endurance."
            },
            {
                "date": today,
                "duration_minutes": 55,
                "notes": "Full Body Functional Hypertrophy and Core."
            }
        ]

        workout_objs = []
        for w in workouts_data:
            workout_objs.append(Workout(**w))

        db.session.add_all(workout_objs)
        db.session.commit()
        print(f"[+] Added {len(workout_objs)} workouts.")

        print("[*] Seeding WorkoutExercises (Join relationships)...")
        # Lookup helper
        ex_map = {ex.name: ex for ex in exercise_objs}

        associations = [
            # Workout 1: Upper Body
            WorkoutExercise(
                workout=workout_objs[0],
                exercise=ex_map["Barbell Bench Press"],
                sets=4,
                reps=8,
                duration_seconds=None
            ),
            WorkoutExercise(
                workout=workout_objs[0],
                exercise=ex_map["Dumbbell Overhead Shoulder Press"],
                sets=3,
                reps=10,
                duration_seconds=None
            ),
            WorkoutExercise(
                workout=workout_objs[0],
                exercise=ex_map["Push-Ups"],
                sets=3,
                reps=20,
                duration_seconds=None
            ),

            # Workout 2: Lower Body & Core
            WorkoutExercise(
                workout=workout_objs[1],
                exercise=ex_map["Barbell Back Squat"],
                sets=5,
                reps=5,
                duration_seconds=None
            ),
            WorkoutExercise(
                workout=workout_objs[1],
                exercise=ex_map["Conventional Deadlift"],
                sets=4,
                reps=6,
                duration_seconds=None
            ),
            WorkoutExercise(
                workout=workout_objs[1],
                exercise=ex_map["Standard Forearm Plank"],
                sets=3,
                reps=None,
                duration_seconds=90
            ),

            # Workout 3: Cardio & Conditioning
            WorkoutExercise(
                workout=workout_objs[2],
                exercise=ex_map["Treadmill Interval Sprint"],
                sets=6,
                reps=None,
                duration_seconds=120
            ),
            WorkoutExercise(
                workout=workout_objs[2],
                exercise=ex_map["Jump Rope"],
                sets=4,
                reps=100,
                duration_seconds=60
            ),
            WorkoutExercise(
                workout=workout_objs[2],
                exercise=ex_map["Hanging Leg Raises"],
                sets=3,
                reps=15,
                duration_seconds=None
            ),

            # Workout 4: Full Body
            WorkoutExercise(
                workout=workout_objs[3],
                exercise=ex_map["Pull-Ups"],
                sets=4,
                reps=10,
                duration_seconds=None
            ),
            WorkoutExercise(
                workout=workout_objs[3],
                exercise=ex_map["Barbell Back Squat"],
                sets=3,
                reps=12,
                duration_seconds=None
            ),
            WorkoutExercise(
                workout=workout_objs[3],
                exercise=ex_map["Standard Forearm Plank"],
                sets=3,
                reps=None,
                duration_seconds=60
            )
        ]

        db.session.add_all(associations)
        db.session.commit()
        print(f"[+] Added {len(associations)} workout-exercise association links.")
        print("[✓] Database seeding completed successfully!")


if __name__ == '__main__':
    seed_database()
