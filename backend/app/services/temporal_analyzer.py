from typing import List, Optional
from ..models.audit import AuditEvent, Incident
from .audit_store import audit_store
from ..core.config import settings

class TemporalRiskAnalyzer:
    
    def __init__(self):
        self.window_seconds = settings.temporal_window_seconds
        self.denial_threshold = settings.max_consecutive_denials_threshold

    def analyze_event_sequence(self, workflow_id: str) -> List[Incident]:
        
        events = [e for e in audit_store._events if e.workflow_id == workflow_id]
        if not events:
            return []

        new_incidents: List[Incident] = []

        has_injection_flag = any(
            e.advisory_model_analysis and any("INSTRUCTION_OVERRIDE" in f or "EXFILTRATION" in f for f in e.advisory_model_analysis.flags)
            or (e.provenance and e.provenance.untrusted_input_origin)
            for e in events
        )
        has_restricted_read_denial = any(
            e.operation == "READ" and "finance" in e.target_resource_or_recipient and e.decision == "DENY"
            for e in events
        )
        has_outbound_transfer_attempt = any(
            e.operation == "TRANSFER" and ("ext://" in e.target_resource_or_recipient or "communication" in e.target_resource_or_recipient)
            for e in events
        )

        if has_injection_flag and (has_restricted_read_denial or has_outbound_transfer_attempt):
            existing = [inc for inc in audit_store._incidents if inc.workflow_id == workflow_id and inc.rule_name == "RULE_MULTI_STEP_EXFILTRATION_CHAIN"]
            if not existing:
                correlated_ids = [e.event_id for e in events]
                affected_agents = list({e.source_agent_id for e in events})
                inc = audit_store.record_incident(
                    rule_name="RULE_MULTI_STEP_EXFILTRATION_CHAIN",
                    description="Coordinated multi-step attack chain detected: prompt injection origin followed by unauthorized restricted access and exfiltration routing attempt.",
                    workflow_id=workflow_id,
                    correlated_event_ids=correlated_ids,
                    affected_agents=affected_agents,
                    severity="CRITICAL"
                )
                new_incidents.append(inc)

        denied_events = [e for e in events if e.decision == "DENY"]
        if len(denied_events) >= self.denial_threshold:
            existing = [inc for inc in audit_store._incidents if inc.workflow_id == workflow_id and inc.rule_name == "RULE_REPEATED_ACCESS_PROBING"]
            if not existing:
                correlated_ids = [e.event_id for e in denied_events]
                affected_agents = list({e.source_agent_id for e in denied_events})
                inc = audit_store.record_incident(
                    rule_name="RULE_REPEATED_ACCESS_PROBING",
                    description=f"Threshold breach: detected {len(denied_events)} consecutive denied security operations within workflow.",
                    workflow_id=workflow_id,
                    correlated_event_ids=correlated_ids,
                    affected_agents=affected_agents,
                    severity="HIGH"
                )
                new_incidents.append(inc)

        return new_incidents

temporal_analyzer = TemporalRiskAnalyzer()
