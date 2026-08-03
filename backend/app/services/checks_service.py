"""Checks Service - Verification orchestration"""
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import VerificationExecution, VerificationResult


class ChecksService:
    """
    Orchestrates creditworthiness, anti-fraud, and AML/PBC checks.
    Normalizes heterogeneous provider outcomes into PASS/REJECT/REVIEW decisions.
    """

    def __init__(self, db: Session):
        self.db = db

    def execute_checks(
        self,
        journey_id: str,
        customer_id: str,
        entity_id: str,
        check_context: Dict[str, Any]
    ) -> VerificationExecution:
        """
        Initiate parallel verification checks.

        In production, calls verification adapters (creditworthiness, fraud, AML).
        Returns execution record with initial PENDING status.
        """
        execution_id = f"chk_{uuid.uuid4().hex[:16]}"

        execution = VerificationExecution(
            execution_id=execution_id,
            journey_id=journey_id,
            customer_id=customer_id,
            entity_id=entity_id,
            status="PENDING"
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        # In production: trigger async verification calls here
        # For now, simulate immediate completion with mock results
        self._simulate_checks(execution_id, journey_id)

        return execution

    def _simulate_checks(
        self,
        execution_id: str,
        journey_id: str
    ) -> None:
        """
        Simulate verification checks (for testing).
        In production, this would be async via adapters.
        """
        # Simulate creditworthiness check
        self._record_check_result(
            execution_id=execution_id,
            journey_id=journey_id,
            check_type="CREDITWORTHINESS",
            provider="CREDIT_BUREAU",
            decision="PASS",
            provider_response={"score": 750, "rating": "A"}
        )

        # Simulate anti-fraud check
        self._record_check_result(
            execution_id=execution_id,
            journey_id=journey_id,
            check_type="ANTI_FRAUD",
            provider="FRAUD_SERVICE",
            decision="PASS",
            provider_response={"risk_score": 0.15, "verdict": "LOW_RISK"}
        )

        # Simulate AML/PBC check
        self._record_check_result(
            execution_id=execution_id,
            journey_id=journey_id,
            check_type="AML_PBC",
            provider="AML_SERVICE",
            decision="PASS",
            provider_response={"pep_match": False, "sanctions_match": False}
        )

        # Update execution status
        execution = self.db.query(VerificationExecution).filter(
            VerificationExecution.execution_id == execution_id
        ).first()

        if execution:
            execution.status = "COMPLETED"
            self.db.commit()

    def _record_check_result(
        self,
        execution_id: str,
        journey_id: str,
        check_type: str,
        provider: str,
        decision: str,
        provider_response: Dict[str, Any]
    ) -> VerificationResult:
        """Record individual check result"""
        result = VerificationResult(
            execution_id=execution_id,
            journey_id=journey_id,
            check_type=check_type,
            provider=provider,
            decision=decision,
            provider_response=provider_response
        )

        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)

        return result

    def get_execution_status(
        self,
        execution_id: str
    ) -> Optional[VerificationExecution]:
        """Get verification execution status"""
        return self.db.query(VerificationExecution).filter(
            VerificationExecution.execution_id == execution_id
        ).first()

    def get_latest_execution_for_journey(
        self,
        journey_id: str
    ) -> Optional[VerificationExecution]:
        """Get the latest verification execution for a journey"""
        return self.db.query(VerificationExecution).filter(
            VerificationExecution.journey_id == journey_id
        ).order_by(VerificationExecution.created_at.desc()).first()

    def get_check_results(
        self,
        execution_id: str
    ) -> List[VerificationResult]:
        """Get all check results for an execution"""
        return self.db.query(VerificationResult).filter(
            VerificationResult.execution_id == execution_id
        ).all()

    def get_normalized_decision(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get normalized decision from all checks.

        Returns:
            {
                "decision": "PASS" | "REJECT" | "REVIEW",
                "reason_code": optional blocking reason,
                "check_results": individual check outcomes
            }
        """
        results = self.get_check_results(execution_id)

        if not results:
            return {
                "decision": "PENDING",
                "reason_code": "CHECKS_NOT_COMPLETED",
                "check_results": []
            }

        # Aggregate decisions
        decisions = [r.decision for r in results]

        # If any REJECT, overall is REJECT
        if "REJECT" in decisions:
            return {
                "decision": "REJECT",
                "reason_code": "VERIFICATION_FAILED",
                "check_results": [
                    {
                        "check_type": r.check_type,
                        "decision": r.decision,
                        "provider": r.provider
                    }
                    for r in results
                ]
            }

        # If any REVIEW, overall is REVIEW
        if "REVIEW" in decisions:
            return {
                "decision": "REVIEW",
                "reason_code": "MANUAL_REVIEW_REQUIRED",
                "check_results": [
                    {
                        "check_type": r.check_type,
                        "decision": r.decision,
                        "provider": r.provider
                    }
                    for r in results
                ]
            }

        # All PASS
        return {
            "decision": "PASS",
            "reason_code": None,
            "check_results": [
                {
                    "check_type": r.check_type,
                    "decision": r.decision,
                    "provider": r.provider
                }
                for r in results
            ]
        }
