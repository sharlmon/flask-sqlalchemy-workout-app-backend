"""
Database Models for Workout Application Backend.

Defines SQLAlchemy entities:
- Exercise: reusable physical movement/exercise specifications
- Workout: training session records
- WorkoutExercise: association join entity tracking sets, reps, and duration
"""

from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Exercise(db.Model):
    """Exercise entity representing distinct fitness movements."""
    __tablename__ = 'exercises'

    __table_args__ = (
        CheckConstraint('length(name) >= 2', name='check_exercise_name_length'),
    )

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Attributes & Table Constraints
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan'
    )

    # Association proxy to access workouts directly through WorkoutExercise
    workouts = association_proxy('workout_exercises', 'workout')

    # Model Validations
    @validates('name')
    def validate_name(self, key, name):
        """Ensure exercise name is a non-empty string of at least 2 characters."""
        if not name or not isinstance(name, str) or len(name.strip()) < 2:
            raise ValueError("Exercise name must be a string with at least 2 characters.")
        return name.strip()

    @validates('category')
    def validate_category(self, key, category):
        """Ensure exercise category is valid and non-empty."""
        if not category or not isinstance(category, str) or len(category.strip()) < 2:
            raise ValueError("Exercise category must be a non-empty string.")
        return category.strip()

    def __repr__(self):
        return f"<Exercise id={self.id} name='{self.name}' category='{self.category}'>"


class Workout(db.Model):
    """Workout session entity logging training dates, duration, and notes."""
    __tablename__ = 'workouts'

    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_workout_duration_positive'),
    )

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Attributes & Table Constraints
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan'
    )

    # Association proxy to access exercises directly through WorkoutExercise
    exercises = association_proxy('workout_exercises', 'exercise')

    # Model Validations
    @validates('duration_minutes')
    def validate_duration_minutes(self, key, duration):
        """Ensure workout duration is a positive integer."""
        if duration is None:
            raise ValueError("Workout duration in minutes is required.")
        try:
            val = int(duration)
            if val <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("Workout duration must be a positive integer greater than 0.")
        return val

    @validates('date')
    def validate_date(self, key, date_val):
        """Ensure date is a valid date object or parseable ISO date string."""
        if date_val is None:
            raise ValueError("Workout date is required.")
        if isinstance(date_val, str):
            try:
                date_val = datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Workout date must be formatted as YYYY-MM-DD.")
        elif not isinstance(date_val, (date, datetime)):
            raise ValueError("Workout date must be a valid Date object or string.")
        if isinstance(date_val, datetime):
            date_val = date_val.date()
        return date_val

    def __repr__(self):
        return f"<Workout id={self.id} date='{self.date}' duration={self.duration_minutes}m>"


class WorkoutExercise(db.Model):
    """
    Join table linking Workouts and Exercises.
    Stores session-specific performance parameters (sets, reps, duration).
    """
    __tablename__ = 'workout_exercises'

    __table_args__ = (
        CheckConstraint('reps IS NULL OR reps >= 0', name='check_reps_non_negative'),
        CheckConstraint('sets IS NULL OR sets >= 0', name='check_sets_non_negative'),
        CheckConstraint('duration_seconds IS NULL OR duration_seconds >= 0', name='check_duration_seconds_non_negative'),
    )

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete='CASCADE'),
        nullable=False
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercises.id', ondelete='CASCADE'),
        nullable=False
    )

    # Exercise metrics
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model Validations
    @validates('sets')
    def validate_sets(self, key, sets_val):
        """Ensure sets is non-negative if provided."""
        if sets_val is not None:
            try:
                val = int(sets_val)
                if val < 0:
                    raise ValueError()
                return val
            except (ValueError, TypeError):
                raise ValueError("Sets must be a non-negative integer.")
        return sets_val

    @validates('reps')
    def validate_reps(self, key, reps_val):
        """Ensure reps is non-negative if provided."""
        if reps_val is not None:
            try:
                val = int(reps_val)
                if val < 0:
                    raise ValueError()
                return val
            except (ValueError, TypeError):
                raise ValueError("Reps must be a non-negative integer.")
        return reps_val

    @validates('duration_seconds')
    def validate_duration_seconds(self, key, duration_val):
        """Ensure duration_seconds is non-negative if provided."""
        if duration_val is not None:
            try:
                val = int(duration_val)
                if val < 0:
                    raise ValueError()
                return val
            except (ValueError, TypeError):
                raise ValueError("Duration in seconds must be a non-negative integer.")
        return duration_val

    def __repr__(self):
        return f"<WorkoutExercise id={self.id} workout_id={self.workout_id} exercise_id={self.exercise_id}>"
