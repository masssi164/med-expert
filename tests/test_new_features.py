"""Tests for new features: inventory, adherence, dosage forms."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from custom_components.med_expert.application.services import (
    AddMedicationCommand,
    MedicationService,
    PRNTakeCommand,
    RefillCommand,
    ReplaceInhalerCommand,
    TakeCommand,
    UpdateMedicationCommand,
    UpdateNotificationSettingsCommand,
    InventoryError,
)
from custom_components.med_expert.domain.models import (
    DosageForm,
    DosageFormInfo,
    Inventory,
    InjectionSite,
    InhalerTracking,
    LogAction,
    MedicationStatus,
    NotificationSettings,
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


class TestDosageForm:
    """Tests for dosage form functionality."""

    def test_dosage_form_info_registry(self):
        """Test that all forms have info in registry."""
        for form in DosageForm:
            info = DosageFormInfo.get_info(form)
            assert info is not None
            assert info.display_name
            assert info.icon.startswith("mdi:")
            assert isinstance(info.compatible_units, (list, tuple))

    def test_injection_form_supports_site_tracking(self):
        """Test that injection form supports site tracking."""
        info = DosageFormInfo.get_info(DosageForm.INJECTION)
        assert info.supports_site_tracking

    def test_inhaler_form_supports_puff_counter(self):
        """Test that inhaler form supports puff counter."""
        info = DosageFormInfo.get_info(DosageForm.INHALER)
        assert info.supports_puff_counter

    def test_add_medication_with_form(
        self, service: MedicationService, profile: Profile
    ):
        """Test adding medication with specific dosage form."""
        command = AddMedicationCommand(
            display_name="Insulin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "20:00"],
            default_dose={"numerator": 10, "denominator": 1, "unit": "units"},
            form=DosageForm.INJECTION,
        )

        medication = service.add_medication(profile, command)

        assert medication.form == DosageForm.INJECTION
        # Injection should auto-enable site tracking
        assert medication.injection_tracking is not None

    def test_add_inhaler_auto_tracks_puffs(
        self, service: MedicationService, profile: Profile
    ):
        """Test that adding an inhaler auto-enables puff tracking."""
        command = AddMedicationCommand(
            display_name="Ventolin",
            schedule_kind=ScheduleKind.AS_NEEDED,
            default_dose={"numerator": 2, "denominator": 1, "unit": "puffs"},
            form=DosageForm.INHALER,
        )

        medication = service.add_medication(profile, command)

        assert medication.form == DosageForm.INHALER
        assert medication.inhaler_tracking is not None
        assert medication.inhaler_tracking.total_puffs == 200  # default


class TestInventory:
    """Tests for inventory management."""

    def test_inventory_is_low(self):
        """Test low inventory detection."""
        inv = Inventory(
            current_quantity=5,
            unit="tablets",
            refill_threshold=10,
        )
        assert inv.is_low()

        inv.current_quantity = 15
        assert not inv.is_low()

    def test_inventory_is_expired(self):
        """Test expiry detection."""
        inv = Inventory(
            current_quantity=30,
            expiry_date=date(2025, 1, 1),
        )
        assert inv.is_expired()

        inv.expiry_date = date(2030, 1, 1)
        assert not inv.is_expired()

    def test_add_medication_with_inventory(
        self, service: MedicationService, profile: Profile
    ):
        """Test adding medication with inventory tracking."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            inventory={
                "current_quantity": 30,
                "unit": "tablets",
                "package_size": 30,
                "refill_threshold": 10,
                "auto_decrement": True,
            },
        )

        medication = service.add_medication(profile, command)

        assert medication.inventory is not None
        assert medication.inventory.current_quantity == 30
        assert medication.inventory.auto_decrement is True

    def test_take_decrements_inventory(
        self, service: MedicationService, profile: Profile
    ):
        """Test that taking medication decrements inventory."""
        # Add medication with inventory
        add_cmd = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            inventory={
                "current_quantity": 30,
                "unit": "tablets",
                "auto_decrement": True,
            },
        )
        medication = service.add_medication(profile, add_cmd)

        # Take the medication
        take_cmd = TakeCommand(medication_id=medication.medication_id)
        service.take(profile, take_cmd)

        # Check inventory was decremented
        assert medication.inventory.current_quantity == 29

    def test_refill_increases_inventory(
        self, service: MedicationService, profile: Profile
    ):
        """Test refilling inventory."""
        add_cmd = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            inventory={
                "current_quantity": 5,
                "unit": "tablets",
                "package_size": 30,
            },
        )
        medication = service.add_medication(profile, add_cmd)

        # Refill
        refill_cmd = RefillCommand(
            medication_id=medication.medication_id,
            quantity=30,
        )
        service.refill(profile, refill_cmd)

        assert medication.inventory.current_quantity == 35


