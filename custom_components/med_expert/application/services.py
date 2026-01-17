"""
Application services for med_expert.

Contains use cases, commands, and DTOs for medication management.
Coordinates between domain models, repository, and providers.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from custom_components.med_expert.domain.models import (
    DoseQuantity,
    LogAction,
    LogRecord,
    Medication,
    MedicationRef,
    MedicationStatus,
    Profile,
    ReminderPolicy,
    ScheduleKind,
    ScheduleSpec,
)
from custom_components.med_expert.domain.policies import compute_snooze_until
from custom_components.med_expert.domain.schedule import compute_next_occurrence

# Type alias for state change callback
StateChangeCallback = Callable[[str, str], Awaitable[None]]  # (profile_id, medication_id)


class MedicationServiceError(Exception):
    """Base exception for medication service errors."""



class ProfileNotFoundError(MedicationServiceError):
    """Raised when a profile is not found."""



class MedicationNotFoundError(MedicationServiceError):
    """Raised when a medication is not found."""



class ValidationError(MedicationServiceError):
    """Raised when validation fails."""



# ============================================================================
# Commands (DTOs for service operations)
# ============================================================================


@dataclass
class AddMedicationCommand:
    """Command to add a medication to a profile."""

    display_name: str
    schedule_kind: ScheduleKind
    times: list[str] | None = None
    weekdays: list[int] | None = None
    interval_minutes: int | None = None
    slot_doses: dict[str, dict] | None = None  # slot_key -> dose dict
    default_dose: dict | None = None  # {numerator, denominator, unit}
    policy: dict | None = None
    start_date: str | None = None  # ISO format
    end_date: str | None = None  # ISO format

    def validate(self) -> None:
        """Validate the command."""
        if not self.display_name or not self.display_name.strip():
            msg = "Display name is required"
            raise ValidationError(msg)

        if self.schedule_kind == ScheduleKind.TIMES_PER_DAY:
            if not self.times:
                msg = "Times are required for times_per_day schedule"
                raise ValidationError(msg)
            for time_str in self.times:
                if not _is_valid_time(time_str):
                    msg = f"Invalid time format: {time_str}"
                    raise ValidationError(msg)

        elif self.schedule_kind == ScheduleKind.WEEKLY:
            if not self.weekdays:
                msg = "Weekdays are required for weekly schedule"
                raise ValidationError(msg)
            if not self.times:
                msg = "Times are required for weekly schedule"
                raise ValidationError(msg)
            for wd in self.weekdays:
                if not 0 <= wd <= 6:
                    msg = f"Invalid weekday: {wd}"
                    raise ValidationError(msg)

        elif self.schedule_kind == ScheduleKind.INTERVAL:
            if not self.interval_minutes or self.interval_minutes <= 0:
                msg = "Positive interval_minutes is required for interval schedule"
                raise ValidationError(msg)

        # Validate doses
        if self.default_dose:
            _validate_dose_dict(self.default_dose)

        if self.slot_doses:
            for dose_dict in self.slot_doses.values():
                _validate_dose_dict(dose_dict)


@dataclass
class UpdateMedicationCommand:
    """Command to update a medication."""

    medication_id: str
    display_name: str | None = None
    schedule_updates: dict | None = None
    policy_updates: dict | None = None


@dataclass
class TakeCommand:
    """Command to mark a medication as taken."""

    medication_id: str
    taken_at: datetime | None = None
    dose_override: dict | None = None  # {numerator, denominator, unit}


@dataclass
class PRNTakeCommand:
    """Command to log a PRN (as-needed) intake."""

    medication_id: str
    dose: dict  # {numerator, denominator, unit}
    taken_at: datetime | None = None
    note: str | None = None


@dataclass
class SnoozeCommand:
    """Command to snooze a medication reminder."""

    medication_id: str
    minutes: int | None = None
    until: datetime | None = None


@dataclass
class SkipCommand:
    """Command to skip a scheduled dose."""

    medication_id: str
    reason: str | None = None


# ============================================================================
# Application Service
# ============================================================================


class MedicationService:
    """
    Application service for medication management.

    Coordinates domain operations, persistence, and state updates.
    """

    def __init__(
        self,
        get_now: Callable[[], datetime] | None = None,
    ) -> None:
        """
        Initialize the service.

        Args:
            get_now: Function to get current time (for testing).

        """
        self._get_now = get_now or (lambda: datetime.now(ZoneInfo("UTC")))

    def add_medication(
        self,
        profile: Profile,
        command: AddMedicationCommand,
    ) -> Medication:
        """
        Add a medication to a profile.

        Args:
            profile: The profile to add to.
            command: The add medication command.

        Returns:
            The created medication.

        """
        command.validate()

        # Build schedule spec
        slot_doses = None
        if command.slot_doses:
            slot_doses = {
                k: DoseQuantity.from_dict(v)
                for k, v in command.slot_doses.items()
            }

        default_dose = None
        if command.default_dose:
            default_dose = DoseQuantity.from_dict(command.default_dose)

        # Parse dates
        start_date = None
        if command.start_date:
            from datetime import date
            start_date = date.fromisoformat(command.start_date)

        end_date = None
        if command.end_date:
            from datetime import date
            end_date = date.fromisoformat(command.end_date)

        schedule = ScheduleSpec(
            kind=command.schedule_kind,
            times=command.times,
            weekdays=command.weekdays,
            interval_minutes=command.interval_minutes,
            start_date=start_date,
            end_date=end_date,
            slot_doses=slot_doses,
            default_dose=default_dose,
        )

        # Build policy
        policy = ReminderPolicy()
        if command.policy:
            policy = ReminderPolicy.from_dict(command.policy)

        # Create medication
        medication = Medication.create(
            display_name=command.display_name.strip(),
            schedule=schedule,
            policy=policy,
        )

        # Compute initial state
        self._recompute_state(profile, medication)

        # Add to profile
        profile.add_medication(medication)

        return medication

    def update_medication(
        self,
        profile: Profile,
        command: UpdateMedicationCommand,
    ) -> Medication:
        """
        Update a medication.

        Args:
            profile: The profile containing the medication.
            command: The update command.

        Returns:
            The updated medication.

        Raises:
            MedicationNotFoundError: If medication not found.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        # Update display name
        if command.display_name is not None:
            medication.display_name = command.display_name.strip()
            medication.ref = MedicationRef(
                provider=medication.ref.provider,
                external_id=medication.ref.external_id,
                display_name=medication.display_name,
            )

        # Update schedule
        if command.schedule_updates:
            schedule_dict = medication.schedule.to_dict()
            schedule_dict.update(command.schedule_updates)
            medication.schedule = ScheduleSpec.from_dict(schedule_dict)

        # Update policy
        if command.policy_updates:
            policy_dict = medication.policy.to_dict()
            policy_dict.update(command.policy_updates)
            medication.policy = ReminderPolicy.from_dict(policy_dict)

        # Recompute state
        self._recompute_state(profile, medication)

        return medication

    def remove_medication(
        self,
        profile: Profile,
        medication_id: str,
    ) -> Medication | None:
        """
        Remove a medication from a profile.

        Args:
            profile: The profile.
            medication_id: The medication ID.

        Returns:
            The removed medication or None.

        """
        return profile.remove_medication(medication_id)

    def take(
        self,
        profile: Profile,
        command: TakeCommand,
    ) -> LogRecord:
        """
        Mark a scheduled medication as taken.

        Args:
            profile: The profile.
            command: The take command.

        Returns:
            The log record.

        Raises:
            MedicationNotFoundError: If medication not found.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        now = self._get_now()
        taken_at = command.taken_at or now

        # Determine dose
        if command.dose_override:
            dose = DoseQuantity.from_dict(command.dose_override)
        elif medication.state.next_dose:
            dose = medication.state.next_dose
        elif medication.schedule.default_dose:
            dose = medication.schedule.default_dose
        else:
            dose = DoseQuantity.normalize(1, 1, "dose")

        # Create log record
        log = LogRecord(
            action=LogAction.TAKEN,
            taken_at=taken_at,
            scheduled_for=medication.state.next_due,
            dose=dose,
            slot_key=medication.state.next_slot_key,
        )

        profile.add_log(log)

        # Update medication state
        medication.state.last_taken = taken_at
        medication.state.snooze_until = None

        # Recompute next occurrence
        self._recompute_state(profile, medication)

        return log

    def prn_take(
        self,
        profile: Profile,
        command: PRNTakeCommand,
    ) -> LogRecord:
        """
        Log a PRN (as-needed) intake.

        Args:
            profile: The profile.
            command: The PRN take command.

        Returns:
            The log record.

        Raises:
            MedicationNotFoundError: If medication not found.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        now = self._get_now()
        taken_at = command.taken_at or now
        dose = DoseQuantity.from_dict(command.dose)

        # Create log record with scheduled_for=None (PRN marker)
        meta = {}
        if command.note:
            meta["note"] = command.note

        log = LogRecord(
            action=LogAction.PRN_TAKEN,
            taken_at=taken_at,
            scheduled_for=None,  # PRN has no scheduled time
            dose=dose,
            meta=meta if meta else None,
        )

        profile.add_log(log)

        # Check if PRN affects schedule
        if medication.policy.prn_affects_schedule:
            medication.state.last_taken = taken_at
            self._recompute_state(profile, medication)

        return log

    def snooze(
        self,
        profile: Profile,
        command: SnoozeCommand,
    ) -> datetime:
        """
        Snooze a medication reminder.

        Args:
            profile: The profile.
            command: The snooze command.

        Returns:
            The snooze end time.

        Raises:
            MedicationNotFoundError: If medication not found.
            ValidationError: If medication has no active schedule.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        # Can't snooze PRN-only medications
        if medication.schedule.kind == ScheduleKind.AS_NEEDED:
            msg = "Cannot snooze PRN-only medication"
            raise ValidationError(msg)

        now = self._get_now()

        # Determine snooze end time
        if command.until:
            snooze_until = command.until
        else:
            snooze_until = compute_snooze_until(
                medication.policy, now, command.minutes
            )

        # Create log record
        log = LogRecord(
            action=LogAction.SNOOZED,
            taken_at=now,
            scheduled_for=medication.state.next_due,
            dose=medication.state.next_dose,
            meta={"snooze_until": snooze_until.isoformat()},
        )

        profile.add_log(log)

        # Update state
        medication.state.snooze_until = snooze_until
        medication.state.status = MedicationStatus.SNOOZED

        return snooze_until

    def skip(
        self,
        profile: Profile,
        command: SkipCommand,
    ) -> LogRecord:
        """
        Skip a scheduled dose.

        Args:
            profile: The profile.
            command: The skip command.

        Returns:
            The log record.

        Raises:
            MedicationNotFoundError: If medication not found.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        now = self._get_now()

        # Create log record
        meta = {}
        if command.reason:
            meta["reason"] = command.reason

        log = LogRecord(
            action=LogAction.SKIPPED,
            taken_at=now,
            scheduled_for=medication.state.next_due,
            dose=medication.state.next_dose,
            slot_key=medication.state.next_slot_key,
            meta=meta if meta else None,
        )

        profile.add_log(log)

        # Update state - mark the scheduled slot as taken to move to next slot
        # We use the scheduled time (not current time) so _is_same_slot_taken works
        if medication.state.next_due:
            medication.state.last_taken = medication.state.next_due
        else:
            medication.state.last_taken = now
        medication.state.snooze_until = None

        # Recompute next occurrence
        self._recompute_state(profile, medication)

        return log

    def recompute_all_states(self, profile: Profile) -> None:
        """
        Recompute states for all medications in a profile.

        Args:
            profile: The profile.

        """
        for medication in profile.medications.values():
            self._recompute_state(profile, medication)

    def _recompute_state(self, profile: Profile, medication: Medication) -> None:
        """
        Recompute the state for a medication.

        Args:
            profile: The profile (for timezone).
            medication: The medication.

        """
        now = self._get_now()

        occurrence, status = compute_next_occurrence(
            timezone=profile.timezone,
            schedule=medication.schedule,
            now=now,
            last_taken=medication.state.last_taken,
            snooze_until=medication.state.snooze_until,
            policy=medication.policy,
        )

        if occurrence:
            medication.state.next_due = occurrence.scheduled_for
            medication.state.next_dose = occurrence.dose
            medication.state.next_slot_key = occurrence.slot_key
        else:
            medication.state.next_due = None
            medication.state.next_dose = None
            medication.state.next_slot_key = None

        medication.state.status = status


# ============================================================================
# Helper functions
# ============================================================================


def _is_valid_time(time_str: str) -> bool:
    """Validate time string format (HH:MM)."""
    if not time_str or len(time_str) != 5:
        return False
    try:
        hour, minute = map(int, time_str.split(":"))
        return 0 <= hour <= 23 and 0 <= minute <= 59
    except (ValueError, AttributeError):
        return False


def _validate_dose_dict(dose_dict: dict) -> None:
    """Validate a dose dictionary."""
    required_keys = {"numerator", "denominator", "unit"}
    if not all(k in dose_dict for k in required_keys):
        msg = f"Dose must have {required_keys}"
        raise ValidationError(msg)

    if not isinstance(dose_dict["numerator"], int):
        msg = "Dose numerator must be an integer"
        raise ValidationError(msg)
    if not isinstance(dose_dict["denominator"], int):
        msg = "Dose denominator must be an integer"
        raise ValidationError(msg)
    if dose_dict["denominator"] == 0:
        msg = "Dose denominator cannot be zero"
        raise ValidationError(msg)
    if not isinstance(dose_dict["unit"], str) or not dose_dict["unit"]:
        msg = "Dose unit must be a non-empty string"
        raise ValidationError(msg)
