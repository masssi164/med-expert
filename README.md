# Med Expert

**Home Assistant Custom Integration for Medication Management**

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Med Expert is a Home Assistant custom integration that helps you manage medication reminders and track intake history. Create profiles with multiple medications, set flexible schedules, and never miss a dose.

> ⚠️ **DISCLAIMER**: This is **not a medical device**. Med Expert provides reminders and logging only. It does **not** provide dosage advice or medical recommendations. Always follow your healthcare provider's instructions.

## Features

- 📋 **Multiple Profiles**: Create separate profiles for different people or use cases
- 💊 **Multiple Medications per Profile**: Manage all medications in one place
- 🎨 **Frontend Panel**: Beautiful TypeScript-based UI panel for medication management
- ⏰ **Flexible Schedules**: 
  - `times_per_day`: Specific times (8:00, 12:00, 20:00)
  - `interval`: Every X hours
  - `weekly`: Specific days and times
  - `as_needed`: PRN/on-demand medications
- 💉 **Variable Doses**: Different doses for each time slot (e.g., 1 tablet morning, ½ tablet evening)
- 🔢 **Rational Doses**: No float rounding errors (uses fractions: 1, ½, ¼)
- 💊 **Dosage Forms**: Tablet, capsule, injection, inhaler, drops, patch, cream, and more
- 📦 **Inventory Tracking**: Track stock levels with auto-decrement and low-stock warnings
- 💉 **Injection Site Rotation**: Smart rotation for injection-based medications
- 🌬️ **Inhaler Puff Counter**: Track remaining puffs in inhalers
- 📊 **Adherence Analytics**: Track daily/weekly/monthly adherence rates and streaks
- 🔔 **Actionable Notifications**: TAKEN/SNOOZE/SKIP buttons on mobile notifications
- 📱 **Configurable Notifications**: Set your preferred notification target (mobile_app, etc.)
- 🆘 **PRN Logging**: Log as-needed doses outside the schedule
- 😴 **Snooze**: Delay reminders temporarily
- ⏭️ **Skip**: Skip a dose with optional reason
- 🕐 **DST-Safe**: Handles daylight saving time transitions correctly
- 📊 **History Logging**: Complete intake history with doses and timestamps

## What's New in v0.2.0

### Dosage Forms with Compatible Units
Each medication can now have a specific form (tablet, capsule, injection, inhaler, etc.) with form-specific icons and compatible units.

### Inventory Management
- Track current stock levels
- Auto-decrement on take
- Low-stock warnings
- Expiry date tracking
- Pharmacy contact info

### Adherence Tracking
- Daily, weekly, and monthly adherence rates
- Current and longest streak tracking
- Most-missed slot and medication identification

### Actionable Mobile Notifications
- TAKEN, SNOOZE, SKIP buttons on notifications
- Configurable notification targets per profile
- Notification grouping support

### Injection Site Rotation
Smart site rotation for insulin and other injectable medications.

### Inhaler Tracking
Track remaining puffs in inhalers with low-puff warnings.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → Custom repositories
3. Add this repository URL as an Integration
4. Search for "Med Expert" and install
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/med_expert` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Creating a Profile

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Med Expert**
4. Enter a profile name (e.g., "My Medications")
5. Click **Submit**

### Adding Medications

Use the `med_expert.add_medication` service:

```yaml
service: med_expert.add_medication
data:
  entry_id: "your_config_entry_id"
  display_name: "Aspirin"
  schedule_kind: "times_per_day"
  times:
    - "08:00"
    - "20:00"
  slot_doses:
    "08:00":
      numerator: 1
      denominator: 1
      unit: "tablet"
    "20:00":
      numerator: 1
      denominator: 2
      unit: "tablet"
```

## Schedule Types

### times_per_day

Take medication at specific times each day:

```yaml
schedule_kind: "times_per_day"
times:
  - "08:00"
  - "12:00"
  - "20:00"
slot_doses:
  "08:00":
    numerator: 1
    denominator: 1
    unit: "tablet"
  "12:00":
    numerator: 1
    denominator: 2
    unit: "tablet"
  "20:00":
    numerator: 1
    denominator: 1
    unit: "tablet"
