"""Base interface."""

from datetime import datetime
from typing import Any, Protocol, Type, TypeVar

from wse_exercises.core.mathem.enums import Exercises

from .componets import (
    Answer,
    Question,
    TaskConditions,
    TaskConfig,
)

TaskConfigT = TypeVar('TaskConfigT', bound=TaskConfig)
TaskConditionsT = TypeVar('TaskConditionsT', bound=TaskConditions)
QuestionT = TypeVar('QuestionT', bound=Question)
AnswerT = TypeVar('AnswerT', bound=Answer)

T = TypeVar('T', bound='ITask[Any, Any, Any, Any]')


class ITask(
    Protocol[
        TaskConfigT,
        TaskConditionsT,
        QuestionT,
        AnswerT,
    ],
):
    """The interface of the task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    created: datetime
    error_msg: str

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Instantiate the class from a dictionary of attributes."""

    @classmethod
    def from_json(cls: Type[T], data: str | bytes) -> T:
        """Instantiate the class from a JSON string or bytes."""

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary."""

    def to_json(self) -> str:
        """Serialize the instance to a JSON string."""
