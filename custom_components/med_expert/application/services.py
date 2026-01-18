"""
Application services for med_expert.

Contains use cases, commands, and DTOs for medication management.
Coordinates between domain models, repository, and providers.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from custom_components.med_expert.domain.models import (
    AdherenceStats,
    DosageForm,
    DosageFormInfo,
    DoseQuantity,
    InhalerTracking,
    InjectionSite,
    InjectionTracking,
    Inventory,
    LogAction,
    LogRecord,
    Medication,
    MedicationRef,
    MedicationStatus,
    NotificationSettings,
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



class InventoryError(MedicationServiceError):
    """Raised when there's an inventory-related error."""



class UnitCompatibilityError(ValidationError):
    """Raised when a unit is incompatible with a dosage form."""



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
    # New fields
    form: str | None = None  # DosageForm value
    default_unit: str | None = None
    inventory: dict | None = None  # Inventory fields
    notes: str | None = None
    interaction_warnings: list[dict] | None = None

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

        elif self.schedule_kind == ScheduleKind.DEPOT:
            if not self.interval_minutes or self.interval_minutes <= 0:
                msg = "Positive interval_minutes is required for depot schedule"
                raise ValidationError(msg)

        # Validate form and unit compatibility
        if self.form:
            try:
                dosage_form = DosageForm(self.form)
                compatible_units = DosageFormInfo.get_compatible_units(dosage_form)
                if self.default_unit and self.default_unit not in compatible_units:
                    msg = f"Unit '{self.default_unit}' is not compatible with form '{self.form}'. Compatible units: {compatible_units}"
                    raise UnitCompatibilityError(msg)
            except ValueError:
                msg = f"Invalid dosage form: {self.form}"
                raise ValidationError(msg) from None

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
    # New fields
    form: str | None = None
    default_unit: str | None = None
    inventory_updates: dict | None = None
    notes: str | None = None
    is_active: bool | None = None
    interaction_warnings: list[dict] | None = None


@dataclass
class TakeCommand:
    """Command to mark a medication as taken."""

    medication_id: str
    taken_at: datetime | None = None
    dose_override: dict | None = None  # {numerator, denominator, unit}
    injection_site: str | None = None  # For injection tracking


@dataclass
class PRNTakeCommand:
    """Command to log a PRN (as-needed) intake."""

    medication_id: str
    dose: dict  # {numerator, denominator, unit}
    taken_at: datetime | None = None
    note: str | None = None
    injection_site: str | None = None  # For injection tracking


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


@dataclass
class RefillCommand:
    """Command to refill medication inventory."""

    medication_id: str
    quantity: int | None = None  # If None, use package_size
    expiry_date: str | None = None  # ISO format


@dataclass
class UpdateInventoryCommand:
    """Command to update inventory settings."""

    medication_id: str
    current_quantity: int | None = None
    package_size: int | None = None
    refill_threshold: int | None = None
    auto_decrement: bool | None = None
    expiry_date: str | None = None  # ISO format
    pharmacy_name: str | None = None
    pharmacy_phone: str | None = None
    notes: str | None = None


@dataclass
class ReplaceInhalerCommand:
    """Command to replace an inhaler."""

    medication_id: str
    total_puffs: int | None = None  # If None, use previous total


