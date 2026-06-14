"""
test_api.py — FastAPI Routes Testing
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"

# ── Test Data ──
TEST_USER = {
    "username": "testuser99",
    "email": "testuser99@test.com",
    "password": "test123",
    "role": "customer"
}

SAMPLE_BUG = {
    "bug_type": "MemoryLeak",
    "component": "Database",
    "environment": "Production",
    "platform": "Web",
    "operating_system": "Ubuntu20",
    "browser": "Chrome",
    "reporter_role": "Developer",
    "module": "Core",
    "status": "Open",
    "affected_users": 500,
    "response_time_ms": 3200,
    "business_impact_score": 8.5,
    "reproduction_rate": 0.9,
    "memory_usage_mb": 1024,
    "cpu_usage_pct": 85.0,
    "fix_time_hours": 12,
    "reopen_count": 2,
    "sla_breached": 1,
    "is_security_related": 0,
    "customer_reported": 1
}


# ════════════════════════════════════════
# TEST 1 — API Health Check
# ════════════════════════════════════════
def test_api_running():
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    print("✅ API Health Check — PASS")


# ════════════════════════════════════════
# TEST 2 — Register
# ════════════════════════════════════════
def test_register_new_user():
    res = requests.post(f"{BASE_URL}/register", json=TEST_USER)
    assert res.status_code == 200
    assert res.json()["success"] == True
    print("✅ Register New User — PASS")


def test_register_duplicate_user():
    res = requests.post(f"{BASE_URL}/register", json=TEST_USER)
    assert res.status_code == 400
    print("✅ Duplicate Register Error — PASS")


# ════════════════════════════════════════
# TEST 3 — Login
# ════════════════════════════════════════
def test_login_valid():
    res = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    assert res.status_code == 200
    assert "token" in res.json()
    print("✅ Valid Login — PASS")


def test_login_invalid():
    res = requests.post(f"{BASE_URL}/login", json={
        "username": "wronguser",
        "password": "wrongpass"
    })
    assert res.status_code == 401
    print("✅ Invalid Login Error — PASS")


# ════════════════════════════════════════
# TEST 4 — Predict (Token required)
# ════════════════════════════════════════
def test_predict_with_token():
    # Pehle login karo token lene ke liye
    login_res = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.post(f"{BASE_URL}/predict",
                        json=SAMPLE_BUG,
                        headers=headers)
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert "predicted_severity" in res.json()["result"]
    print("✅ Predict with Token — PASS")


def test_predict_without_token():
    res = requests.post(f"{BASE_URL}/predict", json=SAMPLE_BUG)
    assert res.status_code == 403
    print("✅ Predict without Token — PASS")


# ════════════════════════════════════════
# TEST 5 — Admin Routes
# ════════════════════════════════════════
def test_admin_routes_blocked_for_customer():
    # Customer token se admin route try karo
    login_res = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(f"{BASE_URL}/admin/all-predictions",
                       headers=headers)
    assert res.status_code == 403
    print("✅ Admin Route Blocked for Customer — PASS")


def test_admin_stats_with_admin_token():
    login_res = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "admin@123"
    })
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    assert res.status_code == 200
    assert "stats" in res.json()
    print("✅ Admin Stats — PASS")


# ════════════════════════════════════════
# RUN
# ════════════════════════════════════════
if __name__ == "__main__":
    print("\n🧪 Running API Tests...\n")
    test_api_running()
    test_register_new_user()
    test_register_duplicate_user()
    test_login_valid()
    test_login_invalid()
    test_predict_with_token()
    test_predict_without_token()
    test_admin_routes_blocked_for_customer()
    test_admin_stats_with_admin_token()
    print("\n🎉 All Tests Done!")