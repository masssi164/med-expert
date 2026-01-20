# Med Expert - AI Coding Instructions

## Project Overview
Med Expert is a Home Assistant custom integration for medication management. It follows a layered architecture separating pure domain logic from HA-specific code.

## Architecture

### Layer Structure
```
custom_components/med_expert/
├── domain/          # Pure Python, NO Home Assistant dependencies
│   ├── models.py    # Core domain models (Profile, Medication, DoseQuantity)
│   ├── schedule.py  # Schedule computation (DST-safe)
│   └── policies.py  # Business rules for notifications/reminders
├── application/
│   └── services.py  # Use cases via Command DTOs (AddMedicationCommand, etc.)
├── runtime/
│   ├── manager.py   # ProfileManager - coordinates all components per profile
│   ├── scheduler.py # HA event-based reminder scheduling
│   └── notifications.py
├── providers/       # External medication database integration (OpenFDA, RxNorm)
├── store.py         # ProfileRepository + schema migrations
└── ha_services.py   # HA service registration (voluptuous schemas)
```

### Key Design Decisions
- **One config entry = one profile**: Each HA config entry maps to a `Profile` containing multiple medications
- **Rational doses**: Uses `DoseQuantity(numerator, denominator, unit)` to avoid float rounding (½ tablet, not 0.5)
- **Command pattern**: All mutations go through Command DTOs validated before execution
- **DST-safe scheduling**: All datetime operations use `ZoneInfo`, never naive datetimes

## Development Workflow

```bash
# Install dependencies
scripts/setup

# Run local HA instance with integration
scripts/develop    # Starts HA on localhost:8123

# Lint and format (uses ruff)
scripts/lint

# Run tests
pytest tests/
```

## Testing Patterns

Tests can run without full HA framework. The [conftest.py](tests/conftest.py) mocks HA modules when `pytest-homeassistant-custom-component` is unavailable:

```python
# Domain/service tests use fixed time injection
@pytest.fixture
def service(fixed_now: datetime) -> MedicationService:
    return MedicationService(get_now=lambda: fixed_now)
```

For config flow tests requiring real HA fixtures, install full test dependencies.

## Code Patterns

### Adding New Services
1. Define Command DTO in [application/services.py](custom_components/med_expert/application/services.py) with `validate()` method
2. Add service handler in [ha_services.py](custom_components/med_expert/ha_services.py) with voluptuous schema
3. Document in [services.yaml](custom_components/med_expert/services.yaml)
4. Wire through [runtime/manager.py](custom_components/med_expert/runtime/manager.py)

### Domain Model Changes
1. Update models in [domain/models.py](custom_components/med_expert/domain/models.py) (include `to_dict`/`from_dict`)
2. Bump `CURRENT_SCHEMA_VERSION` in [store.py](custom_components/med_expert/store.py)
3. Add migration in `_async_migrate()` method
4. Test serialization roundtrip

### Schedule Types
Medication schedules use `ScheduleKind` enum:
- `times_per_day`: Fixed times with per-slot doses
- `interval`: Every X minutes from last take
- `weekly`: Specific weekdays and times
- `as_needed`: PRN medications (no scheduled occurrences)
- `depot`: Long-acting injections with appointment tracking

## Notification System

### Mobile App Actionable Notifications
The notification flow in [runtime/notifications.py](custom_components/med_expert/runtime/notifications.py):
1. `NotificationManager` sends notifications via `notify.{target}` service (e.g., `notify.mobile_app_my_phone`)
2. Notifications include action buttons: `MED_EXPERT_TAKEN`, `MED_EXPERT_SNOOZE`, `MED_EXPERT_SKIP`
3. `ProfileManager` subscribes to `mobile_app_notification_action` events on startup
4. Action events are routed to `_handle_notification_action()` which calls the appropriate command

### Notification Data Flow
```
Scheduler → on_due callback → NotificationManager.async_send_due_notification()
    ↓
Mobile App ← notify.mobile_app_* service call with actions
    ↓
User taps action → HA event: mobile_app_notification_action
    ↓
ProfileManager._handle_notification_action() → TakeCommand/SnoozeCommand/SkipCommand
```

