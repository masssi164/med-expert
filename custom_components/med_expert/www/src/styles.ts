/**
 * Shared CSS styles for Med Expert Panel components
 */

import { css } from 'lit';

export const baseStyles = css`
  :host {
    display: block;
    height: 100vh;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family);
  }

  .panel-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* Buttons */
  button {
    font-family: inherit;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: var(--primary-color);
    color: white;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
  }

  .btn-primary:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }

  .btn-secondary {
    padding: 8px 16px;
    background: var(--secondary-background-color);
    color: var(--primary-text-color);
    border-radius: 8px;
    font-size: 14px;
  }

  .btn-secondary:hover {
    background: var(--divider-color);
  }

  .btn-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    padding: 0;
    background: transparent;
    color: var(--secondary-text-color);
    border-radius: 50%;
  }

  .btn-icon:hover {
    background: var(--secondary-background-color);
  }

  /* Form elements */
  .form-field {
    margin-bottom: 24px;
  }

  .form-field label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--primary-text-color);
  }

  .form-input {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
    box-sizing: border-box;
  }

  .form-input:focus {
    outline: none;
    border-color: var(--primary-color);
  }

  .form-textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    box-sizing: border-box;
  }

  .error {
    color: var(--error-color);
    font-size: 12px;
    margin-top: 4px;
  }

  /* Alerts */
  .alert {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .alert-warning {
    background: #fff3e0;
    color: #e65100;
    border-left: 4px solid #ff9800;
  }

  /* Info box */
  .info-box {
    display: flex;
    gap: 12px;
    padding: 16px;
    background: rgba(var(--rgb-primary-color), 0.1);
    border-radius: 8px;
    color: var(--primary-text-color);
  }

  .info-box ha-icon {
    flex-shrink: 0;
    color: var(--primary-color);
  }
`;

export const headerStyles = css`
  .header {
    background: var(--card-background-color);
    border-bottom: 1px solid var(--divider-color);
    padding: 16px 24px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: 24px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo ha-icon {
    --mdc-icon-size: 32px;
    color: var(--primary-color);
  }

  .logo h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
  }

  .profile-select {
    padding: 8px 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
  }

  .header-stats {
    display: flex;
    gap: 24px;
    margin-left: auto;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--primary-color);
  }

  .stat-label {
    font-size: 12px;
    color: var(--secondary-text-color);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

export const tabStyles = css`
  .tabs {
    display: flex;
    background: var(--card-background-color);
    border-bottom: 1px solid var(--divider-color);
    padding: 0 24px;
    overflow-x: auto;
  }

  .tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px 20px;
    border: none;
    background: none;
    color: var(--secondary-text-color);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
  }

  .tab:hover {
    color: var(--primary-text-color);
    background: var(--secondary-background-color);
  }

  .tab.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
  }

  .tab ha-icon {
    --mdc-icon-size: 20px;
  }
`;

export const cardStyles = css`
  .med-card {
    background: var(--card-background-color);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left: 4px solid var(--divider-color);
    transition: all 0.2s;
  }

  .med-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .med-card[data-status='due'] {
    border-left-color: #ff9800;
  }

  .med-card[data-status='missed'] {
    border-left-color: #f44336;
  }

  .med-card[data-status='prn'] {
    border-left-color: #9c27b0;
  }

  .med-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .med-card-header ha-icon {
    --mdc-icon-size: 24px;
    color: var(--primary-color);
  }

  .med-info {
    flex: 1;
  }

  .med-info h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 500;
  }

  .med-dose {
    font-size: 13px;
    color: var(--secondary-text-color);
  }

  .med-card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .med-detail {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--secondary-text-color);
  }

  .med-detail ha-icon {
    --mdc-icon-size: 16px;
  }

  .med-detail.inventory .warning {
    color: #ff9800;
    margin-left: auto;
  }

  .med-card-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
  }

  .action-btn.take {
    background: #4caf50;
    color: white;
    flex: 1;
  }

  .action-btn.snooze {
    background: #2196f3;
    color: white;
  }

  .action-btn.skip {
    background: #f44336;
    color: white;
  }

  .action-btn ha-icon {
    --mdc-icon-size: 16px;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    background: var(--secondary-background-color);
  }

  .status-badge.status-ok {
    color: #4caf50;
  }
`;

export const wizardStyles = css`
  .wizard-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 24px;
  }

  .wizard {
    background: var(--card-background-color);
    border-radius: 16px;
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .wizard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--divider-color);
  }

  .wizard-header h2 {
    margin: 0;
    font-size: 20px;
  }

  .wizard-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }

  .wizard-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px 24px;
    border-top: 1px solid var(--divider-color);
  }

  .wizard-stepper {
    display: flex;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid var(--divider-color);
    overflow-x: auto;
  }

  .wizard-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    min-width: 80px;
  }

  .step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--card-background-color);
    border: 2px solid var(--divider-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: var(--secondary-text-color);
  }

  .wizard-step.active .step-circle {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }

  .wizard-step.completed .step-circle {
    background: var(--success-color);
    border-color: var(--success-color);
    color: white;
  }

  .step-label {
    font-size: 12px;
    color: var(--secondary-text-color);
  }

  .wizard-step.active .step-label {
    color: var(--primary-text-color);
    font-weight: 600;
  }

  .step-line {
    flex: 1;
    height: 2px;
    background: var(--divider-color);
    margin: 0 8px;
    min-width: 20px;
  }

  .wizard-section {
    max-width: 600px;
    margin: 0 auto;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }

  .form-option {
    padding: 16px;
    border: 2px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
  }

  .form-option:hover {
    border-color: var(--primary-color);
  }

  .form-option.selected {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color), 0.1);
  }

  .schedule-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
  }

  .schedule-option {
    padding: 16px;
    border: 2px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
  }

  .schedule-option:hover {
    border-color: var(--primary-color);
  }

  .schedule-option.selected {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color), 0.1);
  }

  .time-row {
    display: flex;
    gap: 12px;
    margin-bottom: 8px;
  }

  .time-row .form-input {
    flex: 1;
  }

  .weekday-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
  }

  .weekday-btn {
    padding: 12px 8px;
    border: 2px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }

  .weekday-btn:hover {
    border-color: var(--primary-color);
  }

  .weekday-btn.selected {
    border-color: var(--primary-color);
    background: var(--primary-color);
    color: white;
  }

  .dose-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .dose-input {
    width: 80px;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
  }

  .checkbox-label input[type='checkbox'] {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  .review {
    background: var(--card-background-color);
    border-radius: 12px;
    padding: 24px;
  }

  .review h3 {
    margin: 0 0 24px 0;
  }

  .review-item {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--divider-color);
  }

  .review-item:last-child {
    border-bottom: none;
  }

  .review-label {
    font-weight: 500;
    color: var(--secondary-text-color);
  }

  .review-value {
    color: var(--primary-text-color);
    text-align: right;
  }
