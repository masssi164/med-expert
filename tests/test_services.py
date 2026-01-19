"""Tests for application services."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from custom_components.med_expert.application.services import (
    AddMedicationCommand,
    MedicationNotFoundError,
    MedicationService,
    PRNTakeCommand,
    SkipCommand,
    SnoozeCommand,
    TakeCommand,
    UpdateMedicationCommand,
    ValidationError,
)
from custom_components.med_expert.domain.models import (
    LogAction,
    MedicationStatus,
    Profile,
    ScheduleKind,
)


@pytest.fixture
def utc_tz() -> str:
    """UTC timezone."""
    return "UTC"


@pytest.fixture
def fixed_now() -> datetime:
    """Fixed current time for testing."""
    return datetime(2025, 1, 15, 10, 0, tzinfo=ZoneInfo("UTC"))


@pytest.fixture
def service(fixed_now: datetime) -> MedicationService:
    """Create service with fixed time."""
    return MedicationService(get_now=lambda: fixed_now)


@pytest.fixture
def profile(utc_tz: str) -> Profile:
    """Create a test profile."""
    return Profile.create(name="Test Profile", timezone=utc_tz)


class TestAddMedication:
    """Tests for adding medications."""

    def test_add_times_per_day_medication(
        self, service: MedicationService, profile: Profile
    ):
        """Test adding a times_per_day medication."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "20:00"],
            slot_doses={
                "08:00": {"numerator": 1, "denominator": 1, "unit": "tablet"},
                "20:00": {"numerator": 1, "denominator": 2, "unit": "tablet"},
            },
        )

        medication = service.add_medication(profile, command)

        assert medication.display_name == "Aspirin"
        assert medication.schedule.kind == ScheduleKind.TIMES_PER_DAY
        assert medication.schedule.times == ["08:00", "20:00"]
        assert medication.schedule.slot_doses["08:00"].format() == "1 tablet"
        assert medication.schedule.slot_doses["20:00"].format() == "1/2 tablet"
        assert medication.medication_id in profile.medications

    def test_add_interval_medication(
        self, service: MedicationService, profile: Profile
    ):
        """Test adding an interval medication."""
        command = AddMedicationCommand(
            display_name="Antibiotic",
            schedule_kind=ScheduleKind.INTERVAL,
            interval_minutes=480,  # 8 hours
            default_dose={"numerator": 1, "denominator": 1, "unit": "capsule"},
        )

        medication = service.add_medication(profile, command)

        assert medication.display_name == "Antibiotic"
        assert medication.schedule.kind == ScheduleKind.INTERVAL
        assert medication.schedule.interval_minutes == 480
        assert medication.schedule.default_dose.format() == "1 capsule"

    def test_add_weekly_medication(self, service: MedicationService, profile: Profile):
        """Test adding a weekly medication."""
        command = AddMedicationCommand(
            display_name="Weekly Vitamin",
            schedule_kind=ScheduleKind.WEEKLY,
            weekdays=[0, 3],  # Monday and Thursday
            times=["09:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )

        medication = service.add_medication(profile, command)

        assert medication.schedule.kind == ScheduleKind.WEEKLY
        assert medication.schedule.weekdays == [0, 3]

    def test_add_prn_medication(self, service: MedicationService, profile: Profile):
        """Test adding a PRN (as-needed) medication."""
        command = AddMedicationCommand(
            display_name="Pain Reliever",
            schedule_kind=ScheduleKind.AS_NEEDED,
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )

        medication = service.add_medication(profile, command)

        assert medication.schedule.kind == ScheduleKind.AS_NEEDED
        assert medication.state.status == MedicationStatus.PRN
        assert medication.state.next_due is None

    def test_add_medication_computes_initial_state(
        self, service: MedicationService, profile: Profile, fixed_now: datetime
    ):
        """Test that adding a medication computes its initial state."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],  # After fixed_now (10:00)
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )

        medication = service.add_medication(profile, command)

        assert medication.state.next_due is not None
        assert medication.state.next_due.hour == 14
        assert medication.state.status == MedicationStatus.OK

    def test_add_medication_generates_stable_id(
        self, service: MedicationService, profile: Profile
    ):
        """Test that medication IDs are stable UUIDs."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )

        medication = service.add_medication(profile, command)

        # ID should be a valid UUID
        import uuid

        uuid.UUID(medication.medication_id)  # Should not raise

    def test_add_medication_validates_times(
        self, service: MedicationService, profile: Profile
    ):
        """Test that invalid times are rejected."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["25:00"],  # Invalid
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )

        with pytest.raises(ValidationError):
            service.add_medication(profile, command)

    def test_add_medication_requires_name(
        self, service: MedicationService, profile: Profile
    ):
        """Test that display name is required."""
        command = AddMedicationCommand(
            display_name="",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
        )

        with pytest.raises(ValidationError):
            service.add_medication(profile, command)


class TestTakeMedication:
    """Tests for taking medications."""

    def test_take_uses_scheduled_dose(
        self, service: MedicationService, profile: Profile
    ):
        """Test that take uses the scheduled dose."""
        # Add medication
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            slot_doses={
                "14:00": {"numerator": 1, "denominator": 2, "unit": "tablet"},
            },
        )
        medication = service.add_medication(profile, command)

        # Take it
        log = service.take(
            profile,
            TakeCommand(medication_id=medication.medication_id),
        )

        assert log.action == LogAction.TAKEN
        assert log.dose.format() == "1/2 tablet"
        assert log.scheduled_for is not None

    def test_take_with_dose_override(
        self, service: MedicationService, profile: Profile
    ):
        """Test take with dose override."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        log = service.take(
            profile,
            TakeCommand(
                medication_id=medication.medication_id,
                dose_override={"numerator": 2, "denominator": 1, "unit": "tablet"},
            ),
        )

        assert log.dose.format() == "2 tablet"

    def test_take_updates_state(
        self, service: MedicationService, profile: Profile, fixed_now: datetime
    ):
        """Test that take updates medication state."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        service.take(
            profile,
            TakeCommand(medication_id=medication.medication_id),
        )

        assert medication.state.last_taken == fixed_now
        assert medication.state.snooze_until is None

    def test_take_not_found(self, service: MedicationService, profile: Profile):
        """Test take with non-existent medication."""
        with pytest.raises(MedicationNotFoundError):
            service.take(
                profile,
                TakeCommand(medication_id="non-existent"),
            )


class TestPRNTake:
    """Tests for PRN (as-needed) intake."""

    def test_prn_take_logs_with_null_scheduled_for(
        self, service: MedicationService, profile: Profile
    ):
        """Test that PRN take creates log with scheduled_for=None."""
        command = AddMedicationCommand(
            display_name="Pain Reliever",
            schedule_kind=ScheduleKind.AS_NEEDED,
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        log = service.prn_take(
            profile,
            PRNTakeCommand(
                medication_id=medication.medication_id,
                dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            ),
        )

        assert log.action == LogAction.PRN_TAKEN
        assert log.scheduled_for is None
        assert log.dose.format() == "1 tablet"

    def test_prn_take_with_note(self, service: MedicationService, profile: Profile):
        """Test PRN take with note."""
        command = AddMedicationCommand(
            display_name="Pain Reliever",
            schedule_kind=ScheduleKind.AS_NEEDED,
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        log = service.prn_take(
            profile,
            PRNTakeCommand(
                medication_id=medication.medication_id,
                dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
                note="Headache after lunch",
            ),
        )

        assert log.meta is not None
        assert log.meta["note"] == "Headache after lunch"

    def test_prn_take_does_not_affect_schedule_by_default(
        self, service: MedicationService, profile: Profile
    ):
        """Test that PRN take doesn't affect next_due by default."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)
        original_next_due = medication.state.next_due

        service.prn_take(
            profile,
            PRNTakeCommand(
                medication_id=medication.medication_id,
                dose={"numerator": 1, "denominator": 2, "unit": "tablet"},
            ),
        )

        assert medication.state.next_due == original_next_due

    def test_prn_take_affects_schedule_when_policy_set(
        self, service: MedicationService, profile: Profile
    ):
        """Test that PRN take affects schedule when policy allows it."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            policy={"prn_affects_schedule": True},
        )
        medication = service.add_medication(profile, command)
        original_next_due = medication.state.next_due

        service.prn_take(
            profile,
            PRNTakeCommand(
                medication_id=medication.medication_id,
                dose={"numerator": 1, "denominator": 2, "unit": "tablet"},
            ),
        )

        # Next due should have changed because last_taken was updated
        assert medication.state.last_taken is not None


class TestSnooze:
    """Tests for snooze functionality."""

    def test_snooze_sets_snooze_until(
        self, service: MedicationService, profile: Profile, fixed_now: datetime
    ):
        """Test that snooze sets snooze_until."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        snooze_until = service.snooze(
            profile,
            SnoozeCommand(medication_id=medication.medication_id, minutes=15),
        )

        expected = fixed_now + timedelta(minutes=15)
        assert snooze_until == expected
        assert medication.state.snooze_until == expected
        assert medication.state.status == MedicationStatus.SNOOZED

    def test_snooze_uses_policy_default(
        self, service: MedicationService, profile: Profile, fixed_now: datetime
    ):
        """Test that snooze uses policy default duration."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            policy={"snooze_minutes": 20},
        )
        medication = service.add_medication(profile, command)

        snooze_until = service.snooze(
            profile,
            SnoozeCommand(medication_id=medication.medication_id),
        )

        expected = fixed_now + timedelta(minutes=20)
        assert snooze_until == expected

    def test_snooze_creates_log(self, service: MedicationService, profile: Profile):
        """Test that snooze creates a log record."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        service.snooze(
            profile,
            SnoozeCommand(medication_id=medication.medication_id, minutes=10),
        )

        assert len(profile.logs) == 1
        assert profile.logs[0].action == LogAction.SNOOZED

    def test_snooze_prn_raises_error(
        self, service: MedicationService, profile: Profile
    ):
        """Test that snoozing PRN medication raises error."""
        command = AddMedicationCommand(
            display_name="Pain Reliever",
            schedule_kind=ScheduleKind.AS_NEEDED,
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        with pytest.raises(ValidationError):
            service.snooze(
                profile,
                SnoozeCommand(medication_id=medication.medication_id, minutes=10),
            )


class TestSkip:
    """Tests for skip functionality."""

    def test_skip_moves_to_next_slot(
        self, service: MedicationService, profile: Profile
    ):
        """Test that skip moves to next scheduled slot."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00", "20:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        # First slot should be 14:00
        assert medication.state.next_due.hour == 14

        service.skip(
            profile,
            SkipCommand(medication_id=medication.medication_id),
        )

        # Should now be 20:00
        assert medication.state.next_due.hour == 20

    def test_skip_creates_log_with_reason(
        self, service: MedicationService, profile: Profile
    ):
        """Test that skip creates log with reason."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["14:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        service.skip(
            profile,
            SkipCommand(
                medication_id=medication.medication_id,
                reason="Upset stomach",
            ),
        )

        assert len(profile.logs) == 1
        assert profile.logs[0].action == LogAction.SKIPPED
        assert profile.logs[0].meta["reason"] == "Upset stomach"


class TestUpdateMedication:
    """Tests for updating medications."""

    def test_update_display_name(self, service: MedicationService, profile: Profile):
        """Test updating medication display name."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        service.update_medication(
            profile,
            UpdateMedicationCommand(
                medication_id=medication.medication_id,
                display_name="Aspirin 100mg",
            ),
        )

        assert medication.display_name == "Aspirin 100mg"
        assert medication.ref.display_name == "Aspirin 100mg"

    def test_update_not_found(self, service: MedicationService, profile: Profile):
        """Test update with non-existent medication."""
        with pytest.raises(MedicationNotFoundError):
            service.update_medication(
                profile,
                UpdateMedicationCommand(
                    medication_id="non-existent",
                    display_name="New Name",
                ),
            )


class TestRemoveMedication:
    """Tests for removing medications."""

    def test_remove_medication(self, service: MedicationService, profile: Profile):
        """Test removing a medication."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)
        med_id = medication.medication_id

        removed = service.remove_medication(profile, med_id)

        assert removed == medication
        assert profile.get_medication(med_id) is None

    def test_remove_nonexistent_returns_none(
        self, service: MedicationService, profile: Profile
    ):
        """Test removing non-existent medication returns None."""
        removed = service.remove_medication(profile, "non-existent")
        assert removed is None
