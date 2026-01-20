/**
 * Tests for constants
 */

import { describe, it, expect } from 'vitest';
import {
  STATUS_COLORS,
  STATUS_ICONS,
  FORM_ICONS,
  TABS,
  FORM_OPTIONS,
  SCHEDULE_OPTIONS,
  WEEKDAY_LABELS,
  DOSE_UNITS,
  MS_PER_MINUTE,
  MS_PER_HOUR,
  MS_PER_DAY,
} from './constants';

describe('STATUS_COLORS', () => {
  it('has all required statuses', () => {
    expect(STATUS_COLORS).toHaveProperty('due');
    expect(STATUS_COLORS).toHaveProperty('missed');
    expect(STATUS_COLORS).toHaveProperty('snoozed');
    expect(STATUS_COLORS).toHaveProperty('ok');
    expect(STATUS_COLORS).toHaveProperty('prn');
  });

  it('has valid hex colors', () => {
    Object.values(STATUS_COLORS).forEach((color) => {
      expect(color).toMatch(/^#[0-9a-fA-F]{6}$/);
    });
  });
});

describe('STATUS_ICONS', () => {
  it('has all required statuses', () => {
    expect(STATUS_ICONS).toHaveProperty('due');
    expect(STATUS_ICONS).toHaveProperty('missed');
    expect(STATUS_ICONS).toHaveProperty('snoozed');
    expect(STATUS_ICONS).toHaveProperty('ok');
    expect(STATUS_ICONS).toHaveProperty('prn');
  });

  it('has valid mdi icon format', () => {
    Object.values(STATUS_ICONS).forEach((icon) => {
      expect(icon).toMatch(/^mdi:[a-z-]+$/);
    });
  });
});

describe('FORM_ICONS', () => {
  it('has common dosage forms', () => {
    expect(FORM_ICONS).toHaveProperty('tablet');
    expect(FORM_ICONS).toHaveProperty('capsule');
    expect(FORM_ICONS).toHaveProperty('injection');
    expect(FORM_ICONS).toHaveProperty('inhaler');
  });

  it('has valid mdi icon format', () => {
    Object.values(FORM_ICONS).forEach((icon) => {
      expect(icon).toMatch(/^mdi:[a-z-]+$/);
    });
  });
});

describe('TABS', () => {
  it('has correct number of tabs', () => {
    expect(TABS).toHaveLength(5);
  });

  it('has required properties for each tab', () => {
    TABS.forEach((tab) => {
      expect(tab).toHaveProperty('id');
      expect(tab).toHaveProperty('label');
      expect(tab).toHaveProperty('icon');
    });
  });

  it('includes medications tab', () => {
    const medicationsTab = TABS.find((t) => t.id === 'medications');
    expect(medicationsTab).toBeDefined();
    expect(medicationsTab?.label).toBe('Medications');
  });
});

describe('FORM_OPTIONS', () => {
  it('has common dosage forms', () => {
    const ids = FORM_OPTIONS.map((f) => f.id);
    expect(ids).toContain('tablet');
    expect(ids).toContain('capsule');
    expect(ids).toContain('injection');
  });

  it('has required properties for each option', () => {
    FORM_OPTIONS.forEach((option) => {
      expect(option).toHaveProperty('id');
      expect(option).toHaveProperty('name');
      expect(option).toHaveProperty('icon');
    });
  });
});

describe('SCHEDULE_OPTIONS', () => {
  it('has all schedule types', () => {
    const ids = SCHEDULE_OPTIONS.map((s) => s.id);
    expect(ids).toContain('times_per_day');
    expect(ids).toContain('interval');
    expect(ids).toContain('weekly');
    expect(ids).toContain('as_needed');
  });
});

describe('WEEKDAY_LABELS', () => {
  it('has 7 days', () => {
    expect(WEEKDAY_LABELS).toHaveLength(7);
  });

  it('starts with Monday', () => {
    expect(WEEKDAY_LABELS[0]).toBe('Mon');
  });

  it('ends with Sunday', () => {
    expect(WEEKDAY_LABELS[6]).toBe('Sun');
  });
});

describe('DOSE_UNITS', () => {
  it('has common units', () => {
    expect(DOSE_UNITS).toContain('tablet');
    expect(DOSE_UNITS).toContain('capsule');
    expect(DOSE_UNITS).toContain('ml');
    expect(DOSE_UNITS).toContain('mg');
  });
});

describe('Time constants', () => {
  it('has correct millisecond values', () => {
    expect(MS_PER_MINUTE).toBe(60_000);
    expect(MS_PER_HOUR).toBe(3_600_000);
    expect(MS_PER_DAY).toBe(86_400_000);
  });

  it('has correct relationships', () => {
    expect(MS_PER_HOUR).toBe(MS_PER_MINUTE * 60);
    expect(MS_PER_DAY).toBe(MS_PER_HOUR * 24);
  });
});
