"""
test_model.py — Model Prediction Testing
"""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from predict import predict_severity

# ════════════════════════════════════════
# TEST DATA
# ════════════════════════════════════════

CRITICAL_BUG = {
    "bug_type": "MemoryLeak",
    "component": "Database",
    "environment": "Production",
    "platform": "Web",
    "operating_system": "Ubuntu20",
    "browser": "Chrome",
    "reporter_role": "Developer",
    "module": "Core",
    "status": "Open",
    "affected_users": 5000,
    "response_time_ms": 8000,
    "business_impact_score": 9.5,
    "reproduction_rate": 0.95,
    "memory_usage_mb": 4096,
    "cpu_usage_pct": 95.0,
    "fix_time_hours": 48,
    "reopen_count": 5,
    "sla_breached": 1,
    "is_security_related": 1,
    "customer_reported": 1
}

LOW_BUG = {
    "bug_type": "UIGlitch",
    "component": "Frontend",
    "environment": "Development",
    "platform": "Web",
    "operating_system": "Windows10",
    "browser": "Chrome",
    "reporter_role": "Developer",
    "module": "Plugin",
    "status": "Open",
    "affected_users": 5,
    "response_time_ms": 100,
    "business_impact_score": 1.0,
    "reproduction_rate": 0.1,
    "memory_usage_mb": 128,
    "cpu_usage_pct": 5.0,
    "fix_time_hours": 1,
    "reopen_count": 0,
    "sla_breached": 0,
    "is_security_related": 0,
    "customer_reported": 0
}


# ════════════════════════════════════════
# TEST 1 — Output Structure
# ════════════════════════════════════════
def test_output_structure():
    result = predict_severity(CRITICAL_BUG)
    assert "predicted_severity" in result
    assert "confidence" in result
    assert "all_probabilities" in result
    assert "color" in result
    print("✅ Output Structure — PASS")


# ════════════════════════════════════════
# TEST 2 — Valid Severity Class
# ════════════════════════════════════════
def test_valid_severity_class():
    result = predict_severity(CRITICAL_BUG)
    assert result["predicted_severity"] in ["Critical", "High", "Medium", "Low"]
    print("✅ Valid Severity Class — PASS")


# ════════════════════════════════════════
# TEST 3 — Probabilities Sum = 100%
# ════════════════════════════════════════
def test_probabilities_sum():
    result = predict_severity(CRITICAL_BUG)
    total = sum(result["all_probabilities"].values())
    assert abs(total - 100.0) < 0.5
    print(f"✅ Probabilities Sum = {total:.2f}% — PASS")


# ════════════════════════════════════════
# TEST 4 — Critical Bug → Critical/High
# ════════════════════════════════════════
def test_critical_bug_prediction():
    result = predict_severity(CRITICAL_BUG)
    assert result["predicted_severity"] in ["Critical", "High"]
    assert result["confidence"] > 70.0
    print(f"✅ Critical Bug → {result['predicted_severity']} "
          f"({result['confidence']:.1f}%) — PASS")


# ════════════════════════════════════════
# TEST 5 — Low Bug → Low/Medium
# ════════════════════════════════════════
def test_low_bug_prediction():
    result = predict_severity(LOW_BUG)
    assert result["predicted_severity"] in ["Low", "Medium"]
    print(f"✅ Low Bug → {result['predicted_severity']} — PASS")


# ════════════════════════════════════════
# TEST 6 — Consistency (Same input = Same output)
# ════════════════════════════════════════
def test_consistency():
    result1 = predict_severity(CRITICAL_BUG)
    result2 = predict_severity(CRITICAL_BUG)
    assert result1["predicted_severity"] == result2["predicted_severity"]
    assert result1["confidence"] == result2["confidence"]
    print("✅ Consistency Test — PASS")


# ════════════════════════════════════════
# TEST 7 — Confidence 0-100 range
# ════════════════════════════════════════
def test_confidence_range():
    result = predict_severity(CRITICAL_BUG)
    assert 0.0 <= result["confidence"] <= 100.0
    print(f"✅ Confidence Range = {result['confidence']:.1f}% — PASS")


# ════════════════════════════════════════
# RUN
# ════════════════════════════════════════
if __name__ == "__main__":
    print("\n🧪 Running Model Tests...\n")
    test_output_structure()
    test_valid_severity_class()
    test_probabilities_sum()
    test_critical_bug_prediction()
    test_low_bug_prediction()
    test_consistency()
    test_confidence_range()
    print("\n🎉 All Model Tests Done!")