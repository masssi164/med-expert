/**
 * Utility functions for Med Expert Panel
 */

import type {
  DayAdherence,
  DosageForm,
  HomeAssistant,
  MedicationData,
  MedicationEvent,
  MedicationGroups,
  MedicationStatus,
  ProfileEntry,
  WizardState,
} from './types';
import {
  FORM_ICONS,
  MS_PER_DAY,
  MS_PER_HOUR,
  MS_PER_MINUTE,
  STATUS_COLORS,
  STATUS_ICONS,
} from './constants';

/**
 * Get color for medication status
 */
export function getStatusColor(status: MedicationStatus | string): string {
  const normalized = (status || 'ok').toLowerCase();
  return STATUS_COLORS[normalized] || '#757575';
}

/**
 * Get icon for medication status
 */
export function getStatusIcon(status: string): string {
  const normalized = (status || 'ok').toLowerCase();
  return STATUS_ICONS[normalized] || 'mdi:pill';
}

/**
 * Get icon for dosage form
 */
export function getFormIcon(form: DosageForm | string | undefined): string {
  if (!form) return 'mdi:medication';
  return FORM_ICONS[form.toLowerCase()] || 'mdi:medication';
}

/**
 * Format next dose time relative to now
 */
export function formatNextDose(nextDoseAt: string | undefined): string {
  if (!nextDoseAt) return 'No schedule';

  const next = new Date(nextDoseAt);
  const now = new Date();
  const diff = next.getTime() - now.getTime();

  if (diff < 0) return 'Overdue';
  if (diff < MS_PER_HOUR) return `${Math.floor(diff / MS_PER_MINUTE)}min`;
  if (diff < MS_PER_DAY) return `${Math.floor(diff / MS_PER_HOUR)}h`;
  return next.toLocaleDateString();
}

/**
 * Format dose as readable string
 */
export function formatDose(
  numerator: number,
  denominator: number,
  unit: string
): string {
  if (denominator === 1) {
    return `${numerator} ${unit}`;
  }
  return `${numerator}/${denominator} ${unit}`;
}

/**
 * Group medications by status
 */
export function groupMedicationsByStatus(
  medications: MedicationData[]
): MedicationGroups {
  const groups: MedicationGroups = { due: [], missed: [], upcoming: [], prn: [] };

  medications.forEach((med) => {
    const status = (med.status || med.state || 'ok').toLowerCase();
    if (status === 'due') groups.due.push(med);
    else if (status === 'missed') groups.missed.push(med);
    else if (status === 'prn') groups.prn.push(med);
    else groups.upcoming.push(med);
  });

  return groups;
}

/**
 * Extract medications from HA states
 */
export function extractMedications(hass: HomeAssistant): MedicationData[] {
  return Object.keys(hass.states)
    .filter((id) => id.startsWith('sensor.') && id.includes('_medication_'))
    .map((id) => {
      const state = hass.states[id];
      return {
        entityId: id,
        ...(state.attributes as Record<string, unknown>),
        state: state.state,
        status: (state.state as MedicationStatus) || 'ok',
      } as MedicationData;
    });
}

/**
 * Extract profiles from HA states
 */
export function extractProfiles(hass: HomeAssistant): ProfileEntry[] {
  return Object.keys(hass.states)
    .filter((id) => id.startsWith('sensor.') && id.includes('adherence_rate'))
    .map((id) => ({
      id,
      name: id
        .replace('sensor.', '')
        .replace('_adherence_rate', '')
        .split('_')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' '),
    }));
}

/**
 * Create default wizard state
 */
export function createDefaultWizardState(
  editingMed?: MedicationData
): WizardState {
  return {
    step: 0,
    displayName: editingMed?.display_name || '',
    form: editingMed?.form || 'tablet',
    scheduleKind: editingMed?.schedule_kind || 'times_per_day',
    times: editingMed?.times || ['08:00'],
    weekdays: editingMed?.weekdays || [1, 2, 3, 4, 5],
    intervalMinutes: editingMed?.interval_minutes || 480,
    doseNumerator: 1,
    doseDenominator: 1,
    doseUnit: 'tablet',
    inventoryEnabled: false,
    currentQuantity: null,
    refillThreshold: null,
    notes: editingMed?.notes || '',
    errors: {},
  };
}

/**
 * Validate wizard state
 */
