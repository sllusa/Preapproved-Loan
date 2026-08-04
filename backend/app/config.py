"""Application configuration management"""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database - defaults to SQLite for local development
    database_url: str = "sqlite:///./preapproved_loan.db"

    # Application
    secret_key: str = "change-this-to-a-secure-random-key-in-production"
    debug: bool = True
    api_port: int = 9000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # External Services (configured via environment variables)
    # Pre-Approval Engine - Timeout: 1500ms
    pre_approval_engine_url: str = "http://localhost:8001"

    # IRIS Core and Disbursement API - Timeout: 4000ms (booking), 2000ms (status)
    iris_api_url: str = "http://localhost:8002"

    # Account Validation Service - Timeout: 1200ms
    account_validation_url: str = "http://localhost:8003"

    # Document Generation Service - Timeout: 3000ms
    document_generation_url: str = "http://localhost:8004"

    # Creditworthiness Service - Timeout: 2500ms
    creditworthiness_service_url: str = "http://localhost:8005"

    # Anti-Fraud Service - Timeout: 2500ms
    fraud_service_url: str = "http://localhost:8006"

    # AML/PBC Service - Timeout: 2500ms
    aml_service_url: str = "http://localhost:8007"

    # PSD2/SCA Signature Service - Provider-driven timeout
    sca_signature_url: str = "http://localhost:8008"

    # Amortization Schedule Service - Timeout: 2000ms
    amortization_service_url: str = "http://localhost:8009"

    # Active-Loan Servicing Context - Timeout: 2000ms
    servicing_context_url: str = "http://localhost:8010"

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
