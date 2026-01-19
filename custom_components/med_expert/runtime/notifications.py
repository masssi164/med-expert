"""
Actionable notifications for medication reminders.

Provides mobile_app notifications with TAKEN, SNOOZE, SKIP buttons.
Handles notification grouping and user-configurable notification targets.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.persistent_notification import (
    async_create as async_create_persistent,
)
from homeassistant.components.persistent_notification import (
    async_dismiss as async_dismiss_persistent,
)

from custom_components.med_expert.const import (
    NOTIFICATION_ACTION_SKIP,
    NOTIFICATION_ACTION_SNOOZE,
    NOTIFICATION_ACTION_TAKEN,
    NOTIFICATION_TAG_PREFIX,
)
from custom_components.med_expert.domain.models import (
    Medication,
    Profile,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages medication notifications.

    Supports both persistent notifications (fallback) and mobile_app
    notifications with actions (TAKEN, SNOOZE, SKIP).
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
    ) -> None:
        """
        Initialize the notification manager.

        Args:
            hass: Home Assistant instance.
            entry_id: Config entry ID.

        """
        self._hass = hass
        self._entry_id = entry_id
        self._active_notifications: dict[str, str] = {}  # medication_id -> tag

    def _get_notification_tag(self, medication_id: str) -> str:
        """Generate a unique notification tag."""
        return f"{NOTIFICATION_TAG_PREFIX}{self._entry_id}_{medication_id}"

    def _get_persistent_id(self, medication_id: str) -> str:
        """Generate persistent notification ID."""
        return f"med_expert_{self._entry_id}_{medication_id}"

    async def async_send_due_notification(
        self,
        profile: Profile,
        medication: Medication,
    ) -> None:
        """
        Send a medication due notification.

        Uses mobile_app notify if target is configured, otherwise
        falls back to persistent notification.

        Args:
            profile: The medication profile.
            medication: The medication that is due.

        """
        settings = profile.notification_settings
        dose_str = ""
        if medication.state.next_dose:
            dose_str = f" ({medication.state.next_dose.format()})"

        message = f"Time to take {medication.display_name}{dose_str}"
        title = "Medication Reminder"

        # Try mobile_app notification first if target is configured
        if settings and settings.notify_target:
            await self._send_actionable_notification(
                profile=profile,
                medication=medication,
                title=title,
                message=message,
                is_missed=False,
            )
        else:
            # Fallback to persistent notification
            await self._send_persistent_notification(
                medication=medication,
                title=title,
                message=message,
            )

    async def async_send_missed_notification(
        self,
        profile: Profile,
        medication: Medication,
    ) -> None:
        """
        Send a medication missed notification.

        Args:
            profile: The medication profile.
            medication: The medication that was missed.

        """
        settings = profile.notification_settings
        dose_str = ""
        if medication.state.next_dose:
            dose_str = f" ({medication.state.next_dose.format()})"

        message = f"MISSED: {medication.display_name}{dose_str}"
        title = "Medication Missed"

        if settings and settings.notify_target:
            await self._send_actionable_notification(
                profile=profile,
                medication=medication,
                title=title,
                message=message,
                is_missed=True,
            )
        else:
            await self._send_persistent_notification(
                medication=medication,
                title=title,
                message=message,
            )

    async def async_dismiss_notification(
        self,
        medication_id: str,
    ) -> None:
        """
        Dismiss notification for a medication.

        Args:
            medication_id: The medication ID.

        """
        # Dismiss persistent notification
        persistent_id = self._get_persistent_id(medication_id)
        async_dismiss_persistent(self._hass, persistent_id)

        # Remove from tracking
        self._active_notifications.pop(medication_id, None)

        _LOGGER.debug("Dismissed notification for medication %s", medication_id)

    async def async_dismiss_all(self) -> None:
        """Dismiss all active notifications."""
        for medication_id in list(self._active_notifications.keys()):
            await self.async_dismiss_notification(medication_id)

    async def _send_actionable_notification(
        self,
        profile: Profile,
        medication: Medication,
        title: str,
        message: str,
        is_missed: bool = False,
    ) -> None:
        """
        Send an actionable notification via mobile_app.

        Args:
            profile: The medication profile.
            medication: The medication.
            title: Notification title.
            message: Notification message.
            is_missed: Whether this is a missed notification.

        """
        settings = profile.notification_settings
        if not settings or not settings.notify_target:
            return

        tag = self._get_notification_tag(medication.medication_id)
        self._active_notifications[medication.medication_id] = tag

        # Build notification data
        data: dict[str, Any] = {
            "tag": tag,
            "group": f"med_expert_{profile.profile_id}"
            if settings.group_notifications
            else None,
            "data": {
                "tag": tag,
                "persistent": True,
                "sticky": True,
                # Action data for handling the response
                "medication_id": medication.medication_id,
                "profile_id": profile.profile_id,
                "entry_id": self._entry_id,
            },
        }

        # Add actions if enabled
        if settings.include_actions:
            data["data"]["actions"] = self._build_actions(
                medication.medication_id,
                profile.profile_id,
                is_missed,
            )

        # Use custom template if available
        if is_missed and settings.missed_template:
            message = settings.missed_template.format(
                medication=medication.display_name,
                dose=medication.state.next_dose.format()
                if medication.state.next_dose
                else "",
            )
        elif not is_missed and settings.reminder_template:
            message = settings.reminder_template.format(
                medication=medication.display_name,
                dose=medication.state.next_dose.format()
                if medication.state.next_dose
                else "",
            )

        # Determine notify target
        # Target should be like "mobile_app_my_phone" -> service "notify.mobile_app_my_phone"
        service_target = settings.notify_target
        if not service_target.startswith("notify."):
            service_target = f"notify.{service_target}"

        try:
            # Call the notify service
            domain, service = service_target.split(".", 1)
            await self._hass.services.async_call(
                domain,
                service,
                {
                    "title": title,
                    "message": message,
                    **data,
                },
                blocking=False,
            )
            _LOGGER.debug(
                "Sent actionable notification to %s for %s",
                service_target,
                medication.display_name,
            )
        except Exception:
            _LOGGER.exception(
                "Failed to send notification to %s, falling back to persistent",
                service_target,
            )
            # Fallback to persistent notification
            await self._send_persistent_notification(
                medication=medication,
                title=title,
                message=message,
            )

    def _build_actions(
        self,
        medication_id: str,
        profile_id: str,
        is_missed: bool,
    ) -> list[dict[str, Any]]:
        """
        Build notification actions for iOS/Android.

        Args:
            medication_id: The medication ID.
            profile_id: The profile ID.
            is_missed: Whether this is a missed notification.

        Returns:
            List of action definitions.

        """
        actions = [
            {
                "action": NOTIFICATION_ACTION_TAKEN,
                "title": "✓ Taken",
                "uri": None,
            },
            {
                "action": NOTIFICATION_ACTION_SNOOZE,
                "title": "⏰ Snooze",
                "uri": None,
            },
        ]

        # Only show skip for non-missed notifications
        if not is_missed:
            actions.append(
                {
                    "action": NOTIFICATION_ACTION_SKIP,
                    "title": "⏭ Skip",
                    "uri": None,
                }
            )

        return actions

    async def _send_persistent_notification(
        self,
        medication: Medication,
        title: str,
        message: str,
    ) -> None:
        """
        Send a persistent notification (fallback).

        Args:
            medication: The medication.
            title: Notification title.
            message: Notification message.

        """
        notification_id = self._get_persistent_id(medication.medication_id)
        self._active_notifications[medication.medication_id] = notification_id

        async_create_persistent(
            self._hass,
            message,
            title=title,
            notification_id=notification_id,
        )

        _LOGGER.debug(
            "Sent persistent notification for %s",
            medication.display_name,
        )

    async def async_send_low_inventory_notification(
        self,
        profile: Profile,
        medication: Medication,
    ) -> None:
        """
        Send a low inventory warning notification.

        Args:
            profile: The medication profile.
            medication: The medication with low inventory.

        """
        if not medication.inventory:
            return

        settings = profile.notification_settings
        message = (
            f"Low stock: {medication.display_name} - "
            f"{medication.inventory.current_quantity} {medication.inventory.unit} remaining"
        )
        title = "Medication Low Stock"

        if settings and settings.notify_target:
            service_target = settings.notify_target
            if not service_target.startswith("notify."):
                service_target = f"notify.{service_target}"

            try:
                domain, service = service_target.split(".", 1)
                await self._hass.services.async_call(
                    domain,
                    service,
                    {
                        "title": title,
                        "message": message,
                        "data": {
                            "tag": f"{NOTIFICATION_TAG_PREFIX}inventory_{medication.medication_id}",
                            "persistent": False,
                        },
                    },
                    blocking=False,
                )
            except Exception:
                _LOGGER.exception("Failed to send low inventory notification")
                # Fallback
                async_create_persistent(
                    self._hass,
                    message,
                    title=title,
                    notification_id=f"med_expert_inventory_{medication.medication_id}",
                )
        else:
            async_create_persistent(
                self._hass,
                message,
                title=title,
                notification_id=f"med_expert_inventory_{medication.medication_id}",
            )
