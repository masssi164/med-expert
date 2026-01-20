# Med Expert Panel

Modern medication management dashboard for Home Assistant sidebar.

## Development Setup

### Prerequisites
- Node.js 18+ 
- npm 9+

### Quick Start

```bash
cd custom_components/med_expert/www

# Install dependencies
npm install

# Run tests
npm test

# Type check
npm run typecheck

# Build (outputs med-expert-panel.js)
npm run build

# Development mode (watch + rebuild)
npm run dev
```

### Build Output

The build outputs `med-expert-panel.js` directly to the `www/` directory. This file is:
- Served by Home Assistant at `/api/med_expert/panel.js`
- Registered as a sidebar panel in `__init__.py`
- A self-contained ES module with Lit bundled

### Directory Structure

```
www/
├── src/
│   ├── index.ts              # Entry point
│   ├── med-expert-panel.ts   # Main LitElement component
│   ├── types.ts              # TypeScript interfaces
│   ├── constants.ts          # STATUS_COLORS, TABS, etc.
│   ├── styles.ts             # CSS-in-JS styles
│   ├── utils.ts              # Helper functions
│   ├── utils.test.ts         # Utility tests
│   └── constants.test.ts     # Constant tests
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
└── med-expert-panel.js       # BUILD OUTPUT (committed)
```

### Testing

```bash
npm test              # Single run
npm run test:watch    # Watch mode
npm run test:coverage # With coverage
```

### How It Works

1. **Python Registration** ([\_\_init\_\_.py](../__init__.py)):
   - Registers static path: `/api/med_expert/panel.js` → `www/med-expert-panel.js`
   - Registers sidebar panel with `async_register_built_in_panel()`

2. **Panel Loading**:
   - HA loads ES module from `/api/med_expert/panel.js`
   - Custom element `<med-expert-panel>` receives `hass`, `narrow`, `route`, `panel` props
   - Panel renders medication dashboard with real-time state updates

3. **Service Calls**:
   - Panel calls `hass.callService()` for take/snooze/skip/add/edit operations
   - Services defined in `services.yaml` and registered in `ha_services.py`

## Features

### 📋 Medications Tab
- Medication cards grouped by status (Due, Missed, Upcoming, PRN)
- Quick actions: Take, Snooze, Skip
- Real-time updates via Home Assistant states
- Inventory warnings for low stock
- Add/Edit medication wizard

### 📊 Adherence Tab
- Adherence rate display
- Charts and statistics (planned)

### 📦 Inventory Tab
- All medications with stock levels
- Low stock warnings
- Quick refill function

### 📜 History Tab
- Medication logs (planned)
- Timeline view (planned)

### ⚙️ Settings Tab
- Profile settings (planned)
- Notification settings (planned)

## Design

- **Modern UI** with Lit 3.0 Web Components
- **Responsive** - Desktop, Tablet, Mobile
- **Dark Mode** via Home Assistant theme
- **Touch-Friendly** buttons and cards
- [ ] History Timeline
- [ ] Profile Settings UI
- [ ] Multi-Profile Support
- [ ] Export/Import Funktionen
- [ ] Medication Reminders Configuration
