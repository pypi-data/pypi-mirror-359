"""Defines base task DTO components."""

from pydantic import BaseModel


class TaskConfig(BaseModel):
    """Base config."""


class TaskConditions(BaseModel):
    """Base conditions."""


class Question(BaseModel):
    """Base question."""


class Answer(BaseModel):
    """Base answer."""
