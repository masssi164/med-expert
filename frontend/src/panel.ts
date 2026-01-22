import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, MedicationStatus, DOSAGE_FORMS, HassEntityAttributes } from './types';
// Import wizard component
import './add-medication-wizard';

type TabType = 'today' | 'calendar' | 'profile' | 'meds';

interface ProfileInfo {
  entry_id: string;
  title: string;
  state: string;
}

interface ParsedMedication {
  entity_id: string;
  medication_id: string;
  entry_id: string;
  name: string;
  status: MedicationStatus;
  next_due: Date | null;
  next_dose: string;
  form: string;
  icon: string;
  inventory?: {
    current: number;
    threshold: number;
    low: boolean;
  };
  attributes: HassEntityAttributes;
}

/**
 * Med Expert Panel - Main frontend panel for medication management
 */
@customElement('med-expert-panel')
export class MedExpertPanel extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public narrow = false;

  @state() private _medications: ParsedMedication[] = [];
  @state() private _loading = true;
  @state() private _error: string | null = null;
  @state() private _activeTab: TabType = 'today';
  @state() private _showWizard = false;
  @state() private _entryId: string | null = null;
  @state() private _profiles: ProfileInfo[] = [];
  @state() private _currentProfile: ProfileInfo | null = null;

  static styles = css`
    :host {
      display: block;
      min-height: 100vh;
      background-color: var(--primary-background-color);
      color: var(--primary-text-color);
    }

    /* App Container */
    .app-container {
      max-width: 600px;
      margin: 0 auto;
      padding-bottom: 80px;
    }

    /* Header */
    .header {
      background: linear-gradient(135deg, var(--primary-color), var(--accent-color, var(--primary-color)));
      color: var(--text-primary-color);
      padding: 20px;
      padding-top: max(20px, env(safe-area-inset-top));
    }

    .header-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }

    .header-subtitle {
      opacity: 0.9;
      margin-top: 4px;
      font-size: 14px;
    }

    .add-btn {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: rgba(255,255,255,0.2);
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }

    .add-btn:hover {
      background: rgba(255,255,255,0.3);
      transform: scale(1.05);
    }

    /* Stats Bar */
    .stats-bar {
      display: flex;
      justify-content: space-around;
      padding: 16px;
      margin-top: 12px;
      background: rgba(255,255,255,0.1);
      border-radius: 12px;
    }

    .stat {
      text-align: center;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 700;
    }

    .stat-label {
      font-size: 11px;
      opacity: 0.9;
      text-transform: uppercase;
    }

    /* Tab Navigation */
    .tab-nav {
      display: flex;
      background: var(--card-background-color);
      border-bottom: 1px solid var(--divider-color);
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .tab {
      flex: 1;
      padding: 14px 8px;
      text-align: center;
      cursor: pointer;
      border: none;
      background: none;
      color: var(--secondary-text-color);
      font-size: 12px;
      font-weight: 500;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }

    .tab.active {
      color: var(--primary-color);
      border-bottom: 2px solid var(--primary-color);
    }

    .tab-icon {
      font-size: 20px;
    }

    /* Content */
    .content {
      padding: 16px;
    }

    /* Section */
    .section {
      margin-bottom: 24px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .section-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--secondary-text-color);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .section-badge {
      background: var(--error-color);
      color: white;
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 10px;
    }

    /* Medication Cards */
    .med-card {
      background: var(--card-background-color);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
      display: flex;
      align-items: center;
      gap: 12px;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .med-card:active {
      transform: scale(0.98);
    }

    .med-card.urgent {
      border-left: 4px solid var(--error-color);
    }

    .med-card.due {
      border-left: 4px solid var(--warning-color);
    }

    .med-card.done {
      opacity: 0.6;
    }

    .med-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: var(--secondary-background-color);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;
    }

    .med-info {
      flex: 1;
      min-width: 0;
    }

    .med-name {
      font-weight: 600;
      font-size: 16px;
      margin-bottom: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .med-dose {
      color: var(--secondary-text-color);
      font-size: 13px;
    }

    .med-time {
      text-align: right;
      flex-shrink: 0;
    }

    .med-time-value {
      font-weight: 600;
      font-size: 15px;
      color: var(--primary-text-color);
    }

    .med-time-label {
      font-size: 11px;
      color: var(--secondary-text-color);
    }

    .med-time-overdue {
      color: var(--error-color);
    }

    /* Action Buttons */
    .med-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--divider-color);
    }

    .action-btn {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .action-btn.take {
      background: var(--success-color, #4CAF50);
      color: white;
    }

    .action-btn.snooze {
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
    }

    .action-btn.skip {
      background: var(--secondary-background-color);
      color: var(--secondary-text-color);
    }

    .action-btn:hover {
      filter: brightness(1.1);
    }

    /* Empty State */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
    }

    .empty-icon {
      font-size: 72px;
      margin-bottom: 16px;
      opacity: 0.5;
    }

    .empty-title {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 8px;
    }

    .empty-text {
      color: var(--secondary-text-color);
      margin-bottom: 24px;
    }

    .empty-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      background: var(--primary-color);
      color: var(--text-primary-color);
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
    }

    /* Loading */
    .loading {
      text-align: center;
      padding: 60px 20px;
      color: var(--secondary-text-color);
    }

    .loading-spinner {
      font-size: 48px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      100% { transform: rotate(360deg); }
    }

    /* Error */
    .error {
      background: var(--error-color);
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      margin: 16px;
    }

    /* Wizard Overlay */
    .wizard-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      z-index: 100;
    }

    /* Medications List Tab */
    .meds-list-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--card-background-color);
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
    }

    .meds-list-item:hover {
      background: var(--secondary-background-color);
    }

    .inventory-warning {
      font-size: 11px;
      color: var(--warning-color);
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 2px;
    }

    /* Calendar placeholder */
    .calendar-placeholder, .stats-placeholder {
      text-align: center;
      padding: 40px;
      color: var(--secondary-text-color);
    }

    /* Profile selector in header */
    .profile-select {
      background: rgba(255,255,255,0.2);
      border: none;
      color: inherit;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 14px;
      cursor: pointer;
    }

    .profile-select option {
      color: var(--primary-text-color);
      background: var(--card-background-color);
    }

    .profile-badge {
      opacity: 0.9;
    }

    /* Profile Tab Styles */
    .profile-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px;
      background: var(--card-background-color);
      border-radius: 12px;
      margin-bottom: 16px;
    }

    .profile-avatar {
      font-size: 48px;
      width: 64px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--primary-color);
      border-radius: 50%;
    }

    .profile-info {
      flex: 1;
    }

    .profile-name {
      font-size: 20px;
      font-weight: 600;
    }

    .profile-status {
      font-size: 14px;
      color: var(--secondary-text-color);
      margin-top: 4px;
    }

    .profile-stats {
      display: flex;
      gap: 16px;
      padding: 12px 16px;
      background: var(--card-background-color);
      border-radius: 8px;
      margin-bottom: 16px;
    }

    .profile-stat {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
    }

    .stat-icon {
      font-size: 18px;
    }

    .profile-list-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--card-background-color);
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .profile-list-item:hover {
      background: var(--secondary-background-color);
    }

    .profile-list-item.active {
      border: 2px solid var(--primary-color);
    }

    .profile-avatar-small {
      font-size: 24px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--secondary-background-color);
      border-radius: 50%;
    }

    .profile-item-info {
      flex: 1;
    }

    .profile-item-name {
      font-weight: 500;
    }

    .profile-item-status {
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .check-mark {
      color: var(--primary-color);
      font-size: 20px;
      font-weight: bold;
    }

    .profile-action-btn {
      width: 100%;
      padding: 14px;
      background: var(--primary-color);
      color: var(--text-primary-color);
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .profile-action-btn:hover {
      opacity: 0.9;
    }

    .no-profile {
      text-align: center;
      padding: 40px;
      color: var(--secondary-text-color);
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this._loadData();
    
    // Auto-refresh every 30 seconds
    this._refreshInterval = setInterval(() => this._loadData(), 30000);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this._refreshInterval) {
      clearInterval(this._refreshInterval);
    }
  }

  private _refreshInterval?: ReturnType<typeof setInterval>;

  private async _loadData() {
    try {
      this._loading = this._medications.length === 0 && this._profiles.length === 0;
      this._error = null;

      // Load profiles from config entries via WebSocket
      await this._loadProfiles();

      // If no current profile selected but profiles exist, select first one
      if (!this._currentProfile && this._profiles.length > 0) {
        this._currentProfile = this._profiles[0];
        this._entryId = this._currentProfile.entry_id;
      }

      // Fetch med_expert medication status sensors
      // Med Expert sensors have 'medication_id' attribute - that's how we identify them
      const entities = Object.keys(this.hass.states).filter((entity_id) => {
        if (!entity_id.startsWith('sensor.') || !entity_id.endsWith('_status')) {
          return false;
        }
        const state = this.hass.states[entity_id];
        // Med Expert status sensors have medication_id attribute
        return state?.attributes?.medication_id !== undefined;
      });

      // Parse medications from sensor entities, filtered by current profile
      this._medications = entities
        .map((entity_id) => {
          const state = this.hass.states[entity_id];
          const baseName = entity_id.replace('sensor.', '').replace('_status', '');
          
          // Find related entities
          const nextDueEntity = this.hass.states[`sensor.${baseName}_next_due`];
          const nextDoseEntity = this.hass.states[`sensor.${baseName}_next_dose`];

          // Extract entry_id from any med_expert entity
          if (!this._entryId && state.attributes.entry_id) {
            this._entryId = state.attributes.entry_id;
          }

          // Parse next due
          let nextDue: Date | null = null;
          if (nextDueEntity?.state && nextDueEntity.state !== 'unknown') {
            nextDue = new Date(nextDueEntity.state);
          }

          // Get form and icon
          const form = state.attributes.form || 'tablet';
          const formInfo = DOSAGE_FORMS[form as keyof typeof DOSAGE_FORMS] || DOSAGE_FORMS.tablet;

          return {
            entity_id,
            medication_id: state.attributes.medication_id || '',
            entry_id: state.attributes.entry_id || '',
            name: state.attributes.friendly_name?.replace(' Status', '') || state.attributes.display_name || baseName,
            status: state.state as MedicationStatus,
            next_due: nextDue,
            next_dose: nextDoseEntity?.state || state.attributes.next_dose || '',
            form,
            icon: formInfo.icon,
            inventory: state.attributes.inventory ? {
              current: state.attributes.inventory.current_quantity || 0,
              threshold: state.attributes.inventory.refill_threshold || 7,
              low: (state.attributes.inventory.current_quantity || 0) <= (state.attributes.inventory.refill_threshold || 7)
            } : undefined,
            attributes: state.attributes
          } as ParsedMedication;
        })
        // Filter by current profile if selected
        .filter((med) => !this._currentProfile || med.entry_id === this._currentProfile.entry_id);

      this._loading = false;
    } catch (error) {
      this._error = `Failed to load medications: ${error}`;
      this._loading = false;
    }
  }

  private async _loadProfiles() {
    try {
      const result = await this.hass.callWS({ type: 'config_entries/get' }) as Array<{
        entry_id: string;
        domain: string;
        title: string;
        state: string;
      }>;
      
      this._profiles = result
        .filter(entry => entry.domain === 'med_expert')
        .map(entry => ({
          entry_id: entry.entry_id,
          title: entry.title,
          state: entry.state
        }));
    } catch (error) {
      console.error('Failed to load profiles:', error);
      this._profiles = [];
    }
  }

  private _selectProfile(profile: ProfileInfo) {
    this._currentProfile = profile;
    this._entryId = profile.entry_id;
    // Reload medications for new profile
    this._loadData();
  }

  // Grouped medications
  private get _dueMedications(): ParsedMedication[] {
    return this._medications.filter(m => m.status === 'due' || m.status === 'missed' || m.status === 'snoozed');
  }

  private get _upcomingMedications(): ParsedMedication[] {
    const now = new Date();
    const endOfDay = new Date(now);
    endOfDay.setHours(23, 59, 59, 999);
    
    return this._medications.filter(m => {
      if (m.status !== 'ok' || !m.next_due) return false;
      return m.next_due <= endOfDay;
    }).sort((a, b) => (a.next_due?.getTime() || 0) - (b.next_due?.getTime() || 0));
  }

  private get _completedToday(): ParsedMedication[] {
    // For now, we don't have a "taken today" status, so this is empty
    // This would require tracking in the backend
    return [];
  }

  private get _stats() {
    const total = this._medications.length;
    const due = this._dueMedications.length;
    const upcoming = this._upcomingMedications.length;
    return { total, due, upcoming };
  }

  private async _takeMedication(medication: ParsedMedication) {
    try {
      await this.hass.callService('med_expert', 'take', {
        medication_id: medication.medication_id,
        entry_id: medication.entry_id
      });
      await this._loadData();
    } catch (error) {
      this._error = `Failed to take medication: ${error}`;
    }
  }

  private async _snoozeMedication(medication: ParsedMedication) {
    try {
      await this.hass.callService('med_expert', 'snooze', {
        medication_id: medication.medication_id,
        entry_id: medication.entry_id
      });
      await this._loadData();
    } catch (error) {
      this._error = `Failed to snooze medication: ${error}`;
    }
  }

  private async _skipMedication(medication: ParsedMedication) {
    try {
      await this.hass.callService('med_expert', 'skip', {
        medication_id: medication.medication_id,
        entry_id: medication.entry_id
      });
      await this._loadData();
    } catch (error) {
      this._error = `Failed to skip medication: ${error}`;
    }
  }

  private _formatTime(date: Date | null): string {
    if (!date) return '--:--';
    return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
  }

  private _formatTimeAgo(date: Date | null): { value: string; label: string; overdue: boolean } {
    if (!date) return { value: '--:--', label: '', overdue: false };
    
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const absDiff = Math.abs(diff);
    const overdue = diff < 0;
    
    if (absDiff < 60000) {
      return { value: 'Jetzt', label: '', overdue };
    } else if (absDiff < 3600000) {
      const mins = Math.round(absDiff / 60000);
      return { 
        value: `${overdue ? '-' : ''}${mins}`, 
        label: 'Min', 
        overdue 
      };
    } else {
      return { 
        value: this._formatTime(date), 
        label: overdue ? 'Überfällig' : 'Uhr', 
        overdue 
      };
    }
  }

  render() {
    if (this._loading) {
      return html`
        <div class="loading">
          <div class="loading-spinner">💊</div>
          <p>Medikamente laden...</p>
        </div>
      `;
    }

    return html`
      <div class="app-container">
        ${this._renderHeader()}
        ${this._renderTabs()}
        
        <div class="content">
          ${this._error ? html`<div class="error">${this._error}</div>` : ''}
          
          ${this._activeTab === 'today' ? this._renderTodayTab() : ''}
          ${this._activeTab === 'calendar' ? this._renderCalendarTab() : ''}
          ${this._activeTab === 'profile' ? this._renderProfileTab() : ''}
          ${this._activeTab === 'meds' ? this._renderMedsTab() : ''}
        </div>
      </div>

      ${this._showWizard ? html`
        <div class="wizard-overlay" @click=${(e: Event) => e.target === e.currentTarget && this._closeWizard()}>
          <add-medication-wizard
            .hass=${this.hass}
            .entryId=${this._entryId || ''}
            @close=${this._closeWizard}
          ></add-medication-wizard>
        </div>
      ` : ''}
    `;
  }

  private _renderHeader() {
    const stats = this._stats;
    const greeting = this._getGreeting();
    const profileName = this._currentProfile?.title || 'Kein Profil';
    
    return html`
      <div class="header">
        <div class="header-top">
          <div>
            <h1>${greeting}</h1>
            <div class="header-subtitle">
              ${this._profiles.length > 1 ? html`
                <select 
                  class="profile-select"
                  .value=${this._currentProfile?.entry_id || ''}
                  @change=${(e: Event) => {
                    const select = e.target as HTMLSelectElement;
                    const profile = this._profiles.find(p => p.entry_id === select.value);
                    if (profile) this._selectProfile(profile);
                  }}
                >
                  ${this._profiles.map(p => html`
                    <option value=${p.entry_id} ?selected=${p.entry_id === this._currentProfile?.entry_id}>
                      ${p.title}
                    </option>
                  `)}
                </select>
                <span style="margin: 0 6px;">•</span>
              ` : this._profiles.length === 1 ? html`
                <span class="profile-badge">👤 ${profileName}</span>
                <span style="margin: 0 6px;">•</span>
              ` : ''}
              ${stats.due > 0 
                ? `${stats.due} Medikament${stats.due > 1 ? 'e' : ''} jetzt fällig`
                : stats.upcoming > 0 
                  ? `${stats.upcoming} noch heute`
                  : 'Alles erledigt 🎉'}
            </div>
          </div>
          <button class="add-btn" @click=${this._openWizard} title="Medikament hinzufügen">
            ➕
          </button>
        </div>
        
        <div class="stats-bar">
          <div class="stat">
            <div class="stat-value">${stats.due}</div>
            <div class="stat-label">Fällig</div>
          </div>
          <div class="stat">
            <div class="stat-value">${stats.upcoming}</div>
            <div class="stat-label">Heute noch</div>
          </div>
          <div class="stat">
            <div class="stat-value">${stats.total}</div>
            <div class="stat-label">Gesamt</div>
          </div>
        </div>
      </div>
    `;
  }

  private _getGreeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return '☀️ Guten Morgen';
    if (hour < 18) return '🌤️ Guten Tag';
    return '🌙 Guten Abend';
  }

  private _renderTabs() {
    const tabs: { id: TabType; icon: string; label: string }[] = [
      { id: 'today', icon: '📅', label: 'Heute' },
      { id: 'calendar', icon: '🗓️', label: 'Kalender' },
      { id: 'profile', icon: '👤', label: 'Profil' },
      { id: 'meds', icon: '💊', label: 'Meds' },
    ];

    return html`
      <nav class="tab-nav">
        ${tabs.map(tab => html`
          <button 
            class="tab ${this._activeTab === tab.id ? 'active' : ''}"
            @click=${() => this._activeTab = tab.id}
          >
            <span class="tab-icon">${tab.icon}</span>
            ${tab.label}
          </button>
        `)}
      </nav>
    `;
  }

  private _renderTodayTab() {
    if (this._medications.length === 0) {
      return this._renderEmptyState();
    }

    const dueMeds = this._dueMedications;
    const upcomingMeds = this._upcomingMedications;

    return html`
      ${dueMeds.length > 0 ? html`
        <div class="section">
          <div class="section-header">
            <span class="section-title">🔴 Jetzt fällig</span>
            <span class="section-badge">${dueMeds.length}</span>
          </div>
          ${dueMeds.map(med => this._renderMedCard(med, true))}
        </div>
      ` : ''}

      ${upcomingMeds.length > 0 ? html`
        <div class="section">
          <div class="section-header">
            <span class="section-title">⏳ Heute noch</span>
          </div>
          ${upcomingMeds.map(med => this._renderMedCard(med, false))}
        </div>
      ` : ''}

      ${dueMeds.length === 0 && upcomingMeds.length === 0 ? html`
        <div class="empty-state">
          <div class="empty-icon">✅</div>
          <div class="empty-title">Alles erledigt!</div>
          <div class="empty-text">Keine Medikamente mehr für heute.</div>
        </div>
      ` : ''}
    `;
  }

  private _renderMedCard(med: ParsedMedication, showActions: boolean) {
    const timeInfo = this._formatTimeAgo(med.next_due);
    const isUrgent = med.status === 'missed';
    const isDue = med.status === 'due' || med.status === 'snoozed';

    return html`
      <div class="med-card ${isUrgent ? 'urgent' : isDue ? 'due' : ''}">
        <div class="med-icon">${med.icon}</div>
        <div class="med-info">
          <div class="med-name">${med.name}</div>
          <div class="med-dose">${med.next_dose}</div>
          ${med.inventory?.low ? html`
            <div class="inventory-warning">⚠️ Nur noch ${med.inventory.current} übrig</div>
          ` : ''}
        </div>
        <div class="med-time">
          <div class="med-time-value ${timeInfo.overdue ? 'med-time-overdue' : ''}">${timeInfo.value}</div>
          <div class="med-time-label">${timeInfo.label}</div>
        </div>
      </div>
      
      ${showActions ? html`
        <div class="med-actions" style="margin-top: -4px; margin-bottom: 12px;">
          <button class="action-btn take" @click=${() => this._takeMedication(med)}>
            ✓ Genommen
          </button>
          <button class="action-btn snooze" @click=${() => this._snoozeMedication(med)}>
            ⏰ Später
          </button>
          <button class="action-btn skip" @click=${() => this._skipMedication(med)}>
            ✕
          </button>
        </div>
      ` : ''}
    `;
  }

  private _renderEmptyState() {
    return html`
      <div class="empty-state">
        <div class="empty-icon">💊</div>
        <div class="empty-title">Keine Medikamente</div>
        <div class="empty-text">Füge dein erstes Medikament hinzu, um loszulegen.</div>
        <button class="empty-btn" @click=${this._openWizard}>
          ➕ Medikament hinzufügen
        </button>
      </div>
    `;
  }

  private _renderCalendarTab() {
    return html`
      <div class="calendar-placeholder">
        <div style="font-size: 48px; margin-bottom: 16px;">🗓️</div>
        <p>Kalenderansicht kommt bald...</p>
      </div>
    `;
  }

  private _renderProfileTab() {
    return html`
      <div class="section">
        <div class="section-header">
          <span class="section-title">Aktuelles Profil</span>
        </div>
        
        ${this._currentProfile ? html`
          <div class="profile-card">
            <div class="profile-avatar">👤</div>
            <div class="profile-info">
              <div class="profile-name">${this._currentProfile.title}</div>
              <div class="profile-status">
                ${this._currentProfile.state === 'loaded' ? '🟢 Aktiv' : '🔴 ' + this._currentProfile.state}
              </div>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="profile-stat">
              <span class="stat-icon">💊</span>
              <span>${this._medications.length} Medikamente</span>
            </div>
          </div>
        ` : html`
          <div class="no-profile">
            <p>Kein Profil ausgewählt</p>
          </div>
        `}
      </div>
      
      ${this._profiles.length > 0 ? html`
        <div class="section">
          <div class="section-header">
            <span class="section-title">Alle Profile (${this._profiles.length})</span>
          </div>
          
          ${this._profiles.map(profile => html`
            <div 
              class="profile-list-item ${profile.entry_id === this._currentProfile?.entry_id ? 'active' : ''}"
              @click=${() => this._selectProfile(profile)}
            >
              <div class="profile-avatar-small">👤</div>
              <div class="profile-item-info">
                <div class="profile-item-name">${profile.title}</div>
                <div class="profile-item-status">
                  ${profile.state === 'loaded' ? 'Aktiv' : profile.state}
                </div>
              </div>
              ${profile.entry_id === this._currentProfile?.entry_id ? html`
                <span class="check-mark">✓</span>
              ` : ''}
            </div>
          `)}
        </div>
      ` : ''}
      
      <div class="section">
        <button class="profile-action-btn" @click=${this._openAddProfile}>
          ➕ Neues Profil erstellen
        </button>
      </div>
    `;
  }

  private _openAddProfile() {
    // Navigate to Home Assistant config flow for med_expert
    window.location.href = '/config/integrations/integration/med_expert';
  }

  private _renderMedsTab() {
    if (this._medications.length === 0) {
      return this._renderEmptyState();
    }

    return html`
      <div class="section">
        <div class="section-header">
          <span class="section-title">Alle Medikamente</span>
        </div>
        ${this._medications.map(med => html`
          <div class="meds-list-item">
            <div class="med-icon">${med.icon}</div>
            <div class="med-info">
              <div class="med-name">${med.name}</div>
              <div class="med-dose">${med.next_dose}</div>
              ${med.inventory ? html`
                <div style="font-size: 11px; color: var(--secondary-text-color);">
                  📦 ${med.inventory.current} auf Lager
                </div>
              ` : ''}
            </div>
          </div>
        `)}
      </div>
    `;
  }

  private async _openWizard() {
    // Find entry_id from first medication
    if (!this._entryId && this._medications.length > 0) {
      this._entryId = this._medications[0].entry_id;
    }
    
    // If still no entry_id, try to get from sensor attributes
    if (!this._entryId) {
      const configEntries = Object.keys(this.hass.states)
        .filter(e => e.includes('med_expert'))
        .map(e => this.hass.states[e]?.attributes?.entry_id)
        .filter(Boolean);
      
      if (configEntries.length > 0) {
        this._entryId = configEntries[0] as string;
      }
    }

    // If still no entry_id, fetch from config entries via WebSocket
    if (!this._entryId) {
      try {
        const result = await this.hass.callWS({ type: 'config_entries/get' }) as Array<{
          entry_id: string;
          domain: string;
          title: string;
        }>;
        const medExpertEntry = result.find(entry => entry.domain === 'med_expert');
        if (medExpertEntry) {
          this._entryId = medExpertEntry.entry_id;
        }
      } catch (error) {
        console.error('Failed to fetch config entries:', error);
      }
    }

    if (!this._entryId) {
      this._error = 'Kein Med Expert Profil gefunden. Bitte erstelle zuerst ein Profil in den Einstellungen.';
      return;
    }
    
    this._showWizard = true;
  }

  private _closeWizard() {
    this._showWizard = false;
    // Reload data to show new medication
    setTimeout(() => this._loadData(), 500);
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'med-expert-panel': MedExpertPanel;
  }
}
