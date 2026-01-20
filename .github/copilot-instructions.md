# Med Expert - Copilot Instructions

This document provides guidance for AI coding agents working on the Med Expert Home Assistant custom integration.

## Project Overview

Med Expert is a Home Assistant custom integration for medication management that helps users:
- Manage multiple medication profiles
- Track medication schedules (daily, interval, weekly, PRN)
- Receive actionable notifications with Take/Snooze/Skip buttons
- Monitor inventory and adherence
- View and interact with medications via a custom frontend panel

## Architecture

The project follows **Domain-Driven Design (DDD)** principles with clear separation of concerns:

### Layer Structure

```
custom_components/med_expert/
├── domain/              # Pure domain logic (no HA dependencies)
│   ├── models.py        # Core entities: Profile, Medication, Schedule, etc.
│   ├── schedule.py      # Schedule computation engine
│   └── policies.py      # Reminder and adherence policies
│
├── application/         # Application services (use cases)
│   └── services.py      # Command handlers for medications
│
├── runtime/             # Runtime components
│   ├── manager.py       # ProfileManager (orchestrates profile lifecycle)
│   ├── scheduler.py     # Scheduler for medication reminders
│   └── notifications.py # NotificationManager for actionable notifications
│
├── providers/           # External data providers
│   ├── base.py          # Provider interface
│   ├── manual.py        # Manual entry provider
│   ├── rxnorm.py        # RxNorm API (future)
│   └── openfda.py       # OpenFDA API (future)
│
├── store.py             # Persistence layer (ProfileStore, ProfileRepository)
├── __init__.py          # HA integration setup
├── config_flow.py       # Configuration UI
├── ha_services.py       # HA service registration
├── websocket_api.py     # WebSocket API for frontend panel
├── sensor.py            # Sensor entities
├── button.py            # Button entities
├── const.py             # Constants
├── data.py              # Runtime data types
└── diagnostics.py       # Diagnostics support
```

### Key Design Principles

1. **Domain Independence**: The `domain/` layer has zero Home Assistant imports
2. **Command Pattern**: Application services handle commands (add_medication, take, snooze, etc.)
3. **Event-Driven**: ProfileManager coordinates async operations
4. **Immutability**: Domain models use dataclasses with immutable patterns
5. **Type Safety**: Strict typing throughout with mypy checks

## Frontend Panel

### Structure

```
frontend/
├── src/
│   └── med-expert-panel.ts  # Main panel component (Lit web component)
├── dist/                     # Compiled JS (gitignored)
├── package.json              # Dependencies and build scripts
├── tsconfig.json             # TypeScript configuration
├── build.js                  # Build script
└── README.md                 # Frontend documentation

custom_components/med_expert/www/
└── med-expert-panel.js       # Built output (served to HA)
```

### Building the Frontend

```bash
cd frontend
npm install
npm run build  # Compiles TypeScript and outputs to www/
```

### Frontend Architecture

- **Technology**: TypeScript + Lit (web components)
- **Communication**: WebSocket API (`med_expert/get_profiles` command)
- **Integration**: Served via `/hacsfiles/med-expert/` static path
- **Features**:
  - Display all medication profiles
  - Show medication status (OK, Due, Missed, Snoozed, PRN)
  - Interactive buttons for Take, Snooze, Skip actions
  - PRN (as-needed) medication logging

## Notifications

Med Expert provides **actionable notifications** with mobile_app integration:

### Notification Flow

1. `Scheduler` detects due medication
2. `NotificationManager.async_send_due_notification()` sends notification
3. Notification includes actions: TAKEN, SNOOZE, SKIP
4. User taps action → HA fires event → Service handler processes
5. `NotificationManager.async_dismiss_notification()` clears notification

### Notification Settings

Configurable per profile:
- `notify_target`: Target service (e.g., `mobile_app_my_phone`)
- `include_actions`: Enable/disable action buttons
- `group_notifications`: Group by profile
- `reminder_template`: Custom message template
- `missed_template`: Custom missed message template

### Fallback

If `notify_target` is not configured, falls back to persistent notifications.

## Developer Workflow

### Setting Up Development Environment

