"""
models.py — Database Table Structure (SQLAlchemy ORM)
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# ── Path ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, '..', 'database', 'bugs.db')
DB_URL   = f"sqlite:///{DB_PATH}"

# ── Setup ──
Base    = declarative_base()
engine  = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


# ── 1. Users Table ──
class User(Base):
    __tablename__ = 'users'

    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String, unique=True, nullable=False)
    email      = Column(String, unique=True, nullable=False)
    password   = Column(String, nullable=False)
    role       = Column(String, default='customer')
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'email':      self.email,
            'role':       self.role,
            'created_at': str(self.created_at)
        }


# ── 2. Login Logs Table ──
class LoginLog(Base):
    __tablename__ = 'login_logs'

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey('users.id'))
    username   = Column(String)
    role       = Column(String)
    login_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'username':   self.username,
            'role':       self.role,
            'login_time': str(self.login_time),
            'ip_address': self.ip_address
        }


# ── 3. Predictions Table ── (user_id add hua)
class Prediction(Base):
    __tablename__ = 'predictions'

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    user_id               = Column(Integer, ForeignKey('users.id'), nullable=True)

    bug_type              = Column(String)
    component             = Column(String)
    environment           = Column(String)
    platform              = Column(String)
    operating_system      = Column(String)
    browser               = Column(String)
    reporter_role         = Column(String)
    module                = Column(String)
    status                = Column(String)

    affected_users        = Column(Integer)
    response_time_ms      = Column(Integer)
    business_impact_score = Column(Float)
    reproduction_rate     = Column(Float)
    memory_usage_mb       = Column(Float)
    cpu_usage_pct         = Column(Float)
    fix_time_hours        = Column(Float)
    reopen_count          = Column(Integer)
    sla_breached          = Column(Integer)
    is_security_related   = Column(Integer)
    customer_reported     = Column(Integer)

    predicted_severity    = Column(String)
    confidence            = Column(Float)
    created_at            = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                    self.id,
            'user_id':               self.user_id,
            'bug_type':              self.bug_type,
            'component':             self.component,
            'environment':           self.environment,
            'platform':              self.platform,
            'operating_system':      self.operating_system,
            'browser':               self.browser,
            'reporter_role':         self.reporter_role,
            'module':                self.module,
            'status':                self.status,
            'affected_users':        self.affected_users,
            'response_time_ms':      self.response_time_ms,
            'business_impact_score': self.business_impact_score,
            'reproduction_rate':     self.reproduction_rate,
            'memory_usage_mb':       self.memory_usage_mb,
            'cpu_usage_pct':         self.cpu_usage_pct,
            'fix_time_hours':        self.fix_time_hours,
            'reopen_count':          self.reopen_count,
            'sla_breached':          self.sla_breached,
            'is_security_related':   self.is_security_related,
            'customer_reported':     self.customer_reported,
            'predicted_severity':    self.predicted_severity,
            'confidence':            self.confidence,
            'created_at':            str(self.created_at)
        }


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    Base.metadata.create_all(engine)
    print("✅ Tables created: users, login_logs, predictions")


if __name__ == '__main__':
    init_db()