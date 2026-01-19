"""
Domain models for med_expert.

Pure domain logic with no Home Assistant dependencies.
Uses rational numbers for doses to avoid float rounding errors.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from math import gcd
from typing import ClassVar
from zoneinfo import ZoneInfo


class ScheduleKind(str, Enum):
    """Types of medication schedules."""

    TIMES_PER_DAY = "times_per_day"
    INTERVAL = "interval"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"
    DEPOT = "depot"  # Long-acting injections with appointment tracking


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
    REFILLED = "refilled"


class DosageForm(str, Enum):
    """Dosage forms with associated metadata."""

    TABLET = "tablet"
    CAPSULE = "capsule"
    INJECTION = "injection"
    NASAL_SPRAY = "nasal_spray"
    INHALER = "inhaler"
    DROPS = "drops"
    CREAM = "cream"
    PATCH = "patch"
    SUPPOSITORY = "suppository"
    LIQUID = "liquid"
    POWDER = "powder"
    OTHER = "other"


class InjectionSite(str, Enum):
    """Injection sites for tracking rotation."""

    LEFT_ARM = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_THIGH = "left_thigh"
    RIGHT_THIGH = "right_thigh"
    ABDOMEN_LEFT = "abdomen_left"
    ABDOMEN_RIGHT = "abdomen_right"
    LEFT_BUTTOCK = "left_buttock"
    RIGHT_BUTTOCK = "right_buttock"


@dataclass(frozen=True)
class DosageFormInfo:
    """Metadata for a dosage form."""

    form: DosageForm
    display_name: str
    icon: str
    compatible_units: tuple[str, ...]
    supports_site_tracking: bool = False
    supports_puff_counter: bool = False

    # Registry of all dosage form info
    REGISTRY: ClassVar[dict[DosageForm, DosageFormInfo]] = {}

    @classmethod
    def get(cls, form: DosageForm) -> DosageFormInfo:
        """Get info for a dosage form."""
        return cls.REGISTRY.get(form, cls.REGISTRY[DosageForm.OTHER])

    @classmethod
    def get_info(cls, form: DosageForm) -> DosageFormInfo:
        """Get info for a dosage form (alias for get)."""
        return cls.get(form)

    @classmethod
    def get_compatible_units(cls, form: DosageForm) -> tuple[str, ...]:
        """Get compatible units for a dosage form."""
        return cls.get(form).compatible_units


# Initialize dosage form registry
DosageFormInfo.REGISTRY = {
    DosageForm.TABLET: DosageFormInfo(
        form=DosageForm.TABLET,
        display_name="Tablet",
        icon="mdi:pill",
        compatible_units=("tablet", "mg", "g", "mcg"),
    ),
    DosageForm.CAPSULE: DosageFormInfo(
        form=DosageForm.CAPSULE,
        display_name="Capsule",
        icon="mdi:pill",
        compatible_units=("capsule", "mg", "g"),
    ),
    DosageForm.INJECTION: DosageFormInfo(
        form=DosageForm.INJECTION,
        display_name="Injection",
        icon="mdi:needle",
        compatible_units=("ml", "IU", "mg", "mcg", "unit"),
        supports_site_tracking=True,
    ),
    DosageForm.NASAL_SPRAY: DosageFormInfo(
        form=DosageForm.NASAL_SPRAY,
        display_name="Nasal Spray",
        icon="mdi:spray",
        compatible_units=("spray", "puff", "mcg"),
        supports_puff_counter=True,
    ),
    DosageForm.INHALER: DosageFormInfo(
        form=DosageForm.INHALER,
        display_name="Inhaler",
        icon="mdi:lungs",
        compatible_units=("puff", "mcg", "mg"),
        supports_puff_counter=True,
    ),
    DosageForm.DROPS: DosageFormInfo(
        form=DosageForm.DROPS,
        display_name="Drops",
        icon="mdi:water",
        compatible_units=("drop", "ml", "mg"),
    ),
    DosageForm.CREAM: DosageFormInfo(
        form=DosageForm.CREAM,
        display_name="Cream/Ointment",
        icon="mdi:lotion",
        compatible_units=("application", "g", "mg"),
    ),
    DosageForm.PATCH: DosageFormInfo(
        form=DosageForm.PATCH,
        display_name="Transdermal Patch",
        icon="mdi:bandage",
        compatible_units=("patch", "mcg/h", "mg"),
    ),
    DosageForm.SUPPOSITORY: DosageFormInfo(
        form=DosageForm.SUPPOSITORY,
        display_name="Suppository",
        icon="mdi:pill",
        compatible_units=("suppository", "mg"),
    ),
    DosageForm.LIQUID: DosageFormInfo(
        form=DosageForm.LIQUID,
        display_name="Liquid/Syrup",
        icon="mdi:bottle-tonic",
        compatible_units=("ml", "teaspoon", "tablespoon", "mg"),
    ),
    DosageForm.POWDER: DosageFormInfo(
        form=DosageForm.POWDER,
        display_name="Powder",
        icon="mdi:powder",
        compatible_units=("sachet", "g", "mg", "scoop"),
    ),
    DosageForm.OTHER: DosageFormInfo(
        form=DosageForm.OTHER,
        display_name="Other",
        icon="mdi:medical-bag",
        compatible_units=("unit", "dose", "application", "mg", "ml", "g"),
    ),
}


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
        new_num = (
            self.numerator * other.denominator + other.numerator * self.denominator
        )
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
            slot_doses = {
                k: DoseQuantity.from_dict(v) for k, v in data["slot_doses"].items()
            }

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
            "snooze_until": self.snooze_until.isoformat()
            if self.snooze_until
            else None,
            "last_taken": self.last_taken.isoformat() if self.last_taken else None,
            "status": self.status.value,
            "last_notified_at": self.last_notified_at.isoformat()
            if self.last_notified_at
            else None,
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
    medication_id: str | None = None  # Added for per-medication log filtering
    scheduled_for: datetime | None = None  # None for PRN
    dose: DoseQuantity | None = None
    slot_key: str | None = None
    injection_site: InjectionSite | None = None  # For injection tracking
    meta: dict | None = None  # additional context (reason, note, etc.)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "action": self.action.value,
            "taken_at": self.taken_at.isoformat(),
            "scheduled_for": self.scheduled_for.isoformat()
            if self.scheduled_for
            else None,
            "dose": self.dose.to_dict() if self.dose else None,
            "slot_key": self.slot_key,
            "meta": self.meta,
        }
        if self.medication_id:
            result["medication_id"] = self.medication_id
        if self.injection_site:
            result["injection_site"] = self.injection_site.value
        return result

    @classmethod
    def from_dict(
        cls, data: dict, default_dose: DoseQuantity | None = None
    ) -> LogRecord:
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

        injection_site = None
        if data.get("injection_site"):
            injection_site = InjectionSite(data["injection_site"])

        return cls(
            action=LogAction(data["action"]),
            taken_at=datetime.fromisoformat(data["taken_at"]),
            medication_id=data.get("medication_id"),
            scheduled_for=scheduled_for,
            dose=dose,
            slot_key=data.get("slot_key"),
            injection_site=injection_site,
            meta=data.get("meta"),
        )


@dataclass
class Inventory:
    """Inventory tracking for a medication."""

    current_quantity: int = 0
    unit: str = "unit"
    package_size: int | None = None
    refill_threshold: int = 7  # Warn when quantity falls below this
    auto_decrement: bool = True  # Automatically decrease on take
    last_refill: date | None = None
    expiry_date: date | None = None
    pharmacy_name: str | None = None
    pharmacy_phone: str | None = None
    notes: str | None = None

    def decrement(self, amount: int = 1) -> None:
        """Decrease inventory by amount."""
        self.current_quantity = max(0, self.current_quantity - amount)

    def refill(self, amount: int | None = None) -> None:
        """Refill inventory."""
        if amount is not None:
            self.current_quantity += amount
        elif self.package_size:
            self.current_quantity += self.package_size
        self.last_refill = date.today()

    def needs_refill(self) -> bool:
        """Check if refill is needed."""
        return self.current_quantity <= self.refill_threshold

    def is_low(self) -> bool:
        """Check if inventory is low (alias for needs_refill)."""
        return self.needs_refill()

    def is_expired(self) -> bool:
        """Check if medication is expired."""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "current_quantity": self.current_quantity,
            "unit": self.unit,
            "package_size": self.package_size,
            "refill_threshold": self.refill_threshold,
            "auto_decrement": self.auto_decrement,
            "last_refill": self.last_refill.isoformat() if self.last_refill else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "pharmacy_name": self.pharmacy_name,
            "pharmacy_phone": self.pharmacy_phone,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Inventory:
        """Create from dictionary."""
        last_refill = None
        if data.get("last_refill"):
            last_refill = date.fromisoformat(data["last_refill"])

        expiry_date = None
        if data.get("expiry_date"):
            expiry_date = date.fromisoformat(data["expiry_date"])

        return cls(
            current_quantity=data.get("current_quantity", 0),
            unit=data.get("unit", "unit"),
            package_size=data.get("package_size"),
            refill_threshold=data.get("refill_threshold", 7),
            auto_decrement=data.get("auto_decrement", True),
            last_refill=last_refill,
            expiry_date=expiry_date,
            pharmacy_name=data.get("pharmacy_name"),
            pharmacy_phone=data.get("pharmacy_phone"),
            notes=data.get("notes"),
        )


@dataclass
class InjectionTracking:
    """Tracking for injection site rotation."""

    sites: list[InjectionSite] = field(default_factory=lambda: list(InjectionSite))
    last_site: InjectionSite | None = None
    rotation_enabled: bool = True

    def get_next_site(self) -> InjectionSite | None:
        """Get the next recommended injection site in rotation."""
        if not self.sites or not self.rotation_enabled:
            return None

        if self.last_site is None:
            return self.sites[0]

        try:
            current_index = self.sites.index(self.last_site)
            next_index = (current_index + 1) % len(self.sites)
            return self.sites[next_index]
        except ValueError:
            return self.sites[0]

    def record_site(self, site: InjectionSite) -> None:
        """Record that a site was used."""
        self.last_site = site

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "sites": [s.value for s in self.sites],
            "last_site": self.last_site.value if self.last_site else None,
            "rotation_enabled": self.rotation_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> InjectionTracking:
        """Create from dictionary."""
        sites = [InjectionSite(s) for s in data.get("sites", [])]
        if not sites:
            sites = list(InjectionSite)

        last_site = None
        if data.get("last_site"):
            last_site = InjectionSite(data["last_site"])

        return cls(
            sites=sites,
            last_site=last_site,
            rotation_enabled=data.get("rotation_enabled", True),
        )


@dataclass
class InhalerTracking:
    """Tracking for inhaler puff counter."""

    total_puffs: int = 200  # Total puffs in device
    used_puffs: int = 0
    low_threshold: int = 20  # Warn when remaining puffs fall below this

    @property
    def remaining_puffs(self) -> int:
        """Get remaining puffs."""
        return max(0, self.total_puffs - self.used_puffs)

    def use_puffs(self, count: int = 1) -> None:
        """Record puff usage."""
        self.used_puffs = min(self.total_puffs, self.used_puffs + count)

    def is_low(self) -> bool:
        """Check if inhaler is running low."""
        return self.remaining_puffs <= self.low_threshold

    def replace(self, total_puffs: int | None = None) -> None:
        """Replace with new inhaler."""
        if total_puffs is not None:
            self.total_puffs = total_puffs
        self.used_puffs = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "total_puffs": self.total_puffs,
            "used_puffs": self.used_puffs,
            "low_threshold": self.low_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict) -> InhalerTracking:
        """Create from dictionary."""
        return cls(
            total_puffs=data.get("total_puffs", 200),
            used_puffs=data.get("used_puffs", 0),
            low_threshold=data.get("low_threshold", 20),
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
    # New fields for enhanced functionality
    form: DosageForm | None = None
    default_unit: str | None = None
    inventory: Inventory | None = None
    injection_tracking: InjectionTracking | None = None
    inhaler_tracking: InhalerTracking | None = None
    # Interaction warnings (simple MVP approach)
    interaction_warnings: list[dict] | None = (
        None  # [{medication_id, min_interval_hours, warning}]
    )
    # User notes
    notes: str | None = None
    # Active flag for soft-delete or pause
    is_active: bool = True

    @classmethod
    def create(
        cls,
        display_name: str,
        schedule: ScheduleSpec,
        ref: MedicationRef | None = None,
        policy: ReminderPolicy | None = None,
        form: DosageForm | None = None,
        default_unit: str | None = None,
        inventory: Inventory | None = None,
    ) -> Medication:
        """Create a new medication with a generated ID."""
        medication_id = str(uuid.uuid4())
        if ref is None:
            ref = MedicationRef(
                provider="manual",
                external_id=medication_id,
                display_name=display_name,
            )

        # Auto-configure tracking based on form
        injection_tracking = None
        inhaler_tracking = None
        if form:
            form_info = DosageFormInfo.get(form)
            if form_info.supports_site_tracking:
                injection_tracking = InjectionTracking()
            if form_info.supports_puff_counter:
                inhaler_tracking = InhalerTracking()

            # Set default unit from form if not provided
            if default_unit is None and form_info.compatible_units:
                default_unit = form_info.compatible_units[0]

        return cls(
            medication_id=medication_id,
            display_name=display_name,
            ref=ref,
            schedule=schedule,
            policy=policy or ReminderPolicy(),
            form=form,
            default_unit=default_unit,
            inventory=inventory,
            injection_tracking=injection_tracking,
            inhaler_tracking=inhaler_tracking,
        )

    def get_icon(self) -> str:
        """Get the icon for this medication based on its form."""
        if self.form:
            return DosageFormInfo.get(self.form).icon
        return "mdi:pill"

    def get_compatible_units(self) -> tuple[str, ...]:
        """Get compatible units for this medication's form."""
        if self.form:
            return DosageFormInfo.get(self.form).compatible_units
        return ("unit", "dose", "mg", "ml", "tablet")

    def get_effective_unit(self, dose: DoseQuantity | None = None) -> str:
        """Get the effective unit for a dose, falling back to default_unit."""
        if dose and dose.unit:
            return dose.unit
        if self.default_unit:
            return self.default_unit
        if self.schedule.default_dose:
            return self.schedule.default_dose.unit
        return "unit"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "medication_id": self.medication_id,
            "display_name": self.display_name,
            "ref": self.ref.to_dict(),
            "schedule": self.schedule.to_dict(),
            "policy": self.policy.to_dict(),
            "state": self.state.to_dict(),
            "is_active": self.is_active,
        }
        if self.form:
            result["form"] = self.form.value
        if self.default_unit:
            result["default_unit"] = self.default_unit
        if self.inventory:
            result["inventory"] = self.inventory.to_dict()
        if self.injection_tracking:
            result["injection_tracking"] = self.injection_tracking.to_dict()
        if self.inhaler_tracking:
            result["inhaler_tracking"] = self.inhaler_tracking.to_dict()
        if self.interaction_warnings:
            result["interaction_warnings"] = self.interaction_warnings
        if self.notes:
            result["notes"] = self.notes
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Medication:
        """Create from dictionary."""
        form = None
        if data.get("form"):
            form = DosageForm(data["form"])

        inventory = None
        if data.get("inventory"):
            inventory = Inventory.from_dict(data["inventory"])

        injection_tracking = None
        if data.get("injection_tracking"):
            injection_tracking = InjectionTracking.from_dict(data["injection_tracking"])

        inhaler_tracking = None
        if data.get("inhaler_tracking"):
            inhaler_tracking = InhalerTracking.from_dict(data["inhaler_tracking"])

        return cls(
            medication_id=data["medication_id"],
            display_name=data["display_name"],
            ref=MedicationRef.from_dict(data["ref"]),
            schedule=ScheduleSpec.from_dict(data["schedule"]),
            policy=ReminderPolicy.from_dict(data.get("policy", {})),
            state=MedicationState.from_dict(data.get("state", {})),
            form=form,
            default_unit=data.get("default_unit"),
            inventory=inventory,
            injection_tracking=injection_tracking,
            inhaler_tracking=inhaler_tracking,
            interaction_warnings=data.get("interaction_warnings"),
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
        )


