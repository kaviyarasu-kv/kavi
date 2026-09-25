# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + SQLite + Jinja2 web application that uses Google's Gemini API to generate personalized 7-day workout plans, nutrition/recovery tips, and feedback-based plan updates.

## Features

- User profile: name, user ID, age, weight, goal, intensity, experience
- Gemini-powered 7-day workout plan
- Gemini-powered nutrition/recovery tip
- Feedback loop that regenerates the complete plan
- SQLite persistence with SQLAlchemy
- HTML/Jinja2 frontend
- Admin/coach dashboard
- JSON API endpoints
- FastAPI Swagger docs at `/docs`
- Responsive mobile-friendly UI
- Environment-variable configuration
- Basic input validation and error handling

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── ai/
│       ├── __init__.py
│       ├── gemini_client.py
│       ├── gemini_generator.py
│       ├── gemini_flash_generator.py
│       └── updated_plan.py
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── error.html
├── static/
│   └── style.css
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 1. Install Python

Use Python 3.11 or newer.

Check:

```bash
python --version
```

## 2. Open the project in VS Code

Open the `FitBuddy` folder in VS Code.

## 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Windows:

```cmd
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
GEMINI_API_KEY=your_real_gemini_api_key
```

You can optionally set `ADMIN_TOKEN`.

## 6. Run

From the project root:

```bash
uvicorn app.main:app --reload
```

Open:

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin: http://127.0.0.1:8000/view-all-users

If `ADMIN_TOKEN` is set, open:

```text
http://127.0.0.1:8000/view-all-users?admin_token=YOUR_TOKEN
```

## 7. Test the normal UI

1. Open the home page.
2. Enter:
   - Name: Kavi
   - User ID: FB001
   - Age: 21
   - Weight: 65
   - Goal: muscle gain
   - Intensity: medium
   - Experience: beginner
3. Click **Generate My 7-Day Plan**.
4. Wait for Gemini to generate the plan.
5. Enter feedback such as:
   `Add more cardio and make Day 6 a recovery day.`
6. Click **Update Plan with AI**.
7. Open the Admin View to see the original and updated plans.

## 8. Test the JSON API

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Endpoint:

```text
POST /api/generate-workout
```

Example JSON:

```json
{
  "user_id": "FB001",
  "name": "Kavi",
  "age": 21,
  "weight": 65,
  "goal": "muscle gain",
  "intensity": "medium",
  "experience": "beginner"
}
```

Feedback endpoint:

```text
POST /api/submit-feedback
```

Example:

```json
{
  "user_id": "FB001",
  "feedback": "Add more cardio and make Day 6 a recovery day."
}
```

## 9. Database

SQLite database file:

```text
fitbuddy.db
```

It is created automatically on first server start.

Tables:

- `users`
- `plans`

The `plans` table stores the original plan and the updated plan separately.

## 10. Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure `.env` exists in the project root and contains:

```env
GEMINI_API_KEY=your_real_key
```

Restart Uvicorn after changing `.env`.

### Gemini model error

Change the model names in `.env` to models available to your Gemini API account:

```env
WORKOUT_MODEL=...
NUTRITION_MODEL=...
```

### Port already in use

Run:

```bash
uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

## Safety note

FitBuddy is a general wellness application. AI-generated fitness content can be incorrect or inappropriate for an individual. The app intentionally avoids medical diagnosis and treatment instructions. Users with injuries, medical conditions, pregnancy, or other special circumstances should consult an appropriately qualified professional before following a new exercise or nutrition program.
