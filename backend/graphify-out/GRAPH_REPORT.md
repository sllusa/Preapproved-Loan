# Graph Report - backend  (2026-08-03)

## Corpus Check
- 101 files · ~25,136 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1025 nodes · 1699 edges · 72 communities (59 shown, 13 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `837b85b8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DocumentService
- EntityConfiguration
- ActivationService
- ChecksService
- User
- test_reconciliation_worker.py
- AccountAdapter
- AmortizationAdapter
- test_pre_approval_adapter.py
- SCAAdapter
- ReconciliationWorker
- BookingService
- dependencies.py
- SignatureService
- DocumentAdapter
- test_auth_module.py
- JourneyInstance
- test_verification_adapters.py
- main.py
- __init__.py
- journey.py
- NotificationService
- get_current_user
- JourneyOrchestrator
- SimulationService
- reconciliation_worker.py
- test_iris_adapter.py
- PreapprovedOfferSnapshot
- simulations.py
- AMLAdapter
- FraudAdapter
- __init__.py
- SimulationSnapshot
- config.py
- database.py
- AccountResponse
- auth.py
- __init__.py
- CreditworthinessAdapter
- list_offers
- .execute_booking
- __init__.py
- test_offers_router.py
- PaginatedResponse
- BookingStatusResponse
- get_user_by_id
- .get_offer_snapshot
- env.py
- DisbursementAccountSelection
- OutboxEvent
- get_booking_status
- StateTransitionError
- offer_service.py
- .simulate
- conftest.py
- __init__.py
- amortization_schedule.py
- audit_event.py
- document_acknowledgement.py
- journey_instance.py
- preapproved_offer_snapshot.py
- reconciliation_case.py
- signature_session.py
- verification_result.py
- .__init__
- __init__.py
- __init__.py
- preapproved-loan-backend

## God Nodes (most connected - your core abstractions)
1. `JourneyOrchestrator` - 36 edges
2. `EntityConfiguration` - 27 edges
3. `ReconciliationWorker` - 24 edges
4. `get_current_user()` - 23 edges
5. `User` - 22 edges
6. `SimulationService` - 22 edges
7. `ReconciliationCase` - 21 edges
8. `AuditService` - 20 edges
9. `BookingService` - 20 edges
10. `hash_password()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_worker_handles_timeout_error()` --indirect_call--> `ReconciliationCase`  [INFERRED]
  tests/test_workers/test_reconciliation_worker.py → app/models/reconciliation_case.py
- `test_state_machine_prevents_invalid_transition()` --indirect_call--> `StateTransitionError`  [INFERRED]
  tests/test_services/test_journey_orchestrator.py → app/services/journey_orchestrator.py
- `adapter()` --calls--> `IRISAdapter`  [EXTRACTED]
  tests/test_adapters/test_iris_adapter.py → app/adapters/iris_adapter.py
- `test_get_user_by_id_returns_user()` --calls--> `hash_password()`  [EXTRACTED]
  tests/test_auth/test_auth_module.py → app/auth.py
- `test_hash_password_returns_different_hash_each_time()` --calls--> `hash_password()`  [EXTRACTED]
  tests/test_auth/test_auth_module.py → app/auth.py

## Import Cycles
- None detected.

## Communities (72 total, 13 thin omitted)

### Community 0 - "DocumentService"
Cohesion: 0.05
Nodes (42): DocumentAcknowledgement, Base, Customer acknowledgement evidence for document packages, DocumentPackage, Base, Generated legal package metadata (SECCI/INE), acknowledge_documents(), generate_document_package() (+34 more)

### Community 1 - "EntityConfiguration"
Cohesion: 0.06
Nodes (30): EntityConfiguration, Base, Multi-entity parameterization configuration, EntityConfigService, Any, Session, Entity Configuration Service - Multi-entity parameterization, Multi-entity configuration management via ParametrizacionEntidad.     Provides e (+22 more)

### Community 2 - "ActivationService"
Cohesion: 0.07
Nodes (34): AmortizationInstallment, Base, Individual repayment installment details, AmortizationSchedule, Base, Loan repayment schedule header, LoanActivationProjection, Base (+26 more)

### Community 3 - "ChecksService"
Cohesion: 0.07
Nodes (30): Base, Parallel checks execution header, VerificationExecution, Base, Individual provider verification outcomes, VerificationResult, execute_verifications(), get_verification_status() (+22 more)

### Community 4 - "User"
Cohesion: 0.10
Nodes (29): authenticate_user(), hash_password(), Authentication module with JWT and bcrypt, Authenticate user by email and password.      Args:         db: Database session, Hash password using bcrypt.      Args:         password: Plain text password, Base, User model for authentication, User model for authentication and authorization (+21 more)

### Community 5 - "test_reconciliation_worker.py"
Cohesion: 0.08
Nodes (26): AuditEvent, Base, Immutable audit event ledger for compliance evidence, Retrieve audit events for a customer, Retrieve audit events for a journey, db_session(), pending_reconciliation_case(), Tests for Reconciliation Worker (+18 more)

### Community 6 - "AccountAdapter"
Cohesion: 0.09
Nodes (21): AccountAdapter, Any, Account Validation Adapter - Disbursement account selection and operability, Adapter for Account Validation Service integration.      Handles:     - Eligible, Normalize account list response for service layer.          Args:             ra, Initialize adapter with timeout budget.          Args:             timeout: Requ, Retrieve eligible disbursement accounts for a customer.          Args:, Validate specific account operability for disbursement.          Args: (+13 more)

### Community 7 - "AmortizationAdapter"
Cohesion: 0.09
Nodes (21): AmortizationAdapter, Any, Amortization Schedule Adapter - Schedule generation and retrieval, Adapter for Amortization Schedule Service integration.      Handles:     - Frenc, Retrieve existing amortization schedule.          Args:             loan_id: Loa, Normalize installment list for service layer.          Args:             raw_ins, Initialize adapter with timeout budget.          Args:             timeout: Requ, Generate French amortization schedule.          Args:             loan_id: Loan (+13 more)

### Community 8 - "test_pre_approval_adapter.py"
Cohesion: 0.08
Nodes (22): PreApprovalAdapter, Any, Adapter for Pre-Approval Engine integration.      Handles:     - Offer retrieval, Normalize offer response and apply entity-specific filtering.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Retrieve pre-approved offers for a customer.          Args:             customer, Revalidate offer status and check for revocation.          Args:             off, adapter() (+14 more)

### Community 9 - "SCAAdapter"
Cohesion: 0.08
Nodes (21): Any, SCA Signature Adapter - PSD2/SCA strong customer authentication, Adapter for PSD2/SCA Signature Service integration.      Handles:     - Signatur, Verify signature session status.          Args:             session_id: Provider, Normalize provider callback status to standard values.          Args:, Initialize adapter with default timeout.          Args:             timeout: Req, Initiate SCA signature session.          Args:             customer_id: Customer, SCAAdapter (+13 more)

### Community 10 - "ReconciliationWorker"
Cohesion: 0.13
Nodes (20): BookingCommand, Base, IRIS booking command attempts and outcomes, Base, Pending timeout/uncertain IRIS booking resolution cases, ReconciliationCase, Session, Process a single reconciliation case.          Args:             db: Database se (+12 more)

### Community 11 - "BookingService"
Cohesion: 0.10
Nodes (23): IdempotencyRecord, Base, Booking/disbursement command idempotency registry, BookingService, Session, Booking Service - Idempotent IRIS booking and disbursement, Implements idempotent command pattern with write-before-send idempotency records, Get pending reconciliation case for a journey (+15 more)

### Community 12 - "dependencies.py"
Cohesion: 0.19
Nodes (15): get_db(), FastAPI dependencies for route handlers, Database session dependency, Disbursement account selection routes, Loan activation and amortization schedule routes, IRIS booking and disbursement routes, Document generation and acknowledgement routes, Offer retrieval and eligibility routes (+7 more)

### Community 13 - "SignatureService"
Cohesion: 0.10
Nodes (19): Base, SCA signature session tracking, SignatureSession, initiate_signature(), Session, Initiate PSD2/SCA signature session.      Returns provider redirect URL and sess, Handle signature callback from SCA provider.      Updates session status and adv, signature_callback() (+11 more)

### Community 14 - "DocumentAdapter"
Cohesion: 0.09
Nodes (19): DocumentAdapter, Any, Document Generation Adapter - Legal package generation, Adapter for Document Generation Service integration.      Handles:     - SECCI/I, Get download URL for a generated document.          Args:             document_i, Normalize document list for service layer.          Args:             raw_docume, Initialize adapter with timeout budget.          Args:             timeout: Requ, Generate legal document package (SECCI or INE).          Args:             custo (+11 more)

### Community 15 - "test_auth_module.py"
Cohesion: 0.10
Nodes (23): decode_access_token(), Verify plain password against hashed password using bcrypt.      Args:         p, Decode and validate JWT access token.      Args:         token: JWT token string, verify_password(), Unit tests for auth module - password hashing and JWT, Test decoding expired JWT token returns None, Test user authentication fails with invalid email, Test that bcrypt generates different hashes for same password (+15 more)

### Community 16 - "JourneyInstance"
Cohesion: 0.10
Nodes (18): JourneyInstance, Base, Canonical journey state aggregate with lifecycle tracking, Any, Retrieve journey by ID, Apply state transition with guards and audit emission.          Args:, Update journey reference fields (simulation_id, account_id, etc.) without state, Create a new journey instance (+10 more)

### Community 17 - "test_verification_adapters.py"
Cohesion: 0.08
Nodes (23): Tests for Verification Adapters (Creditworthiness, Fraud, AML), Test fraud screening with REJECT decision, Test fraud decision normalization by score, Test fraud decision normalization by verdict, Test AML screening with PASS decision, Test AML screening with PEP match (REVIEW), Test AML screening with sanctions match (REJECT), Test AML decision normalization (+15 more)

### Community 18 - "main.py"
Cohesion: 0.11
Nodes (21): health(), lifespan(), FastAPI application entry point, Application lifespan events - startup and shutdown, Root endpoint - health check, Health check endpoint, root(), Session (+13 more)

### Community 19 - "__init__.py"
Cohesion: 0.12
Nodes (13): AuditService, Any, datetime, Session, Audit Service - Immutable audit event persistence, Search audit events with filters, Generate deterministic hash of payload, Captures immutable audit events for compliance evidence.     Implements append-o (+5 more)

### Community 20 - "journey.py"
Cohesion: 0.15
Nodes (18): check_journey_resume(), get_journey(), Session, Journey orchestration and resume routes, Check if journey can be resumed and determine next step.      Validates offer st, Start a new journey for an offer.      Creates journey instance in OFERTA_VIGENT, Retrieve journey details., start_journey() (+10 more)

### Community 21 - "NotificationService"
Cohesion: 0.15
Nodes (12): NotificationService, Any, Session, Notification Service - Customer messaging and notification orchestration, Notify customer that signature is required, Customer notification orchestration for journey milestones, status updates, and, Notify customer of successful disbursement, Notify customer that disbursement is being processed (+4 more)

### Community 22 - "get_current_user"
Cohesion: 0.18
Nodes (19): create_access_token(), Generate JWT access token with customer_id, entity_id, and exp claims.      Args, get_current_user(), Session, Authentication dependency for protected routes.          Validates JWT token fro, HTTPAuthorizationCredentials, Unit tests for auth dependencies - get_current_user, Test get_current_user raises 401 when user_id is not a valid integer (+11 more)

### Community 23 - "JourneyOrchestrator"
Cohesion: 0.14
Nodes (18): JourneyOrchestrator, Enforces lifecycle state machine with guarded transitions and audit event emissi, Check if a state is terminal (no further transitions allowed), Tests for Journey Orchestrator Service, Test complete happy path state progression, Test terminal state detection, Test optimistic locking prevents concurrent updates, Test updating journey reference fields (+10 more)

### Community 24 - "SimulationService"
Cohesion: 0.14
Nodes (19): Stateless simulation API with amount/term validation and snapshot persistence., SimulationService, Tests for Simulation Service, Test simulation rejects termMonths > offer.maxTermMonths, Test simulation validates amount >= entity.minAmount, Test simulation calculates installment, total cost correctly, Test persisting simulation snapshot, Test retrieving confirmed simulation (+11 more)

### Community 25 - "reconciliation_worker.py"
Cohesion: 0.14
Nodes (10): IRISAdapter, Any, IRIS Core and Disbursement Adapter - Booking and disbursement orchestration, Adapter for IRIS Core and Disbursement API integration.      Handles:     - Idem, Poll booking status from IRIS.          Args:             iris_reference: IRIS l, Submit disbursement command for a booked loan.          Args:             iris_r, Initialize adapter with separate timeout budgets.          Args:             boo, Submit idempotent booking command to IRIS.          Args:             idempotenc (+2 more)

### Community 26 - "test_iris_adapter.py"
Cohesion: 0.12
Nodes (15): adapter(), Tests for IRIS Adapter, Test successful status retrieval, Create adapter instance, Test status retrieval for not found booking, Test successful disbursement submission, Test successful booking with immediate confirmation, Test booking with pending status (+7 more)

### Community 27 - "PreapprovedOfferSnapshot"
Cohesion: 0.15
Nodes (14): PreapprovedOfferSnapshot, Base, Retrieved offer evidence for journey start/resume, Tests for simulations router, Test that simulation rejects amount exceeding offer max, Test POST /api/v1/simulations/calculate validates offer exists, Test GET /api/v1/simulations/{simulation_id} returns 404, Test POST /api/v1/simulations/confirm requires valid simulation (+6 more)

### Community 28 - "simulations.py"
Cohesion: 0.16
Nodes (14): confirm_simulation(), create_simulation(), Session, Calculate real-time simulation for requested amount and term.      Validates amo, Confirm simulation and proceed to account selection.      Advances journey state, Config, BaseModel, Schemas for simulation endpoints (+6 more)

### Community 29 - "AMLAdapter"
Cohesion: 0.17
Nodes (9): AMLAdapter, Any, AML/PBC Verification Adapter - Anti-money laundering and PEP screening, Adapter for AML/PBC Service integration.      Handles:     - Anti-money launderi, Normalize AML/PBC screening result to standard decision.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Perform AML/PBC screening.          Args:             customer_id: Customer iden, aml_adapter() (+1 more)

### Community 30 - "FraudAdapter"
Cohesion: 0.17
Nodes (9): FraudAdapter, Any, Anti-Fraud Verification Adapter - Fraud screening, Adapter for Anti-Fraud Service integration.      Handles:     - Fraud risk scree, Normalize fraud screening result to standard decision.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Perform anti-fraud screening.          Args:             customer_id: Customer i, fraud_adapter() (+1 more)

### Community 31 - "__init__.py"
Cohesion: 0.18
Nodes (8): External integration adapters, Any, Servicing Adapter - Active loan servicing handoff, Adapter for Active-Loan Servicing Context integration.      Handles:     - Loan, Get active loan status from servicing context.          Args:             iris_r, Initialize adapter with timeout budget.          Args:             timeout: Requ, Project active loan to servicing context.          Args:             iris_refere, ServicingAdapter

### Community 32 - "SimulationSnapshot"
Cohesion: 0.15
Nodes (8): Base, Confirmed and draft simulation versions, SimulationSnapshot, Simulation Service - Real-time pricing simulation, Persist simulation snapshot, Retrieve simulation snapshot by ID, Get latest simulation for a journey, Get confirmed simulation for a journey

### Community 33 - "config.py"
Cohesion: 0.17
Nodes (8): Creditworthiness Verification Adapter - Light creditworthiness checks, Pre-Approval Engine Adapter - Offer retrieval and eligibility, Config, Application configuration management, Parse CORS origins from comma-separated string, Application settings loaded from environment variables, Settings, BaseSettings

### Community 34 - "database.py"
Cohesion: 0.17
Nodes (7): get_db(), Database connection and session management, Database session dependency for FastAPI routes, Amortization Installment model, Document Package model, Entity Configuration model, Verification Execution model

### Community 35 - "AccountResponse"
Cohesion: 0.20
Nodes (11): list_disbursement_accounts(), Session, Retrieve eligible disbursement accounts for the customer.      Returns list of a, Select a disbursement account for the loan.      Validates account operability a, select_disbursement_account(), AccountResponse, AccountsListResponse, BaseModel (+3 more)

### Community 36 - "auth.py"
Cohesion: 0.24
Nodes (11): login(), LoginRequest, LoginResponse, BaseModel, Session, Authentication router - login endpoint, Login request payload, User information in response (+3 more)

### Community 37 - "__init__.py"
Cohesion: 0.24
Nodes (10): Pydantic schemas for request/response validation, Config, BaseModel, Schemas for signature endpoints, Signature session response, Signature callback from SCA provider, Initiate PSD2/SCA signature session, SignatureCallbackRequest (+2 more)

### Community 38 - "CreditworthinessAdapter"
Cohesion: 0.20
Nodes (8): CreditworthinessAdapter, Any, Adapter for Creditworthiness Service integration.      Handles:     - Light cred, Normalize heterogeneous provider decisions to standard values.          Args:, Initialize adapter with timeout budget.          Args:             timeout: Requ, Perform light creditworthiness verification.          Args:             customer, creditworthiness_adapter(), Create creditworthiness adapter instance

### Community 39 - "list_offers"
Cohesion: 0.22
Nodes (10): list_offers(), Session, Retrieve actionable pre-approved offers for the authenticated customer.      Ret, Config, OfferResponse, OffersListResponse, BaseModel, Schemas for offer endpoints (+2 more)

### Community 40 - ".execute_booking"
Cohesion: 0.20
Nodes (6): Any, Simulate IRIS booking call (for testing), Get latest booking command for a journey, Get latest booking status for a journey, Generate deterministic idempotency key.          Format: {entityId}:{journeyId}:, Execute idempotent booking command to IRIS.          Implements write-before-sen

### Community 41 - "__init__.py"
Cohesion: 0.20
Nodes (5): Booking Command model, Idempotency Record model, ORM models for the Pre-Approved Loan Platform, Loan Activation Projection model, Simulation Snapshot model

### Community 42 - "test_offers_router.py"
Cohesion: 0.20
Nodes (9): Tests for offers router, Test that list_offers validates entity configuration exists, Test GET /api/v1/offers/{offer_id} returns 404 for nonexistent offer, Test GET /api/v1/offers/{offer_id} returns offer details, Test GET /api/v1/offers/ returns offers list, test_get_offer_returns_404_for_nonexistent_offer(), test_get_offer_returns_offer_details(), test_list_offers_returns_offers_list() (+1 more)

### Community 43 - "PaginatedResponse"
Cohesion: 0.22
Nodes (6): PaginatedResponse, BaseModel, Pagination wrapper for list endpoints, Total number of pages, Whether there is a next page, Whether there is a previous page

### Community 44 - "BookingStatusResponse"
Cohesion: 0.29
Nodes (7): BookingExecuteRequest, BookingStatusResponse, Config, BaseModel, Schemas for booking and disbursement endpoints, Booking and disbursement status, Execute IRIS booking and disbursement

### Community 45 - "get_user_by_id"
Cohesion: 0.29
Nodes (7): get_user_by_id(), Session, Retrieve user by ID.      Args:         db: Database session         user_id: Us, Test retrieving user by ID, Test retrieving non-existent user returns None, test_get_user_by_id_returns_none_for_nonexistent(), test_get_user_by_id_returns_user()

### Community 46 - ".get_offer_snapshot"
Cohesion: 0.29
Nodes (4): Any, Revalidate offer status on resume or before sensitive transitions.          In p, Retrieve actionable offers for a customer.          In production, this would ca, Retrieve offer snapshot by ID

### Community 47 - "env.py"
Cohesion: 0.33
Nodes (5): Alembic migration environment configuration, Run migrations in 'offline' mode, Run migrations in 'online' mode, run_migrations_offline(), run_migrations_online()

### Community 48 - "DisbursementAccountSelection"
Cohesion: 0.40
Nodes (4): DisbursementAccountSelection, Base, Disbursement Account Selection model, Selected disbursement account with operability validation

### Community 49 - "OutboxEvent"
Cohesion: 0.40
Nodes (4): OutboxEvent, Base, Outbox Event model - transactional event publication, Transactional outbox for reliable event emission

### Community 50 - "get_booking_status"
Cohesion: 0.40
Nodes (5): execute_booking(), get_booking_status(), Session, Execute idempotent IRIS booking and disbursement.      Implements write-before-s, Poll booking and disbursement status.      Returns current status and reconcilia

### Community 51 - "StateTransitionError"
Cohesion: 0.40
Nodes (4): Raised when an invalid state transition is attempted, Validate that a state transition is allowed.          Args:             current_, StateTransitionError, Exception

### Community 52 - "offer_service.py"
Cohesion: 0.40
Nodes (3): datetime, Offer Service - Offer retrieval and eligibility normalization, Persist offer snapshot for journey start/resume

### Community 53 - ".simulate"
Cohesion: 0.50
Nodes (3): Any, Calculate loan pricing.         Simplified French amortization schedule calculat, Perform real-time simulation with validation.          Args:             journey

### Community 54 - "conftest.py"
Cohesion: 0.50
Nodes (3): db_session(), Pytest fixtures for testing, Create an in-memory SQLite database session for testing.     Each test gets a fr

## Knowledge Gaps
- **10 isolated node(s):** `Config`, `Config`, `Config`, `Config`, `Config` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IRISAdapter` connect `reconciliation_worker.py` to `ReconciliationWorker`, `test_iris_adapter.py`, `__init__.py`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `JourneyOrchestrator` connect `JourneyOrchestrator` to `DocumentService`, `AccountResponse`, `ReconciliationWorker`, `dependencies.py`, `SignatureService`, `JourneyInstance`, `__init__.py`, `journey.py`, `StateTransitionError`, `reconciliation_worker.py`, `simulations.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `EntityConfiguration` connect `EntityConfiguration` to `DocumentService`, `SimulationSnapshot`, `database.py`, `User`, `test_reconciliation_worker.py`, `__init__.py`, `.get_offer_snapshot`, `main.py`, `offer_service.py`, `.simulate`, `JourneyOrchestrator`, `SimulationService`, `PreapprovedOfferSnapshot`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `JourneyOrchestrator` (e.g. with `AuditService` and `ReconciliationWorker`) actually correct?**
  _`JourneyOrchestrator` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `EntityConfiguration` (e.g. with `.generate_document_package()` and `.retrieve_offers()`) actually correct?**
  _`EntityConfiguration` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `ReconciliationWorker` (e.g. with `IRISAdapter` and `AuditService`) actually correct?**
  _`ReconciliationWorker` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Config`, `Config` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._