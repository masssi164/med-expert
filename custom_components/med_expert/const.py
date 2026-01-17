"""Constants for med_expert."""

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "med_expert"

# Config keys
CONF_PROFILE_NAME: Final = "profile_name"
CONF_TIMEZONE: Final = "timezone"

# Default values
DEFAULT_GRACE_MINUTES: Final = 30
DEFAULT_SNOOZE_MINUTES: Final = 10

# Status values
STATUS_OK: Final = "ok"
STATUS_DUE: Final = "due"
STATUS_SNOOZED: Final = "snoozed"
STATUS_MISSED: Final = "missed"
STATUS_PRN: Final = "prn"

# Log actions
ACTION_TAKEN: Final = "taken"
ACTION_PRN_TAKEN: Final = "prn_taken"
ACTION_SNOOZED: Final = "snoozed"
ACTION_SKIPPED: Final = "skipped"
ACTION_MISSED: Final = "missed"

# Schedule kinds
SCHEDULE_TIMES_PER_DAY: Final = "times_per_day"
SCHEDULE_INTERVAL: Final = "interval"
SCHEDULE_WEEKLY: Final = "weekly"
SCHEDULE_AS_NEEDED: Final = "as_needed"

# Store
STORE_KEY: Final = "med_expert_data"
STORE_VERSION: Final = 1
