/**
 * Med Expert Panel - Entry Point
 * Exports all components and utilities for Home Assistant integration
 */

// Export main component
export { MedExpertPanel } from './med-expert-panel';

// Export types
export type {
  HomeAssistant,
  HassState,
  MedicationStatus,
  DosageForm,
  ScheduleKind,
  Inventory,
  DoseQuantity,
  MedicationData,
  ProfileEntry,
  MedicationGroups,
  WizardState,
  DayAdherence,
  MedicationEvent,
  TabDef,
  FormOption,
  ScheduleOption,
} from './types';

// Export constants
export {
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

// Export utilities
export {
  getStatusColor,
  getStatusIcon,
  getFormIcon,
  formatNextDose,
  formatDose,
  groupMedicationsByStatus,
  extractMedications,
  extractProfiles,
  createDefaultWizardState,
  validateWizardState,
  buildServiceData,
  getCalendarDays,
  getAdherenceForDay,
  getEventsForDay,
  formatDate,
  formatMonthYear,
  isSameDay,
  isToday,
} from './utils';
