/**
 * Constants for Med Expert Panel
 */

import type { FormOption, ScheduleOption, TabDef } from './types';

/**
 * Status color mapping
 */
export const STATUS_COLORS: Record<string, string> = {
  due: '#ff9800',
  missed: '#f44336',
  snoozed: '#2196f3',
  ok: '#4caf50',
  prn: '#9c27b0',
};

/**
 * Status icon mapping
 */
export const STATUS_ICONS: Record<string, string> = {
  due: 'mdi:bell-ring',
  missed: 'mdi:alert-circle',
  snoozed: 'mdi:clock-outline',
  ok: 'mdi:check-circle',
  prn: 'mdi:hand-extended',
  taken: 'mdi:check-circle',
  skipped: 'mdi:close-circle',
};

/**
 * Dosage form icon mapping
 */
export const FORM_ICONS: Record<string, string> = {
  tablet: 'mdi:pill',
  capsule: 'mdi:capsule',
  injection: 'mdi:needle',
  inhaler: 'mdi:air-filter',
  drops: 'mdi:eyedropper',
  liquid: 'mdi:cup-water',
  cream: 'mdi:lotion',
  patch: 'mdi:bandage',
  nasal_spray: 'mdi:spray',
  suppository: 'mdi:medication',
  powder: 'mdi:grain',
  other: 'mdi:medication',
};

/**
 * Tab definitions
 */
export const TABS: TabDef[] = [
  { id: 'medications', label: 'Medications', icon: 'mdi:pill' },
  { id: 'adherence', label: 'Adherence', icon: 'mdi:chart-line' },
  { id: 'inventory', label: 'Inventory', icon: 'mdi:package-variant' },
  { id: 'history', label: 'History', icon: 'mdi:history' },
  { id: 'settings', label: 'Settings', icon: 'mdi:cog' },
];

/**
 * Dosage form options for wizard
 */
export const FORM_OPTIONS: FormOption[] = [
  { id: 'tablet', name: 'Tablet', icon: 'mdi:pill' },
  { id: 'capsule', name: 'Capsule', icon: 'mdi:capsule' },
  { id: 'injection', name: 'Injection', icon: 'mdi:needle' },
  { id: 'inhaler', name: 'Inhaler', icon: 'mdi:lungs' },
  { id: 'drops', name: 'Drops', icon: 'mdi:eyedropper' },
  { id: 'liquid', name: 'Liquid', icon: 'mdi:cup-water' },
  { id: 'cream', name: 'Cream', icon: 'mdi:lotion' },
  { id: 'patch', name: 'Patch', icon: 'mdi:bandage' },
];

/**
 * Schedule type options for wizard
 */
export const SCHEDULE_OPTIONS: ScheduleOption[] = [
  { id: 'times_per_day', name: 'Times per Day', icon: 'mdi:clock-outline' },
  { id: 'interval', name: 'Interval', icon: 'mdi:timer-outline' },
  { id: 'weekly', name: 'Weekly', icon: 'mdi:calendar-week' },
  { id: 'as_needed', name: 'As Needed (PRN)', icon: 'mdi:hand-extended' },
];

/**
 * Weekday labels
 */
export const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

/**
 * Dose unit suggestions
 */
export const DOSE_UNITS = [
  'tablet',
  'capsule',
  'ml',
  'mg',
  'puff',
  'spray',
  'drop',
  'IU',
  'mcg',
  'g',
];

/**
 * Time constants (milliseconds)
 */
export const MS_PER_MINUTE = 60_000;
export const MS_PER_HOUR = 3_600_000;
export const MS_PER_DAY = 86_400_000;