export function validateWizardState(state: WizardState): Record<string, string> {
  const errors: Record<string, string> = {};

  if (!state.displayName.trim()) {
    errors.displayName = 'Name is required';
  }

  if (
    (state.scheduleKind === 'times_per_day' || state.scheduleKind === 'weekly') &&
    state.times.length === 0
  ) {
    errors.times = 'At least one time is required';
  }

  if (state.scheduleKind === 'weekly' && state.weekdays.length === 0) {
    errors.weekdays = 'At least one weekday is required';
  }

  if (state.scheduleKind === 'interval' && state.intervalMinutes <= 0) {
    errors.intervalMinutes = 'Interval must be positive';
  }

  if (state.doseNumerator <= 0) {
    errors.doseNumerator = 'Dose must be positive';
  }

  if (state.doseDenominator <= 0) {
    errors.doseDenominator = 'Dose denominator must be positive';
  }

  return errors;
}

/**
 * Build service data from wizard state
 */
export function buildServiceData(
  state: WizardState,
  profileId: string
): Record<string, unknown> {
  const data: Record<string, unknown> = {
    entry_id: profileId,
    display_name: state.displayName,
    form: state.form,
    schedule_kind: state.scheduleKind,
    default_dose: {
      numerator: state.doseNumerator,
      denominator: state.doseDenominator,
      unit: state.doseUnit,
    },
  };

  if (state.scheduleKind === 'times_per_day' || state.scheduleKind === 'weekly') {
    data.times = state.times;
  }

  if (state.scheduleKind === 'weekly') {
    data.weekdays = state.weekdays;
  }

  if (state.scheduleKind === 'interval') {
    data.interval_minutes = state.intervalMinutes;
  }

  if (state.inventoryEnabled && state.currentQuantity !== null) {
    data.inventory = {
      current_quantity: state.currentQuantity,
      refill_threshold: state.refillThreshold,
    };
  }

  if (state.notes) {
    data.notes = state.notes;
  }

  return data;
}

/**
 * Get calendar days for a month
 */
export function getCalendarDays(
  year: number,
  month: number
): { day: number; isEmpty: boolean }[] {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days: { day: number; isEmpty: boolean }[] = [];

  // Empty cells for days before month starts (Monday-based week)
  const emptyDays = firstDay === 0 ? 6 : firstDay - 1;
  for (let i = 0; i < emptyDays; i++) {
    days.push({ day: 0, isEmpty: true });
  }

  // Days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    days.push({ day, isEmpty: false });
  }

  return days;
}

/**
 * Calculate adherence for a day (simplified mock)
 * TODO: Connect to actual medication log data
 */
export function getAdherenceForDay(
  _date: Date,
  medications: MedicationData[]
): DayAdherence {
  const total = medications.filter(
    (m) => m.schedule_kind !== 'as_needed'
  ).length;
  // This is mock data - real implementation would query medication logs
  const taken = Math.floor(Math.random() * (total + 1));

  let className: DayAdherence['class'] = '';
  if (total > 0) {
    const rate = taken / total;
    if (rate === 1) className = 'perfect';
    else if (rate >= 0.8) className = 'good';
    else if (rate > 0) className = 'partial';
    else className = 'missed';
  }

  return { taken, total, class: className };
}

/**
 * Get events for a day (simplified mock)
 * TODO: Connect to actual medication log data
 */
export function getEventsForDay(_date: Date): MedicationEvent[] {
  // This is mock data - real implementation would query medication logs
  return [
    {
      time: '08:00',
      medication: 'Aspirin 100mg',
      dose: '1 tablet',
      status: 'taken',
      statusText: 'Taken on time',
    },
    {
      time: '12:00',
      medication: 'Vitamin D',
      dose: '1 capsule',
      status: 'taken',
      statusText: 'Taken on time',
    },
    {
      time: '20:00',
      medication: 'Blood Pressure Med',
      dose: '1/2 tablet',
      status: 'snoozed',
      statusText: 'Snoozed 30min',
    },
  ];
}

/**
 * Format date for display
 */
export function formatDate(date: Date, format: 'short' | 'long' = 'long'): string {
  if (format === 'short') {
    return date.toLocaleDateString();
  }
  return date.toLocaleDateString('en', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Format month/year for calendar header
 */
export function formatMonthYear(year: number, month: number): string {
  return new Date(year, month).toLocaleDateString('en', {
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Check if two dates are the same day
 */
export function isSameDay(a: Date, b: Date): boolean {
  return a.toDateString() === b.toDateString();
}

/**
 * Check if a date is today
 */
export function isToday(date: Date): boolean {
  return isSameDay(date, new Date());
}
