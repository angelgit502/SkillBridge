# 🌉 SkillBridge

SkillBridge is a peer-to-peer skill exchange web application designed for CHRIST University students, built with Python, Streamlit, and SQLite. Every student is both a learner and a provider. An administrator monitors campus activity through a real-time analytics dashboard and handles content moderation.

## Project Structure

```
skillbridge/
├── .streamlit/
│   └── config.toml         # Light theme, teal accent (#1F6F78), minimal toolbar
├── app.py                  # Entry point: auth, CSS injection & role-based navigation
├── config.py               # Relative DB_PATH = "skillbridge.db" and DEPARTMENTS
├── check_tables.py         # Verification script for database tables
├── requirements.txt        # streamlit>=1.50, pandas, plotly, pytest
├── .gitignore              # Ignores skillbridge.db and .venv
├── README.md               # Documentation and setup instructions
├── db/
│   ├── database.py         # get_connection (foreign keys ON, Row factory, auto-seed)
│   ├── init_db.py          # Schema initialization from schema.sql
│   ├── schema.sql          # 8 tables, constraints, foreign keys, and indexes
│   ├── security.py         # Salted PBKDF2-SHA256 password hashing (200k iterations)
│   └── seed.py             # Demo and test seed data
├── services/               # Pure business logic (NO Streamlit code)
│   ├── __init__.py
│   ├── admin.py            # Moderation queue and student account status
│   ├── analytics.py        # Dashboard metrics and aggregations
│   ├── auth.py             # Registration, login, and user queries
│   ├── feedback.py         # 1-5 star ratings and student reports
│   ├── profile.py          # Profile updates, teach/learn skills, hidden toggle
│   ├── requests.py         # Request lifecycle, status transitions, duplicate checks
│   ├── sessions.py         # Slot publishing, atomic booking, session lifecycle
│   └── skills.py           # Skill search and category/department filtering
├── views/                  # Streamlit screens (NO SQL queries)
│   ├── __init__.py
│   ├── admin_dashboard.py  # KPI metrics, Plotly charts, moderation & student management
│   ├── discover.py         # Two-column listing grid with expandable request forms
│   ├── feedback.py         # Post-session review submission & ratings history
│   ├── my_requests.py      # Incoming & Sent requests with contextual action buttons
│   ├── profile.py          # Profile editor and teaching/learning skill manager
│   └── sessions.py         # Live countdown card, slot publisher & booking interface
├── ui/                     # Presentation styling only (NO business logic or SQL)
│   ├── __init__.py
│   ├── navigation.py       # Shared role-based Streamlit page registry
│   └── theme.py            # CSS variables, status badges, Plotly themes, live countdown
└── tests/
    ├── __init__.py
    ├── conftest.py         # Isolated temporary SQLite database per test
    ├── test_core.py        # Security and request lifecycle tests
    └── test_workflows.py   # Student/admin persistence and workflow tests
```

## Setup & Running

1. **Install Python 3.10+ and dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```powershell
   python -m db.init_db
   ```
   The app creates the database automatically when needed and loads the demo dataset when the login screen is opened on an empty database. Existing databases are not overwritten. To load sample data manually into an empty database, run `python -m db.seed`.

3. **Run the automated test suite:**
   ```powershell
   python -m pytest -v
   ```

4. **Launch the application:**
   ```powershell
   python -m streamlit run app.py
   ```

## Optional Demo Credentials

The following accounts are created automatically when the login screen opens on an empty database. The sample dataset can also be loaded manually with `python -m db.seed`.

### Administrator
| Role | Email | Password |
|---|---|---|
| Administrator | `admin@christuniversity.in` | `Admin@1234` |

### Students
All demo student accounts use password: `Demo@1234`

| Name | Email | Department | Teaches / Learns |
|---|---|---|---|
| Asha Menon | `asha.menon@christuniversity.in` | Computer Science | Teaches Python / Learns Figma |
| Rahul Verma | `rahul.verma@christuniversity.in` | Commerce | Teaches Excel / Learns Python |
| Meera Thomas | `meera.thomas@christuniversity.in` | Design | Teaches Graphic Design, Figma / Learns Public Speaking |
| Arjun Nair | `arjun.nair@christuniversity.in` | Computer Science | Teaches Public Speaking / Learns Python |
| Priya Kapoor | `priya.kapoor@christuniversity.in` | Psychology | Teaches Guitar / Learns Graphic Design |

