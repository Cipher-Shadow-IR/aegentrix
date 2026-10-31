from datetime import datetime, timezone, timedelta
import pytest
from backend.app.services.temporal_analyzer import temporal_analyzer
from backend.app.services.audit_store import audit_store
from backend.app.services.gateway import gateway

@pytest.fixture(autouse=True)
def clean_audit_store():
    audit_store.clear()
    yield
    audit_store.clear()

def test_sliding_time_window_filtering():
    
    now = datetime.now(timezone.utc)
    old_time = (now - timedelta(seconds=temporal_analyzer.window_seconds + 60)).isoformat()
    recent_time = now.isoformat()

    for i in range(3):
        ev = audit_store.record_event(
            workflow_id="wf_expired_window",
            correlation_id=f"corr_{i}",
            source_agent_id="agent://research-01",
            operation="READ",
            target_resource_or_recipient="res://finance/restricted.csv",
            decision="DENY",
            reason_code="UNAUTHORIZED_RESOURCE_ACCESS",
            reason_description="Denied access"
        )
        ev.timestamp = old_time

    active_events = temporal_analyzer.get_window_events(workflow_id="wf_expired_window", reference_time=now)
    assert len(active_events) == 0

    incidents = temporal_analyzer.analyze_event_sequence(workflow_id="wf_expired_window", reference_time=now)
    assert len(incidents) == 0

def test_cumulative_byte_size_data_exfiltration_threshold():
    
    workflow_id = "wf_cumulative_exfil"
    corr_id = "corr_exfil_test"

    for i in range(3):
        res, ev = gateway.execute_operation(
            workflow_id=workflow_id,
            correlation_id=corr_id,
            source_agent_id="agent://research-01",
            operation="READ",
            target_resource=f"res://research/doc_part_{i}.pdf",
            payload_size_bytes=20000
        )
        assert res.decision.value == "ALLOW"
        assert ev.payload_size_bytes == 20000

    incidents = [
        inc for inc in audit_store.get_incidents()
        if inc.workflow_id == workflow_id and inc.rule_name == "RULE_CUMULATIVE_DATA_EXFILTRATION_THRESHOLD"
    ]
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.severity == "HIGH"
    assert "Cumulative volume threshold breach" in inc.description
    assert len(inc.correlated_event_ids) == 3
    assert "agent://research-01" in inc.affected_agents

def test_incident_status_update_lifecycle():
    
    inc = audit_store.record_incident(
        rule_name="RULE_REPEATED_ACCESS_PROBING",
        description="Repeated unauthorized probe attempts",
        workflow_id="wf_lifecycle_test",
        correlated_event_ids=["evt_001", "evt_002"],
        affected_agents=["agent://research-01"],
        severity="HIGH"
    )
    assert inc.status == "OPEN"
    assert inc.resolved_by is None

    updated_1 = audit_store.update_incident_status(
        incident_id=inc.incident_id,
        status="CONTAINED",
        actor="admin://sec-analyst",
        notes="Agent tokens revoked and perimeter sandboxed."
    )
    assert updated_1 is not None
    assert updated_1.status == "CONTAINED"
    assert updated_1.resolved_by == "admin://sec-analyst"
    assert "sandboxed" in updated_1.resolution_notes
    assert updated_1.updated_at is not None

    updated_2 = audit_store.update_incident_status(
        incident_id=inc.incident_id,
        status="RESOLVED",
        actor="admin://ciso",
        notes="Root cause mitigated, false-positive rules adjusted."
    )
    assert updated_2.status == "RESOLVED"
    assert updated_2.resolved_by == "admin://ciso"

    with pytest.raises(ValueError) as exc:
        audit_store.update_incident_status(
            incident_id=inc.incident_id,
            status="INVALID_STATUS"
        )
    assert "Invalid incident status" in str(exc.value)
