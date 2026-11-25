-- Settings applied to every connection
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Users: both students and the admin
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash   TEXT    NOT NULL,
    department      TEXT    NOT NULL,
    bio             TEXT    NOT NULL DEFAULT '',
    role            TEXT    NOT NULL DEFAULT 'student'
                    CHECK (role IN ('student', 'admin')),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 2. Skills: master list, so "Python" and "python" are one row
CREATE TABLE IF NOT EXISTS skills (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    category    TEXT NOT NULL
);

-- 3. User_skills: links users to skills, as "teach" or "learn".
--    This table is also the skill listing that students browse.
CREATE TABLE IF NOT EXISTS user_skills (
    user_id     INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    skill_id    INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    kind        TEXT    NOT NULL CHECK (kind IN ('teach', 'learn')),
    is_hidden   INTEGER NOT NULL DEFAULT 0 CHECK (is_hidden IN (0, 1)),
    PRIMARY KEY (user_id, skill_id, kind)
);

-- 4. Requests: a learner asks a provider to teach a skill
CREATE TABLE IF NOT EXISTS requests (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id  INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    skill_id    INTEGER NOT NULL REFERENCES skills(id),
    message     TEXT    NOT NULL DEFAULT '',
    status      TEXT    NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','accepted','awaiting_confirmation','rejected','completed','cancelled')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (learner_id <> provider_id)          -- nobody requests their own skill
);

-- 5. Slots: time windows a provider offers
--    Times use 'YYYY-MM-DD HH:MM' so text comparison sorts correctly.
CREATE TABLE IF NOT EXISTS slots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_time  TEXT    NOT NULL,
    end_time    TEXT    NOT NULL,
    CHECK (end_time > start_time)
);

-- 6. Sessions: created when a learner books a slot for an accepted request
--    UNIQUE on slot_id means a slot can be booked only once.
--    UNIQUE on request_id means one session per request.
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id  INTEGER NOT NULL UNIQUE REFERENCES requests(id) ON DELETE CASCADE,
    slot_id     INTEGER NOT NULL UNIQUE REFERENCES slots(id)    ON DELETE CASCADE,
    status      TEXT    NOT NULL DEFAULT 'scheduled'
                CHECK (status IN ('scheduled','completed','cancelled')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 7. Feedback: one rating per completed session
CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 8. Reports: any user can flag a user or a skill listing
CREATE TABLE IF NOT EXISTS reports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_type  TEXT    NOT NULL CHECK (target_type IN ('user', 'skill_listing')),
    target_user_id  INTEGER REFERENCES users(id)  ON DELETE CASCADE,
    target_skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    request_id   INTEGER REFERENCES requests(id) ON DELETE CASCADE,
    reason       TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved')),
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Indexes for the queries the app runs most often
CREATE INDEX IF NOT EXISTS idx_users_department      ON users(department);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill     ON user_skills(skill_id, kind);
CREATE INDEX IF NOT EXISTS idx_skills_category       ON skills(category);
CREATE INDEX IF NOT EXISTS idx_requests_provider     ON requests(provider_id, status);
CREATE INDEX IF NOT EXISTS idx_requests_learner      ON requests(learner_id, status);
CREATE INDEX IF NOT EXISTS idx_slots_provider        ON slots(provider_id, start_time);
CREATE INDEX IF NOT EXISTS idx_reports_status        ON reports(status);