## Key Features & Page Layouts

### 1. Authentication (Login & Registration)
- Centered narrow layout (`st.columns([1, 2, 1])`).
- University email validation (`*@christuniversity.in`).
- Passwords must be at least 8 characters and match confirmation; stored exclusively as salted PBKDF2-SHA256 hashes.
- Inactive accounts are blocked with a clear notice.

### 2. Discover (Students)
- Filters at top: skill search, department, and category in `st.columns([3, 2, 2])`.
- Two-column responsive card grid (`st.container(border=True)`).
- Students never see their own listings.
- Expandable form to send learning requests with custom message.
- Option to flag inappropriate content via report expander.

### 3. My Requests (Students)
- Two tabs: **Incoming** (requests for skills you teach) and **Sent** (requests you submitted).
- Status badges with unified colors:
  - `Pending`: Amber `#FEF3C7` / `#92400E`
  - `Accepted`: Blue `#DBEAFE` / `#1E40AF`
  - `Awaiting Learner Confirmation`: Amber `#FEF3C7` / `#92400E`
  - `Completed`: Green `#DCFCE7` / `#166534`
  - `Rejected`: Red `#FEE2E2` / `#991B1B`
  - `Cancelled`: Gray `#F3F4F6` / `#374151`
- Action buttons dynamically adapt to role and status:
  - Provider: Accept, Reject, Cancel (pending).
  - Learner: Cancel (pending).
  - Provider: Mark completed, Cancel (accepted); marking completed requests learner confirmation.
  - Learner: Cancel (accepted), then Confirm Completion or Report Issue while awaiting confirmation.

### 4. Sessions & Live Countdown (Students)
- **Next Session Card** at top with `.sb-next` accent border and live countdown ticking every second in `Asia/Kolkata` time (`st.fragment(run_every=1)`).
- **Publish Time Slots**: Providers publish `YYYY-MM-DD HH:MM` time windows (`end_time > start_time`).
- **Book Slots**: Learners select an accepted request and book an available slot in a single atomic database transaction.
- Status updates: Providers request completion; learners confirm it. Either party can cancel accepted sessions.

### 5. Feedback & Ratings (Learners & Providers)
- Confirmed completed sessions unlock 1–5 star reviews with written comments (1 review per session).
- Only learners who attended the session can submit feedback.
- History tabs: view feedback given and feedback received.

### 6. Profile Management (Students)
- Edit personal name, department, and bio.
- Manage skills to teach (with `is_hidden` toggle to pause listings without deleting).
- Manage skills to learn.
- Option to add new skills directly into the campus catalog.

### 7. Admin Dashboard (Administrator)
- Filter by department applies across all metrics and charts.
- 4 KPI cards: Total Students, Total Requests, Pending, and Accepted/Completed.
- Horizontal bar chart of Top 10 most requested skills (accent `#1F6F78`).
- Donut chart of requests by status.
- Department participation chart and provider ratings table.
- **Moderation Queue**: Resolve reports and optionally deactivate abusive accounts.
- **Student Management**: View all campus accounts and toggle active status.
- Live polling: metrics and charts update every 15 seconds (`st.fragment(run_every=15)`).

## Database Summary

SQLite database (`skillbridge.db`) with `PRAGMA foreign_keys = ON;` and WAL mode:
- `users`: id, name, email (unique, NOCASE), password_hash, department, bio, role, is_active, created_at.
- `skills`: id, name (unique, NOCASE), category.
- `user_skills`: user_id, skill_id, kind (`teach`/`learn`), is_hidden. PRIMARY KEY `(user_id, skill_id, kind)`.
- `requests`: id, learner_id, provider_id, skill_id, message, status, created_at, updated_at. CHECK `learner_id <> provider_id`.
- `slots`: id, provider_id, start_time, end_time (text `YYYY-MM-DD HH:MM`). CHECK `end_time > start_time`.
- `sessions`: id, request_id (unique), slot_id (unique), status (`scheduled`/`completed`/`cancelled`).
- `feedback`: id, session_id (unique), rating (1–5), comment, created_at.
- `reports`: id, reporter_id, target_type (`user`/`skill_listing`), target_user_id, target_skill_id, reason, status (`open`/`resolved`).
- Indexes on: department, `(skill_id, kind)`, category, `(provider_id, status)`, `(learner_id, status)`, `(provider_id, start_time)`, and report status.
