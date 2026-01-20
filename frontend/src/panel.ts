import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, LovelaceCard } from './types';

/**
 * Med Expert Panel - Main frontend panel for medication management
 */
@customElement('med-expert-panel')
export class MedExpertPanel extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public narrow = false;

  @state() private _medications: any[] = [];
  @state() private _profiles: any[] = [];
  @state() private _loading = true;
  @state() private _error: string | null = null;

  static styles = css`
    :host {
      display: block;
      padding: 16px;
      background-color: var(--primary-background-color);
      color: var(--primary-text-color);
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .header h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 400;
    }

    .loading {
      text-align: center;
      padding: 48px;
      color: var(--secondary-text-color);
    }

    .error {
      background-color: var(--error-color);
      color: var(--text-primary-color);
      padding: 16px;
      border-radius: 4px;
      margin-bottom: 16px;
    }

    .medications-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }

    .medication-card {
      background-color: var(--card-background-color);
      border-radius: 8px;
      padding: 16px;
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
    }

    .medication-name {
      font-size: 18px;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .medication-status {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      text-transform: uppercase;
    }

    .medication-status.ok {
      background-color: var(--success-color);
      color: var(--text-primary-color);
    }

    .medication-status.due {
      background-color: var(--warning-color);
      color: var(--text-primary-color);
    }

    .medication-status.missed {
      background-color: var(--error-color);
      color: var(--text-primary-color);
    }

    .medication-info {
      margin-top: 12px;
      font-size: 14px;
      color: var(--secondary-text-color);
    }

    .medication-actions {
      display: flex;
      gap: 8px;
      margin-top: 16px;
    }

    .btn {
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: background-color 0.2s;
    }

    .btn-primary {
      background-color: var(--primary-color);
      color: var(--text-primary-color);
    }

    .btn-primary:hover {
      background-color: var(--dark-primary-color);
    }

    .btn-secondary {
      background-color: var(--secondary-background-color);
      color: var(--primary-text-color);
    }

    .btn-secondary:hover {
      background-color: var(--divider-color);
    }

    .empty-state {
      text-align: center;
      padding: 48px;
      color: var(--secondary-text-color);
    }

    .empty-state-icon {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.5;
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

      // Fetch medications from Home Assistant
      const entities = Object.keys(this.hass.states).filter(
        (entity_id) => entity_id.startsWith('sensor.') && entity_id.includes('med_expert')
      );

      // Parse medications from sensor entities
      this._medications = entities
        .filter((entity_id) => entity_id.endsWith('_status'))
        .map((entity_id) => {
          const state = this.hass.states[entity_id];
          const baseName = entity_id.replace('sensor.', '').replace('_status', '');
          
          // Find related entities
          const nextDueEntity = this.hass.states[`sensor.${baseName}_next_due`];
          const nextDoseEntity = this.hass.states[`sensor.${baseName}_next_dose`];

          return {
            entity_id,
            name: state.attributes.friendly_name || baseName,
            status: state.state,
            next_due: nextDueEntity?.state,
            next_dose: nextDoseEntity?.state,
            attributes: state.attributes
          };
        });

      this._loading = false;
    } catch (error) {
      this._error = `Failed to load medications: ${error}`;
      this._loading = false;
    }
  }

  private async _takeMedication(medication: any) {
    try {
      // Call the med_expert.take service
      await this.hass.callService('med_expert', 'take', {
        medication_id: medication.attributes.medication_id,
        entry_id: medication.attributes.entry_id
      });
      
      // Refresh data
      await this._loadData();
    } catch (error) {
      this._error = `Failed to mark medication as taken: ${error}`;
    }
  }

  private async _snoozeMedication(medication: any) {
    try {
      await this.hass.callService('med_expert', 'snooze', {
        medication_id: medication.attributes.medication_id,
        entry_id: medication.attributes.entry_id
      });
      
      await this._loadData();
    } catch (error) {
      this._error = `Failed to snooze medication: ${error}`;
    }
  }

  render() {
    if (this._loading) {
      return html`
        <div class="loading">
          <ha-circular-progress active></ha-circular-progress>
          <p>Loading medications...</p>
        </div>
      `;
    }

    return html`
      <div class="header">
        <h1>💊 Med Expert</h1>
      </div>

      ${this._error
        ? html`<div class="error">${this._error}</div>`
        : ''}

      ${this._medications.length === 0
        ? html`
            <div class="empty-state">
              <div class="empty-state-icon">💊</div>
              <h2>No Medications Found</h2>
              <p>Add medications using the Med Expert integration services.</p>
            </div>
          `
        : html`
            <div class="medications-grid">
              ${this._medications.map(
                (med) => html`
                  <div class="medication-card">
                    <div class="medication-name">${med.name}</div>
                    <span class="medication-status ${med.status}">
                      ${med.status}
                    </span>
                    
                    <div class="medication-info">
                      ${med.next_due
                        ? html`<div>📅 Next: ${new Date(med.next_due).toLocaleString()}</div>`
                        : ''}
                      ${med.next_dose
                        ? html`<div>💊 Dose: ${med.next_dose}</div>`
                        : ''}
                    </div>

                    ${med.status === 'due' || med.status === 'missed'
                      ? html`
                          <div class="medication-actions">
                            <button
                              class="btn btn-primary"
                              @click=${() => this._takeMedication(med)}
                            >
                              ✓ Take
                            </button>
                            <button
                              class="btn btn-secondary"
                              @click=${() => this._snoozeMedication(med)}
                            >
                              ⏰ Snooze
                            </button>
                          </div>
                        `
                      : ''}
                  </div>
                `
              )}
            </div>
          `}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'med-expert-panel': MedExpertPanel;
  }
}