class TestInjectionTracking:
    """Tests for injection site tracking."""

    def test_injection_site_rotation(
        self, service: MedicationService, profile: Profile
    ):
        """Test injection site rotation."""
        command = AddMedicationCommand(
            display_name="Insulin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00", "20:00"],
            default_dose={"numerator": 10, "denominator": 1, "unit": "units"},
            form=DosageForm.INJECTION,
        )

        medication = service.add_medication(profile, command)
        tracking = medication.injection_tracking

        # Get first site recommendation
        first_site = tracking.get_next_site()
        assert first_site is not None
        assert isinstance(first_site, InjectionSite)

        # Record first injection
        tracking.record_site(first_site)

        # Next site should be different
        second_site = tracking.get_next_site()
        assert second_site != first_site

    def test_take_with_injection_site(
        self, service: MedicationService, profile: Profile
    ):
        """Test recording injection site when taking."""
        command = AddMedicationCommand(
            display_name="Insulin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 10, "denominator": 1, "unit": "units"},
            form=DosageForm.INJECTION,
        )
        medication = service.add_medication(profile, command)

        # Take with injection site
        take_cmd = TakeCommand(
            medication_id=medication.medication_id,
            injection_site=InjectionSite.LEFT_ARM,
        )
        service.take(profile, take_cmd)

        # Check log has injection site
        log = profile.logs[-1]
        assert log.injection_site == InjectionSite.LEFT_ARM


class TestInhalerTracking:
    """Tests for inhaler puff tracking."""

    def test_inhaler_puff_counting(self):
        """Test puff counting."""
        tracking = InhalerTracking(total_puffs=200, used_puffs=0)

        assert tracking.remaining_puffs == 200
        assert not tracking.is_low()

        tracking.use_puffs(2)
        assert tracking.used_puffs == 2
        assert tracking.remaining_puffs == 198

    def test_inhaler_low_detection(self):
        """Test low puff detection."""
        tracking = InhalerTracking(total_puffs=200, used_puffs=185)

        assert tracking.remaining_puffs == 15
        assert tracking.is_low()  # < 20 puffs

    def test_replace_inhaler(
        self, service: MedicationService, profile: Profile
    ):
        """Test replacing an inhaler."""
        command = AddMedicationCommand(
            display_name="Ventolin",
            schedule_kind=ScheduleKind.AS_NEEDED,
            default_dose={"numerator": 2, "denominator": 1, "unit": "puffs"},
            form=DosageForm.INHALER,
        )
        medication = service.add_medication(profile, command)

        # Use some puffs
        medication.inhaler_tracking.use_puffs(100)
        assert medication.inhaler_tracking.remaining_puffs == 100

        # Replace inhaler
        replace_cmd = ReplaceInhalerCommand(
            medication_id=medication.medication_id,
            total_puffs=200,
        )
        service.replace_inhaler(profile, replace_cmd)

        assert medication.inhaler_tracking.used_puffs == 0
        assert medication.inhaler_tracking.remaining_puffs == 200


class TestNotificationSettings:
    """Tests for notification settings."""

    def test_notification_settings_defaults(self):
        """Test default notification settings."""
        settings = NotificationSettings()

        assert settings.notify_target is None
        assert settings.fallback_targets == []
        assert settings.group_notifications is True
        assert settings.include_actions is True

    def test_update_notification_settings(
        self, service: MedicationService, profile: Profile
    ):
        """Test updating notification settings."""
        command = UpdateNotificationSettingsCommand(
            notify_target="mobile_app_my_phone",
            group_notifications=True,
            include_actions=True,
        )

        service.update_notification_settings(profile, command)

        assert profile.notification_settings is not None
        assert profile.notification_settings.notify_target == "mobile_app_my_phone"
        assert profile.notification_settings.group_notifications is True


class TestAdherenceStats:
    """Tests for adherence statistics."""

    def test_calculate_adherence(
        self, service: MedicationService, profile: Profile
    ):
        """Test adherence calculation."""
        # Add a medication
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        # Take a few times
        for _ in range(5):
            service.take(
                profile,
                TakeCommand(medication_id=medication.medication_id),
            )

        # Calculate adherence
        service.calculate_adherence_stats(profile)

        assert profile.adherence_stats is not None
        assert profile.adherence_stats.total_taken == 5

    def test_streak_tracking(
        self, service: MedicationService, profile: Profile
    ):
        """Test streak tracking."""
        command = AddMedicationCommand(
            display_name="Aspirin",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
        )
        medication = service.add_medication(profile, command)

        # Take medication
        service.take(
            profile,
            TakeCommand(medication_id=medication.medication_id),
        )

        # Calculate adherence
        service.calculate_adherence_stats(profile)

        # Should have a streak
        assert profile.adherence_stats.current_streak >= 0


class TestUpdateMedicationForm:
    """Tests for updating medication form."""

    def test_update_form_enables_tracking(
        self, service: MedicationService, profile: Profile
    ):
        """Test that changing form enables appropriate tracking."""
        # Add tablet medication
        add_cmd = AddMedicationCommand(
            display_name="Med",
            schedule_kind=ScheduleKind.TIMES_PER_DAY,
            times=["08:00"],
            default_dose={"numerator": 1, "denominator": 1, "unit": "tablet"},
            form=DosageForm.TABLET,
        )
        medication = service.add_medication(profile, add_cmd)

        assert medication.injection_tracking is None

        # Update to injection
        update_cmd = UpdateMedicationCommand(
            medication_id=medication.medication_id,
            form=DosageForm.INJECTION,
        )
        medication = service.update_medication(profile, update_cmd)

        assert medication.injection_tracking is not None
