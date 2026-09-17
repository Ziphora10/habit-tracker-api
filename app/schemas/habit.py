from datetime import date

from pydantic import BaseModel, ConfigDict


class HabitCreate(BaseModel):
    name: str
    description: str | None = None


class HabitUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    owner_id: int


class HabitLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    completed_on: date


class StreakOut(BaseModel):
    habit_id: int
    current_streak: int
    longest_streak: int
    total_completions: int
