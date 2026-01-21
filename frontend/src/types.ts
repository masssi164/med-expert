/**
 * Type definitions for Home Assistant
 */

export interface HomeAssistant {
  states: { [entity_id: string]: HassEntity };
  callService: (domain: string, service: string, serviceData?: object) => Promise<void>;
  callWS: (msg: object) => Promise<any>;
  language: string;
  themes: any;
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

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: { [key: string]: any };
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
  setConfig(config: any): void;
  getCardSize?(): number;
}

export interface Medication {
  medication_id: string;
  display_name: string;
  schedule_kind: string;
  status: string;
  next_due?: string;
  next_dose?: string;
}
