# Med Expert Frontend Panel

This directory contains the TypeScript source code for the Med Expert frontend panel.

## Structure

```
frontend/
├── src/
│   ├── panel.ts          # Main panel component (Lit Element)
│   └── types.ts          # TypeScript type definitions
├── package.json          # NPM dependencies
├── tsconfig.json         # TypeScript configuration
├── webpack.config.js     # Webpack build configuration
└── .eslintrc.json       # ESLint configuration
```

## Development

### Prerequisites

- Node.js 18+ and npm
- TypeScript knowledge
- Familiarity with Lit web components

### Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Build the frontend:
   ```bash
   npm run build
   ```

   This compiles TypeScript to JavaScript and outputs to `../custom_components/med_expert/www/med-expert-panel.js`

3. Development mode (auto-rebuild on changes):
   ```bash
   npm run dev
   ```

### Testing

After building, restart Home Assistant to load the panel. The panel JavaScript will be served at:
```
/api/med_expert/www/med-expert-panel.js
```

### Linting

Run ESLint to check code quality:
```bash
npm run lint
```

Run TypeScript type checking:
```bash
npm run type-check
```

## Architecture

### Panel Component (`panel.ts`)

The main `med-expert-panel` component is built with [Lit](https://lit.dev/), a lightweight web component library.

**Key Features:**
- Fetches medication data from Home Assistant entities
- Displays medication cards with status badges
- Provides "Take" and "Snooze" action buttons
- Auto-refreshes data after actions

**Home Assistant Integration:**
- Uses the `hass` property to access Home Assistant state
- Calls `med_expert.take` and `med_expert.snooze` services
- Reads sensor entities with pattern `sensor.*_med_expert_*_status`

### Type Definitions (`types.ts`)

TypeScript interfaces for:
- `HomeAssistant` - Core HA object
- `HassEntity` - Entity state structure
- `Medication` - Medication data model

## Build Output

The build process:
1. Compiles TypeScript (`.ts`) to JavaScript
2. Bundles all dependencies using Webpack
3. Outputs a single `med-expert-panel.js` file to `../custom_components/med_expert/www/`
4. Generates source maps (`.js.map`) for debugging

## Adding to Home Assistant

To make the panel accessible in Home Assistant's sidebar:

1. Build the frontend: `npm run build`
2. The Python integration (`__init__.py`) registers the static path
3. Add a panel configuration in Home Assistant's `configuration.yaml`:

```yaml
panel_custom:
  - name: med-expert-panel
    sidebar_title: Medications
    sidebar_icon: mdi:pill
    url_path: med-expert
    module_url: /api/med_expert/www/med-expert-panel.js
```

4. Restart Home Assistant
5. The panel will appear in the sidebar

## Customization

### Styling

The panel uses CSS custom properties (CSS variables) from Home Assistant's theme system:

- `--primary-background-color` - Main background
- `--card-background-color` - Card backgrounds
- `--primary-color` - Primary action color
- `--success-color`, `--warning-color`, `--error-color` - Status colors

### Adding Features

To add new features:

1. Edit `src/panel.ts` to add UI components
2. Call Home Assistant services via `this.hass.callService()`
3. Update `src/types.ts` if new types are needed
4. Rebuild with `npm run build`

## Troubleshooting

### Panel not loading

1. Check browser console for errors
2. Verify `med-expert-panel.js` exists in `../custom_components/med_expert/www/`
3. Check Home Assistant logs for errors
4. Clear browser cache

### TypeScript errors

Run type checking:
```bash
npm run type-check
```

### Build errors

1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check Node.js version (should be 18+)

## Resources

- [Lit Documentation](https://lit.dev/)
- [Home Assistant Frontend Development](https://developers.home-assistant.io/docs/frontend/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Webpack Documentation](https://webpack.js.org/)
