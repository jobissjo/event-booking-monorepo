from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.payment import PaymentIntentCreate, PaymentResponse, PaymentStatusUpdate
from app.services.payment_service import PaymentService


router = APIRouter()


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


@router.post("/payments/intents", response_model=PaymentResponse, status_code=201)
async def create_payment_intent(
    payment_in: PaymentIntentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    return await service.create_payment_intent(payment_in)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service),
):
    return await service.get_payment(payment_id)


@router.patch("/payments/{payment_id}/status", response_model=PaymentResponse)
async def update_payment_status(
    payment_id: UUID,
    status_in: PaymentStatusUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    return await service.update_payment_status(payment_id, status_in)
