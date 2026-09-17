from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.habit import Habit, HabitLog
from app.models.user import User
from app.schemas.habit import (
    HabitCreate,
    HabitLogOut,
    HabitOut,
    HabitUpdate,
    StreakOut,
)

router = APIRouter(prefix="/habits", tags=["habits"])


def _get_owned_habit(habit_id: int, db: Session, user: User) -> Habit:
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.owner_id == user.id)
        .first()
    )
    if habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )
    return habit


@router.post("", response_model=HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit_in: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habit = Habit(
        name=habit_in.name,
        description=habit_in.description,
        owner_id=current_user.id,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=list[HabitOut])
def list_habits(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Habit).filter(Habit.owner_id == current_user.id).all()


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_habit(habit_id, db, current_user)


@router.put("/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: int,
    habit_in: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habit = _get_owned_habit(habit_id, db, current_user)
    if habit_in.name is not None:
        habit.name = habit_in.name
    if habit_in.description is not None:
        habit.description = habit_in.description
    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habit = _get_owned_habit(habit_id, db, current_user)
    db.delete(habit)
    db.commit()
    return None


@router.post(
    "/{habit_id}/complete",
    response_model=HabitLogOut,
    status_code=status.HTTP_201_CREATED,
)
def mark_done_today(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habit = _get_owned_habit(habit_id, db, current_user)
    today = date.today()

    existing = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit.id, HabitLog.completed_on == today)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Habit already marked done today",
        )

    log = HabitLog(habit_id=habit.id, completed_on=today)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}/streak", response_model=StreakOut)
def get_streak(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habit = _get_owned_habit(habit_id, db, current_user)

    completed_dates = sorted(
        log.completed_on
        for log in db.query(HabitLog).filter(HabitLog.habit_id == habit.id).all()
    )

    current_streak, longest_streak = _calculate_streaks(completed_dates)

    return StreakOut(
        habit_id=habit.id,
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_completions=len(completed_dates),
    )


def _calculate_streaks(completed_dates: list[date]) -> tuple[int, int]:
    """Given a sorted list of unique-or-not dates, compute current and longest
    consecutive-day streaks. 'Current' only counts if it includes today or
    yesterday (otherwise the streak is considered broken)."""
    if not completed_dates:
        return 0, 0

    unique_dates = sorted(set(completed_dates))

    longest = 1
    run = 1
    for i in range(1, len(unique_dates)):
        if unique_dates[i] == unique_dates[i - 1] + timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)

    today = date.today()
    last_date = unique_dates[-1]

    if last_date not in (today, today - timedelta(days=1)):
        current = 0
    else:
        current = 1
        cursor = last_date
        date_set = set(unique_dates)
        while (cursor - timedelta(days=1)) in date_set:
            current += 1
            cursor -= timedelta(days=1)

    return current, longest