1. Clone repository
2. Open in VS Code
3. Click "Reopen in Container" (uses `.devcontainer.json`)
4. Container includes Home Assistant dev instance

### Running Home Assistant

```bash
scripts/develop  # Starts HA with integration loaded
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_schedule.py

# Run with coverage
pytest --cov=custom_components.med_expert tests/
```

### Linting

```bash
scripts/lint  # Runs ruff, mypy, etc.
```

### Frontend Development

```bash
cd frontend
npm run watch  # Watch mode for TypeScript
# In another terminal:
cd ..
scripts/develop  # Run HA
```

## Code Conventions

### Python

- **Style**: Follow PEP 8, enforced by ruff
- **Type Hints**: Required for all functions
- **Docstrings**: Google style for public APIs
- **Imports**: Absolute imports from `custom_components.med_expert`

### TypeScript

- **Style**: Enforced by ESLint and Prettier
- **Decorators**: Use Lit decorators (`@customElement`, `@property`, `@state`)
- **Types**: Strict mode enabled

### Testing

- **Unit Tests**: For domain logic in `tests/`
- **Integration Tests**: For HA integration
- **Test Files**: Named `test_*.py`
- **Fixtures**: Pytest fixtures in `conftest.py`

## Key Integration Points

### Home Assistant Services

Registered in `ha_services.py`:
- `med_expert.add_medication`
- `med_expert.update_medication`
- `med_expert.remove_medication`
- `med_expert.take`
- `med_expert.prn_take`
- `med_expert.snooze`
- `med_expert.skip`

### WebSocket API

Registered in `websocket_api.py`:
- `med_expert/get_profiles`: Returns all profiles with medications

### Entities

- **Sensors**: `next_due`, `status`, `next_dose` per medication
- **Buttons**: `take`, `snooze`, `prn_take` per medication

### Storage

- Stored in `.storage/med_expert` (JSON)
- Uses `ProfileStore` with schema versioning
- Migrations handled in `store.py`

## Common Tasks

### Adding a New Service

1. Add service definition to `services.yaml`
2. Implement handler in `application/services.py`
3. Register in `ha_services.py`
4. Add tests in `tests/`

### Adding a New Sensor

1. Add sensor class in `sensor.py`
2. Update `ProfileManager` to create entity
3. Add tests

### Modifying Domain Models

1. Edit `domain/models.py`
2. Update `store.py` schema version
3. Add migration if needed
4. Update tests

### Frontend Changes

1. Edit `frontend/src/med-expert-panel.ts`
2. Run `npm run build`
3. Refresh HA frontend
4. Test in browser

## Dependencies

### Python

- `homeassistant>=2023.x`: Home Assistant core
- No external dependencies (uses HA's bundled libraries)

### TypeScript

- `lit`: Web components framework
- `typescript`: TypeScript compiler
- `eslint`: Linting
- `prettier`: Code formatting

## Release Process

1. Update version in `manifest.json`
2. Update `README.md` changelog
3. Build frontend: `cd frontend && npm run build`
4. Commit changes
5. Create GitHub release with tag `vX.Y.Z`
6. HACS picks up new release automatically

## Troubleshooting

### Panel Not Loading

- Check `www/med-expert-panel.js` exists
- Verify static path registration in `__init__.py`
- Check browser console for errors
- Verify WebSocket API is registered

### Notifications Not Sending

- Check `notify_target` is configured
- Verify mobile_app service exists
- Check HA logs for notification errors
- Test with persistent notification fallback

### Tests Failing

- Run `pytest -v` for verbose output
- Check for DST-related issues in schedule tests
- Verify fixtures are properly set up

## Security Considerations

- Never log sensitive medication data
- Sanitize user inputs in services
- Use HA's permission system for services
- Validate all WebSocket commands

## Performance Notes

- Schedule computation is lazy (cached until invalidated)
- Entity updates are batched
- Notifications are non-blocking (async)
- Storage writes are debounced

## Future Enhancements

- Integration with RxNorm/OpenFDA APIs
- OCR for prescription scanning
- Medication interaction checking
- Multi-language support
- Enhanced adherence analytics
- Calendar integration