### Configuration
Notification settings stored in `Profile.notification_settings`:
- `notify_target`: Service name like `mobile_app_my_phone`
- `group_notifications`: Group by profile ID
- `include_actions`: Enable/disable action buttons
- `reminder_template` / `missed_template`: Custom message templates with `{medication}`, `{dose}` placeholders

## Frontend Panel

### TypeScript Package Structure
The frontend is a TypeScript package in [www/](custom_components/med_expert/www/):
```
www/
├── src/
│   ├── index.ts              # Entry point, exports all modules
│   ├── med-expert-panel.ts   # Main LitElement component
│   ├── types.ts              # TypeScript interfaces (HomeAssistant, MedicationData, etc.)
│   ├── constants.ts          # STATUS_COLORS, FORM_ICONS, TABS, etc.
│   ├── styles.ts             # CSS-in-JS styles using Lit css``
│   ├── utils.ts              # Helper functions (formatNextDose, groupMedicationsByStatus)
│   ├── utils.test.ts         # Vitest tests for utilities
│   └── constants.test.ts     # Vitest tests for constants
├── package.json              # Lit, TypeScript, Vite, Vitest dependencies
├── tsconfig.json             # Strict TypeScript config
├── vite.config.ts            # Build config → outputs med-expert-panel.js
├── vitest.config.ts          # Test config with jsdom environment
└── med-expert-panel.js       # BUILD OUTPUT (committed, served by HA)
```

### How Panel Registration Works
1. **Python side** ([\_\_init\_\_.py](custom_components/med_expert/__init__.py)):
   - Registers static path: `/api/med_expert/panel.js` → `www/med-expert-panel.js`
   - Registers sidebar panel via `async_register_built_in_panel()`
2. **Browser side**:
   - HA loads ES module from `/api/med_expert/panel.js`
   - Custom element `<med-expert-panel>` receives `hass`, `narrow`, `route`, `panel` props

### Frontend Development Workflow
```bash
cd custom_components/med_expert/www

# Install dependencies
npm install

# Run tests
npm test              # Single run
npm run test:watch    # Watch mode
npm run test:coverage # With coverage report

# Type check
npm run typecheck

# Build for production (outputs med-expert-panel.js in www/)
npm run build

# Development (watch mode, auto-rebuilds)
npm run dev
```

### Build Output
`npm run build` outputs `med-expert-panel.js` directly to `www/`. This file is:
- Committed to git (it's the production bundle)
- Served by Home Assistant at `/api/med_expert/panel.js`
- A self-contained ES module with Lit bundled

### Panel Features
- Medication dashboard with status colors (due=orange, missed=red, snoozed=blue, ok=green)
- Add/edit medication wizard with step-by-step flow
- Inventory tracking display with low-stock warnings
- Calendar history view with adherence tracking
- Panel state syncs with HA entities: `sensor.{profile}_medication_{med_id}`

## Provider System (Incomplete)

### Current State
[providers/](custom_components/med_expert/providers/) contains stubs for external medication databases:
- `manual.py`: Works - user enters medication details manually
- `openfda.py`: **Stub only** - raises `NotImplementedError`
- `rxnorm.py`: **Stub only** - planned RxNorm/NIH integration

### Provider Interface
Providers implement `MedicationProvider` base class from [providers/base.py](custom_components/med_expert/providers/base.py):
- `search(query, limit) -> list[MedicationCandidate]`
- `resolve(external_id) -> MedicationDetails | None`

Future providers should return `MedicationCandidate` with `dosage_form`, `strength`, and `default_dose_unit` for auto-population.

## Important Conventions

- **No floats for doses**: Always use `DoseQuantity` with integer numerator/denominator
- **Timezone handling**: Store IANA timezone strings, convert via `ZoneInfo(profile.timezone)`
- **Slot keys**: Time-based slots use "HH:MM" format as dictionary keys
- **Entity updates**: Use `async_dispatcher_send()` with `SIGNAL_MEDICATION_UPDATED` pattern
- **Storage versioning**: Always migrate old schemas forward, never break existing data
- **Event constants**: Use constants from [const.py](custom_components/med_expert/const.py) for action/event names
