from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, ProfileBase, Token
from app.repository.user import UserRepository
from app.services.user import UserService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.register_user(user_in)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.authenticate_user(form_data.username, form_data.password)

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user_profile(current_user.id)

@router.put("/me/profile", response_model=UserResponse)
async def update_user_profile_me(
    profile_data: ProfileBase,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.update_user_profile(current_user.id, profile_data)

@router.delete("/me")
async def delete_users_me(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.delete_user(current_user.id)
