from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User, Profile
from app.schemas.user import UserCreate, ProfileBase
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.profile))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.profile))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user: UserCreate) -> User:
        hashed_pwd = get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_pwd)
        self.db.add(db_user)
        await self.db.flush() # flush to get the id
        
        # Create empty profile
        db_profile = Profile(user_id=db_user.id)
        self.db.add(db_profile)
        
        await self.db.commit()
        await self.db.refresh(db_user)
        # load relationship
        stmt = select(User).where(User.id == db_user.id).options(selectinload(User.profile))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_profile(self, user_id: int, profile_data: ProfileBase) -> Profile | None:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.db.execute(stmt)
        profile = result.scalars().first()
        
        if not profile:
            return None
            
        update_data = profile_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)
            
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
