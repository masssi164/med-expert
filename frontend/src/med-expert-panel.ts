/**
 * Med Expert Panel for Home Assistant
 * 
 * A custom panel that displays medication information and allows users to
 * interact with their medication schedule.
 */

import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

interface HomeAssistant {
  callService(domain: string, service: string, data?: Record<string, unknown>): Promise<unknown>;
  callWS<T>(msg: Record<string, unknown>): Promise<T>;
  states: {
    [entity_id: string]: unknown;
  };
}

interface Medication {
  medication_id: string;
  display_name: string;
  status: string;
  next_due?: string;
  next_dose?: string;
  form?: string;
}

interface Profile {
  profile_id: string;
  name: string;
  medications: Medication[];
}

@customElement('med-expert-panel')
export class MedExpertPanel extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public narrow = false;
  
  @state() private _profiles: Profile[] = [];
  @state() private _loading = true;
  @state() private _error: string | null = null;

  static styles = css`
    :host {
      display: block;
      padding: 16px;
      background: var(--primary-background-color);
      min-height: 100vh;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
    }

    h1 {
      margin: 0;
      font-size: 32px;
      font-weight: 300;
      color: var(--primary-text-color);
    }

    .loading {
      text-align: center;
      padding: 48px;
      color: var(--secondary-text-color);
    }

    .error {
      padding: 16px;
      margin: 16px 0;
      background: var(--error-color);
      color: white;
      border-radius: 8px;
    }

    .profile {
      margin-bottom: 32px;
    }

    .profile-header {
      font-size: 24px;
      font-weight: 500;
      margin-bottom: 16px;
      color: var(--primary-text-color);
    }

    .medications {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }

    .medication-card {
      background: var(--card-background-color);
      border-radius: 8px;
      padding: 16px;
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
    }

    .medication-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .medication-name {
      font-size: 18px;
      font-weight: 500;
      color: var(--primary-text-color);
    }

    .medication-status {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .status-ok {
      background: var(--success-color, #4caf50);
      color: white;
    }

    .status-due {
      background: var(--warning-color, #ff9800);
      color: white;
    }

    .status-missed {
      background: var(--error-color, #f44336);
      color: white;
    }

    .status-snoozed {
      background: var(--info-color, #2196f3);
      color: white;
    }

    .medication-info {
      margin: 12px 0;
      color: var(--secondary-text-color);
      font-size: 14px;
    }

    .medication-actions {
      display: flex;
      gap: 8px;
      margin-top: 16px;
    }

    button {
      flex: 1;
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    button:hover {
      filter: brightness(1.1);
    }

    button:active {
      transform: scale(0.98);
    }

    .btn-take {
      background: var(--success-color, #4caf50);
      color: white;
    }

    .btn-snooze {
      background: var(--warning-color, #ff9800);
      color: white;
    }

    .btn-skip {
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
    }

    .btn-prn {
      background: var(--primary-color);
      color: white;
    }

    .empty-state {
      text-align: center;
      padding: 48px;
      color: var(--secondary-text-color);
    }

    .empty-state-icon {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.3;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this._loadData();
  }

  private async _loadData() {
    try {
      this._loading = true;
      this._error = null;

      // Load profiles from Home Assistant
      // This will need to be adjusted based on how data is exposed
      const result = await this.hass.callWS<{ profiles: Profile[] }>({
        type: 'med_expert/get_profiles',
      });

      this._profiles = result.profiles || [];
      this._loading = false;
    } catch (err) {
      const error = err as Error;
      this._error = error.message || 'Failed to load data';
      this._loading = false;
    }
  }

  private async _handleTake(profileId: string, medicationId: string) {
    try {
      await this.hass.callService('med_expert', 'take', {
        entry_id: profileId,
        medication_id: medicationId,
      });
      await this._loadData();
    } catch (err) {
      const error = err as Error;
      this._error = `Failed to take medication: ${error.message}`;
    }
  }

  private async _handleSnooze(profileId: string, medicationId: string) {
    try {
      await this.hass.callService('med_expert', 'snooze', {
        entry_id: profileId,
        medication_id: medicationId,
      });
      await this._loadData();
    } catch (err) {
      const error = err as Error;
      this._error = `Failed to snooze: ${error.message}`;
    }
  }

  private async _handleSkip(profileId: string, medicationId: string) {
    try {
      await this.hass.callService('med_expert', 'skip', {
        entry_id: profileId,
        medication_id: medicationId,
      });
      await this._loadData();
    } catch (err) {
      const error = err as Error;
      this._error = `Failed to skip: ${error.message}`;
    }
  }

  private async _handlePrnTake(profileId: string, medicationId: string) {
    try {
      await this.hass.callService('med_expert', 'prn_take', {
        entry_id: profileId,
        medication_id: medicationId,
      });
      await this._loadData();
    } catch (err) {
      const error = err as Error;
      this._error = `Failed to log PRN: ${error.message}`;
    }
  }

  private _getStatusClass(status: string): string {
    return `medication-status status-${status.toLowerCase()}`;
  }

  private _renderMedication(profile: Profile, med: Medication) {
    const isScheduled = med.status !== 'prn';
    const showActions = med.status === 'due' || med.status === 'missed';

    return html`
      <div class="medication-card">
        <div class="medication-header">
          <div class="medication-name">${med.display_name}</div>
          <div class="${this._getStatusClass(med.status)}">${med.status}</div>
        </div>
        
        <div class="medication-info">
          ${med.next_dose ? html`<div>Next Dose: ${med.next_dose}</div>` : ''}
          ${med.next_due ? html`<div>Due: ${new Date(med.next_due).toLocaleString()}</div>` : ''}
          ${med.form ? html`<div>Form: ${med.form}</div>` : ''}
        </div>

        <div class="medication-actions">
          ${showActions
            ? html`
                <button
                  class="btn-take"
                  @click=${() => this._handleTake(profile.profile_id, med.medication_id)}
                >
                  ✓ Take
                </button>
                <button
                  class="btn-snooze"
                  @click=${() => this._handleSnooze(profile.profile_id, med.medication_id)}
                >
                  ⏰ Snooze
                </button>
                ${isScheduled
                  ? html`
                      <button
                        class="btn-skip"
                        @click=${() => this._handleSkip(profile.profile_id, med.medication_id)}
                      >
                        ⏭ Skip
                      </button>
                    `
                  : ''}
              `
            : ''}
          ${med.status === 'prn'
            ? html`
                <button
                  class="btn-prn"
                  @click=${() => this._handlePrnTake(profile.profile_id, med.medication_id)}
                >
                  💊 Log Intake
                </button>
              `
            : ''}
        </div>
      </div>
    `;
  }

  private _renderProfile(profile: Profile) {
    return html`
      <div class="profile">
        <div class="profile-header">${profile.name}</div>
        ${profile.medications.length > 0
          ? html`
              <div class="medications">
                ${profile.medications.map(med => this._renderMedication(profile, med))}
              </div>
            `
          : html`
              <div class="empty-state">
                <div class="empty-state-icon">💊</div>
                <div>No medications in this profile</div>
              </div>
            `}
      </div>
    `;
  }

  render() {
    if (this._loading) {
      return html`
        <div class="loading">
          <ha-circular-progress active></ha-circular-progress>
          <div>Loading medications...</div>
        </div>
      `;
    }

    return html`
      <div class="header">
        <h1>Med Expert</h1>
      </div>

      ${this._error
        ? html`<div class="error">${this._error}</div>`
        : ''}

      ${this._profiles.length > 0
        ? this._profiles.map(profile => this._renderProfile(profile))
        : html`
            <div class="empty-state">
              <div class="empty-state-icon">💊</div>
              <div>No medication profiles configured</div>
              <div style="margin-top: 16px">
                <a href="/config/integrations">Configure Med Expert</a>
              </div>
            </div>
          `}
    `;
  }
}

// Register the panel with Home Assistant
declare global {
  interface HTMLElementTagNameMap {
    'med-expert-panel': MedExpertPanel;
  }
}
