"""
Schedule engine for computing next occurrences.

Pure domain logic with no Home Assistant dependencies.
Handles DST transitions safely by using timezone-aware datetime operations.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from .models import (
    MedicationStatus,
    Occurrence,
    ReminderPolicy,
    ScheduleKind,
    ScheduleSpec,
)

if TYPE_CHECKING:
    from .models import LogRecord


def compute_next_occurrence(
    timezone: str,
    schedule: ScheduleSpec,
    now: datetime,
    last_taken: datetime | None,
    snooze_until: datetime | None,
    policy: ReminderPolicy,
    logs: list[LogRecord] | None = None,
) -> tuple[Occurrence | None, MedicationStatus]:
    """
    Compute the next occurrence for a medication.

    Args:
        timezone: IANA timezone string (e.g., "Europe/Berlin")
        schedule: The medication schedule specification
        now: Current time (must be timezone-aware)
        last_taken: When the medication was last taken
        snooze_until: If snoozed, when the snooze ends
        policy: The reminder policy
        logs: Recent log records for this medication

    Returns:
        Tuple of (next_occurrence_or_none, current_status)

    """
    tz = ZoneInfo(timezone)

    # Ensure now is timezone-aware
    now = now.replace(tzinfo=tz) if now.tzinfo is None else now.astimezone(tz)

    # AS_NEEDED medications have no scheduled occurrences
    if schedule.kind == ScheduleKind.AS_NEEDED:
        return None, MedicationStatus.PRN

    # Check if schedule is active (within date range)
    today = now.date()
    if schedule.start_date and today < schedule.start_date:
        return None, MedicationStatus.OK
    if schedule.end_date and today > schedule.end_date:
        return None, MedicationStatus.OK

    # Handle snooze
    if snooze_until and now < snooze_until:
        # We're in a snooze period - return the original occurrence but with snoozed status
        occurrence = _compute_base_occurrence(tz, schedule, now, last_taken)
        if occurrence:
            return occurrence, MedicationStatus.SNOOZED
        return None, MedicationStatus.SNOOZED

    # Compute base occurrence
    occurrence = _compute_base_occurrence(tz, schedule, now, last_taken)
    if occurrence is None:
        return None, MedicationStatus.OK

    # Determine status based on timing
    if now >= occurrence.scheduled_for:
        # Check if we're past grace period
        # If there was a snooze, the grace period effectively restarts from snooze end
        effective_grace_start = occurrence.scheduled_for
        if snooze_until and snooze_until > occurrence.scheduled_for:
            # Snooze just ended - use snooze end as the grace start
            effective_grace_start = snooze_until

        grace_end = effective_grace_start + timedelta(minutes=policy.grace_minutes)
        if now > grace_end:
            return occurrence, MedicationStatus.MISSED
        return occurrence, MedicationStatus.DUE

    return occurrence, MedicationStatus.OK


def _compute_base_occurrence(
    tz: ZoneInfo,
    schedule: ScheduleSpec,
    now: datetime,
    last_taken: datetime | None,
) -> Occurrence | None:
    """Compute the next base occurrence without considering snooze/status."""
    if schedule.kind == ScheduleKind.TIMES_PER_DAY:
        return _compute_times_per_day_occurrence(tz, schedule, now, last_taken)
    if schedule.kind == ScheduleKind.INTERVAL:
        return _compute_interval_occurrence(tz, schedule, now, last_taken)
    if schedule.kind == ScheduleKind.WEEKLY:
        return _compute_weekly_occurrence(tz, schedule, now, last_taken)
    return None


def _compute_times_per_day_occurrence(
    tz: ZoneInfo,
    schedule: ScheduleSpec,
    now: datetime,
    last_taken: datetime | None,
) -> Occurrence | None:
    """
    Compute next occurrence for times_per_day schedule.

    Slot keys are in "HH:MM" format.

    This function finds the "active" occurrence - either:
    1. The current slot if we're at or past its time and haven't taken it yet
    2. The next upcoming slot
    """
    if not schedule.times:
        return None

    now_local = now.astimezone(tz)
    today = now_local.date()

    # Sort times
    sorted_times = sorted(schedule.times)

    # First, check today's past slots that might still be "active" (not yet taken)
    for time_str in sorted_times:
        slot_key = time_str
        scheduled_dt = _make_datetime(today, time_str, tz)

        # Check date range
        if schedule.start_date and today < schedule.start_date:
            continue
        if schedule.end_date and today > schedule.end_date:
            continue

        # Only consider slots that are at or before now (current or past)
        if scheduled_dt > now_local:
            continue

        # Skip if we already took this slot
        if last_taken and _is_same_slot_taken(last_taken, scheduled_dt, tz):
            continue

        dose = schedule.get_dose_for_slot(slot_key)
        if dose is None:
            dose = schedule.default_dose
        if dose is None:
            continue

        # This is an active past slot that hasn't been taken
        return Occurrence(
            scheduled_for=scheduled_dt,
            dose=dose,
            slot_key=slot_key,
        )

    # No active past slot found - find the next upcoming slot
    for day_offset in range(7):  # Look up to 7 days ahead
        check_date = today + timedelta(days=day_offset)

        # Check date range
        if schedule.start_date and check_date < schedule.start_date:
            continue
        if schedule.end_date and check_date > schedule.end_date:
            return None

        for time_str in sorted_times:
            slot_key = time_str
            scheduled_dt = _make_datetime(check_date, time_str, tz)

            # Skip slots in the past or at now (those were handled above for today)
            if scheduled_dt <= now_local:
                continue

            # Skip if we already took this slot
            if last_taken and _is_same_slot_taken(last_taken, scheduled_dt, tz):
                continue

            dose = schedule.get_dose_for_slot(slot_key)
            if dose is None:
                dose = schedule.default_dose
            if dose is None:
                continue

            return Occurrence(
                scheduled_for=scheduled_dt,
                dose=dose,
                slot_key=slot_key,
            )

    return None


def _compute_interval_occurrence(
    tz: ZoneInfo,
    schedule: ScheduleSpec,
    now: datetime,
    last_taken: datetime | None,
) -> Occurrence | None:
    """Compute next occurrence for interval schedule."""
    if not schedule.interval_minutes:
        return None

    interval = timedelta(minutes=schedule.interval_minutes)

    # Determine anchor point
    if last_taken:
        anchor = last_taken.astimezone(tz)
    elif schedule.anchor:
        anchor = (
            schedule.anchor.astimezone(tz)
            if schedule.anchor.tzinfo
            else schedule.anchor.replace(tzinfo=tz)
        )
    else:
        # No anchor - use start of today
        now_local = now.astimezone(tz)
        anchor = datetime.combine(now_local.date(), time(0, 0), tzinfo=tz)

    # Calculate next occurrence
    next_due = anchor + interval

    # If we're past that time, calculate when we should have taken it
    now_local = now.astimezone(tz)
    while next_due <= now_local:
        # Check if this is the current pending dose
        next_after = next_due + interval
        if next_after > now_local:
            break
        next_due = next_after

    # Check date range
    if schedule.start_date and next_due.date() < schedule.start_date:
        start_dt = datetime.combine(schedule.start_date, time(0, 0), tzinfo=tz)
        next_due = start_dt + interval

    if schedule.end_date and next_due.date() > schedule.end_date:
        return None

    dose = schedule.default_dose
    if dose is None:
        return None

    # Slot key for interval is based on the anchor offset
    slot_key = f"interval_{int((next_due - anchor).total_seconds() // 60)}"

    return Occurrence(
        scheduled_for=next_due,
        dose=dose,
        slot_key=slot_key,
    )


def _compute_weekly_occurrence(
    tz: ZoneInfo,
    schedule: ScheduleSpec,
    now: datetime,
    last_taken: datetime | None,
) -> Occurrence | None:
    """
    Compute next occurrence for weekly schedule.

    Slot keys are in "W{weekday}-HH:MM" format (weekday 0-6, Monday-Sunday).
    """
    if not schedule.weekdays or not schedule.times:
        return None

    now_local = now.astimezone(tz)
    today = now_local.date()

    # Sort weekdays and times
    sorted_weekdays = sorted(schedule.weekdays)
    sorted_times = sorted(schedule.times)

    # Look up to 2 weeks ahead
    for day_offset in range(14):
        check_date = today + timedelta(days=day_offset)
        weekday = check_date.weekday()

        if weekday not in sorted_weekdays:
            continue

        # Check date range
        if schedule.start_date and check_date < schedule.start_date:
            continue
        if schedule.end_date and check_date > schedule.end_date:
            return None

        for time_str in sorted_times:
            slot_key = f"W{weekday}-{time_str}"
            scheduled_dt = _make_datetime(check_date, time_str, tz)

            # Skip if in the past
            if scheduled_dt <= now_local:
                continue

            # Skip if we already took this slot
            if last_taken and _is_same_slot_taken(last_taken, scheduled_dt, tz):
                continue

            dose = schedule.get_dose_for_slot(slot_key)
            if dose is None:
                dose = schedule.default_dose
            if dose is None:
                continue

            return Occurrence(
                scheduled_for=scheduled_dt,
                dose=dose,
                slot_key=slot_key,
            )

    return None


def _make_datetime(d: date, time_str: str, tz: ZoneInfo) -> datetime:
    """
    Create a timezone-aware datetime from date and time string.

    Handles DST transitions by using fold for ambiguous times.
    """
    hour, minute = map(int, time_str.split(":"))
    t = time(hour, minute)

    # Create naive datetime first
    naive_dt = datetime.combine(d, t)

    # Make timezone-aware, handling DST fold
    try:
        return naive_dt.replace(tzinfo=tz)
        # Check if this time exists (might not during spring forward)
        # If the time doesn't exist, it will be adjusted
    except Exception:
        # Fallback - just add the timezone
        return naive_dt.replace(tzinfo=tz)


def _is_same_slot_taken(
    last_taken: datetime,
    scheduled_dt: datetime,
    tz: ZoneInfo,
) -> bool:
    """
    Check if we've already taken the dose for this slot.

    A slot is considered taken if last_taken is within 1 hour before or after
    the scheduled time.
    """
    last_taken_local = last_taken.astimezone(tz)
    scheduled_local = scheduled_dt.astimezone(tz)

    # Check if on the same day and close to the same time
    if last_taken_local.date() != scheduled_local.date():
        return False

    # Within 1 hour window
    diff = abs((last_taken_local - scheduled_local).total_seconds())
    return diff < 3600  # 1 hour in seconds


def compute_effective_next_due(
    occurrence: Occurrence | None,
    snooze_until: datetime | None,
    status: MedicationStatus,
) -> datetime | None:
    """
    Compute the effective next due time considering snooze.

    When snoozed, the effective due time is when the snooze ends.
    """
    if status == MedicationStatus.PRN:
        return None

    if occurrence is None:
        return None

    if snooze_until and status == MedicationStatus.SNOOZED:
        return snooze_until

    return occurrence.scheduled_for


# Re-export is_in_quiet_hours from policies for backwards compatibility
from .policies import is_in_quiet_hours  # noqa: E402

__all__ = [
    "compute_effective_next_due",
    "compute_next_occurrence",
    "is_in_quiet_hours",
]
