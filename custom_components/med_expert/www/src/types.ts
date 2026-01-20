/**
 * Type definitions for Med Expert Panel
 * Interfaces for Home Assistant integration and medication data
 */

/**
 * Home Assistant state object
 */
export interface HassState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
  context: {
    id: string;
    parent_id: string | null;
    user_id: string | null;
  };
}

/**
 * Home Assistant instance interface (simplified)
 */
export interface HomeAssistant {
  states: Record<string, HassState>;
  callService: (
    domain: string,
    service: string,
    data?: Record<string, unknown>
  ) => Promise<void>;
  config: {
    time_zone: string;
  };
}

/**
 * Medication status values
 */
export type MedicationStatus = 'ok' | 'due' | 'snoozed' | 'missed' | 'prn';

/**
 * Dosage form types
 */
export type DosageForm =
  | 'tablet'
  | 'capsule'
  | 'injection'
  | 'inhaler'
  | 'drops'
  | 'liquid'
  | 'cream'
  | 'patch'
  | 'nasal_spray'
  | 'suppository'
  | 'powder'
  | 'other';

/**
 * Schedule kind types
 */
export type ScheduleKind =
  | 'times_per_day'
  | 'interval'
  | 'weekly'
  | 'as_needed'
  | 'depot';

/**
 * Inventory information for a medication
 */
export interface Inventory {
  current_quantity: number;
  unit?: string;
  refill_threshold?: number;
  low_stock?: boolean;
  expiry_date?: string;
}

/**
 * Dose quantity with rational representation
 */
export interface DoseQuantity {
  numerator: number;
  denominator: number;
  unit: string;
}

/**
 * Medication data from HA entity state
 */
export interface MedicationData {
  entityId: string;
  medication_id: string;
  display_name?: string;
  medication_name?: string;
  form?: DosageForm;
  schedule_kind?: ScheduleKind;
  status: MedicationStatus;
  state: string;
  default_dose?: string;
  next_dose?: DoseQuantity;
  next_dose_at?: string;
  times?: string[];
  weekdays?: number[];
  interval_minutes?: number;
  inventory?: Inventory;
  notes?: string;
}

/**
 * Profile entry from HA states
 */
export interface ProfileEntry {
  id: string;
  name: string;
}

/**
 * Grouped medications by status
 */
export interface MedicationGroups {
  due: MedicationData[];
  missed: MedicationData[];
  upcoming: MedicationData[];
  prn: MedicationData[];
}

/**
 * Wizard state for add/edit medication
 */
export interface WizardState {
  step: number;
  displayName: string;
  form: DosageForm;
  scheduleKind: ScheduleKind;
  times: string[];
  weekdays: number[];
  intervalMinutes: number;
  doseNumerator: number;
  doseDenominator: number;
  doseUnit: string;
  inventoryEnabled: boolean;
  currentQuantity: number | null;
  refillThreshold: number | null;
  notes: string;
  errors: Record<string, string>;
}

/**
 * Calendar day adherence data
 */
export interface DayAdherence {
  taken: number;
  total: number;
  class: '' | 'perfect' | 'good' | 'partial' | 'missed';
}

/**
 * Medication event for history view
 */
export interface MedicationEvent {
  time: string;
  medication: string;
  dose: string;
  status: 'taken' | 'snoozed' | 'skipped' | 'missed';
  statusText: string;
}

/**
 * Tab definition
 */
export interface TabDef {
  id: string;
  label: string;
  icon: string;
}

/**
 * Form option for wizard
 */
export interface FormOption {
  id: DosageForm;
  name: string;
  icon: string;
}

/**
 * Schedule type option for wizard
 */
export interface ScheduleOption {
  id: ScheduleKind;
  name: string;
  icon: string;
}
