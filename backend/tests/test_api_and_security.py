import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.agent_registry import agent_registry
from backend.app.services.audit_store import audit_store
from backend.app.services.gateway import gateway
from backend.app.models.policy import DecisionType, ReasonCode

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_state():
    agent_registry.reset()
    audit_store.clear()
    yield
    agent_registry.reset()
    audit_store.clear()

def test_api_health_check():
    
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "ai_model_api_key" not in data

def test_agent_revocation_mid_workflow_e2e():
    
    workflow_id = "wf_revocation_e2e"
    corr_id = "corr_revocation_e2e"

    res1, ev1 = gateway.execute_operation(
        workflow_id=workflow_id,
        correlation_id=corr_id,
        source_agent_id="agent://research-01",
        operation="READ",
        target_resource="res://research/whitepaper.pdf"
    )
    assert res1.decision == DecisionType.ALLOW
    assert ev1.decision == "ALLOW"

    patch_res = client.patch(
        "/api/agents/agent://research-01/status",
        json={"status": "REVOKED", "reason": "Compromised prompt injection session detected"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "REVOKED"
    assert patch_res.json()["revocation_reason"] == "Compromised prompt injection session detected"

    res2, ev2 = gateway.execute_operation(
        workflow_id=workflow_id,
        correlation_id=corr_id,
        source_agent_id="agent://research-01",
        operation="READ",
        target_resource="res://research/whitepaper.pdf"
    )
    assert res2.decision == DecisionType.DENY
    assert res2.reason_code == ReasonCode.AGENT_SUSPENDED_OR_REVOKED
    assert ev2.decision == "DENY"
    assert ev2.reason_code == "AGENT_SUSPENDED_OR_REVOKED"
    assert "REVOKED" in ev2.reason_description

def test_api_malformed_json_fails_safely():
    
    res = client.post("/api/approvals", json={"invalid_field": 123})
    assert res.status_code == 422
    err_detail = res.json()
    assert "detail" in err_detail

    res_scen = client.post("/api/scenarios/non_existent_scenario_999/run", json={})
    assert res_scen.status_code == 404

    res_raw = client.post(
        "/api/tools/execute",
        content="THIS IS NOT VALID JSON {{{{",
        headers={"Content-Type": "application/json"}
    )
    assert res_raw.status_code == 422

def test_api_unauthorized_tool_call_denied():
    
    res = client.post(
        "/api/tools/execute",
        json={
            "source_agent_id": "agent://research-01",
            "tool_uri": "tool://worker_reboot",
            "parameters": {"worker_id": "w-01", "force": True}
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "DENY"
    assert data["reason_code"] == "UNSAFE_TOOL_CALL"
    assert "not authorized to invoke tool" in data["reason_description"]

def test_api_tool_call_invalid_schema_parameters_denied():
    
    res = client.post(
        "/api/tools/execute",
        json={
            "source_agent_id": "agent://research-01",
            "tool_uri": "tool://web_scraper",
            "parameters": {"url": "http://169.254.169.254/latest/meta-data/", "timeout_sec": 5}
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "DENY"
    assert data["reason_code"] == "UNSAFE_TOOL_CALL"
    assert "SSRF prevention" in data["reason_description"]

def test_api_tool_call_allowlisted_and_valid():
    
    res = client.post(
        "/api/tools/execute",
        json={
            "source_agent_id": "agent://operations-01",
            "tool_uri": "tool://sandbox_health_check",
            "parameters": {"target_sandbox_id": "sandbox_alpha", "deep_check": False}
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "ALLOW"
    assert data["reason_code"] == "AUTHORIZED"

def test_api_incident_status_update_and_retrieval():
    
    inc = audit_store.record_incident(
        rule_name="RULE_REPEATED_ACCESS_PROBING",
        description="Brute force access probing",
        workflow_id="wf_api_inc",
        correlated_event_ids=["evt_x1"],
        affected_agents=["agent://research-01"],
        severity="HIGH"
    )

    get_res = client.get(f"/api/incidents/{inc.incident_id}")
    assert get_res.status_code == 200
    assert get_res.json()["incident_id"] == inc.incident_id
    assert get_res.json()["status"] == "OPEN"

    patch_res = client.patch(
        f"/api/incidents/{inc.incident_id}/status",
        json={"status": "CONTAINED", "actor": "admin://sec-lead", "notes": "Quarantined agent"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "CONTAINED"
    assert patch_res.json()["resolved_by"] == "admin://sec-lead"

    err_res = client.patch(
        f"/api/incidents/{inc.incident_id}/status",
        json={"status": "NOT_A_VALID_STATUS"}
    )
    assert err_res.status_code == 400
