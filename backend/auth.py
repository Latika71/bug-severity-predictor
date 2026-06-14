import os
from datetime import datetime, timedelta

import bcrypt
import jwt

# Secret key (.env se bhi le sakte ho)
SECRET_KEY = os.getenv("SECRET_KEY", "bug_severity_super_secret_key")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_token(data: dict) -> str:
    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow() +
        timedelta(hours=TOKEN_EXPIRE_HOURS)
    )

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None