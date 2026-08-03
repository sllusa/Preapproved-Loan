"""API routers package"""
from app.routers.accounts import router as accounts_router
from app.routers.activation import router as activation_router
from app.routers.auth import router as auth_router
from app.routers.booking import router as booking_router
from app.routers.documents import router as documents_router
from app.routers.journey import router as journey_router
from app.routers.offers import router as offers_router
from app.routers.signature import router as signature_router
from app.routers.simulations import router as simulations_router
from app.routers.verifications import router as verifications_router

__all__ = [
    "auth_router",
    "offers_router",
    "simulations_router",
    "accounts_router",
    "documents_router",
    "verifications_router",
    "signature_router",
    "booking_router",
    "activation_router",
    "journey_router",
]
