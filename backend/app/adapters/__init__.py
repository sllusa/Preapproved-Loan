"""External integration adapters"""
from app.adapters.account_adapter import AccountAdapter
from app.adapters.aml_adapter import AMLAdapter
from app.adapters.amortization_adapter import AmortizationAdapter
from app.adapters.creditworthiness_adapter import CreditworthinessAdapter
from app.adapters.document_adapter import DocumentAdapter
from app.adapters.fraud_adapter import FraudAdapter
from app.adapters.iris_adapter import IRISAdapter
from app.adapters.pre_approval_adapter import PreApprovalAdapter
from app.adapters.sca_adapter import SCAAdapter
from app.adapters.servicing_adapter import ServicingAdapter

__all__ = [
    "AccountAdapter",
    "AMLAdapter",
    "AmortizationAdapter",
    "CreditworthinessAdapter",
    "DocumentAdapter",
    "FraudAdapter",
    "IRISAdapter",
    "PreApprovalAdapter",
    "SCAAdapter",
    "ServicingAdapter",
]
