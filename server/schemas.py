"""
Marshmallow Schemas for Workout Application.

Handles serialization and deserialization of models, nested relational representations,
and schema-level input validations.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class ExerciseSchema(Schema):
    """Schema for Exercise entity serialization and validation."""
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=100, error="Exercise name must be between 2 and 100 characters.")
        ]
    )
    category = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=50, error="Category must be between 2 and 50 characters.")
        ]
    )
    equipment_needed = fields.Bool(load_default=False)

    @validates('name')
    def validate_name_not_blank(self, value, **kwargs):
        """Ensure name is not only whitespace."""
        if not value or not value.strip():
            raise ValidationError("Exercise name cannot be empty or blank.")


class WorkoutExerciseDetailSchema(Schema):
    """Nested schema representing a WorkoutExercise within a Workout response."""
    id = fields.Int(dump_only=True)
    exercise_id = fields.Int()
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)


class WorkoutSchema(Schema):
    """Schema for Workout session serialization and input validation."""
    id = fields.Int(dump_only=True)
    date = fields.Date(
        required=True,
        format="%Y-%m-%d",
        error_messages={"invalid": "Not a valid date format. Please use YYYY-MM-DD."}
    )
    duration_minutes = fields.Int(
        required=True,
        validate=[
            validate.Range(min=1, max=1440, error="Duration must be between 1 and 1440 minutes (24 hours).")
        ]
    )
    notes = fields.Str(allow_none=True)
    workout_exercises = fields.Nested(WorkoutExerciseDetailSchema, many=True, dump_only=True)


class ExerciseWithWorkoutsSchema(ExerciseSchema):
    """Schema for Exercise that includes associated workouts through WorkoutExercises."""
    workout_exercises = fields.Nested(
        Schema.from_dict({
            "id": fields.Int(),
            "workout_id": fields.Int(),
            "reps": fields.Int(allow_none=True),
            "sets": fields.Int(allow_none=True),
            "duration_seconds": fields.Int(allow_none=True),
            "workout": fields.Nested(WorkoutSchema, exclude=('workout_exercises',))
        }),
        many=True,
        dump_only=True
    )


class WorkoutExerciseSchema(Schema):
    """Schema for creating and viewing WorkoutExercise join records."""
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(
        allow_none=True,
        validate=[
            validate.Range(min=0, max=1000, error="Reps must be a non-negative number between 0 and 1000.")
        ]
    )
    sets = fields.Int(
        allow_none=True,
        validate=[
            validate.Range(min=0, max=100, error="Sets must be a non-negative number between 0 and 100.")
        ]
    )
    duration_seconds = fields.Int(
        allow_none=True,
        validate=[
            validate.Range(min=0, max=86400, error="Duration in seconds must be between 0 and 86400.")
        ]
    )
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSchema, exclude=('workout_exercises',), dump_only=True)

    @validates('workout_id')
    def validate_workout_id(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Workout ID must be a positive integer.")

    @validates('exercise_id')
    def validate_exercise_id(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Exercise ID must be a positive integer.")


# Instantiated schema instances for reusable imports
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_with_workouts_schema = ExerciseWithWorkoutsSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
