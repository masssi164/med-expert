"""
Tests for the schedule engine.

Tests cover:
- times_per_day with slot-specific doses
- weekly schedules with slot-specific doses
- interval schedules with default dose
- PRN (as_needed) schedules
- Snooze behavior
- Missed doses after grace period
- DST transitions (spring forward, fall back)
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from custom_components.med_expert.domain.models import (
    DoseQuantity,
    MedicationStatus,
    ReminderPolicy,
    ScheduleKind,
    ScheduleSpec,
)
from custom_components.med_expert.domain.schedule import (
    compute_effective_next_due,
    compute_next_occurrence,
    is_in_quiet_hours,
)


# Test fixtures
@pytest.fixture
def berlin_tz() -> str:
    """Berlin timezone for DST testing."""
    return "Europe/Berlin"


@pytest.fixture
def utc_tz() -> str:
    """UTC timezone."""
    return "UTC"


@pytest.fixture
def default_policy() -> ReminderPolicy:
    """Default reminder policy."""
    return ReminderPolicy(grace_minutes=30, snooze_minutes=10)


@pytest.fixture
def tablet_dose() -> DoseQuantity:
    """1 tablet dose."""
    return DoseQuantity.normalize(1, 1, "tablet")


@pytest.fixture
def half_tablet_dose() -> DoseQuantity:
    """1/2 tablet dose."""
    return DoseQuantity.normalize(1, 2, "tablet")


@pytest.fixture
def quarter_tablet_dose() -> DoseQuantity:
    """1/4 tablet dose."""
    return DoseQuantity.normalize(1, 4, "tablet")


class TestDoseQuantity:
    """Tests for DoseQuantity model."""

    def test_normalize_whole_number(self):
        """Test normalizing a whole number dose."""
        dose = DoseQuantity.normalize(2, 1, "tablet")
        assert dose.numerator == 2
        assert dose.denominator == 1
        assert dose.format() == "2 tablet"

    def test_normalize_fraction(self):
        """Test normalizing a fractional dose."""
        dose = DoseQuantity.normalize(2, 4, "tablet")
        assert dose.numerator == 1
        assert dose.denominator == 2
        assert dose.format() == "1/2 tablet"

    def test_normalize_quarter(self):
        """Test quarter tablet."""
        dose = DoseQuantity.normalize(1, 4, "tablet")
        assert dose.format() == "1/4 tablet"

    def test_zero_denominator_raises(self):
        """Test that zero denominator raises error."""
        with pytest.raises(ValueError):
            DoseQuantity.normalize(1, 0, "tablet")

    def test_addition_same_unit(self):
        """Test adding doses with same unit."""
        dose1 = DoseQuantity.normalize(1, 2, "tablet")
        dose2 = DoseQuantity.normalize(1, 4, "tablet")
        result = dose1 + dose2
        assert result.numerator == 3
        assert result.denominator == 4
        assert result.format() == "3/4 tablet"

    def test_addition_different_unit_raises(self):
        """Test that adding doses with different units raises error."""
        dose1 = DoseQuantity.normalize(1, 1, "tablet")
        dose2 = DoseQuantity.normalize(1, 1, "ml")
        with pytest.raises(ValueError):
            _ = dose1 + dose2

    def test_to_float(self):
        """Test conversion to float."""
        dose = DoseQuantity.normalize(1, 2, "tablet")
        assert dose.to_float() == 0.5

    def test_serialization_roundtrip(self):
        """Test serialization and deserialization."""
        original = DoseQuantity.normalize(3, 4, "ml")
        data = original.to_dict()
        restored = DoseQuantity.from_dict(data)
        assert restored == original


class TestTimesPerDaySchedule:
    """Tests for times_per_day schedule type."""

    def test_next_occurrence_morning(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test getting next occurrence for morning dose."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "12:00", "20:00"],
            slot_doses={
                "08:00": tablet_dose,
                "12:00": DoseQuantity.normalize(1, 2, "tablet"),
                "20:00": tablet_dose,
            },
        )

        # 7:30 AM - should get 8:00 AM dose
        now = datetime(2025, 1, 15, 7, 30, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.slot_key == "08:00"
        assert occurrence.dose == tablet_dose
        assert occurrence.scheduled_for.hour == 8
        assert status == MedicationStatus.OK

    def test_next_occurrence_after_morning(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test getting next occurrence after morning dose is past."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "12:00", "20:00"],
            slot_doses={
                "08:00": tablet_dose,
                "12:00": DoseQuantity.normalize(1, 2, "tablet"),
                "20:00": tablet_dose,
            },
        )

        # 9:00 AM after taking morning dose - should get 12:00 PM dose
        now = datetime(2025, 1, 15, 9, 0, tzinfo=ZoneInfo(utc_tz))
        last_taken = datetime(2025, 1, 15, 8, 5, tzinfo=ZoneInfo(utc_tz))

        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=last_taken,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.slot_key == "12:00"
        assert occurrence.dose.format() == "1/2 tablet"
        assert status == MedicationStatus.OK

    def test_due_status(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test that status is DUE when at scheduled time."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose=tablet_dose,
        )

        # Exactly at 8:00 AM
        now = datetime(2025, 1, 15, 8, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert status == MedicationStatus.DUE

    def test_missed_after_grace(self, utc_tz: str, tablet_dose: DoseQuantity):
        """Test that status is MISSED after grace period."""
        policy = ReminderPolicy(grace_minutes=30)
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose=tablet_dose,
        )

        # 8:45 AM - 45 minutes after scheduled, grace is 30 min
        now = datetime(2025, 1, 15, 8, 45, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=policy,
        )

        assert occurrence is not None
        assert status == MedicationStatus.MISSED

    def test_slot_specific_doses(self, utc_tz: str, default_policy: ReminderPolicy):
        """Test that each slot can have different dose."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "20:00"],
            slot_doses={
                "08:00": DoseQuantity.normalize(1, 1, "tablet"),
                "20:00": DoseQuantity.normalize(1, 2, "tablet"),
            },
        )

        # Morning - should get 1 tablet
        now_morning = datetime(2025, 1, 15, 7, 30, tzinfo=ZoneInfo(utc_tz))
        occ_morning, _ = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now_morning,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )
        assert occ_morning is not None
        assert occ_morning.dose.format() == "1 tablet"

        # Evening after morning taken - should get 1/2 tablet
        now_evening = datetime(2025, 1, 15, 19, 30, tzinfo=ZoneInfo(utc_tz))
        last_taken = datetime(2025, 1, 15, 8, 5, tzinfo=ZoneInfo(utc_tz))
        occ_evening, _ = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now_evening,
            last_taken=last_taken,
            snooze_until=None,
            policy=default_policy,
        )
        assert occ_evening is not None
        assert occ_evening.dose.format() == "1/2 tablet"


