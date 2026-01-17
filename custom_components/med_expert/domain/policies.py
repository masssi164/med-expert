"""
Policy logic for med_expert.

Contains business rules for notifications, rate limiting, and scheduling behavior.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from .models import MedicationState, ReminderPolicy


def should_send_notification(
    policy: ReminderPolicy,
    state: MedicationState,
    now: datetime,
) -> bool:
    """
    Determine if a notification should be sent.

    Considers:
    - Rate limiting (don't spam notifications)
    - Repeat policy
    - Max retries
    """
    # Check if we've recently notified
    if state.last_notified_at:
        min_interval = timedelta(minutes=max(1, policy.snooze_minutes // 2))
        if now - state.last_notified_at < min_interval:
            return False

    return True


def should_repeat_notification(
    policy: ReminderPolicy,
    state: MedicationState,
    now: datetime,
    notification_count: int,
) -> bool:
    """
    Determine if a notification should be repeated.

    Args:
        policy: The reminder policy
        state: Current medication state
        now: Current time
        notification_count: How many notifications have been sent for this occurrence

    Returns:
        True if should repeat

    """
    if not policy.repeat_minutes:
        return False

    if policy.max_retries is not None and notification_count >= policy.max_retries:
        return False

    if not state.last_notified_at:
        return True

    time_since_last = now - state.last_notified_at
    return time_since_last >= timedelta(minutes=policy.repeat_minutes)


def compute_snooze_until(
    policy: ReminderPolicy,
    now: datetime,
    minutes: int | None = None,
) -> datetime:
    """
    Compute the snooze end time.

    Args:
        policy: The reminder policy
        now: Current time
        minutes: Override snooze duration (optional)

    Returns:
        When the snooze should end

    """
    duration = minutes if minutes is not None else policy.snooze_minutes
    return now + timedelta(minutes=duration)


def is_within_grace_period(
    scheduled_for: datetime,
    now: datetime,
    policy: ReminderPolicy,
) -> bool:
    """Check if current time is within the grace period for a scheduled dose."""
    if now < scheduled_for:
        return False

    grace_end = scheduled_for + timedelta(minutes=policy.grace_minutes)
    return now <= grace_end


def is_dose_missed(
    scheduled_for: datetime,
    now: datetime,
    policy: ReminderPolicy,
) -> bool:
    """Check if a dose should be marked as missed."""
    grace_end = scheduled_for + timedelta(minutes=policy.grace_minutes)
    return now > grace_end


def is_in_quiet_hours(
    now: datetime,
    timezone: str,
    policy: ReminderPolicy,
) -> bool:
    """
    Check if current time is within quiet hours.

    Handles overnight ranges (e.g., 22:00 to 07:00).

    Args:
        now: Current datetime (timezone-aware)
        timezone: Timezone string (e.g., "Europe/Berlin")
        policy: Reminder policy with quiet hours settings

    Returns:
        True if currently in quiet hours

    """
    if not policy.quiet_hours_start or not policy.quiet_hours_end:
        return False

    tz = ZoneInfo(timezone)
    now_local = now.astimezone(tz)

    start_hour, start_min = map(int, policy.quiet_hours_start.split(":"))
    end_hour, end_min = map(int, policy.quiet_hours_end.split(":"))

    current_minutes = now_local.hour * 60 + now_local.minute
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min

    if start_minutes <= end_minutes:
        # Normal case: e.g., 22:00 to 23:00
        return start_minutes <= current_minutes < end_minutes
    # Overnight case: e.g., 22:00 to 07:00
    return current_minutes >= start_minutes or current_minutes < end_minutes
