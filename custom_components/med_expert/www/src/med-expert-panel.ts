/**
 * Med Expert Panel - Main Component
 * Complete Medication Management Dashboard for Home Assistant
 */

import { LitElement, html, type PropertyValues } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

import type {
  HomeAssistant,
  MedicationData,
  MedicationGroups,
  ProfileEntry,
  WizardState,
} from './types';
import { TABS, FORM_OPTIONS, SCHEDULE_OPTIONS, WEEKDAY_LABELS } from './constants';
import {
  extractMedications,
  extractProfiles,
  formatNextDose,
  getFormIcon,
  getStatusIcon,
  groupMedicationsByStatus,
  createDefaultWizardState,
  validateWizardState,
  buildServiceData,
  getCalendarDays,
  getAdherenceForDay,
  getEventsForDay,
  formatDate,
  formatMonthYear,
  isToday,
  isSameDay,
} from './utils';
import {
  baseStyles,
  headerStyles,
  tabStyles,
  cardStyles,
  wizardStyles,
  calendarStyles,
  contentStyles,
  responsiveStyles,
} from './styles';

@customElement('med-expert-panel')
export class MedExpertPanel extends LitElement {
  static override styles = [
    baseStyles,
    headerStyles,
    tabStyles,
    cardStyles,
    wizardStyles,
    calendarStyles,
    contentStyles,
    responsiveStyles,
  ];

  @property({ type: Object }) hass?: HomeAssistant;
  @property({ type: Boolean }) narrow = false;
  @property({ type: Object }) route?: unknown;
  @property({ type: Object }) panel?: unknown;

  @state() private _activeTab = 'medications';
  @state() private _selectedProfile: string | null = null;
  @state() private _medications: MedicationData[] = [];
  @state() private _wizardOpen = false;
  @state() private _editingMed: MedicationData | null = null;
  @state() private _loading = false;
  @state() private _wizardState: WizardState | null = null;
  @state() private _historyMonth = new Date().getMonth();
  @state() private _historyYear = new Date().getFullYear();
  @state() private _selectedDate: Date | null = null;

  override connectedCallback(): void {
    super.connectedCallback();
    this._loadProfiles();
  }

  protected override updated(changedProps: PropertyValues): void {
    if (changedProps.has('hass') && this.hass) {
      this._updateMedications();
    }
  }

  private _loadProfiles(): void {
    if (!this.hass) return;

    const profiles = extractProfiles(this.hass);
    if (profiles.length > 0 && !this._selectedProfile) {
      this._selectedProfile = profiles[0].id;
    }
  }

  private _updateMedications(): void {
    if (!this.hass) return;
    this._medications = extractMedications(this.hass);
  }

