# Copilot Instructions for Med Expert

## Project Overview

Med Expert is a **Home Assistant custom integration** for medication management with a TypeScript frontend panel. It provides medication scheduling, dose tracking, inventory management, and actionable mobile notifications.

**Key Features**: Multiple profiles, flexible schedules (times/interval/weekly/PRN), rational doses (½, ¼ tablet), inventory tracking, injection site rotation, inhaler puff counters, adherence analytics, mobile notifications with TAKEN/SNOOZE/SKIP actions.

## Architecture

```
med-expert/
├── custom_components/med_expert/    # HA integration (deployed)
│   ├── domain/          # Pure Python - NO HA dependencies
│   │   ├── models.py    # Profile, Medication, DoseQuantity, enums
│   │   ├── schedule.py  # Next occurrence computation (DST-safe)
│   │   └── policies.py  # Snooze, grace period rules
│   ├── application/     # Use cases via command pattern
│   │   └── services.py  # MedicationService + command DTOs
│   ├── runtime/         # HA-specific runtime
│   │   ├── manager.py   # ProfileManager (orchestrates everything)
│   │   ├── scheduler.py # async_track_point_in_time callbacks
│   │   └── notifications.py  # mobile_app + persistent notifications
│   ├── store.py         # Persistence with schema migrations
│   ├── ha_services.py   # HA service definitions (voluptuous)
│   ├── sensor.py        # Medication status sensors
│   ├── button.py        # Take/snooze/skip buttons
│   └── www/             # Built JS output only (do NOT edit directly)
│
├── frontend/            # TypeScript source (SSOT for frontend)
│   ├── src/
│   │   ├── panel.ts     # Lit 3 web component
│   │   └── types.ts     # HA type definitions
│   ├── package.json
│   ├── tsconfig.json
│   └── webpack.config.js  # Builds → ../custom_components/med_expert/www/
│
└── tests/               # pytest with HA mocking
```

**Key principle**: Domain layer (`domain/`) must remain HA-independent for testability. Import from `domain/` into other layers, never the reverse.

## Frontend Panel

The frontend is a **Lit 3 web component** in `frontend/` (source of truth). Built JS is output to `www/`.

```yaml
# configuration.yaml
panel_custom:
  - name: med-expert-panel
    sidebar_title: Medications
    sidebar_icon: mdi:pill
    url_path: med-expert
    module_url: /api/med_expert/www/med-expert-panel.js
```

**Build workflow** (from project root):
```bash
cd frontend && npm install && npm run build  # → custom_components/med_expert/www/med-expert-panel.js
npm run dev  # Watch mode for development
```

**Important**: Never edit files in `www/` directly - always edit in `frontend/src/` and rebuild.

## Notification System

`runtime/notifications.py` sends **actionable mobile notifications** via `notify.mobile_app_*`:

- **Actions**: `MED_EXPERT_TAKEN`, `MED_EXPERT_SNOOZE`, `MED_EXPERT_SKIP`
- **Tag format**: `med_expert_{entry_id}_{medication_id}` (for dismissal)
- **Fallback**: `persistent_notification` if no mobile target configured

Action events are handled in `manager.py` via `mobile_app_notification_action` event listener.

## Data Flow

```
User Action (panel/notification/service call)
    ↓
ha_services.py (validates via voluptuous)
    ↓
ProfileManager (runtime/manager.py)
    ↓
MedicationService (application/services.py) ← Command DTOs
    ↓
Domain models (domain/models.py)
    ↓
ProfileRepository → Store (persistence)
    ↓
Scheduler reschedules → NotificationManager updates
    ↓
Entity states updated → Frontend reflects changes
```

## Code Patterns

### Rational Doses (avoid floats)
Doses use `DoseQuantity(numerator, denominator, unit)` to prevent rounding errors:
```python
# Correct: 1/2 tablet
DoseQuantity(numerator=1, denominator=2, unit="tablet")
# Wrong: DoseQuantity(0.5, "tablet")
```

### Command Pattern for Services
All mutations use command dataclasses in `application/services.py`:
```python
command = AddMedicationCommand(
    display_name="Aspirin",
    schedule_kind=ScheduleKind.TIMES_PER_DAY,
    times=["08:00", "20:00"],
)
medication = service.add_medication(profile, command)
```

### Timezone Handling
Always use `ZoneInfo` (never `pytz`). All datetime operations must be timezone-aware:
```python
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo(profile.timezone))
```

### Storage Migrations
When changing stored data structure, bump `STORE_VERSION` in `const.py` and add migration in `store.py`:
```python
def _migrate_v1_to_v2(self, data: dict) -> dict:
    # Add new fields with defaults for existing data
```

## Developer Commands

```bash
scripts/setup       # Install dependencies (pip install -r requirements.txt)
scripts/lint        # Format and lint (ruff format + ruff check --fix)
scripts/develop     # Run local HA instance with integration loaded

# Tests (domain tests work without HA, config_flow needs pytest-homeassistant-custom-component)
pytest tests/

# Frontend (Lit + TypeScript → builds to custom_components/med_expert/www/)
cd frontend && npm install && npm run build
```

## Testing Strategy

- **Domain tests** (`test_services.py`, `test_schedule.py`): Mock HA via `conftest.py`, test pure logic
- **Integration tests**: Use `pytest-homeassistant-custom-component` for config flows
- Use `MedicationService(get_now=lambda: fixed_datetime)` for deterministic time in tests

## Key Files to Reference

| Concept | File |
|---------|------|
| All domain models/enums | [domain/models.py](../custom_components/med_expert/domain/models.py) |
| Schedule computation | [domain/schedule.py](../custom_components/med_expert/domain/schedule.py) |
| Service commands/DTOs | [application/services.py](../custom_components/med_expert/application/services.py) |
| HA service schemas | [ha_services.py](../custom_components/med_expert/ha_services.py) |
| Profile manager | [runtime/manager.py](../custom_components/med_expert/runtime/manager.py) |

## Common Tasks

**Adding a new medication field**: Update `Medication` in `models.py` → Add to `AddMedicationCommand` → Update `ha_services.py` schema → Add storage migration if persisted

**Adding a new HA service**: Define in `ha_services.py` with voluptuous schema → Register in `async_register_services` → Add to `services.yaml` for UI
