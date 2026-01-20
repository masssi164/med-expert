# Med Expert Frontend Panel

TypeScript-based frontend panel for the Med Expert Home Assistant integration.

## Development

### Prerequisites

- Node.js 18+ and npm
- TypeScript knowledge
- Familiarity with Lit web components

### Setup

```bash
cd frontend
npm install
```

### Build

```bash
# One-time build
npm run build

# Watch mode (rebuilds on changes)
npm run watch
```

This will compile TypeScript to JavaScript and output to `custom_components/med_expert/www/med-expert-panel.js`.

### Linting

```bash
npm run lint
npm run format
```

## Architecture

The panel is built using:
- **TypeScript** for type safety
- **Lit** for web components
- **Home Assistant Frontend API** for integration

### File Structure

```
frontend/
├── src/
│   └── med-expert-panel.ts    # Main panel component
├── dist/                       # Compiled JS (gitignored)
├── package.json
├── tsconfig.json
├── build.js                    # Build script
└── README.md
```

## Integration with Home Assistant

The panel is registered in `custom_components/med_expert/__init__.py` and served from the `www/` directory.

Home Assistant automatically serves files from:
```
/hacsfiles/med-expert/med-expert-panel.js
```

## Panel Features

- Display all medication profiles
- Show medication status (OK, Due, Missed, Snoozed, PRN)
- Interactive buttons for Take, Snooze, Skip actions
- PRN (as-needed) medication logging
- Real-time updates via Home Assistant WebSocket API

## Adding Features

1. Edit `src/med-expert-panel.ts`
2. Run `npm run build`
3. Refresh Home Assistant frontend
4. Test the changes

## Testing

The panel integrates with Home Assistant's testing framework. Currently, manual testing is required:

1. Build the panel
2. Restart Home Assistant
3. Navigate to the Med Expert panel
4. Test all interactions

## Troubleshooting

### Panel not loading
- Check browser console for errors
- Verify `www/med-expert-panel.js` exists
- Check Home Assistant logs for panel registration

### Build errors
- Run `npm install` to ensure dependencies are installed
- Check TypeScript errors with `npm run lint`
- Verify Node.js version is 18+
