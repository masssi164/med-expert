"""
Domain models for med_expert.

Pure domain logic with no Home Assistant dependencies.
Uses rational numbers for doses to avoid float rounding errors.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from math import gcd


class ScheduleKind(str, Enum):
    """Types of medication schedules."""

    TIMES_PER_DAY = "times_per_day"
    INTERVAL = "interval"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


class MedicationStatus(str, Enum):
    """Status of a medication."""

    OK = "ok"
    DUE = "due"
    SNOOZED = "snoozed"
    MISSED = "missed"
    PRN = "prn"  # as-needed only medication


class LogAction(str, Enum):
    """Actions that can be logged."""

    TAKEN = "taken"
    PRN_TAKEN = "prn_taken"
    SNOOZED = "snoozed"
    SKIPPED = "skipped"
    MISSED = "missed"


@dataclass(frozen=True)
class DoseQuantity:
    """
    Represents a dose as a rational number to avoid float rounding errors.

    Examples:
        - 1 tablet: DoseQuantity(1, 1, "tablet")
        - 1/2 tablet: DoseQuantity(1, 2, "tablet")
        - 1/4 tablet: DoseQuantity(1, 4, "tablet")
        - 2.5 ml: DoseQuantity(5, 2, "ml")

    """

    numerator: int
    denominator: int
    unit: str

    def __post_init__(self) -> None:
        """Validate and normalize the dose."""
        if self.denominator == 0:
            msg = "Denominator cannot be zero"
            raise ValueError(msg)
        if self.numerator < 0 or self.denominator < 0:
            msg = "Numerator and denominator must be non-negative"
            raise ValueError(msg)

    @classmethod
    def normalize(cls, numerator: int, denominator: int, unit: str) -> DoseQuantity:
        """Create a normalized dose quantity (reduce to lowest terms)."""
        if denominator == 0:
            msg = "Denominator cannot be zero"
            raise ValueError(msg)
        if numerator == 0:
            return cls(0, 1, unit)

        divisor = gcd(abs(numerator), abs(denominator))
        return cls(numerator // divisor, denominator // divisor, unit)

    def format(self) -> str:
        """
        Format the dose as a human-readable string.

        Examples:
            - "1 tablet"
            - "1/2 tablet"
            - "1/4 ml"

        """
        if self.denominator == 1:
            return f"{self.numerator} {self.unit}"
        return f"{self.numerator}/{self.denominator} {self.unit}"

    def to_float(self) -> float:
        """Convert to float (for display/comparison only, not for calculations)."""
        return self.numerator / self.denominator

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "numerator": self.numerator,
            "denominator": self.denominator,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DoseQuantity:
        """Create from dictionary."""
        return cls.normalize(
            numerator=data["numerator"],
            denominator=data["denominator"],
            unit=data["unit"],
        )

    def __add__(self, other: DoseQuantity) -> DoseQuantity:
        """Add two doses (must have same unit)."""
        if self.unit != other.unit:
            msg = f"Cannot add doses with different units: {self.unit} vs {other.unit}"
            raise ValueError(msg)
        new_num = self.numerator * other.denominator + other.numerator * self.denominator
        new_denom = self.denominator * other.denominator
        return DoseQuantity.normalize(new_num, new_denom, self.unit)


@dataclass(frozen=True)
class MedicationRef:
    """Reference to a medication in an external system."""

    provider: str  # e.g., "manual", "rxnorm", "openfda"
    external_id: str
    display_name: str

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "provider": self.provider,
            "external_id": self.external_id,
            "display_name": self.display_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MedicationRef:
        """Create from dictionary."""
        return cls(
            provider=data["provider"],
            external_id=data["external_id"],
            display_name=data["display_name"],
        )


@dataclass
class ScheduleSpec:
    """
    Specification for when a medication should be taken.

    For times_per_day:
        - times: ["08:00", "12:00", "20:00"]
        - slot_doses: {"08:00": DoseQuantity, "12:00": DoseQuantity, ...}

    For weekly:
        - weekdays: [0, 2, 4]  # Monday, Wednesday, Friday (0=Monday)
        - times: ["08:00"]
        - slot_doses: {"W0-08:00": DoseQuantity, "W2-08:00": DoseQuantity, ...}

    For interval:
        - interval_minutes: 480  # every 8 hours
        - anchor: datetime  # when to start counting from
        - default_dose: DoseQuantity

    For as_needed:
        - No times, just PRN with default_dose
    """

    kind: ScheduleKind
    times: list[str] | None = None  # ["HH:MM", ...]
    weekdays: list[int] | None = None  # [0-6] for Monday-Sunday
    interval_minutes: int | None = None
    anchor: datetime | None = None
    start_date: date | None = None
    end_date: date | None = None
    slot_doses: dict[str, DoseQuantity] | None = None  # key -> dose
    default_dose: DoseQuantity | None = None

    def get_dose_for_slot(self, slot_key: str) -> DoseQuantity | None:
        """Get the dose for a specific slot."""
        if self.slot_doses and slot_key in self.slot_doses:
            return self.slot_doses[slot_key]
        return self.default_dose

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result: dict = {"kind": self.kind.value}
        if self.times is not None:
            result["times"] = self.times
        if self.weekdays is not None:
            result["weekdays"] = self.weekdays
        if self.interval_minutes is not None:
            result["interval_minutes"] = self.interval_minutes
        if self.anchor is not None:
            result["anchor"] = self.anchor.isoformat()
        if self.start_date is not None:
            result["start_date"] = self.start_date.isoformat()
        if self.end_date is not None:
            result["end_date"] = self.end_date.isoformat()
        if self.slot_doses is not None:
            result["slot_doses"] = {k: v.to_dict() for k, v in self.slot_doses.items()}
        if self.default_dose is not None:
            result["default_dose"] = self.default_dose.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> ScheduleSpec:
        """Create from dictionary."""
        slot_doses = None
        if data.get("slot_doses"):
            slot_doses = {k: DoseQuantity.from_dict(v) for k, v in data["slot_doses"].items()}

        default_dose = None
        if data.get("default_dose"):
            default_dose = DoseQuantity.from_dict(data["default_dose"])

        anchor = None
        if data.get("anchor"):
            anchor = datetime.fromisoformat(data["anchor"])

        start_date = None
        if data.get("start_date"):
            start_date = date.fromisoformat(data["start_date"])

        end_date = None
        if data.get("end_date"):
            end_date = date.fromisoformat(data["end_date"])

        return cls(
            kind=ScheduleKind(data["kind"]),
            times=data.get("times"),
            weekdays=data.get("weekdays"),
            interval_minutes=data.get("interval_minutes"),
            anchor=anchor,
            start_date=start_date,
            end_date=end_date,
            slot_doses=slot_doses,
            default_dose=default_dose,
        )


@dataclass
class ReminderPolicy:
    """Policy for reminders and scheduling behavior."""

    grace_minutes: int = 30  # time after due before marking as missed
    snooze_minutes: int = 10  # default snooze duration
    prn_affects_schedule: bool = False  # whether PRN intake affects next scheduled dose
    repeat_minutes: int | None = None  # repeat reminder interval (None = no repeat)
    max_retries: int | None = None  # max reminder repeats
    quiet_hours_start: str | None = None  # "HH:MM" format
    quiet_hours_end: str | None = None  # "HH:MM" format

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "grace_minutes": self.grace_minutes,
            "snooze_minutes": self.snooze_minutes,
            "prn_affects_schedule": self.prn_affects_schedule,
            "repeat_minutes": self.repeat_minutes,
            "max_retries": self.max_retries,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ReminderPolicy:
        """Create from dictionary."""
        return cls(
            grace_minutes=data.get("grace_minutes", 30),
            snooze_minutes=data.get("snooze_minutes", 10),
            prn_affects_schedule=data.get("prn_affects_schedule", False),
            repeat_minutes=data.get("repeat_minutes"),
            max_retries=data.get("max_retries"),
            quiet_hours_start=data.get("quiet_hours_start"),
            quiet_hours_end=data.get("quiet_hours_end"),
        )


@dataclass
class MedicationState:
    """Current state of a medication."""

    next_due: datetime | None = None
    next_dose: DoseQuantity | None = None
    next_slot_key: str | None = None
    snooze_until: datetime | None = None
    last_taken: datetime | None = None
    status: MedicationStatus = MedicationStatus.OK
    last_notified_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "next_due": self.next_due.isoformat() if self.next_due else None,
            "next_dose": self.next_dose.to_dict() if self.next_dose else None,
            "next_slot_key": self.next_slot_key,
            "snooze_until": self.snooze_until.isoformat() if self.snooze_until else None,
            "last_taken": self.last_taken.isoformat() if self.last_taken else None,
            "status": self.status.value,
            "last_notified_at": self.last_notified_at.isoformat() if self.last_notified_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MedicationState:
        """Create from dictionary."""
        next_due = None
        if data.get("next_due"):
            next_due = datetime.fromisoformat(data["next_due"])

        next_dose = None
        if data.get("next_dose"):
            next_dose = DoseQuantity.from_dict(data["next_dose"])

        snooze_until = None
        if data.get("snooze_until"):
            snooze_until = datetime.fromisoformat(data["snooze_until"])

        last_taken = None
        if data.get("last_taken"):
            last_taken = datetime.fromisoformat(data["last_taken"])

        last_notified_at = None
        if data.get("last_notified_at"):
            last_notified_at = datetime.fromisoformat(data["last_notified_at"])

        return cls(
            next_due=next_due,
            next_dose=next_dose,
            next_slot_key=data.get("next_slot_key"),
            snooze_until=snooze_until,
            last_taken=last_taken,
            status=MedicationStatus(data.get("status", "ok")),
            last_notified_at=last_notified_at,
        )


@dataclass
class LogRecord:
    """Record of a medication-related action."""

    action: LogAction
    taken_at: datetime
    scheduled_for: datetime | None = None  # None for PRN
    dose: DoseQuantity | None = None
    slot_key: str | None = None
    meta: dict | None = None  # additional context (reason, note, etc.)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "action": self.action.value,
            "taken_at": self.taken_at.isoformat(),
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "dose": self.dose.to_dict() if self.dose else None,
            "slot_key": self.slot_key,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict, default_dose: DoseQuantity | None = None) -> LogRecord:
        """
        Create from dictionary.

        Args:
            data: The dictionary to create from.
            default_dose: Default dose to use if dose is missing (for migration).

        """
        scheduled_for = None
        if data.get("scheduled_for"):
            scheduled_for = datetime.fromisoformat(data["scheduled_for"])

        dose = default_dose
        if data.get("dose"):
            dose = DoseQuantity.from_dict(data["dose"])

        return cls(
            action=LogAction(data["action"]),
            taken_at=datetime.fromisoformat(data["taken_at"]),
            scheduled_for=scheduled_for,
            dose=dose,
            slot_key=data.get("slot_key"),
            meta=data.get("meta"),
        )


@dataclass
class Medication:
    """A medication with its schedule and current state."""

    medication_id: str
    display_name: str
    ref: MedicationRef
    schedule: ScheduleSpec
    policy: ReminderPolicy = field(default_factory=ReminderPolicy)
    state: MedicationState = field(default_factory=MedicationState)

    @classmethod
    def create(
        cls,
        display_name: str,
        schedule: ScheduleSpec,
        ref: MedicationRef | None = None,
        policy: ReminderPolicy | None = None,
    ) -> Medication:
        """Create a new medication with a generated ID."""
        medication_id = str(uuid.uuid4())
        if ref is None:
            ref = MedicationRef(
                provider="manual",
                external_id=medication_id,
                display_name=display_name,
            )
        return cls(
            medication_id=medication_id,
            display_name=display_name,
            ref=ref,
            schedule=schedule,
            policy=policy or ReminderPolicy(),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "medication_id": self.medication_id,
            "display_name": self.display_name,
            "ref": self.ref.to_dict(),
            "schedule": self.schedule.to_dict(),
            "policy": self.policy.to_dict(),
            "state": self.state.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Medication:
        """Create from dictionary."""
        return cls(
            medication_id=data["medication_id"],
            display_name=data["display_name"],
            ref=MedicationRef.from_dict(data["ref"]),
            schedule=ScheduleSpec.from_dict(data["schedule"]),
            policy=ReminderPolicy.from_dict(data.get("policy", {})),
            state=MedicationState.from_dict(data.get("state", {})),
        )


@dataclass
class Profile:
    """
    A medication profile (aggregate root).

    One profile per config entry. Contains multiple medications and their logs.
    """

    profile_id: str
    name: str
    timezone: str
    medications: dict[str, Medication] = field(default_factory=dict)
    logs: list[LogRecord] = field(default_factory=list)
    default_policy: ReminderPolicy = field(default_factory=ReminderPolicy)

    @classmethod
    def create(
        cls,
        name: str,
        timezone: str,
        default_policy: ReminderPolicy | None = None,
    ) -> Profile:
        """Create a new profile with a generated ID."""
        return cls(
            profile_id=str(uuid.uuid4()),
            name=name,
            timezone=timezone,
            default_policy=default_policy or ReminderPolicy(),
        )

    def add_medication(self, medication: Medication) -> None:
        """Add a medication to this profile."""
        self.medications[medication.medication_id] = medication

    def remove_medication(self, medication_id: str) -> Medication | None:
        """Remove a medication from this profile."""
        return self.medications.pop(medication_id, None)

    def get_medication(self, medication_id: str) -> Medication | None:
        """Get a medication by ID."""
        return self.medications.get(medication_id)

    def add_log(self, log: LogRecord) -> None:
        """Add a log record."""
        self.logs.append(log)

    def get_logs_for_medication(
        self, medication_id: str, limit: int | None = None
    ) -> list[LogRecord]:
        """Get log records for a specific medication."""
        # Logs don't have medication_id, so we'd need to add that
        # For now, return all logs (this is a simplification)
        logs = self.logs
        if limit:
            logs = logs[-limit:]
        return logs

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "timezone": self.timezone,
            "medications": {k: v.to_dict() for k, v in self.medications.items()},
            "logs": [log.to_dict() for log in self.logs],
            "default_policy": self.default_policy.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Profile:
        """Create from dictionary."""
        medications = {}
        for med_id, med_data in data.get("medications", {}).items():
            medications[med_id] = Medication.from_dict(med_data)

        # Get default dose for log migration
        default_dose = None
        if medications:
            first_med = next(iter(medications.values()))
            default_dose = first_med.schedule.default_dose

        logs = []
        for log_data in data.get("logs", []):
            logs.append(LogRecord.from_dict(log_data, default_dose))

        return cls(
            profile_id=data["profile_id"],
            name=data["name"],
            timezone=data["timezone"],
            medications=medications,
            logs=logs,
            default_policy=ReminderPolicy.from_dict(data.get("default_policy", {})),
        )


@dataclass(frozen=True)
class Occurrence:
    """
    A single scheduled occurrence of a medication.

    Represents when a dose is due to be taken.
    """

    scheduled_for: datetime
    dose: DoseQuantity
    slot_key: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "scheduled_for": self.scheduled_for.isoformat(),
            "dose": self.dose.to_dict(),
            "slot_key": self.slot_key,
        }