@dataclass
class NotificationSettings:
    """Settings for notifications."""

    # Primary notification target (e.g., "notify.mobile_app_iphone")
    notify_target: str | None = None
    # Fallback targets
    fallback_targets: list[str] = field(default_factory=list)
    # Group notifications when multiple meds are due at same time
    group_notifications: bool = True
    # Include action buttons in notifications
    include_actions: bool = True
    # Custom notification title template
    title_template: str | None = None
    # Custom notification message template
    message_template: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "notify_target": self.notify_target,
            "fallback_targets": self.fallback_targets,
            "group_notifications": self.group_notifications,
            "include_actions": self.include_actions,
            "title_template": self.title_template,
            "message_template": self.message_template,
        }

    @classmethod
    def from_dict(cls, data: dict) -> NotificationSettings:
        """Create from dictionary."""
        return cls(
            notify_target=data.get("notify_target"),
            fallback_targets=data.get("fallback_targets"),
            group_notifications=data.get("group_notifications", True),
            include_actions=data.get("include_actions", True),
            title_template=data.get("title_template"),
            message_template=data.get("message_template"),
        )


@dataclass
class AdherenceStats:
    """Adherence statistics for a profile."""

    # Calculated adherence rates
    daily_rate: float = 0.0
    weekly_rate: float = 0.0
    monthly_rate: float = 0.0
    # Streak tracking
    current_streak: int = 0
    longest_streak: int = 0
    last_streak_date: date | None = None
    # Problem detection
    most_missed_slot: str | None = None
    most_missed_medication: str | None = None
    most_missed_medication_id: str | None = None
    # Totals for tracking
    total_taken: int = 0
    total_missed: int = 0
    total_skipped: int = 0
    # Last calculation time
    last_calculated: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "daily_rate": self.daily_rate,
            "weekly_rate": self.weekly_rate,
            "monthly_rate": self.monthly_rate,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_streak_date": self.last_streak_date.isoformat()
            if self.last_streak_date
            else None,
            "most_missed_slot": self.most_missed_slot,
            "most_missed_medication": self.most_missed_medication,
            "most_missed_medication_id": self.most_missed_medication_id,
            "total_taken": self.total_taken,
            "total_missed": self.total_missed,
            "total_skipped": self.total_skipped,
            "last_calculated": self.last_calculated.isoformat()
            if self.last_calculated
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AdherenceStats:
        """Create from dictionary."""
        last_streak_date = None
        if data.get("last_streak_date"):
            last_streak_date = date.fromisoformat(data["last_streak_date"])

        last_calculated = None
        if data.get("last_calculated"):
            last_calculated = datetime.fromisoformat(data["last_calculated"])

        return cls(
            daily_rate=data.get("daily_rate", 0.0),
            weekly_rate=data.get("weekly_rate", 0.0),
            monthly_rate=data.get("monthly_rate", 0.0),
            current_streak=data.get("current_streak", 0),
            longest_streak=data.get("longest_streak", 0),
            last_streak_date=last_streak_date,
            most_missed_slot=data.get("most_missed_slot"),
            most_missed_medication=data.get("most_missed_medication"),
            most_missed_medication_id=data.get("most_missed_medication_id"),
            total_taken=data.get("total_taken", 0),
            total_missed=data.get("total_missed", 0),
            total_skipped=data.get("total_skipped", 0),
            last_calculated=last_calculated,
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
    # New fields
    notification_settings: NotificationSettings = field(
        default_factory=NotificationSettings
    )
    adherence_stats: AdherenceStats = field(default_factory=AdherenceStats)
    # User metadata
    owner_name: str | None = None  # For multi-user display
    avatar: str | None = None  # Icon or image reference

    @classmethod
    def create(
        cls,
        name: str,
        timezone: str,
        default_policy: ReminderPolicy | None = None,
        notification_settings: NotificationSettings | None = None,
        owner_name: str | None = None,
    ) -> Profile:
        """Create a new profile with a generated ID."""
        return cls(
            profile_id=str(uuid.uuid4()),
            name=name,
            timezone=timezone,
            default_policy=default_policy or ReminderPolicy(),
            notification_settings=notification_settings or NotificationSettings(),
            owner_name=owner_name,
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
        filtered = [log for log in self.logs if log.medication_id == medication_id]
        if limit:
            filtered = filtered[-limit:]
        return filtered

    def get_recent_logs(
        self, days: int = 7, limit: int | None = None
    ) -> list[LogRecord]:
        """Get recent log records within the specified number of days."""
        tz = ZoneInfo(self.timezone)
        cutoff = datetime.now(tz) - timedelta(days=days)
        recent = [log for log in self.logs if log.taken_at >= cutoff]
        if limit:
            recent = recent[-limit:]
        return recent

    def calculate_adherence(self, days: int = 30) -> float:
        """
        Calculate adherence rate for the specified number of days.

        Returns percentage (0-100) of taken vs expected doses.
        """
        tz = ZoneInfo(self.timezone)
        cutoff = datetime.now(tz) - timedelta(days=days)
        taken_count = sum(
            1
            for log in self.logs
            if log.taken_at >= cutoff
            and log.action in (LogAction.TAKEN, LogAction.PRN_TAKEN)
        )
        expected_count = sum(
            1
            for log in self.logs
            if log.taken_at >= cutoff
            and log.action
            in (
                LogAction.TAKEN,
                LogAction.PRN_TAKEN,
                LogAction.SKIPPED,
                LogAction.MISSED,
            )
        )
        if expected_count == 0:
            return 100.0
        return round((taken_count / expected_count) * 100, 1)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "profile_id": self.profile_id,
            "name": self.name,
            "timezone": self.timezone,
            "medications": {k: v.to_dict() for k, v in self.medications.items()},
            "logs": [log.to_dict() for log in self.logs],
            "default_policy": self.default_policy.to_dict(),
            "notification_settings": self.notification_settings.to_dict(),
            "adherence_stats": self.adherence_stats.to_dict(),
        }
        if self.owner_name:
            result["owner_name"] = self.owner_name
        if self.avatar:
            result["avatar"] = self.avatar
        return result

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

        notification_settings = NotificationSettings()
        if data.get("notification_settings"):
            notification_settings = NotificationSettings.from_dict(
                data["notification_settings"]
            )

        adherence_stats = AdherenceStats()
        if data.get("adherence_stats"):
            adherence_stats = AdherenceStats.from_dict(data["adherence_stats"])

        return cls(
            profile_id=data["profile_id"],
            name=data["name"],
            timezone=data["timezone"],
            medications=medications,
            logs=logs,
            default_policy=ReminderPolicy.from_dict(data.get("default_policy", {})),
            notification_settings=notification_settings,
            adherence_stats=adherence_stats,
            owner_name=data.get("owner_name"),
            avatar=data.get("avatar"),
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