  private async _callService(
    service: string,
    data: Record<string, unknown>
  ): Promise<void> {
    if (!this.hass) return;

    this._loading = true;
    try {
      await this.hass.callService('med_expert', service, data);
      this._showToast(`${service} successful`, 'success');
    } catch (error) {
      console.error('Service call failed:', error);
      this._showToast(
        `Failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'error'
      );
    } finally {
      this._loading = false;
    }
  }

  private _showToast(message: string, _type: string = 'info'): void {
    const event = new CustomEvent('hass-notification', {
      detail: { message, duration: 3000 },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  private _getProfiles(): ProfileEntry[] {
    if (!this.hass) return [];
    return extractProfiles(this.hass);
  }

  private _getProfileId(): string | null {
    return this._selectedProfile;
  }

  private async _handleAction(action: string, medId: string): Promise<void> {
    const profileId = this._getProfileId();
    if (!profileId) return;

    switch (action) {
      case 'take':
      case 'prn-take':
        await this._callService(action === 'prn-take' ? 'prn_take' : 'take', {
          entry_id: profileId,
          medication_id: medId,
        });
        break;
      case 'snooze':
        await this._callService('snooze', {
          entry_id: profileId,
          medication_id: medId,
          minutes: 15,
        });
        break;
      case 'skip':
        await this._callService('skip', {
          entry_id: profileId,
          medication_id: medId,
        });
        break;
    }
  }

  private _editMedication(med: MedicationData): void {
    this._editingMed = med;
    this._wizardState = createDefaultWizardState(med);
    this._wizardOpen = true;
  }

  private _openWizard(): void {
    this._wizardState = createDefaultWizardState();
    this._wizardOpen = true;
  }

  private _closeWizard(): void {
    this._wizardOpen = false;
    this._editingMed = null;
    this._wizardState = null;
  }

  private async _submitWizard(): Promise<void> {
    if (!this._wizardState) return;

    const errors = validateWizardState(this._wizardState);
    if (Object.keys(errors).length > 0) {
      this._wizardState = { ...this._wizardState, errors };
      return;
    }

    const profileId = this._getProfileId();
    if (!profileId) return;

    const data = buildServiceData(this._wizardState, profileId);
    await this._callService('add_medication', data);
    this._closeWizard();
  }

  private _changeMonth(delta: number): void {
    const newDate = new Date(this._historyYear, this._historyMonth + delta, 1);
    this._historyMonth = newDate.getMonth();
    this._historyYear = newDate.getFullYear();
  }

  private _selectDay(date: Date): void {
    this._selectedDate = date;
  }

  private async _refillMedication(med: MedicationData): Promise<void> {
    const quantity = prompt('Enter quantity to add:', '30');
    if (!quantity) return;

    await this._callService('refill', {
      entry_id: this._getProfileId(),
      medication_id: med.medication_id,
      quantity: parseInt(quantity),
    });
  }

  protected override render() {
    if (this._loading) {
      return html`
        <div class="panel-container loading">
          <ha-icon icon="mdi:loading" class="spin"></ha-icon>
          <span>Loading...</span>
        </div>
      `;
    }
    return html`
      <div class="panel-container">
        ${this._renderHeader()} ${this._renderTabs()} ${this._renderContent()}
        ${this._wizardOpen ? this._renderWizard() : ''}
      </div>
    `;
  }

  private _renderHeader() {
    const profiles = this._getProfiles();
    const adherenceEntity = this.hass?.states?.[this._selectedProfile || ''];
    const adherenceRate = adherenceEntity?.state || 'N/A';

    return html`
      <header class="header">
        <div class="header-content">
          <div class="logo">
            <ha-icon icon="mdi:pill"></ha-icon>
            <h1>Med Expert</h1>
          </div>

          ${profiles.length > 1
            ? html`
                <select
                  class="profile-select"
                  @change=${(e: Event) =>
                    (this._selectedProfile = (e.target as HTMLSelectElement).value)}
                >
                  ${profiles.map(
                    (p) => html`
                      <option
                        value="${p.id}"
                        ?selected=${p.id === this._selectedProfile}
                      >
                        ${p.name}
                      </option>
                    `
                  )}
                </select>
              `
            : html`<h2>${profiles[0]?.name}</h2>`}

          <div class="header-stats">
            <div class="stat">
              <span class="stat-value">${this._medications.length}</span>
              <span class="stat-label">Medications</span>
            </div>
            <div class="stat">
              <span class="stat-value">${adherenceRate}%</span>
              <span class="stat-label">Adherence</span>
            </div>
          </div>
        </div>
      </header>
    `;
  }

  private _renderTabs() {
    return html`
      <nav class="tabs">
        ${TABS.map(
          (tab) => html`
            <button
              class="tab ${this._activeTab === tab.id ? 'active' : ''}"
              @click=${() => (this._activeTab = tab.id)}
            >
              <ha-icon icon="${tab.icon}"></ha-icon>
              ${!this.narrow ? html`<span>${tab.label}</span>` : ''}
            </button>
          `
        )}
      </nav>
    `;
  }

  private _renderContent() {
    switch (this._activeTab) {
      case 'medications':
        return this._renderMedicationsTab();
      case 'adherence':
        return this._renderAdherenceTab();
      case 'inventory':
        return this._renderInventoryTab();
      case 'history':
        return this._renderHistoryTab();
      case 'settings':
        return this._renderSettingsTab();
      default:
        return html`<div>Unknown tab</div>`;
    }
  }

  private _renderMedicationsTab() {
    const grouped: MedicationGroups = groupMedicationsByStatus(this._medications);

    return html`
      <div class="content medications-content">
        <div class="content-header">
          <h2>Your Medications</h2>
          <button class="btn-primary" @click=${this._openWizard}>
            <ha-icon icon="mdi:plus"></ha-icon>
            Add Medication
          </button>
        </div>

        ${grouped.due.length > 0
          ? html`
              <section class="med-section">
                <h3><ha-icon icon="mdi:bell-ring"></ha-icon> Due Now</h3>
                <div class="med-list">
                  ${grouped.due.map((med) => this._renderMedicationCard(med))}
                </div>
              </section>
            `
          : ''}
        ${grouped.missed.length > 0
          ? html`
              <section class="med-section">
                <h3><ha-icon icon="mdi:alert-circle"></ha-icon> Missed</h3>
                <div class="med-list">
                  ${grouped.missed.map((med) => this._renderMedicationCard(med))}
                </div>
              </section>
            `
          : ''}
        ${grouped.upcoming.length > 0
          ? html`
              <section class="med-section">
                <h3><ha-icon icon="mdi:clock-outline"></ha-icon> Upcoming</h3>
                <div class="med-list">
                  ${grouped.upcoming.map((med) => this._renderMedicationCard(med))}
                </div>
              </section>
            `
          : ''}
        ${grouped.prn.length > 0
          ? html`
              <section class="med-section">
                <h3><ha-icon icon="mdi:hand-extended"></ha-icon> As Needed</h3>
                <div class="med-list">
                  ${grouped.prn.map((med) => this._renderMedicationCard(med))}
                </div>
              </section>
            `
          : ''}
      </div>
    `;
  }

  private _renderMedicationCard(med: MedicationData) {
    const status = (med.status || med.state || 'ok').toLowerCase();
    const isPRN = status === 'prn';
    const needsAction = status === 'due' || status === 'missed';

    return html`
      <div class="med-card" data-status="${status}">
        <div class="med-card-header">
          <ha-icon icon="${getFormIcon(med.form)}"></ha-icon>
          <div class="med-info">
            <h4>${med.display_name || med.medication_name || 'Unknown'}</h4>
            <span class="med-dose">${med.default_dose || 'Dose not specified'}</span>
          </div>
          <button class="btn-icon" @click=${() => this._editMedication(med)}>
            <ha-icon icon="mdi:pencil"></ha-icon>
          </button>
        </div>

        <div class="med-card-body">
          <div class="med-detail">
            <ha-icon icon="mdi:clock-outline"></ha-icon>
            <span>${formatNextDose(med.next_dose_at)}</span>
          </div>

          ${med.inventory
            ? html`
                <div class="med-detail inventory">
                  <ha-icon icon="mdi:package-variant"></ha-icon>
                  <span
                    >${med.inventory.current_quantity || 0}
                    ${med.inventory.unit || 'units'}</span
                  >
                  ${med.inventory.low_stock
                    ? html` <ha-icon class="warning" icon="mdi:alert"></ha-icon> `
                    : ''}
                </div>
              `
            : ''}
        </div>

        <div class="med-card-actions">
          ${isPRN
            ? html`
                <button
                  class="action-btn take"
                  @click=${() => this._handleAction('prn-take', med.medication_id)}
                >
                  <ha-icon icon="mdi:check"></ha-icon>
                  Take as needed
                </button>
              `
            : needsAction
              ? html`
                  <button
                    class="action-btn take"
                    @click=${() => this._handleAction('take', med.medication_id)}
                  >
                    <ha-icon icon="mdi:check"></ha-icon>
                    Taken
                  </button>
                  <button
                    class="action-btn snooze"
                    @click=${() => this._handleAction('snooze', med.medication_id)}
                  >
                    <ha-icon icon="mdi:clock-outline"></ha-icon>
                    Snooze
                  </button>
                  <button
                    class="action-btn skip"
                    @click=${() => this._handleAction('skip', med.medication_id)}
                  >
                    <ha-icon icon="mdi:close"></ha-icon>
                    Skip
                  </button>
                `
              : html`
                  <span class="status-badge status-${status}">
                    <ha-icon icon="${getStatusIcon(status)}"></ha-icon>
                    ${status.toUpperCase()}
                  </span>
                `}
        </div>
      </div>
    `;
  }

  private _renderAdherenceTab() {
    return html`
      <div class="content">
        <h2>Adherence Statistics</h2>
        <p>Coming soon: Charts and adherence tracking</p>
      </div>
    `;
  }

  private _renderInventoryTab() {
    const lowStockMeds = this._medications.filter((m) => m.inventory?.low_stock);

    return html`
      <div class="content">
        <h2>Inventory Management</h2>

        ${lowStockMeds.length > 0
          ? html`
              <div class="alert alert-warning">
                <ha-icon icon="mdi:alert"></ha-icon>
                <span>${lowStockMeds.length} medication(s) running low</span>
              </div>
            `
          : ''}

        <div class="inventory-list">
          ${this._medications
            .filter((m) => m.inventory)
            .map(
              (med) => html`
                <div class="inventory-item">
                  <div class="item-info">
                    <h4>${med.display_name}</h4>
                    <span
                      >${med.inventory?.current_quantity || 0}
                      ${med.inventory?.unit || 'units'}</span
                    >
                  </div>
                  <button
                    class="btn-secondary"
                    @click=${() => this._refillMedication(med)}
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                    Refill
                  </button>
                </div>
              `
            )}
        </div>
      </div>
    `;
  }

  private _renderHistoryTab() {
    const today = new Date();

    return html`
      <div class="content">
        <div class="section-header">
          <h2>Calendar View</h2>
          <div class="calendar-nav">
            <button class="btn-icon" @click=${() => this._changeMonth(-1)}>
              <ha-icon icon="mdi:chevron-left"></ha-icon>
            </button>
            <span>${formatMonthYear(this._historyYear, this._historyMonth)}</span>
            <button class="btn-icon" @click=${() => this._changeMonth(1)}>
              <ha-icon icon="mdi:chevron-right"></ha-icon>
            </button>
            <button
              class="btn-secondary"
              @click=${() => {
                this._historyMonth = today.getMonth();
                this._historyYear = today.getFullYear();
              }}
            >
              Today
            </button>
          </div>
        </div>

        ${this._renderCalendar()} ${this._renderDayDetails()}
      </div>
    `;
  }

  private _renderCalendar() {
    const days = getCalendarDays(this._historyYear, this._historyMonth);

    return html`
      <div class="calendar">
        <div class="calendar-header">
          ${WEEKDAY_LABELS.map(
            (day) => html` <div class="calendar-weekday">${day}</div> `
          )}
        </div>
        <div class="calendar-grid">
          ${days.map((dayData) => {
            if (dayData.isEmpty) {
              return html`<div class="calendar-day empty"></div>`;
            }

            const date = new Date(
              this._historyYear,
              this._historyMonth,
              dayData.day
            );
            const adherence = getAdherenceForDay(date, this._medications);
            const isSelectedDay =
              this._selectedDate && isSameDay(date, this._selectedDate);

            return html`
              <div
                class="calendar-day ${isToday(date) ? 'today' : ''} ${isSelectedDay
                  ? 'selected'
                  : ''} ${adherence.class}"
                @click=${() => this._selectDay(date)}
              >
                <span class="day-number">${dayData.day}</span>
                ${adherence.taken > 0 || adherence.total > 0
                  ? html`
                      <span class="day-doses"
                        >${adherence.taken}/${adherence.total}</span
                      >
                    `
                  : ''}
              </div>
            `;
          })}
        </div>
        <div class="calendar-legend">
          <div class="legend-item">
            <div class="legend-color perfect"></div>
            <span>Perfect</span>
          </div>
          <div class="legend-item">
            <div class="legend-color good"></div>
            <span>Good</span>
          </div>
          <div class="legend-item">
            <div class="legend-color partial"></div>
            <span>Partial</span>
          </div>
          <div class="legend-item">
            <div class="legend-color missed"></div>
            <span>Missed</span>
          </div>
        </div>
      </div>
    `;
  }

  private _renderDayDetails() {
    if (!this._selectedDate) return '';

    const events = getEventsForDay(this._selectedDate);

    return html`
      <div class="day-details">
        <h3>${formatDate(this._selectedDate)}</h3>
        ${events.length === 0
          ? html` <p class="no-data">No medication events on this day</p> `
          : html`
              <div class="events-timeline">
                ${events.map(
                  (event) => html`
                    <div class="event-item ${event.status}">
                      <div class="event-time">${event.time}</div>
                      <div class="event-content">
                        <div class="event-medication">${event.medication}</div>
                        <div class="event-dose">${event.dose}</div>
                        <div class="event-status">
                          <ha-icon icon="${getStatusIcon(event.status)}"></ha-icon>
                          ${event.statusText}
                        </div>
                      </div>
                    </div>
                  `
                )}
              </div>
            `}
      </div>
    `;
  }

  private _renderSettingsTab() {
    return html`
      <div class="content">
        <h2>Profile Settings</h2>
        <p>Coming soon: Notification settings, quiet hours, etc.</p>
      </div>
    `;
  }

  private _renderWizard() {
    if (!this._wizardState) {
      this._wizardState = createDefaultWizardState(
        this._editingMed || undefined
      );
    }

    const steps = ['Basics', 'Schedule', 'Dosage', 'Options', 'Review'];
    const s = this._wizardState;

    return html`
      <div
        class="wizard-overlay"
        @click=${(e: Event) => e.target === e.currentTarget && this._closeWizard()}
      >
        <div class="wizard">
          <div class="wizard-header">
            <h2>${this._editingMed ? 'Edit' : 'Add'} Medication</h2>
            <button class="btn-icon" @click=${this._closeWizard}>
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>

          <div class="wizard-stepper">
            ${steps.map(
              (step, idx) => html`
                <div
                  class="wizard-step ${idx === s.step ? 'active' : ''} ${idx <
                  s.step
                    ? 'completed'
                    : ''}"
                >
                  <div class="step-circle">${idx < s.step ? '✓' : idx + 1}</div>
                  <span class="step-label">${step}</span>
                </div>
                ${idx < steps.length - 1
                  ? html`<div class="step-line"></div>`
                  : ''}
              `
            )}
          </div>

          <div class="wizard-content">
            ${s.step === 0 ? this._renderWizardBasics() : ''}
            ${s.step === 1 ? this._renderWizardSchedule() : ''}
            ${s.step === 2 ? this._renderWizardDosage() : ''}
            ${s.step === 3 ? this._renderWizardOptions() : ''}
            ${s.step === 4 ? this._renderWizardReview() : ''}
          </div>

          <div class="wizard-footer">
            <button class="btn-secondary" @click=${this._closeWizard}>
              Cancel
            </button>
            ${s.step > 0
              ? html`
                  <button
                    class="btn-secondary"
                    @click=${() => {
                      if (this._wizardState) {
                        this._wizardState = { ...this._wizardState, step: s.step - 1 };
                      }
                    }}
                  >
                    Back
                  </button>
                `
              : ''}
            ${s.step < 4
              ? html`
                  <button
                    class="btn-primary"
                    @click=${() => {
                      if (this._wizardState) {
                        this._wizardState = { ...this._wizardState, step: s.step + 1 };
                      }
                    }}
                  >
                    Next
                  </button>
                `
              : html`
                  <button class="btn-primary" @click=${this._submitWizard}>
                    ${this._editingMed ? 'Save Changes' : 'Add Medication'}
                  </button>
                `}
          </div>
        </div>
      </div>
    `;
  }

  private _renderWizardBasics() {
    const s = this._wizardState!;

    return html`
      <div class="wizard-section">
        <div class="form-field">
          <label>Medication Name *</label>
          <input
            type="text"
            .value=${s.displayName}
            @input=${(e: Event) => {
              if (this._wizardState) {
                this._wizardState = {
                  ...this._wizardState,
                  displayName: (e.target as HTMLInputElement).value,
                };
              }
            }}
            placeholder="e.g., Aspirin, Metformin"
            class="form-input"
          />
          ${s.errors.displayName
            ? html`<span class="error">${s.errors.displayName}</span>`
            : ''}
        </div>

        <div class="form-field">
          <label>Dosage Form</label>
          <div class="form-grid">
            ${FORM_OPTIONS.map(
              (form) => html`
                <button
                  class="form-option ${s.form === form.id ? 'selected' : ''}"
                  @click=${() => {
                    if (this._wizardState) {
                      this._wizardState = { ...this._wizardState, form: form.id };
                    }
                  }}
                >
                  <ha-icon icon="${form.icon}"></ha-icon>
                  <span>${form.name}</span>
                </button>
              `
            )}
          </div>
        </div>
      </div>
    `;
  }

  private _renderWizardSchedule() {
    const s = this._wizardState!;

    return html`
      <div class="wizard-section">
        <div class="form-field">
          <label>Schedule Type</label>
          <div class="schedule-grid">
            ${SCHEDULE_OPTIONS.map(
              (type) => html`
                <button
                  class="schedule-option ${s.scheduleKind === type.id
                    ? 'selected'
                    : ''}"
                  @click=${() => {
                    if (this._wizardState) {
                      this._wizardState = {
                        ...this._wizardState,
                        scheduleKind: type.id,
                      };
                    }
                  }}
                >
                  <ha-icon icon="${type.icon}"></ha-icon>
                  <span>${type.name}</span>
                </button>
              `
            )}
          </div>
        </div>

        ${s.scheduleKind === 'times_per_day' || s.scheduleKind === 'weekly'
          ? html`
              <div class="form-field">
                <label>Times</label>
                ${s.times.map(
                  (time, idx) => html`
                    <div class="time-row">
                      <input
                        type="time"
                        .value=${time}
                        @change=${(e: Event) => {
                          if (this._wizardState) {
                            const newTimes = [...this._wizardState.times];
                            newTimes[idx] = (e.target as HTMLInputElement).value;
                            this._wizardState = {
                              ...this._wizardState,
                              times: newTimes,
                            };
                          }
                        }}
                        class="form-input"
                      />
                      ${s.times.length > 1
                        ? html`
                            <button
                              class="btn-icon"
                              @click=${() => {
                                if (this._wizardState) {
                                  const newTimes = this._wizardState.times.filter(
                                    (_, i) => i !== idx
                                  );
                                  this._wizardState = {
                                    ...this._wizardState,
                                    times: newTimes,
                                  };
                                }
                              }}
                            >
                              <ha-icon icon="mdi:delete"></ha-icon>
                            </button>
                          `
                        : ''}
                    </div>
                  `
                )}
                <button
                  class="btn-secondary"
                  @click=${() => {
                    if (this._wizardState) {
                      this._wizardState = {
                        ...this._wizardState,
                        times: [...this._wizardState.times, '12:00'],
                      };
                    }
                  }}
                >
                  <ha-icon icon="mdi:plus"></ha-icon>
                  Add Time
                </button>
              </div>
            `
          : ''}
        ${s.scheduleKind === 'weekly'
          ? html`
              <div class="form-field">
                <label>Weekdays</label>
                <div class="weekday-grid">
                  ${WEEKDAY_LABELS.map(
                    (day, idx) => html`
                      <button
                        class="weekday-btn ${s.weekdays.includes(idx + 1)
                          ? 'selected'
                          : ''}"
                        @click=${() => {
                          if (this._wizardState) {
                            const dayNum = idx + 1;
                            const newWeekdays = s.weekdays.includes(dayNum)
                              ? s.weekdays.filter((d) => d !== dayNum)
                              : [...s.weekdays, dayNum];
                            this._wizardState = {
                              ...this._wizardState,
                              weekdays: newWeekdays,
                            };
                          }
                        }}
                      >
                        ${day}
                      </button>
                    `
                  )}
                </div>
              </div>
            `
          : ''}
        ${s.scheduleKind === 'interval'
          ? html`
              <div class="form-field">
                <label>Interval (hours)</label>
                <input
                  type="number"
                  .value=${(s.intervalMinutes / 60).toString()}
                  @input=${(e: Event) => {
                    if (this._wizardState) {
                      this._wizardState = {
                        ...this._wizardState,
                        intervalMinutes:
                          parseInt((e.target as HTMLInputElement).value) * 60,
                      };
                    }
                  }}
                  min="1"
                  max="24"
                  class="form-input"
                />
              </div>
            `
          : ''}
        ${s.scheduleKind === 'as_needed'
          ? html`
              <div class="info-box">
                <ha-icon icon="mdi:information"></ha-icon>
                <p>
                  This medication can be taken as needed (PRN). No fixed schedule
                  will be set.
                </p>
              </div>
            `
          : ''}
      </div>
    `;
  }

  private _renderWizardDosage() {
    const s = this._wizardState!;

    return html`
      <div class="wizard-section">
        <div class="form-field">
          <label>Default Dose</label>
          <div class="dose-row">
            <input
              type="number"
              .value=${s.doseNumerator.toString()}
              @input=${(e: Event) => {
                if (this._wizardState) {
                  this._wizardState = {
                    ...this._wizardState,
                    doseNumerator: parseInt((e.target as HTMLInputElement).value),
                  };
                }
              }}
              min="1"
              class="form-input dose-input"
              placeholder="1"
            />
            <span>/</span>
            <input
              type="number"
              .value=${s.doseDenominator.toString()}
              @input=${(e: Event) => {
                if (this._wizardState) {
                  this._wizardState = {
                    ...this._wizardState,
                    doseDenominator: parseInt((e.target as HTMLInputElement).value),
                  };
                }
              }}
              min="1"
              class="form-input dose-input"
              placeholder="1"
            />
            <input
              type="text"
              .value=${s.doseUnit}
              @input=${(e: Event) => {
                if (this._wizardState) {
                  this._wizardState = {
                    ...this._wizardState,
                    doseUnit: (e.target as HTMLInputElement).value,
                  };
                }
              }}
              class="form-input"
              placeholder="tablet"
              list="units-list"
            />
            <datalist id="units-list">
              <option>tablet</option>
              <option>capsule</option>
              <option>ml</option>
              <option>mg</option>
              <option>puff</option>
              <option>spray</option>
              <option>drop</option>
            </datalist>
          </div>
          <small>e.g., 1/2 tablet or 2/1 ml</small>
        </div>
      </div>
    `;
  }

  private _renderWizardOptions() {
    const s = this._wizardState!;

    return html`
      <div class="wizard-section">
        <div class="form-field">
          <label class="checkbox-label">
            <input
              type="checkbox"
              .checked=${s.inventoryEnabled}
              @change=${(e: Event) => {
                if (this._wizardState) {
                  this._wizardState = {
                    ...this._wizardState,
                    inventoryEnabled: (e.target as HTMLInputElement).checked,
                  };
                }
              }}
            />
            <span>Track Inventory</span>
          </label>
        </div>

        ${s.inventoryEnabled
          ? html`
              <div class="form-field">
                <label>Current Quantity</label>
                <input
                  type="number"
                  .value=${s.currentQuantity?.toString() || ''}
                  @input=${(e: Event) => {
                    if (this._wizardState) {
                      this._wizardState = {
                        ...this._wizardState,
                        currentQuantity:
                          parseInt((e.target as HTMLInputElement).value) || null,
                      };
                    }
                  }}
                  min="0"
                  class="form-input"
                  placeholder="e.g., 30"
                />
              </div>

              <div class="form-field">
                <label>Refill Threshold</label>
                <input
                  type="number"
                  .value=${s.refillThreshold?.toString() || ''}
                  @input=${(e: Event) => {
                    if (this._wizardState) {
                      this._wizardState = {
                        ...this._wizardState,
                        refillThreshold:
                          parseInt((e.target as HTMLInputElement).value) || null,
                      };
                    }
                  }}
                  min="0"
                  class="form-input"
                  placeholder="e.g., 5"
                />
                <small>Get notified when inventory drops below this amount</small>
              </div>
            `
          : ''}

        <div class="form-field">
          <label>Notes (optional)</label>
          <textarea
            .value=${s.notes}
            @input=${(e: Event) => {
              if (this._wizardState) {
                this._wizardState = {
                  ...this._wizardState,
                  notes: (e.target as HTMLTextAreaElement).value,
                };
              }
            }}
            class="form-textarea"
            placeholder="Additional information..."
            rows="3"
          ></textarea>
        </div>
      </div>
    `;
  }

  private _renderWizardReview() {
    const s = this._wizardState!;

    return html`
      <div class="wizard-section review">
        <h3>Review Medication</h3>

        <div class="review-item">
          <span class="review-label">Name:</span>
          <span class="review-value">${s.displayName}</span>
        </div>

        <div class="review-item">
          <span class="review-label">Form:</span>
          <span class="review-value">${s.form}</span>
        </div>

        <div class="review-item">
          <span class="review-label">Schedule:</span>
          <span class="review-value">
            ${s.scheduleKind === 'times_per_day'
              ? `${s.times.length}x daily at ${s.times.join(', ')}`
              : ''}
            ${s.scheduleKind === 'interval'
              ? `Every ${s.intervalMinutes / 60} hours`
              : ''}
            ${s.scheduleKind === 'weekly'
              ? `Weekly on ${s.weekdays.map((d) => WEEKDAY_LABELS[d - 1]).join(', ')}`
              : ''}
            ${s.scheduleKind === 'as_needed' ? 'As needed (PRN)' : ''}
          </span>
        </div>

        <div class="review-item">
          <span class="review-label">Dose:</span>
          <span class="review-value"
            >${s.doseNumerator}/${s.doseDenominator} ${s.doseUnit}</span
          >
        </div>

        ${s.inventoryEnabled
          ? html`
              <div class="review-item">
                <span class="review-label">Inventory:</span>
                <span class="review-value">
                  ${s.currentQuantity || 0} units (refill at
                  ${s.refillThreshold || 0})
                </span>
              </div>
            `
          : ''}
        ${s.notes
          ? html`
              <div class="review-item">
                <span class="review-label">Notes:</span>
                <span class="review-value">${s.notes}</span>
              </div>
            `
          : ''}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'med-expert-panel': MedExpertPanel;
  }
}