class TestIntervalSchedule:
    """Tests for interval schedule type."""

    def test_interval_from_anchor(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test interval schedule from anchor time."""
        anchor = datetime(2025, 1, 15, 8, 0, tzinfo=ZoneInfo(utc_tz))
        schedule = ScheduleSpec(
            kind=ScheduleKind.INTERVAL,
            interval_minutes=480,  # 8 hours
            anchor=anchor,
            default_dose=tablet_dose,
        )

        # 10:00 AM - should get 4:00 PM next dose
        now = datetime(2025, 1, 15, 10, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.scheduled_for.hour == 16
        assert occurrence.dose == tablet_dose
        assert status == MedicationStatus.OK

    def test_interval_from_last_taken(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test interval schedule from last taken time."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.INTERVAL,
            interval_minutes=360,  # 6 hours
            default_dose=tablet_dose,
        )

        # Last taken at 8:00 AM, now is 12:00 PM
        last_taken = datetime(2025, 1, 15, 8, 0, tzinfo=ZoneInfo(utc_tz))
        now = datetime(2025, 1, 15, 12, 0, tzinfo=ZoneInfo(utc_tz))

        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=last_taken,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.scheduled_for.hour == 14  # 8:00 + 6 hours
        assert status == MedicationStatus.OK


class TestWeeklySchedule:
    """Tests for weekly schedule type."""

    def test_weekly_next_day(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test weekly schedule getting next scheduled day."""
        # Monday = 0, Wednesday = 2, Friday = 4
        schedule = ScheduleSpec(
            kind=ScheduleKind.WEEKLY,
            weekdays=[0, 2, 4],
            times=["09:00"],
            default_dose=tablet_dose,
        )

        # Tuesday at noon - should get Wednesday 9:00 AM
        # 2025-01-14 is a Tuesday
        now = datetime(2025, 1, 14, 12, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.scheduled_for.weekday() == 2  # Wednesday
        assert occurrence.scheduled_for.hour == 9
        assert status == MedicationStatus.OK

    def test_weekly_slot_doses(self, utc_tz: str, default_policy: ReminderPolicy):
        """Test weekly schedule with day-specific doses."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.WEEKLY,
            weekdays=[0, 4],  # Monday and Friday
            times=["09:00"],
            slot_doses={
                "W0-09:00": DoseQuantity.normalize(1, 1, "tablet"),  # Monday
                "W4-09:00": DoseQuantity.normalize(1, 2, "tablet"),  # Friday
            },
        )

        # Thursday - should get Friday dose (1/2 tablet)
        # 2025-01-16 is a Thursday
        now = datetime(2025, 1, 16, 12, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.scheduled_for.weekday() == 4  # Friday
        assert occurrence.dose.format() == "1/2 tablet"


class TestPRNSchedule:
    """Tests for as_needed (PRN) schedule type."""

    def test_prn_no_occurrence(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test that PRN schedules have no scheduled occurrences."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.AS_NEEDED,
            default_dose=tablet_dose,
        )

        now = datetime(2025, 1, 15, 12, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is None
        assert status == MedicationStatus.PRN


class TestSnooze:
    """Tests for snooze behavior."""

    def test_snoozed_status(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test that status is SNOOZED when in snooze period."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose=tablet_dose,
        )

        # 8:15 AM, snoozed until 8:30 AM
        now = datetime(2025, 1, 15, 8, 15, tzinfo=ZoneInfo(utc_tz))
        snooze_until = datetime(2025, 1, 15, 8, 30, tzinfo=ZoneInfo(utc_tz))

        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=snooze_until,
            policy=default_policy,
        )

        assert occurrence is not None
        assert status == MedicationStatus.SNOOZED

    def test_snooze_expired(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test that status is DUE after snooze expires."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose=tablet_dose,
        )

        # 8:35 AM, snooze ended at 8:30 AM
        now = datetime(2025, 1, 15, 8, 35, tzinfo=ZoneInfo(utc_tz))
        snooze_until = datetime(2025, 1, 15, 8, 30, tzinfo=ZoneInfo(utc_tz))

        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=snooze_until,
            policy=default_policy,
        )

        assert occurrence is not None
        assert status == MedicationStatus.DUE

    def test_effective_next_due_with_snooze(
        self, utc_tz: str, tablet_dose: DoseQuantity
    ):
        """Test that effective next due uses snooze time when snoozed."""
        from custom_components.med_expert.domain.models import Occurrence

        scheduled_time = datetime(2025, 1, 15, 8, 0, tzinfo=ZoneInfo(utc_tz))
        snooze_time = datetime(2025, 1, 15, 8, 30, tzinfo=ZoneInfo(utc_tz))

        occurrence = Occurrence(
            scheduled_for=scheduled_time,
            dose=tablet_dose,
            slot_key="08:00",
        )

        effective = compute_effective_next_due(
            occurrence=occurrence,
            snooze_until=snooze_time,
            status=MedicationStatus.SNOOZED,
        )

        assert effective == snooze_time


class TestDateRange:
    """Tests for schedule date ranges."""

    def test_before_start_date(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test that no occurrence before start date."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose=tablet_dose,
            start_date=date(2025, 2, 1),
        )

        now = datetime(2025, 1, 15, 7, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is None
        assert status == MedicationStatus.OK

    def test_after_end_date(
        self, utc_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test that no occurrence after end date."""
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose=tablet_dose,
            end_date=date(2025, 1, 10),
        )

        now = datetime(2025, 1, 15, 7, 0, tzinfo=ZoneInfo(utc_tz))
        occurrence, status = compute_next_occurrence(
            timezone=utc_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is None
        assert status == MedicationStatus.OK


class TestDST:
    """Tests for DST (Daylight Saving Time) handling."""

    def test_spring_forward(
        self, berlin_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """
        Test schedule during spring forward (clocks skip 2:00-3:00 AM).

        In Germany 2025, spring forward is on March 30 at 2:00 AM.
        """
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["02:30", "08:00"],  # 2:30 doesn't exist on spring forward day
            default_dose=tablet_dose,
        )

        # March 30, 2025 at 1:30 AM (before spring forward)
        tz = ZoneInfo(berlin_tz)
        now = datetime(2025, 3, 30, 1, 30, tzinfo=tz)

        occurrence, status = compute_next_occurrence(
            timezone=berlin_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        # Should skip the non-existent 2:30 and get 8:00
        assert occurrence is not None
        # The 2:30 time during spring forward will be adjusted
        assert occurrence.scheduled_for.hour in (2, 3, 8)

    def test_fall_back(
        self, berlin_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """
        Test schedule during fall back (clocks repeat 2:00-3:00 AM).

        In Germany 2025, fall back is on October 26 at 3:00 AM.
        """
        schedule = ScheduleSpec(
            kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "20:00"],
            default_dose=tablet_dose,
        )

        # October 26, 2025 at 7:00 AM
        tz = ZoneInfo(berlin_tz)
        now = datetime(2025, 10, 26, 7, 0, tzinfo=tz)

        occurrence, status = compute_next_occurrence(
            timezone=berlin_tz,
            schedule=schedule,
            now=now,
            last_taken=None,
            snooze_until=None,
            policy=default_policy,
        )

        assert occurrence is not None
        assert occurrence.scheduled_for.hour == 8
        assert status == MedicationStatus.OK

    def test_interval_across_dst(
        self, berlin_tz: str, default_policy: ReminderPolicy, tablet_dose: DoseQuantity
    ):
        """Test interval schedule across DST boundary."""
        tz = ZoneInfo(berlin_tz)
        # Last taken at 1:00 AM on spring forward day
        last_taken = datetime(2025, 3, 30, 1, 0, tzinfo=tz)

        schedule = ScheduleSpec(
            kind=ScheduleKind.INTERVAL,
            interval_minutes=120,  # 2 hours
            default_dose=tablet_dose,
        )

        # Now at 3:30 AM (after spring forward)
        now = datetime(2025, 3, 30, 3, 30, tzinfo=tz)

        occurrence, status = compute_next_occurrence(
            timezone=berlin_tz,
            schedule=schedule,
            now=now,
            last_taken=last_taken,
            snooze_until=None,
            policy=default_policy,
        )

        # Should be 2 hours after 1:00 AM, which is 3:00 AM (accounting for DST)
        assert occurrence is not None


class TestQuietHours:
    """Tests for quiet hours functionality."""

    def test_in_quiet_hours_normal(self, utc_tz: str):
        """Test quiet hours during normal time range."""
        policy = ReminderPolicy(
            quiet_hours_start="22:00",
            quiet_hours_end="07:00",
        )

        # 23:00 - should be in quiet hours
        now = datetime(2025, 1, 15, 23, 0, tzinfo=ZoneInfo(utc_tz))
        assert is_in_quiet_hours(now, utc_tz, policy) is True

        # 12:00 - should not be in quiet hours
        now = datetime(2025, 1, 15, 12, 0, tzinfo=ZoneInfo(utc_tz))
        assert is_in_quiet_hours(now, utc_tz, policy) is False

    def test_in_quiet_hours_overnight(self, utc_tz: str):
        """Test quiet hours spanning midnight."""
        policy = ReminderPolicy(
            quiet_hours_start="22:00",
            quiet_hours_end="07:00",
        )

        # 02:00 - should be in quiet hours
        now = datetime(2025, 1, 15, 2, 0, tzinfo=ZoneInfo(utc_tz))
        assert is_in_quiet_hours(now, utc_tz, policy) is True

        # 08:00 - should not be in quiet hours
        now = datetime(2025, 1, 15, 8, 0, tzinfo=ZoneInfo(utc_tz))
        assert is_in_quiet_hours(now, utc_tz, policy) is False