```

### interval

Take medication every X minutes:

```yaml
schedule_kind: "interval"
interval_minutes: 480  # Every 8 hours
default_dose:
  numerator: 1
  denominator: 1
  unit: "capsule"
```

### weekly

Take medication on specific days:

```yaml
schedule_kind: "weekly"
weekdays:
  - 0  # Monday
  - 3  # Thursday
times:
  - "09:00"
slot_doses:
  "W0-09:00":
    numerator: 1
    denominator: 1
    unit: "tablet"
  "W3-09:00":
    numerator: 1
    denominator: 1
    unit: "tablet"
```

### as_needed (PRN)

Medication taken as needed, no scheduled times:

```yaml
schedule_kind: "as_needed"
default_dose:
  numerator: 1
  denominator: 1
  unit: "tablet"
```

## Dose Format

Doses use rational numbers (fractions) to avoid float precision issues:

| Dose | numerator | denominator | Display |
|------|-----------|-------------|---------|
| 1 tablet | 1 | 1 | "1 tablet" |
| ½ tablet | 1 | 2 | "1/2 tablet" |
| ¼ tablet | 1 | 4 | "1/4 tablet" |
| 2 tablets | 2 | 1 | "2 tablet" |
| 1½ tablets | 3 | 2 | "3/2 tablet" |

## Entities

For each medication, the following entities are created:

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.<medication>_next_due` | Next scheduled time (timestamp) |
| `sensor.<medication>_status` | Current status (ok/due/snoozed/missed/prn) |
| `sensor.<medication>_next_dose` | Formatted next dose (e.g., "1/2 tablet") |

### Buttons

| Entity | Description |
|--------|-------------|
| `button.<medication>_take` | Mark as taken |
| `button.<medication>_snooze` | Snooze reminder |
| `button.<medication>_prn_take` | Log PRN intake |

## Services

### med_expert.take

Mark a scheduled medication as taken.

```yaml
service: med_expert.take
data:
  entry_id: "config_entry_id"
  medication_id: "medication_uuid"
  # Optional: override the dose
  dose_numerator: 2
  dose_denominator: 1
  dose_unit: "tablet"
```

### med_expert.prn_take

Log an as-needed (PRN) intake outside of schedule.

```yaml
service: med_expert.prn_take
data:
  entry_id: "config_entry_id"
  medication_id: "medication_uuid"
  dose_numerator: 1
  dose_denominator: 1
  dose_unit: "tablet"
  note: "Headache after lunch"  # Optional
```

PRN intakes are logged with `scheduled_for: null` and by default do **not** affect the next scheduled dose.

### med_expert.snooze

Snooze a medication reminder.

```yaml
service: med_expert.snooze
data:
  entry_id: "config_entry_id"
  medication_id: "medication_uuid"
  minutes: 15  # Optional, uses policy default
```

### med_expert.skip

Skip the current scheduled dose.

```yaml
service: med_expert.skip
data:
  entry_id: "config_entry_id"
  medication_id: "medication_uuid"
  reason: "Upset stomach"  # Optional
```

### med_expert.add_medication

Add a new medication to a profile.

### med_expert.update_medication

Update an existing medication.

### med_expert.remove_medication

Remove a medication from a profile.

## Policy Options

Each medication can have a reminder policy:

```yaml
policy:
  grace_minutes: 30       # Time before marking as missed
  snooze_minutes: 10      # Default snooze duration
  prn_affects_schedule: false  # PRN intake affects next scheduled dose
  repeat_minutes: 5       # Repeat reminder interval (optional)
  max_retries: 3          # Max reminder repeats (optional)
  quiet_hours_start: "22:00"  # No notifications start (optional)
  quiet_hours_end: "07:00"    # No notifications end (optional)
```

## Custom Notification Templates

You can customize notification messages using the `med_expert.update_notification_settings` service:

```yaml
service: med_expert.update_notification_settings
data:
  entry_id: "your_config_entry_id"
  title_template: "Medication Time: {medication}"
  message_template: "Take {dose} now"
```

### Available Template Variables

The following variables are available in both `title_template` and `message_template`:

