/**
 * Type definitions for Home Assistant and Med Expert
 */

export interface HomeAssistant {
  states: { [entity_id: string]: HassEntity };
  callService: (domain: string, service: string, serviceData?: object) => Promise<void>;
  callWS: (msg: object) => Promise<unknown>;
  language: string;
  themes: Record<string, unknown>;
  panelUrl: string;
  user?: {
    id: string;
    name: string;
    is_admin: boolean;
  };
  config: {
    latitude: number;
    longitude: number;
    elevation: number;
    unit_system: {
      length: string;
      mass: string;
      temperature: string;
      volume: string;
    };
    location_name: string;
    time_zone: string;
    version: string;
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type HassEntityAttributes = Record<string, any>;

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: HassEntityAttributes;
  context: {
    id: string;
    parent_id?: string;
    user_id?: string;
  };
  last_changed: string;
  last_updated: string;
}

export interface LovelaceCard {
  hass?: HomeAssistant;
  setConfig(config: Record<string, unknown>): void;
  getCardSize?(): number;
}

// ============================================================================
// Med Expert Domain Types
// ============================================================================

export type ScheduleKind = 'times_per_day' | 'interval' | 'weekly' | 'as_needed' | 'depot';
export type MedicationStatus = 'ok' | 'due' | 'snoozed' | 'missed' | 'prn';
export type DosageForm = 'tablet' | 'capsule' | 'injection' | 'nasal_spray' | 'inhaler' | 'drops' | 'cream' | 'patch' | 'suppository' | 'liquid' | 'powder' | 'other';

export interface DoseQuantity {
  numerator: number;
  denominator: number;
  unit: string;
}

export interface Medication {
  medication_id: string;
  display_name: string;
  form?: DosageForm;
  default_unit?: string;
  schedule_kind: ScheduleKind;
  status: MedicationStatus;
  next_due?: string;
  next_dose?: DoseQuantity;
  inventory?: {
    current_quantity: number;
    unit: string;
    refill_threshold: number;
  };
  notes?: string;
  is_active: boolean;
}

export interface MedicationFormData {
  // Step 1: Form Type
  form: DosageForm;
  
  // Step 2: Details
  display_name: string;
  strength?: string;
  strength_unit?: string;
  dose_numerator: number;
  dose_denominator: number;
  dose_unit: string;
  notes?: string;
  
  // Step 3: Schedule
  schedule_kind: ScheduleKind;
  times?: string[];
  weekdays?: number[];
  interval_minutes?: number;
  
  // Step 4: Inventory & Reminders
  track_inventory: boolean;
  current_quantity?: number;
  refill_threshold?: number;
  grace_minutes: number;
  snooze_minutes: number;
}

export interface Profile {
  profile_id: string;
  name: string;
  entry_id: string;
  medications: Medication[];
  adherence_rate?: number;
}

// Dosage form metadata for UI
export const DOSAGE_FORMS: Record<DosageForm, { icon: string; label: string; units: string[] }> = {
  tablet: { icon: '💊', label: 'Tablette', units: ['tablet', 'mg', 'g'] },
  capsule: { icon: '💊', label: 'Kapsel', units: ['capsule', 'mg', 'g'] },
  injection: { icon: '💉', label: 'Spritze', units: ['ml', 'IU', 'mg', 'unit'] },
  nasal_spray: { icon: '👃', label: 'Nasenspray', units: ['spray', 'puff'] },
  inhaler: { icon: '🫁', label: 'Inhalator', units: ['puff', 'mcg'] },
  drops: { icon: '💧', label: 'Tropfen', units: ['drop', 'ml'] },
  cream: { icon: '🧴', label: 'Creme/Salbe', units: ['application', 'g'] },
  patch: { icon: '🩹', label: 'Pflaster', units: ['patch'] },
  suppository: { icon: '💊', label: 'Zäpfchen', units: ['suppository'] },
  liquid: { icon: '🧪', label: 'Saft/Lösung', units: ['ml', 'teaspoon', 'tablespoon'] },
  powder: { icon: '📦', label: 'Pulver', units: ['sachet', 'scoop', 'g'] },
  other: { icon: '📦', label: 'Sonstige', units: ['unit', 'dose', 'application'] },
};

export const SCHEDULE_TYPES: Record<ScheduleKind, { icon: string; label: string; description: string }> = {
  times_per_day: { icon: '🕐', label: 'Täglich zu festen Zeiten', description: 'z.B. 8:00, 12:00, 18:00' },
  interval: { icon: '⏱️', label: 'Alle X Stunden', description: 'z.B. alle 8 Stunden' },
  weekly: { icon: '📅', label: 'Bestimmte Wochentage', description: 'z.B. Mo, Mi, Fr' },
  as_needed: { icon: '🆘', label: 'Bei Bedarf (PRN)', description: 'Nur wenn nötig' },
  depot: { icon: '💉', label: 'Depot-Injektion', description: 'Termin-basiert (z.B. monatlich)' },
};

export const WEEKDAYS = [
  { value: 0, short: 'Mo', long: 'Montag' },
  { value: 1, short: 'Di', long: 'Dienstag' },
  { value: 2, short: 'Mi', long: 'Mittwoch' },
  { value: 3, short: 'Do', long: 'Donnerstag' },
  { value: 4, short: 'Fr', long: 'Freitag' },
  { value: 5, short: 'Sa', long: 'Samstag' },
  { value: 6, short: 'So', long: 'Sonntag' },
];

export const DOSE_PRESETS = [
  { label: '¼', numerator: 1, denominator: 4 },
  { label: '½', numerator: 1, denominator: 2 },
  { label: '1', numerator: 1, denominator: 1 },
  { label: '1½', numerator: 3, denominator: 2 },
  { label: '2', numerator: 2, denominator: 1 },
];
