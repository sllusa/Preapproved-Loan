/**
 * TypeScript types matching backend API contracts
 * All fields use snake_case to match backend Pydantic models
 */

// Common types
export interface ErrorResponse {
  detail: string;
  status_code: number;
  retryable?: boolean;
  error_code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  entity_id: string;
  is_admin: boolean;
}

// Offer types
export interface PreapprovedOffer {
  offer_id: string;
  customer_id: string;
  entity_id: string;
  max_amount: number;
  max_term_months: number;
  indicative_tin: number;
  indicative_tae: number;
  validity_ends_at: string;
  offer_status: string;
  existing_journey_id?: string;
  resumable_state?: string;
}

export interface OffersResponse {
  offers: PreapprovedOffer[];
  total: number;
}

// Journey types
export interface JourneyInstance {
  journey_id: string;
  customer_id: string;
  entity_id: string;
  offer_id: string;
  current_state: string;
  channel_last_used: string;
  resume_deadline_at?: string;
  version: number;
}

// Simulation types
export interface SimulationRequest {
  amount: number;
  term_months: number;
  selected_account_id: string;
}

export interface SimulationResult {
  simulation_id: string;
  amount: number;
  term_months: number;
  tin: number;
  tae: number;
  installment_amount: number;
  total_cost: number;
  total_interest: number;
}

export interface SimulationResponse {
  journey_id: string;
  state: string;
  simulation: SimulationResult;
  account_selection?: {
    account_id: string;
    is_operable: boolean;
  };
}

export interface SimulationConfirmResponse {
  journey_id: string;
  state: string;
  confirmed_simulation_id: string;
  next_action: string;
}

// Account types
export interface DisbursementAccount {
  account_id: string;
  iban_masked: string;
  account_type: string;
  operable: boolean;
  failure_reason_code?: string;
  balance?: number;
}

export interface AccountsResponse {
  journey_id: string;
  accounts: DisbursementAccount[];
}

export interface AccountSelectRequest {
  account_id: string;
}

export interface AccountSelectResponse {
  journey_id: string;
  selected_account_id: string;
  operable: boolean;
  validated_at: string;
}

// Document types
export interface DocumentMetadata {
  document_type: string;
  storage_ref: string;
  file_name: string;
  file_size: number;
  content_type: string;
}

export interface DocumentPackage {
  package_id: string;
  variant: string;
  version: string;
  language_code: string;
  documents: DocumentMetadata[];
}

export interface DocumentGenerateResponse {
  journey_id: string;
  state: string;
  document_package: DocumentPackage;
}

export interface DocumentAcknowledgeRequest {
  package_id: string;
  acknowledged_at: string;
}

export interface DocumentAcknowledgeResponse {
  journey_id: string;
  state: string;
  acknowledgement_recorded: boolean;
}

// Verification types
export interface ChecksExecuteResponse {
  journey_id: string;
  state: string;
  check_execution_id: string;
  status: string;
}

export interface ChecksStatusResponse {
  journey_id: string;
  normalized_decision: string;
  creditworthiness_status: string;
  fraud_status: string;
  aml_status: string;
  next_state: string;
  reason_code?: string;
}

// Signature types
export interface SignatureInitiateResponse {
  journey_id: string;
  state: string;
  signature_session_id: string;
  sca_redirect_url: string;
  expires_at: string;
}

export interface SignatureCallbackRequest {
  signature_session_id: string;
  provider_reference: string;
  status: string;
  completed_at: string;
}

export interface SignatureCallbackResponse {
  journey_id: string;
  state: string;
  signature_status: string;
}

// Booking types
export interface BookingExecuteResponse {
  journey_id: string;
  booking_command_id: string;
  state: string;
  booking_status: string;
  pending_reconciliation: boolean;
}

export interface BookingStatusResponse {
  journey_id: string;
  booking_status: string;
  last_checked_at: string;
  support_reference?: string;
}

// Activation types
export interface AmortizationScheduleSummary {
  schedule_id: string;
  installment_count: number;
  first_due_date: string;
}

export interface ActivationStatusResponse {
  journey_id: string;
  state: string;
  loan_id: string;
  servicing_reference: string;
  amortization_schedule: AmortizationScheduleSummary;
}

export interface AmortizationInstallment {
  installment_number: number;
  due_date: string;
  principal_amount: number;
  interest_amount: number;
  total_amount: number;
  outstanding_balance?: number;
}

export interface AmortizationScheduleResponse {
  loan_id: string;
  currency: string;
  installments: AmortizationInstallment[];
}
