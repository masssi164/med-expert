"""Diagnostics support for Med Expert."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MedExpertConfigEntry

# Keys to redact from diagnostics
TO_REDACT = {
    "medication_id",
    "profile_id",
    "external_id",
    "note",
    "reason",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: MedExpertConfigEntry,
) -> dict[str, Any]:
    """
    Return diagnostics for a config entry.

    Provides a redacted view of the profile for troubleshooting.
    """
    manager = entry.runtime_data.manager
    profile = manager.profile

    # Collect medication summaries (redacted)
    medications_summary = []
    for med in profile.medications.values():
        medications_summary.append({
            "display_name": med.display_name,
            "schedule_kind": med.schedule.kind.value,
            "status": med.state.status.value,
            "has_next_due": med.state.next_due is not None,
            "has_snooze": med.state.snooze_until is not None,
            "has_last_taken": med.state.last_taken is not None,
            "policy": {
                "grace_minutes": med.policy.grace_minutes,
                "snooze_minutes": med.policy.snooze_minutes,
                "prn_affects_schedule": med.policy.prn_affects_schedule,
                "has_quiet_hours": med.policy.quiet_hours_start is not None,
            },
        })

    # Collect log statistics (no personal data)
    log_stats = {
        "total_logs": len(profile.logs),
        "action_counts": {},
    }
    for log in profile.logs:
        action = log.action.value
        log_stats["action_counts"][action] = log_stats["action_counts"].get(action, 0) + 1

    # Schedule kind distribution
    schedule_kinds = {}
    for med in profile.medications.values():
        kind = med.schedule.kind.value
        schedule_kinds[kind] = schedule_kinds.get(kind, 0) + 1

    diagnostics = {
        "profile": {
            "name": profile.name,
            "timezone": profile.timezone,
            "medication_count": len(profile.medications),
        },
        "medications": medications_summary,
        "schedule_kind_distribution": schedule_kinds,
        "log_statistics": log_stats,
        "entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "version": entry.version,
        },
    }

    return async_redact_data(diagnostics, TO_REDACT)
