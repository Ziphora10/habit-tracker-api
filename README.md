# Habit Tracker API

A backend REST API for tracking daily habits, built with **FastAPI**, **SQLAlchemy**, and **JWT authentication**. Users can sign up, log in, create habits, mark them done for the day, and see their current and longest streaks.

## Features

- JWT-based authentication (signup / login)
- CRUD endpoints for habits, scoped per user
- "Mark done today" endpoint with duplicate-completion protection
- Streak calculation (current streak + longest streak + total completions)
- SQLite by default (zero setup), swappable to Postgres via `DATABASE_URL`
- Pytest test suite (auth, CRUD, ownership, streak logic)
- Dockerfile + docker-compose for containerized runs
- GitHub Actions CI (lint + test on every push/PR)

## Tech Stack

Python · FastAPI · SQLAlchemy · Pydantic · python-jose (JWT) · passlib (bcrypt) · SQLite · Docker · GitHub Actions

## Project Structure

```
app/
  core/       # config, database session, security (JWT/hashing), auth dependency
  models/     # SQLAlchemy models: User, Habit, HabitLog
  schemas/    # Pydantic request/response schemas
  routers/    # auth.py, habits.py
  main.py     # FastAPI app entrypoint
tests/        # pytest suite
```

## Getting Started

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/Ziphora10/habit-tracker-api.git
cd habit-tracker-api
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables (optional)

```bash
cp .env.example .env
# edit SECRET_KEY etc. as needed
```

Defaults work out of the box with SQLite — no configuration required for local dev.

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

Visit the interactive API docs at **http://127.0.0.1:8000/docs**.

### 4. Run the tests

```bash
pytest -v
```

## Running with Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## API Overview

| Method | Endpoint                    | Description                        | Auth required |
|--------|------------------------------|-------------------------------------|----------------|
| POST   | `/auth/signup`               | Create a new user                   | No             |
| POST   | `/auth/login`                | Log in, get a JWT access token      | No             |
| POST   | `/habits`                    | Create a habit                      | Yes            |
| GET    | `/habits`                    | List your habits                    | Yes            |
| GET    | `/habits/{habit_id}`         | Get a single habit                  | Yes            |
| PUT    | `/habits/{habit_id}`         | Update a habit                      | Yes            |
| DELETE | `/habits/{habit_id}`         | Delete a habit                      | Yes            |
| POST   | `/habits/{habit_id}/complete`| Mark the habit done for today       | Yes            |
| GET    | `/habits/{habit_id}/streak`  | Get current/longest streak stats    | Yes            |

### Example: end-to-end flow

```bash
# Sign up
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "supersecret"}'

# Log in (note: OAuth2 form fields, not JSON)
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=you@example.com&password=supersecret"
# => {"access_token": "...", "token_type": "bearer"}

# Create a habit
curl -X POST http://127.0.0.1:8000/habits \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Read", "description": "Read 10 pages a day"}'

# Mark it done today
curl -X POST http://127.0.0.1:8000/habits/1/complete \
  -H "Authorization: Bearer <TOKEN>"

# Check your streak
curl http://127.0.0.1:8000/habits/1/streak \
  -H "Authorization: Bearer <TOKEN>"
```

## How streaks are calculated

A habit's **current streak** counts consecutive days up to and including today or yesterday (if you haven't marked today yet but did yesterday, the streak is still "alive"). Missing both today and yesterday resets the current streak to 0, while the **longest streak** ever achieved is preserved separately.

## Roadmap Ideas

- Postgres support via docker-compose profile
- Weekly/monthly habit frequencies (not just daily)
- Reminders/notifications
- Pagination on habit list

## License

MIT
