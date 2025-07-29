"""Defines base class for task."""

from datetime import datetime
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel, Field

# TODO: Fix import
from wse_exercises.core.mathem.enums import Exercises

T = TypeVar('T', bound='Task[Any, Any, Any, Any]')

AnswerT = TypeVar('AnswerT')
QuestionT = TypeVar('QuestionT')
TaskConfigT = TypeVar('TaskConfigT')
TaskConditionsT = TypeVar('TaskConditionsT')


class Task(
    BaseModel,
    Generic[TaskConfigT, TaskConditionsT, QuestionT, AnswerT],
):
    """Base class for DTO exercise task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    created: datetime = Field(default_factory=datetime.now)
    error_msg: str = Field(default='', frozen=True)

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Instantiate the class from a dictionary of attributes."""
        return cls.parse_obj(data)

    @classmethod
    def from_json(cls: Type[T], data: str | bytes) -> T:
        """Instantiate the class from a JSON string or bytes."""
        return cls.parse_raw(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary."""

        def convert_datetime(data: dict[str, Any]) -> dict[str, Any]:
            dict_data: dict[str, Any] = {}

            for key, value in data.items():
                if isinstance(value, datetime):
                    dict_data[key] = value.isoformat()
                elif isinstance(value, dict):
                    dict_data[key] = convert_datetime(value)
                else:
                    dict_data[key] = value

            return dict_data

        return convert_datetime(self.dict())

    def to_json(self) -> str:
        """Serialize the instance to a JSON string."""
        return self.json()
