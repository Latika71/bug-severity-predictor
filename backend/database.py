"""
database.py — SQLite Database Connection + Queries
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, '..', 'database', 'bugs.db')


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT DEFAULT 'customer',
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            username   TEXT,
            role       TEXT,
            login_time TEXT,
            ip_address TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id               INTEGER,
            bug_type              TEXT,
            component             TEXT,
            environment           TEXT,
            platform              TEXT,
            operating_system      TEXT,
            browser               TEXT,
            reporter_role         TEXT,
            module                TEXT,
            status                TEXT,
            affected_users        INTEGER,
            response_time_ms      INTEGER,
            business_impact_score REAL,
            reproduction_rate     REAL,
            memory_usage_mb       REAL,
            cpu_usage_pct         REAL,
            fix_time_hours        REAL,
            reopen_count          INTEGER,
            sla_breached          INTEGER,
            is_security_related   INTEGER,
            customer_reported     INTEGER,
            predicted_severity    TEXT,
            confidence            REAL,
            created_at            TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized!")


# ════════════════════════════
# PREDICTIONS — same as before
# ════════════════════════════

def save_prediction(input_dict: dict, result: dict, user_id: int = None):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (
            user_id,
            bug_type, component, environment, platform,
            operating_system, browser, reporter_role, module, status,
            affected_users, response_time_ms, business_impact_score,
            reproduction_rate, memory_usage_mb, cpu_usage_pct,
            fix_time_hours, reopen_count, sla_breached,
            is_security_related, customer_reported,
            predicted_severity, confidence, created_at
        ) VALUES (
            :user_id,
            :bug_type, :component, :environment, :platform,
            :operating_system, :browser, :reporter_role, :module, :status,
            :affected_users, :response_time_ms, :business_impact_score,
            :reproduction_rate, :memory_usage_mb, :cpu_usage_pct,
            :fix_time_hours, :reopen_count, :sla_breached,
            :is_security_related, :customer_reported,
            :predicted_severity, :confidence, :created_at
        )
    ''', {
        **input_dict,
        'user_id':             user_id,
        'predicted_severity':  result['predicted_severity'],
        'confidence':          result['confidence'],
        'created_at':          datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    conn.commit()
    conn.close()


def get_all_predictions(limit: int = 50):
    """Sabki predictions — admin ke liye"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM predictions ORDER BY created_at DESC LIMIT ?', (limit,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_user_predictions(user_id: int, limit: int = 50):
    """Sirf ek customer ki predictions"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC LIMIT ?',
        (user_id, limit)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_stats():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT predicted_severity, COUNT(*) as count
        FROM predictions GROUP BY predicted_severity
    ''')
    stats = {row['predicted_severity']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return stats


# ════════════════════════════
# USERS — naye functions
# ════════════════════════════

def create_user(username: str, email: str, hashed_password: str, role: str = 'customer'):
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, hashed_password, role,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False   # username ya email already exists
    finally:
        conn.close()


def get_user_by_username(username: str):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    """Admin ke liye — sabke users"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ════════════════════════════
# LOGIN LOGS — naye functions
# ════════════════════════════

def save_login_log(user_id: int, username: str, role: str, ip: str):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO login_logs (user_id, username, role, login_time, ip_address)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, role,
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ip))
    conn.commit()
    conn.close()


def get_all_login_logs(limit: int = 100):
    """Admin ke liye — sabke login history"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM login_logs ORDER BY login_time DESC LIMIT ?', (limit,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


if __name__ == '__main__':
    init_db()
    print("Stats:", get_stats())