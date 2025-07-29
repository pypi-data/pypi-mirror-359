"""Defines protocol for Simple math exercise interface."""

from wse_exercises.base.interfaces import ITask

from .task import (
    MathTaskConditions,
    MathTaskConfig,
    MathTextTaskAnswer,
    MathTextTaskQuestion,
)


class ISimpleMathExercise(
    ITask[
        MathTaskConfig,
        MathTaskConditions,
        MathTextTaskQuestion,
        MathTextTaskAnswer,
    ]
):
    """Protocol for Simple math exercise interface."""