- `{medication}`: The medication display name (e.g., "Aspirin 100mg")
- `{dose}`: The formatted dose (e.g., "1 tablet", "1/2 tablet")

### Examples

**Simple reminder:**
```yaml
title_template: "💊 Reminder"
message_template: "Time to take {medication} - {dose}"
```

**Detailed reminder:**
```yaml
title_template: "Medication: {medication}"
message_template: "Please take {dose} as prescribed"
```

**Note:** These templates use Python string formatting (`.format()`), not Jinja2 templates. Use `{variable}` syntax, not `{{ variable }}`.

## Project Structure

```
custom_components/med_expert/
├── __init__.py           # Integration setup
├── config_flow.py        # Configuration UI
├── const.py              # Constants
├── data.py               # Runtime data types
├── diagnostics.py        # Diagnostics support
├── ha_services.py        # HA service registration
├── sensor.py             # Sensor entities
├── button.py             # Button entities
├── store.py              # Persistence layer
├── manifest.json         # Integration manifest
├── translations/         # Translations
│   └── en.json
├── domain/               # Pure domain logic (no HA imports)
│   ├── models.py         # Domain models (Profile, Medication, etc.)
│   ├── schedule.py       # Schedule computation engine
│   └── policies.py       # Policy logic
├── application/          # Application services
│   └── services.py       # Use cases and commands
├── providers/            # Medication providers
│   ├── base.py           # Provider interface
│   ├── manual.py         # Manual entry provider
│   ├── rxnorm.py         # RxNorm stub (future)
│   └── openfda.py        # OpenFDA stub (future)
└── runtime/              # Runtime components
    ├── manager.py        # Profile manager
    └── scheduler.py      # Reminder scheduler
```

## Architecture

Med Expert follows **Domain-Driven Design (DDD)** principles:

- **Domain Layer** (`domain/`): Pure business logic, no Home Assistant dependencies
- **Application Layer** (`application/`): Use cases and command handlers
- **Infrastructure Layer** (`store.py`, `providers/`): Persistence and external integrations
- **HA Adapters** (`__init__.py`, `sensor.py`, `button.py`, etc.): Home Assistant integration

## Development

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm (for frontend development)
- Visual Studio Code with Dev Containers extension
- Docker

### Setup

1. Clone the repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted
4. Run `scripts/develop` to start Home Assistant

### Frontend Development

The integration includes a TypeScript-based frontend panel. To build the frontend:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Or watch for changes during development
npm run dev
```

See [frontend/README.md](frontend/README.md) for detailed frontend development instructions.

### Adding the Frontend Panel

To add the Med Expert panel to your Home Assistant sidebar, add this to your `configuration.yaml`:

```yaml
panel_custom:
  - name: med-expert-panel
    sidebar_title: Medications
    sidebar_icon: mdi:pill
    url_path: med-expert
    module_url: /api/med_expert/www/med-expert-panel.js
```

Then restart Home Assistant.

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_schedule.py

# Run with coverage
pytest --cov=custom_components.med_expert tests/
```

### Linting

```bash
# Python linting
scripts/lint

# Frontend linting
cd frontend && npm run lint
```

### Key Test Cases

- **Schedule Engine**: times_per_day, interval, weekly, as_needed
- **DST Transitions**: Spring forward, fall back
- **Snooze/Missed**: Grace period, status transitions
- **PRN**: Logging with null scheduled_for
- **Migrations**: Schema version upgrades

## Troubleshooting

### Medication not appearing

1. Check the logs: **Settings** → **System** → **Logs**
2. Search for "med_expert"
3. Verify the config entry is loaded

### Notifications not showing

1. Ensure notifications are enabled in Home Assistant
2. Check quiet hours settings
3. Verify the medication status is "due"

### Wrong timezone

The integration uses your Home Assistant timezone. Check **Settings** → **System** → **General** → **Time zone**.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

⚠️ **This integration is for reminder and logging purposes only.**

- It is **not** a medical device
- It does **not** provide dosage recommendations
- It does **not** replace professional medical advice
- Always follow your healthcare provider's instructions

The developers are not responsible for any health outcomes related to the use of this software.
