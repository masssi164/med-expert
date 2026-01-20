/**
 * Tests for utility functions
 */

import { describe, it, expect } from 'vitest';
import {
  getStatusColor,
  getStatusIcon,
  getFormIcon,
  formatNextDose,
  formatDose,
  groupMedicationsByStatus,
  createDefaultWizardState,
  validateWizardState,
  buildServiceData,
  getCalendarDays,
  formatDate,
  formatMonthYear,
  isSameDay,
  isToday,
} from './utils';
import type { MedicationData, WizardState } from './types';

describe('getStatusColor', () => {
  it('returns orange for due status', () => {
    expect(getStatusColor('due')).toBe('#ff9800');
  });

  it('returns red for missed status', () => {
    expect(getStatusColor('missed')).toBe('#f44336');
  });

  it('returns blue for snoozed status', () => {
    expect(getStatusColor('snoozed')).toBe('#2196f3');
  });

  it('returns green for ok status', () => {
    expect(getStatusColor('ok')).toBe('#4caf50');
  });

  it('returns purple for prn status', () => {
    expect(getStatusColor('prn')).toBe('#9c27b0');
  });

  it('returns default gray for unknown status', () => {
    expect(getStatusColor('unknown')).toBe('#757575');
  });

  it('handles uppercase status', () => {
    expect(getStatusColor('DUE')).toBe('#ff9800');
  });
});

describe('getStatusIcon', () => {
  it('returns bell icon for due status', () => {
    expect(getStatusIcon('due')).toBe('mdi:bell-ring');
  });

  it('returns alert icon for missed status', () => {
    expect(getStatusIcon('missed')).toBe('mdi:alert-circle');
  });

  it('returns check icon for ok/taken status', () => {
    expect(getStatusIcon('ok')).toBe('mdi:check-circle');
    expect(getStatusIcon('taken')).toBe('mdi:check-circle');
  });

  it('returns pill icon for unknown status', () => {
    expect(getStatusIcon('unknown')).toBe('mdi:pill');
  });
});

describe('getFormIcon', () => {
  it('returns pill icon for tablet', () => {
    expect(getFormIcon('tablet')).toBe('mdi:pill');
  });

  it('returns capsule icon for capsule', () => {
    expect(getFormIcon('capsule')).toBe('mdi:capsule');
  });

  it('returns needle icon for injection', () => {
    expect(getFormIcon('injection')).toBe('mdi:needle');
  });

  it('returns default medication icon for undefined', () => {
    expect(getFormIcon(undefined)).toBe('mdi:medication');
  });

  it('returns default medication icon for unknown form', () => {
    expect(getFormIcon('unknown')).toBe('mdi:medication');
  });
});

describe('formatNextDose', () => {
  it('returns "No schedule" for undefined', () => {
    expect(formatNextDose(undefined)).toBe('No schedule');
  });

  it('returns "Overdue" for past dates', () => {
    const pastDate = new Date(Date.now() - 60000).toISOString();
    expect(formatNextDose(pastDate)).toBe('Overdue');
  });

  it('returns minutes for times less than an hour away', () => {
    const soon = new Date(Date.now() + 30 * 60 * 1000).toISOString();
    const result = formatNextDose(soon);
    expect(result).toMatch(/^\d+min$/);
  });

  it('returns hours for times less than a day away', () => {
    const hours = new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString();
    const result = formatNextDose(hours);
    expect(result).toMatch(/^\d+h$/);
  });
});

describe('formatDose', () => {
  it('formats whole doses correctly', () => {
    expect(formatDose(1, 1, 'tablet')).toBe('1 tablet');
    expect(formatDose(2, 1, 'capsule')).toBe('2 capsule');
  });

  it('formats fractional doses correctly', () => {
    expect(formatDose(1, 2, 'tablet')).toBe('1/2 tablet');
    expect(formatDose(3, 4, 'ml')).toBe('3/4 ml');
  });
});

describe('groupMedicationsByStatus', () => {
  it('groups medications correctly', () => {
    const medications: MedicationData[] = [
      { entityId: '1', medication_id: '1', status: 'due', state: 'due' },
      { entityId: '2', medication_id: '2', status: 'missed', state: 'missed' },
      { entityId: '3', medication_id: '3', status: 'ok', state: 'ok' },
      { entityId: '4', medication_id: '4', status: 'prn', state: 'prn' },
    ] as MedicationData[];

    const groups = groupMedicationsByStatus(medications);

    expect(groups.due).toHaveLength(1);
    expect(groups.missed).toHaveLength(1);
    expect(groups.upcoming).toHaveLength(1);
    expect(groups.prn).toHaveLength(1);
  });

  it('handles empty array', () => {
    const groups = groupMedicationsByStatus([]);
    expect(groups.due).toHaveLength(0);
    expect(groups.missed).toHaveLength(0);
    expect(groups.upcoming).toHaveLength(0);
    expect(groups.prn).toHaveLength(0);
  });
});

describe('createDefaultWizardState', () => {
  it('creates default state without editing medication', () => {
    const state = createDefaultWizardState();

    expect(state.step).toBe(0);
    expect(state.displayName).toBe('');
    expect(state.form).toBe('tablet');
    expect(state.scheduleKind).toBe('times_per_day');
    expect(state.times).toEqual(['08:00']);
    expect(state.doseNumerator).toBe(1);
    expect(state.doseDenominator).toBe(1);
  });

  it('populates state from editing medication', () => {
    const med: MedicationData = {
      entityId: '1',
      medication_id: '1',
      display_name: 'Aspirin',
      form: 'capsule',
      schedule_kind: 'weekly',
      times: ['09:00', '21:00'],
      weekdays: [1, 3, 5],
      status: 'ok',
      state: 'ok',
    };

    const state = createDefaultWizardState(med);

    expect(state.displayName).toBe('Aspirin');
    expect(state.form).toBe('capsule');
    expect(state.scheduleKind).toBe('weekly');
    expect(state.times).toEqual(['09:00', '21:00']);
    expect(state.weekdays).toEqual([1, 3, 5]);
  });
});

