import sys, os                                                   
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

# ── TEMPORARY DEBUG ──
try:
    from predict import predict_severity
    from database import init_db, save_prediction, get_all_predictions, get_user_predictions, get_stats, get_all_users, get_all_login_logs, create_user, get_user_by_username, save_login_log
    from auth import hash_password, verify_password, create_token, decode_token
    print("✅ ALL IMPORTS SUCCESSFUL")
except Exception as debug_e:
    import traceback
    print("❌ IMPORT FAILED:")
    traceback.print_exc()


"""
app.py — Bug Severity Predictor (Flask → FastAPI)
"""

import os
import traceback
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from predict import predict_severity
from database import (
    init_db, save_prediction,
    get_all_predictions, get_user_predictions,
    get_stats, get_all_users, get_all_login_logs
)
from auth import (
    hash_password, verify_password,
    create_token, decode_token
)
from database import create_user, get_user_by_username, save_login_log

# ── App Setup ──
app = FastAPI(title="Bug Severity Predictor API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ── DB initialize on startup ──
@app.on_event("startup")
def startup():
    init_db()
    print("✅ DB Ready!")

# ════════════════════════════════════════
# PYDANTIC MODELS (Request body shapes)
# ════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "customer"   # customer ya admin

class LoginRequest(BaseModel):
    username: str
    password: str

class PredictRequest(BaseModel):
    bug_type: str
    component: str
    environment: str
    platform: str
    operating_system: str
    browser: str
    reporter_role: str
    module: str
    status: str
    affected_users: int = 100
    response_time_ms: int = 500
    business_impact_score: float = 5.0
    reproduction_rate: float = 0.5
    memory_usage_mb: float = 512.0
    cpu_usage_pct: float = 50.0
    fix_time_hours: float = 8.0
    reopen_count: int = 0
    sla_breached: int = 0
    is_security_related: int = 0
    customer_reported: int = 0

# ════════════════════════════════════════
# AUTH HELPER — Token se user nikalo
# ════════════════════════════════════════

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload  # {'user_id': ..., 'username': ..., 'role': ...}

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ════════════════════════════════════════
# ROUTES — Public
# ════════════════════════════════════════

@app.get("/")
def root():
    return {"status": "ok", "message": "Bug Severity Predictor API v2.0 (FastAPI)"}


@app.post("/register")
def register(body: RegisterRequest):
    """Naya user register karo"""
    hashed = hash_password(body.password)
    success = create_user(body.username, body.email, hashed, body.role)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists. Please try a different one or login."
        )
    return {"success": True, "message": f"User '{body.username}' registered!"}


@app.post("/login")
def login(body: LoginRequest, request: Request):
    """Login → JWT token return karo"""
    user = get_user_by_username(body.username)

    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail=(" Access Denied — The username or password you entered is incorrect. Please try again.")
        )

    token = create_token({
        "user_id":  user["id"],
        "username": user["username"],
        "role":     user["role"]
    })

    # Login log save karo
    save_login_log(
        user_id=user["id"],
        username=user["username"],
        role=user["role"],
        ip=request.client.host
    )

    return {
        "success":  True,
        "token":    token,
        "username": user["username"],
        "role":     user["role"]
    }


# ════════════════════════════════════════
# ROUTES — Customer (Login required)
# ════════════════════════════════════════

@app.post("/predict")
def predict(body: PredictRequest, current_user: dict = Depends(get_current_user)):
    """Bug severity predict karo — login required"""
    try:
        input_dict = body.dict()
        result = predict_severity(input_dict)

        # DB mein save karo with user_id
        save_prediction(
            input_dict=input_dict,
            result=result,
            user_id=current_user["user_id"]
        )

        return {"success": True, "result": result}

    except Exception as e:
        print("\n" + "="*60)
        print("PREDICTION ERROR")
        print("ERROR:", str(e))
        traceback.print_exc()
        print("="*60 + "\n")

        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@app.get("/my-history")
def my_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Sirf apni predictions dekho"""
    rows = get_user_predictions(current_user["user_id"], limit)
    return {"success": True, "data": rows}


@app.get("/my-stats")
def my_stats(current_user: dict = Depends(get_current_user)):
    """Apni prediction stats"""
    rows = get_user_predictions(current_user["user_id"], limit=1000)
    stats = {}
    for row in rows:
        sev = row["predicted_severity"]
        stats[sev] = stats.get(sev, 0) + 1
    return {"success": True, "stats": stats, "total": len(rows)}


# ════════════════════════════════════════
# ROUTES — Admin only
# ════════════════════════════════════════

@app.get("/admin/all-predictions")
def admin_all_predictions(
    limit: int = 50,
    admin: dict = Depends(require_admin)
):
    """Sabki predictions — admin only"""
    rows = get_all_predictions(limit)
    return {"success": True, "data": rows}


@app.get("/admin/all-users")
def admin_all_users(admin: dict = Depends(require_admin)):
    """Saare registered users — admin only"""
    users = get_all_users()
    return {"success": True, "data": users}


@app.get("/admin/stats")
def admin_stats(admin: dict = Depends(require_admin)):
    """Overall severity stats — admin only"""
    stats = get_stats()
    return {"success": True, "stats": stats}


@app.get("/admin/login-logs")
def admin_login_logs(
    limit: int = 100,
    admin: dict = Depends(require_admin)
):
    """Saare login logs — admin only"""
    logs = get_all_login_logs(limit)
    return {"success": True, "data": logs}


# ════════════════════════════════════════
# RUN
# ════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