@dataclass
class UpdateNotificationSettingsCommand:
    """Command to update profile notification settings."""

    notify_target: str | None = None
    fallback_targets: list[str] | None = None
    group_notifications: bool | None = None
    include_actions: bool | None = None
    title_template: str | None = None
    message_template: str | None = None


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

        # Parse form
        form = None
        if command.form:
            form = DosageForm(command.form)

        # Build inventory
        inventory = None
        if command.inventory:
            inventory = Inventory.from_dict(command.inventory)

        # Create medication with new fields
        medication = Medication.create(
            display_name=command.display_name.strip(),
            schedule=schedule,
            policy=policy,
            form=form,
            default_unit=command.default_unit,
            inventory=inventory,
        )

        # Set additional fields
        if command.notes:
            medication.notes = command.notes
        if command.interaction_warnings:
            medication.interaction_warnings = command.interaction_warnings

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

        # Update form
        if command.form is not None:
            medication.form = DosageForm(command.form) if command.form else None
            # Auto-configure tracking based on new form
            if medication.form:
                form_info = DosageFormInfo.get(medication.form)
                if form_info.supports_site_tracking and not medication.injection_tracking:
                    medication.injection_tracking = InjectionTracking()
                if form_info.supports_puff_counter and not medication.inhaler_tracking:
                    medication.inhaler_tracking = InhalerTracking()

        # Update default unit
        if command.default_unit is not None:
            medication.default_unit = command.default_unit

        # Update inventory
        if command.inventory_updates:
            if medication.inventory is None:
                medication.inventory = Inventory()
            inv = medication.inventory
            updates = command.inventory_updates
            if "current_quantity" in updates:
                inv.current_quantity = updates["current_quantity"]
            if "package_size" in updates:
                inv.package_size = updates["package_size"]
            if "refill_threshold" in updates:
                inv.refill_threshold = updates["refill_threshold"]
            if "auto_decrement" in updates:
                inv.auto_decrement = updates["auto_decrement"]
            if "expiry_date" in updates:
                inv.expiry_date = date.fromisoformat(updates["expiry_date"]) if updates["expiry_date"] else None
            if "pharmacy_name" in updates:
                inv.pharmacy_name = updates["pharmacy_name"]
            if "pharmacy_phone" in updates:
                inv.pharmacy_phone = updates["pharmacy_phone"]
            if "notes" in updates:
                inv.notes = updates["notes"]

        # Update notes
        if command.notes is not None:
            medication.notes = command.notes

        # Update active status
        if command.is_active is not None:
            medication.is_active = command.is_active

        # Update interaction warnings
        if command.interaction_warnings is not None:
            medication.interaction_warnings = command.interaction_warnings

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
            # Use default_unit from medication or fallback
            unit = medication.default_unit or "dose"
            dose = DoseQuantity.normalize(1, 1, unit)

        # Handle injection site tracking
        injection_site = None
        if command.injection_site:
            injection_site = InjectionSite(command.injection_site)
        elif medication.injection_tracking and medication.injection_tracking.rotation_enabled:
            injection_site = medication.injection_tracking.get_next_site()

        # Create log record with medication_id for filtering
        log = LogRecord(
            action=LogAction.TAKEN,
            taken_at=taken_at,
            medication_id=command.medication_id,
            scheduled_for=medication.state.next_due,
            dose=dose,
            slot_key=medication.state.next_slot_key,
            injection_site=injection_site,
        )

        profile.add_log(log)

        # Update injection tracking
        if injection_site and medication.injection_tracking:
            medication.injection_tracking.record_site(injection_site)

        # Update inventory
        if medication.inventory and medication.inventory.auto_decrement:
            # Decrement by dose amount (use numerator/denominator for fractional)
            decrement_amount = max(1, int(dose.to_float()))
            medication.inventory.decrement(decrement_amount)

        # Update inhaler tracking
        if medication.inhaler_tracking and dose.unit in ("puff", "spray"):
            medication.inhaler_tracking.use_puffs(int(dose.to_float()))

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

        # Handle injection site tracking
        injection_site = None
        if command.injection_site:
            injection_site = InjectionSite(command.injection_site)
        elif medication.injection_tracking and medication.injection_tracking.rotation_enabled:
            injection_site = medication.injection_tracking.get_next_site()

        # Create log record with scheduled_for=None (PRN marker)
        meta = {}
        if command.note:
            meta["note"] = command.note

        log = LogRecord(
            action=LogAction.PRN_TAKEN,
            taken_at=taken_at,
            medication_id=command.medication_id,
            scheduled_for=None,  # PRN has no scheduled time
            dose=dose,
            injection_site=injection_site,
            meta=meta if meta else None,
        )

        profile.add_log(log)

        # Update injection tracking
        if injection_site and medication.injection_tracking:
            medication.injection_tracking.record_site(injection_site)

        # Update inventory
        if medication.inventory and medication.inventory.auto_decrement:
            decrement_amount = max(1, int(dose.to_float()))
            medication.inventory.decrement(decrement_amount)

        # Update inhaler tracking
        if medication.inhaler_tracking and dose.unit in ("puff", "spray"):
            medication.inhaler_tracking.use_puffs(int(dose.to_float()))

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

    def refill(
        self,
        profile: Profile,
        command: RefillCommand,
    ) -> LogRecord:
        """
        Refill medication inventory.

        Args:
            profile: The profile.
            command: The refill command.

        Returns:
            The log record.

        Raises:
            MedicationNotFoundError: If medication not found.
            InventoryError: If medication has no inventory configured.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        if medication.inventory is None:
            medication.inventory = Inventory()

        # Perform refill
        medication.inventory.refill(command.quantity)

        # Update expiry date if provided
        if command.expiry_date:
            medication.inventory.expiry_date = date.fromisoformat(command.expiry_date)

        now = self._get_now()

        # Create log record
        log = LogRecord(
            action=LogAction.REFILLED,
            taken_at=now,
            medication_id=command.medication_id,
            meta={
                "quantity": command.quantity or medication.inventory.package_size,
                "new_total": medication.inventory.current_quantity,
            },
        )

        profile.add_log(log)

        return log

    def replace_inhaler(
        self,
        profile: Profile,
        command: ReplaceInhalerCommand,
    ) -> None:
        """
        Replace an inhaler with a new one.

        Args:
            profile: The profile.
            command: The replace command.

        Raises:
            MedicationNotFoundError: If medication not found.
            ValidationError: If medication is not an inhaler.

        """
        medication = profile.get_medication(command.medication_id)
        if medication is None:
            msg = f"Medication {command.medication_id} not found"
            raise MedicationNotFoundError(msg)

        if medication.inhaler_tracking is None:
            msg = "Medication is not configured for inhaler tracking"
            raise ValidationError(msg)

        medication.inhaler_tracking.replace(command.total_puffs)

    def update_notification_settings(
        self,
        profile: Profile,
        command: UpdateNotificationSettingsCommand,
    ) -> None:
        """
        Update profile notification settings.

        Args:
            profile: The profile.
            command: The update command.

        """
        settings = profile.notification_settings

        if command.notify_target is not None:
            settings.notify_target = command.notify_target
        if command.fallback_targets is not None:
            settings.fallback_targets = command.fallback_targets
        if command.group_notifications is not None:
            settings.group_notifications = command.group_notifications
        if command.include_actions is not None:
            settings.include_actions = command.include_actions
        if command.title_template is not None:
            settings.title_template = command.title_template
        if command.message_template is not None:
            settings.message_template = command.message_template

    def calculate_adherence_stats(self, profile: Profile) -> AdherenceStats:
        """
        Calculate adherence statistics for a profile.

        Args:
            profile: The profile.

        Returns:
            Updated adherence stats.

        """
        now = self._get_now()
        stats = profile.adherence_stats

        # Calculate rates
        stats.daily_rate = profile.calculate_adherence(days=1)
        stats.weekly_rate = profile.calculate_adherence(days=7)
        stats.monthly_rate = profile.calculate_adherence(days=30)

        # Count totals (last 30 days)
        cutoff = now - timedelta(days=30)
        stats.total_taken = sum(
            1 for log in profile.logs
            if log.taken_at >= cutoff and log.action in (LogAction.TAKEN, LogAction.PRN_TAKEN)
        )
        stats.total_missed = sum(
            1 for log in profile.logs
            if log.taken_at >= cutoff and log.action == LogAction.MISSED
        )
        stats.total_skipped = sum(
            1 for log in profile.logs
            if log.taken_at >= cutoff and log.action == LogAction.SKIPPED
        )

        # Calculate streak
        stats.current_streak = self._calculate_current_streak(profile)
        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak

        # Find most missed slot
        stats.most_missed_slot = self._find_most_missed_slot(profile)
        most_missed_med_id = self._find_most_missed_medication(profile)
        stats.most_missed_medication_id = most_missed_med_id
        if most_missed_med_id:
            med = profile.get_medication(most_missed_med_id)
            stats.most_missed_medication = med.display_name if med else None

        stats.last_calculated = now

        return stats

    def _calculate_current_streak(self, profile: Profile) -> int:
        """Calculate the current consecutive days streak of taking all medications."""
        if not profile.logs:
            return 0

        today = self._get_now().date()
        streak = 0
        current_date = today

        # Group logs by date and check if all scheduled meds were taken
        scheduled_meds = [
            med for med in profile.medications.values()
            if med.schedule.kind != ScheduleKind.AS_NEEDED and med.is_active
        ]

        if not scheduled_meds:
            return 0

        for days_back in range(365):  # Max 1 year
            check_date = today - timedelta(days=days_back)
            logs_for_date = [
                log for log in profile.logs
                if log.taken_at.date() == check_date
                and log.action == LogAction.TAKEN
            ]

            # Check if all scheduled meds have at least one taken log
            med_ids_taken = {log.medication_id for log in logs_for_date if log.medication_id}

            # Simplified check: if any medication was taken, count the day
            # A more sophisticated version would check against expected doses
            if med_ids_taken:
                streak += 1
            else:
                break

        return streak

    def _find_most_missed_slot(self, profile: Profile) -> str | None:
        """Find the time slot with the most missed doses."""
        from collections import Counter

        missed_slots = [
            log.slot_key for log in profile.logs
            if log.action == LogAction.MISSED and log.slot_key
        ]

        if not missed_slots:
            return None

        counter = Counter(missed_slots)
        return counter.most_common(1)[0][0]

    def _find_most_missed_medication(self, profile: Profile) -> str | None:
        """Find the medication with the most missed doses."""
        from collections import Counter

        missed_meds = [
            log.medication_id for log in profile.logs
            if log.action == LogAction.MISSED and log.medication_id
        ]

        if not missed_meds:
            return None

        counter = Counter(missed_meds)
        return counter.most_common(1)[0][0]

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