`;

export const calendarStyles = css`
  .calendar-nav {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .calendar-nav span {
    font-weight: 600;
    font-size: 18px;
  }

  .calendar {
    margin-top: 24px;
  }

  .calendar-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-bottom: 8px;
  }

  .calendar-weekday {
    text-align: center;
    font-weight: 600;
    font-size: 12px;
    color: var(--secondary-text-color);
    padding: 16px;
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
  }

  .calendar-day {
    aspect-ratio: 1;
    padding: 8px;
    border-radius: 8px;
    background: var(--card-background-color);
    border: 2px solid var(--divider-color);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: all 0.2s;
  }

  .calendar-day:hover {
    border-color: var(--primary-color);
    transform: scale(1.05);
  }

  .calendar-day.empty {
    background: transparent;
    border: none;
    cursor: default;
  }

  .calendar-day.empty:hover {
    transform: none;
  }

  .calendar-day.today {
    border-color: var(--primary-color);
    font-weight: 700;
  }

  .calendar-day.selected {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }

  .calendar-day.perfect {
    background: var(--success-color);
    border-color: var(--success-color);
    color: white;
  }

  .calendar-day.good {
    background: rgba(var(--rgb-success-color, 76, 175, 80), 0.5);
    border-color: var(--success-color);
  }

  .calendar-day.partial {
    background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.5);
    border-color: var(--warning-color);
  }

  .calendar-day.missed {
    background: rgba(var(--rgb-error-color, 244, 67, 54), 0.5);
    border-color: var(--error-color);
  }

  .day-number {
    font-size: 16px;
    font-weight: 600;
  }

  .day-doses {
    font-size: 11px;
    opacity: 0.8;
  }

  .calendar-legend {
    display: flex;
    gap: 24px;
    margin-top: 16px;
    justify-content: center;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .legend-color {
    width: 20px;
    height: 20px;
    border-radius: 4px;
  }

  .legend-color.perfect {
    background: var(--success-color);
  }

  .legend-color.good {
    background: rgba(var(--rgb-success-color, 76, 175, 80), 0.5);
  }

  .legend-color.partial {
    background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.5);
  }

  .legend-color.missed {
    background: rgba(var(--rgb-error-color, 244, 67, 54), 0.5);
  }

  .day-details {
    margin-top: 32px;
    padding: 24px;
    background: var(--card-background-color);
    border-radius: 12px;
  }

  .day-details h3 {
    margin: 0 0 16px 0;
  }

  .no-data {
    text-align: center;
    color: var(--secondary-text-color);
    padding: 32px;
  }

  .events-timeline {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .event-item {
    display: flex;
    gap: 16px;
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid var(--divider-color);
    background: var(--primary-background-color);
  }

  .event-item.taken {
    border-left-color: var(--success-color);
  }

  .event-item.snoozed {
    border-left-color: var(--warning-color);
  }

  .event-item.skipped,
  .event-item.missed {
    border-left-color: var(--error-color);
  }

  .event-time {
    font-weight: 600;
    font-size: 16px;
    min-width: 60px;
  }

  .event-content {
    flex: 1;
  }

  .event-medication {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .event-dose {
    font-size: 14px;
    color: var(--secondary-text-color);
    margin-bottom: 8px;
  }

  .event-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
`;

export const contentStyles = css`
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
  }

  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .content-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 500;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .med-section {
    margin-bottom: 32px;
  }

  .med-section h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 500;
    color: var(--secondary-text-color);
  }

  .med-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }

  .inventory-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .inventory-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: var(--card-background-color);
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  }

  .item-info h4 {
    margin: 0 0 4px 0;
    font-size: 16px;
  }

  .item-info span {
    font-size: 14px;
    color: var(--secondary-text-color);
  }
`;

export const responsiveStyles = css`
  @media (max-width: 768px) {
    .header-stats {
      display: none;
    }

    .med-list {
      grid-template-columns: 1fr;
    }

    .tab span {
      display: none;
    }

    .calendar-grid {
      gap: 4px;
    }

    .calendar-day {
      padding: 4px;
    }

    .day-number {
      font-size: 14px;
    }

    .day-doses {
      font-size: 10px;
    }

    .wizard-stepper {
      overflow-x: auto;
    }

    .step-label {
      display: none;
    }
  }
`;
