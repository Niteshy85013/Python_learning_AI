# ITS - Python Tutor (Flask + PostgreSQL)

## Overview
Simple ITS web application to support learning Python. Backend uses Flask + RestrictedPython to safely evaluate learner code. PostgreSQL stores users, exercises, and submissions.

## Requirements
- Python 3.10+ (3.11 recommended)
- PostgreSQL server
- (Optional but recommended) virtualenv or venv
- For production: Docker recommended for sandboxing code execution

## Install & Setup (local / dev)

1. Clone repository (or copy files into a folder):
   $ git clone <repo> its-python-tutor
   $ cd its-python-tutor

2. Create and activate a virtual environment:
   $ python -m venv venv
   $ source venv/bin/activate   # Linux/Mac
   $ venv\Scripts\activate      # Windows

3. Install dependencies:
   $ pip install --upgrade pip
   $ pip install -r requirements.txt

4. Set up PostgreSQL:
   - Create a database and a user, for example:
     $ psql -U postgres
     postgres=# CREATE DATABASE itsdb;
     postgres=# CREATE USER itsuser WITH PASSWORD 'yourpassword';
     postgres=# GRANT ALL PRIVILEGES ON DATABASE itsdb TO itsuser;

   - Update DATABASE_URL in environment or in config.py:
     export DATABASE_URL=postgresql://itsuser:yourpassword@localhost:5432/itsdb
     (On Windows PowerShell use: $env:DATABASE_URL="postgresql://...")

5. Set secret key (recommended):
   export ITS_SECRET_KEY='change-this-to-a-secret'

6. Seed the database with sample exercises and an admin:
   $ python data_seed.py

7. Run the app:
   $ python app.py
   - Open http://127.0.0.1:5000 in your browser.

## Accounts
- Admin sample (if seeded): username: admin, password: admin123

## How the evaluator works (development)
- Submitted code is executed under RestrictedPython in `evaluator.py`.
- The system captures printed output and compares it to the exercise's `expected_output` (simple mechanism for the demo).
- For more complex automated checks, you should store unit tests or implement test harness (recommended future work).

## Security & Production Notes (READ CAREFULLY)
- RestrictedPython reduces risk but can be bypassed in complex ways. **Do not** deploy this on an open production server without additional hardening.
- Recommended production approach:
  - Execute each submission inside a fresh Docker container with strict CPU/memory limits and a maximum timeout.
  - Use UID/GID mapping and AppArmor/SELinux profiles.
  - Sanitize outputs and limit file I/O and network access.
  - Monitor & log suspicious activity and rate-limit submissions.

## Future enhancements
- Replace RestrictedPython with Docker-based sandbox for robust isolation.
- Add unit-test-based exercise evaluation.
- Add code style hints, step-by-step hinting, and adaptive difficulty.
- Add analytics dashboard for teachers.

## Troubleshooting
- If DB errors occur, verify DATABASE_URL and that Postgres is running.
- To inspect DB quickly: use `psql` or pgAdmin and check `users`, `exercises`, `submissions`.

