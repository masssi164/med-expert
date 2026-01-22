import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { 
  HomeAssistant, 
  DosageForm, 
  ScheduleKind,
  MedicationFormData,
  DOSAGE_FORMS,
  SCHEDULE_TYPES,
  WEEKDAYS,
  DOSE_PRESETS,
} from './types';

/**
 * Add Medication Wizard - 4-step wizard for adding medications
 */
@customElement('add-medication-wizard')
export class AddMedicationWizard extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: String }) public entryId!: string;
  
  @state() private _step = 1;
  @state() private _saving = false;
  @state() private _error: string | null = null;
  
  // Form data
  @state() private _formData: MedicationFormData = {
    form: 'tablet',
    display_name: '',
    dose_numerator: 1,
    dose_denominator: 1,
    dose_unit: 'tablet',
    schedule_kind: 'times_per_day',
    times: ['08:00'],
    weekdays: [0, 1, 2, 3, 4], // Mo-Fr
    interval_minutes: 480, // 8 hours
    track_inventory: false,
    current_quantity: 30,
    refill_threshold: 7,
    grace_minutes: 30,
    snooze_minutes: 10,
  };

  static styles = css`
    :host {
      display: block;
    }

    .wizard-container {
      background: var(--card-background-color);
      border-radius: 12px;
      overflow: hidden;
      max-width: 500px;
      margin: 0 auto;
    }

    .wizard-header {
      background: var(--primary-color);
      color: var(--text-primary-color);
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .wizard-header h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 500;
    }

    .step-indicator {
      font-size: 14px;
      opacity: 0.9;
    }

    .wizard-content {
      padding: 24px;
      min-height: 300px;
    }

    .wizard-footer {
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      border-top: 1px solid var(--divider-color);
    }

    .step-title {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 20px;
      color: var(--primary-text-color);
    }

    /* Form Grid */
    .form-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .form-grid-2 {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    /* Form Type Cards */
    .form-type-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px 8px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      background: var(--card-background-color);
    }

    .form-type-card:hover {
      border-color: var(--primary-color);
      background: var(--secondary-background-color);
    }

    .form-type-card.selected {
      border-color: var(--primary-color);
      background: rgba(var(--rgb-primary-color), 0.1);
    }

    .form-type-icon {
      font-size: 32px;
      margin-bottom: 8px;
    }

    .form-type-label {
      font-size: 12px;
      text-align: center;
      color: var(--primary-text-color);
    }

    /* Input Fields */
    .field {
      margin-bottom: 16px;
    }

    .field label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: var(--secondary-text-color);
      margin-bottom: 6px;
      text-transform: uppercase;
    }

    .field input, .field select {
      width: 100%;
      padding: 12px;
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      font-size: 16px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      box-sizing: border-box;
    }

    .field input:focus, .field select:focus {
      outline: none;
      border-color: var(--primary-color);
    }

    .field-row {
      display: flex;
      gap: 12px;
    }

    .field-row .field {
      flex: 1;
    }

    /* Dose Presets */
    .dose-presets {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .dose-preset {
      padding: 10px 16px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      font-weight: 500;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      transition: all 0.2s;
    }

    .dose-preset:hover {
      border-color: var(--primary-color);
    }

    .dose-preset.selected {
      border-color: var(--primary-color);
      background: var(--primary-color);
      color: var(--text-primary-color);
    }

    /* Schedule Type Options */
    .schedule-option {
      display: flex;
      align-items: flex-start;
      padding: 12px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 8px;
      transition: all 0.2s;
    }

    .schedule-option:hover {
      border-color: var(--primary-color);
    }

    .schedule-option.selected {
      border-color: var(--primary-color);
      background: rgba(var(--rgb-primary-color), 0.1);
    }

    .schedule-option-icon {
      font-size: 24px;
      margin-right: 12px;
    }

    .schedule-option-content {
      flex: 1;
    }

    .schedule-option-label {
      font-weight: 500;
      color: var(--primary-text-color);
    }

    .schedule-option-desc {
      font-size: 12px;
      color: var(--secondary-text-color);
      margin-top: 2px;
    }

    /* Weekday Toggles */
    .weekday-toggles {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .weekday-toggle {
      width: 44px;
      height: 44px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-weight: 500;
      font-size: 14px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      transition: all 0.2s;
    }

    .weekday-toggle:hover {
      border-color: var(--primary-color);
    }

    .weekday-toggle.selected {
      border-color: var(--primary-color);
      background: var(--primary-color);
      color: var(--text-primary-color);
    }

    /* Time Inputs */
    .time-inputs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .time-input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }

    .time-input {
      width: 100px;
      padding: 10px 12px;
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      font-size: 16px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
    }

    .remove-time {
      position: absolute;
      right: -8px;
      top: -8px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--error-color);
      color: white;
      border: none;
      cursor: pointer;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .add-time-btn {
      padding: 10px 16px;
      border: 2px dashed var(--divider-color);
      border-radius: 8px;
      background: transparent;
      color: var(--primary-color);
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
    }

    .add-time-btn:hover {
      border-color: var(--primary-color);
      background: rgba(var(--rgb-primary-color), 0.1);
    }

    /* Checkbox */
    .checkbox-field {
      display: flex;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 16px;
    }

    .checkbox-field input {
      width: 20px;
      height: 20px;
      margin-right: 12px;
    }

    .checkbox-field span {
      color: var(--primary-text-color);
    }

    /* Buttons */
    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-primary {
      background: var(--primary-color);
      color: var(--text-primary-color);
    }

    .btn-primary:hover {
      filter: brightness(1.1);
    }

    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
    }

    .btn-secondary:hover {
      background: var(--divider-color);
    }

    .btn-text {
      background: transparent;
      color: var(--primary-color);
      padding: 12px 16px;
    }

    /* Error */
    .error {
      background: var(--error-color);
      color: white;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 16px;
    }

    /* Success */
    .success-message {
      text-align: center;
      padding: 40px 20px;
    }

    .success-icon {
      font-size: 64px;
      margin-bottom: 16px;
    }

    .success-message h3 {
      margin: 0 0 8px;
      color: var(--primary-text-color);
    }

    .success-message p {
      color: var(--secondary-text-color);
      margin: 0 0 24px;
    }
  `;

  render() {
    return html`
      <div class="wizard-container">
        <div class="wizard-header">
          <h2>Medikament hinzufügen</h2>
          <span class="step-indicator">${this._step}/4</span>
        </div>

        <div class="wizard-content">
          ${this._error ? html`<div class="error">${this._error}</div>` : ''}
          
          ${this._step === 1 ? this._renderStep1() : ''}
          ${this._step === 2 ? this._renderStep2() : ''}
          ${this._step === 3 ? this._renderStep3() : ''}
          ${this._step === 4 ? this._renderStep4() : ''}
          ${this._step === 5 ? this._renderSuccess() : ''}
        </div>

        ${this._step < 5 ? html`
          <div class="wizard-footer">
            ${this._step > 1 
              ? html`<button class="btn btn-secondary" @click=${this._prevStep}>← Zurück</button>`
              : html`<button class="btn btn-text" @click=${this._close}>Abbrechen</button>`
            }
            
            ${this._step < 4 
              ? html`<button class="btn btn-primary" @click=${this._nextStep} ?disabled=${!this._canProceed()}>Weiter →</button>`
              : html`<button class="btn btn-primary" @click=${this._save} ?disabled=${this._saving}>
                  ${this._saving ? 'Speichern...' : '💊 Medikament speichern'}
                </button>`
            }
          </div>
        ` : ''}
      </div>
    `;
  }

  private _renderStep1() {
    const forms = Object.entries(DOSAGE_FORMS) as [DosageForm, typeof DOSAGE_FORMS['tablet']][];
    
    return html`
      <div class="step-title">Was möchtest du hinzufügen?</div>
      <div class="form-grid">
        ${forms.map(([key, form]) => html`
          <div 
            class="form-type-card ${this._formData.form === key ? 'selected' : ''}"
            @click=${() => this._selectForm(key)}
          >
            <span class="form-type-icon">${form.icon}</span>
            <span class="form-type-label">${form.label}</span>
          </div>
        `)}
      </div>
    `;
  }

  private _renderStep2() {
    const formInfo = DOSAGE_FORMS[this._formData.form];
    
    return html`
      <div class="step-title">${formInfo.icon} ${formInfo.label} - Details</div>
      
      <div class="field">
        <label>Name *</label>
        <input 
          type="text" 
          placeholder="z.B. Metformin"
          .value=${this._formData.display_name}
          @input=${(e: Event) => this._updateField('display_name', (e.target as HTMLInputElement).value)}
        />
      </div>

      <div class="field-row">
        <div class="field">
          <label>Stärke (optional)</label>
          <input 
            type="text" 
            placeholder="z.B. 500"
            .value=${this._formData.strength || ''}
            @input=${(e: Event) => this._updateField('strength', (e.target as HTMLInputElement).value)}
          />
        </div>
        <div class="field">
          <label>Einheit</label>
          <select 
            .value=${this._formData.strength_unit || 'mg'}
            @change=${(e: Event) => this._updateField('strength_unit', (e.target as HTMLSelectElement).value)}
          >
            <option value="mg">mg</option>
            <option value="g">g</option>
            <option value="mcg">mcg</option>
            <option value="ml">ml</option>
            <option value="IU">IU</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>Dosis pro Einnahme</label>
        <div class="dose-presets">
          ${DOSE_PRESETS.map(preset => html`
            <div 
              class="dose-preset ${this._formData.dose_numerator === preset.numerator && this._formData.dose_denominator === preset.denominator ? 'selected' : ''}"
              @click=${() => this._selectDose(preset.numerator, preset.denominator)}
            >
              ${preset.label}
            </div>
          `)}
        </div>
      </div>

      <div class="field">
        <label>Einheit</label>
        <select 
          .value=${this._formData.dose_unit}
          @change=${(e: Event) => this._updateField('dose_unit', (e.target as HTMLSelectElement).value)}
        >
          ${formInfo.units.map(unit => html`
            <option value=${unit}>${unit}</option>
          `)}
        </select>
      </div>

      <div class="field">
        <label>Notizen (optional)</label>
        <input 
          type="text" 
          placeholder="z.B. Mit dem Essen einnehmen"
          .value=${this._formData.notes || ''}
          @input=${(e: Event) => this._updateField('notes', (e.target as HTMLInputElement).value)}
        />
      </div>
    `;
  }

  private _renderStep3() {
    return html`
      <div class="step-title">Wann nimmst du ${this._formData.display_name || 'dieses Medikament'}?</div>
      
      ${(Object.entries(SCHEDULE_TYPES) as [ScheduleKind, typeof SCHEDULE_TYPES['times_per_day']][]).map(([key, type]) => html`
        <div 
          class="schedule-option ${this._formData.schedule_kind === key ? 'selected' : ''}"
          @click=${() => this._updateField('schedule_kind', key)}
        >
          <span class="schedule-option-icon">${type.icon}</span>
          <div class="schedule-option-content">
            <div class="schedule-option-label">${type.label}</div>
            <div class="schedule-option-desc">${type.description}</div>
          </div>
        </div>
      `)}

      ${this._formData.schedule_kind === 'times_per_day' ? this._renderTimesInput() : ''}
      ${this._formData.schedule_kind === 'weekly' ? this._renderWeeklyInput() : ''}
      ${this._formData.schedule_kind === 'interval' ? this._renderIntervalInput() : ''}
    `;
  }

  private _renderTimesInput() {
    return html`
      <div class="field" style="margin-top: 16px;">
        <label>Um welche Uhrzeit(en)?</label>
        <div class="time-inputs">
          ${(this._formData.times || []).map((time, index) => html`
            <div class="time-input-wrapper">
              <input 
                type="time" 
                class="time-input"
                .value=${time}
                @change=${(e: Event) => this._updateTime(index, (e.target as HTMLInputElement).value)}
              />
              ${(this._formData.times?.length || 0) > 1 ? html`
                <button class="remove-time" @click=${() => this._removeTime(index)}>×</button>
              ` : ''}
            </div>
          `)}
          <button class="add-time-btn" @click=${this._addTime}>+ Zeit</button>
        </div>
      </div>
    `;
  }

  private _renderWeeklyInput() {
    return html`
      <div class="field" style="margin-top: 16px;">
        <label>An welchen Tagen?</label>
        <div class="weekday-toggles">
          ${WEEKDAYS.map(day => html`
            <div 
              class="weekday-toggle ${(this._formData.weekdays || []).includes(day.value) ? 'selected' : ''}"
              @click=${() => this._toggleWeekday(day.value)}
            >
              ${day.short}
            </div>
          `)}
        </div>
      </div>
      ${this._renderTimesInput()}
    `;
  }

  private _renderIntervalInput() {
    return html`
      <div class="field" style="margin-top: 16px;">
        <label>Alle wie viele Stunden?</label>
        <div class="dose-presets">
          ${[4, 6, 8, 12, 24].map(hours => html`
            <div 
              class="dose-preset ${this._formData.interval_minutes === hours * 60 ? 'selected' : ''}"
              @click=${() => this._updateField('interval_minutes', hours * 60)}
            >
              ${hours}h
            </div>
          `)}
        </div>
      </div>
    `;
  }

  private _renderStep4() {
    return html`
      <div class="step-title">Bestand & Erinnerungen</div>
      
      <label class="checkbox-field" @click=${() => this._updateField('track_inventory', !this._formData.track_inventory)}>
        <input type="checkbox" .checked=${this._formData.track_inventory} />
        <span>Bestand verwalten</span>
      </label>

      ${this._formData.track_inventory ? html`
        <div class="field-row">
          <div class="field">
            <label>Aktueller Bestand</label>
            <input 
              type="number" 
              min="0"
              .value=${String(this._formData.current_quantity || 0)}
              @input=${(e: Event) => this._updateField('current_quantity', parseInt((e.target as HTMLInputElement).value) || 0)}
            />
          </div>
          <div class="field">
            <label>Warnen unter</label>
            <input 
              type="number" 
              min="1"
              .value=${String(this._formData.refill_threshold || 7)}
              @input=${(e: Event) => this._updateField('refill_threshold', parseInt((e.target as HTMLInputElement).value) || 7)}
            />
          </div>
        </div>
      ` : ''}

      <div class="field">
        <label>Gnadenfrist (Minuten)</label>
        <div class="dose-presets">
          ${[10, 15, 30, 60].map(mins => html`
            <div 
              class="dose-preset ${this._formData.grace_minutes === mins ? 'selected' : ''}"
              @click=${() => this._updateField('grace_minutes', mins)}
            >
              ${mins} min
            </div>
          `)}
        </div>
        <small style="color: var(--secondary-text-color); font-size: 11px; margin-top: 4px; display: block;">
          Zeit nach Fälligkeit bevor als "verpasst" markiert
        </small>
      </div>

      <div class="field">
        <label>Snooze-Dauer (Minuten)</label>
        <div class="dose-presets">
          ${[5, 10, 15, 30].map(mins => html`
            <div 
              class="dose-preset ${this._formData.snooze_minutes === mins ? 'selected' : ''}"
              @click=${() => this._updateField('snooze_minutes', mins)}
            >
              ${mins} min
            </div>
          `)}
        </div>
      </div>
    `;
  }

  private _renderSuccess() {
    return html`
      <div class="success-message">
        <div class="success-icon">✅</div>
        <h3>${this._formData.display_name} hinzugefügt!</h3>
        <p>Das Medikament wurde erfolgreich angelegt.</p>
        <button class="btn btn-primary" @click=${this._addAnother}>+ Weiteres hinzufügen</button>
        <button class="btn btn-text" @click=${this._close}>Fertig</button>
      </div>
    `;
  }

  // Form helpers
  private _selectForm(form: DosageForm) {
    const formInfo = DOSAGE_FORMS[form];
    this._formData = {
      ...this._formData,
      form,
      dose_unit: formInfo.units[0],
    };
    this.requestUpdate();
  }

  private _selectDose(numerator: number, denominator: number) {
    this._formData = {
      ...this._formData,
      dose_numerator: numerator,
      dose_denominator: denominator,
    };
    this.requestUpdate();
  }

  private _updateField<K extends keyof MedicationFormData>(field: K, value: MedicationFormData[K]) {
    this._formData = {
      ...this._formData,
      [field]: value,
    };
    this.requestUpdate();
  }

  private _addTime() {
    const times = [...(this._formData.times || []), '12:00'];
    this._updateField('times', times);
  }

  private _removeTime(index: number) {
    const times = [...(this._formData.times || [])];
    times.splice(index, 1);
    this._updateField('times', times);
  }

  private _updateTime(index: number, value: string) {
    const times = [...(this._formData.times || [])];
    times[index] = value;
    this._updateField('times', times);
  }

  private _toggleWeekday(day: number) {
    const weekdays = [...(this._formData.weekdays || [])];
    const index = weekdays.indexOf(day);
    if (index >= 0) {
      weekdays.splice(index, 1);
    } else {
      weekdays.push(day);
      weekdays.sort();
    }
    this._updateField('weekdays', weekdays);
  }

  // Navigation
  private _canProceed(): boolean {
    switch (this._step) {
      case 1:
        return !!this._formData.form;
      case 2:
        return !!this._formData.display_name.trim();
      case 3:
        if (this._formData.schedule_kind === 'as_needed') return true;
        if (this._formData.schedule_kind === 'times_per_day') {
          return (this._formData.times?.length || 0) > 0;
        }
        if (this._formData.schedule_kind === 'weekly') {
          return (this._formData.weekdays?.length || 0) > 0 && (this._formData.times?.length || 0) > 0;
        }
        if (this._formData.schedule_kind === 'interval') {
          return (this._formData.interval_minutes || 0) > 0;
        }
        return true;
      default:
        return true;
    }
  }

  private _nextStep() {
    if (this._canProceed()) {
      this._step++;
      this._error = null;
    }
  }

  private _prevStep() {
    if (this._step > 1) {
      this._step--;
      this._error = null;
    }
  }

  private async _save() {
    this._saving = true;
    this._error = null;

    try {
      // Build the service call data
      const displayName = this._formData.strength 
        ? `${this._formData.display_name} ${this._formData.strength}${this._formData.strength_unit || 'mg'}`
        : this._formData.display_name;

      const serviceData: Record<string, unknown> = {
        entry_id: this.entryId,
        display_name: displayName,
        schedule_kind: this._formData.schedule_kind,
        form: this._formData.form,
        default_dose: {
          numerator: this._formData.dose_numerator,
          denominator: this._formData.dose_denominator,
          unit: this._formData.dose_unit,
        },
        policy: {
          grace_minutes: this._formData.grace_minutes,
          snooze_minutes: this._formData.snooze_minutes,
        },
      };

      // Add schedule-specific fields
      if (this._formData.schedule_kind === 'times_per_day' || this._formData.schedule_kind === 'weekly') {
        serviceData.times = this._formData.times;
      }
      if (this._formData.schedule_kind === 'weekly') {
        serviceData.weekdays = this._formData.weekdays;
      }
      if (this._formData.schedule_kind === 'interval' || this._formData.schedule_kind === 'depot') {
        serviceData.interval_minutes = this._formData.interval_minutes;
      }

      // Add inventory if tracking
      if (this._formData.track_inventory) {
        serviceData.inventory = {
          current_quantity: this._formData.current_quantity,
          refill_threshold: this._formData.refill_threshold,
          auto_decrement: true,
        };
      }

      // Add notes if present
      if (this._formData.notes) {
        serviceData.notes = this._formData.notes;
      }

      // Call the service
      await this.hass.callService('med_expert', 'add_medication', serviceData);
      
      this._step = 5; // Success
    } catch (error) {
      this._error = `Fehler beim Speichern: ${error}`;
    } finally {
      this._saving = false;
    }
  }

  private _addAnother() {
    // Reset form
    this._formData = {
      form: 'tablet',
      display_name: '',
      dose_numerator: 1,
      dose_denominator: 1,
      dose_unit: 'tablet',
      schedule_kind: 'times_per_day',
      times: ['08:00'],
      weekdays: [0, 1, 2, 3, 4],
      interval_minutes: 480,
      track_inventory: false,
      current_quantity: 30,
      refill_threshold: 7,
      grace_minutes: 30,
      snooze_minutes: 10,
    };
    this._step = 1;
    this._error = null;
  }

  private _close() {
    this.dispatchEvent(new CustomEvent('close'));
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'add-medication-wizard': AddMedicationWizard;
  }
}