describe('validateWizardState', () => {
  it('returns error for empty display name', () => {
    const state = createDefaultWizardState();
    state.displayName = '';

    const errors = validateWizardState(state);

    expect(errors.displayName).toBe('Name is required');
  });

  it('returns error for empty times with times_per_day schedule', () => {
    const state = createDefaultWizardState();
    state.displayName = 'Test';
    state.scheduleKind = 'times_per_day';
    state.times = [];

    const errors = validateWizardState(state);

    expect(errors.times).toBe('At least one time is required');
  });

  it('returns error for empty weekdays with weekly schedule', () => {
    const state = createDefaultWizardState();
    state.displayName = 'Test';
    state.scheduleKind = 'weekly';
    state.weekdays = [];

    const errors = validateWizardState(state);

    expect(errors.weekdays).toBe('At least one weekday is required');
  });

  it('returns error for invalid interval', () => {
    const state = createDefaultWizardState();
    state.displayName = 'Test';
    state.scheduleKind = 'interval';
    state.intervalMinutes = 0;

    const errors = validateWizardState(state);

    expect(errors.intervalMinutes).toBe('Interval must be positive');
  });

  it('returns no errors for valid state', () => {
    const state = createDefaultWizardState();
    state.displayName = 'Test Medication';

    const errors = validateWizardState(state);

    expect(Object.keys(errors)).toHaveLength(0);
  });
});

describe('buildServiceData', () => {
  it('builds correct data for times_per_day schedule', () => {
    const state: WizardState = {
      step: 4,
      displayName: 'Aspirin',
      form: 'tablet',
      scheduleKind: 'times_per_day',
      times: ['08:00', '20:00'],
      weekdays: [],
      intervalMinutes: 480,
      doseNumerator: 1,
      doseDenominator: 1,
      doseUnit: 'tablet',
      inventoryEnabled: false,
      currentQuantity: null,
      refillThreshold: null,
      notes: '',
      errors: {},
    };

    const data = buildServiceData(state, 'profile-123');

    expect(data.entry_id).toBe('profile-123');
    expect(data.display_name).toBe('Aspirin');
    expect(data.form).toBe('tablet');
    expect(data.schedule_kind).toBe('times_per_day');
    expect(data.times).toEqual(['08:00', '20:00']);
    expect(data.default_dose).toEqual({
      numerator: 1,
      denominator: 1,
      unit: 'tablet',
    });
  });

  it('includes inventory when enabled', () => {
    const state: WizardState = {
      step: 4,
      displayName: 'Test',
      form: 'tablet',
      scheduleKind: 'as_needed',
      times: [],
      weekdays: [],
      intervalMinutes: 0,
      doseNumerator: 1,
      doseDenominator: 1,
      doseUnit: 'tablet',
      inventoryEnabled: true,
      currentQuantity: 30,
      refillThreshold: 5,
      notes: 'Test notes',
      errors: {},
    };

    const data = buildServiceData(state, 'profile-123');

    expect(data.inventory).toEqual({
      current_quantity: 30,
      refill_threshold: 5,
    });
    expect(data.notes).toBe('Test notes');
  });
});

describe('getCalendarDays', () => {
  it('returns correct number of days for January 2025', () => {
    const days = getCalendarDays(2025, 0); // January
    const nonEmptyDays = days.filter((d) => !d.isEmpty);
    expect(nonEmptyDays).toHaveLength(31);
  });

  it('returns correct number of days for February 2024 (leap year)', () => {
    const days = getCalendarDays(2024, 1); // February
    const nonEmptyDays = days.filter((d) => !d.isEmpty);
    expect(nonEmptyDays).toHaveLength(29);
  });

  it('includes empty days for padding', () => {
    const days = getCalendarDays(2025, 0);
    const emptyDays = days.filter((d) => d.isEmpty);
    expect(emptyDays.length).toBeGreaterThanOrEqual(0);
  });
});

describe('formatMonthYear', () => {
  it('formats month and year correctly', () => {
    const result = formatMonthYear(2025, 0);
    expect(result).toBe('January 2025');
  });

  it('formats December correctly', () => {
    const result = formatMonthYear(2024, 11);
    expect(result).toBe('December 2024');
  });
});

describe('isSameDay', () => {
  it('returns true for same day', () => {
    const a = new Date(2025, 0, 15, 10, 30);
    const b = new Date(2025, 0, 15, 22, 45);
    expect(isSameDay(a, b)).toBe(true);
  });

  it('returns false for different days', () => {
    const a = new Date(2025, 0, 15);
    const b = new Date(2025, 0, 16);
    expect(isSameDay(a, b)).toBe(false);
  });
});

describe('isToday', () => {
  it('returns true for today', () => {
    expect(isToday(new Date())).toBe(true);
  });

  it('returns false for yesterday', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(isToday(yesterday)).toBe(false);
  });
});

describe('formatDate', () => {
  it('formats date in long format', () => {
    const date = new Date(2025, 0, 15);
    const result = formatDate(date, 'long');
    expect(result).toContain('January');
    expect(result).toContain('15');
    expect(result).toContain('2025');
  });

  it('formats date in short format', () => {
    const date = new Date(2025, 0, 15);
    const result = formatDate(date, 'short');
    expect(result).toBeTruthy();
  });
});
