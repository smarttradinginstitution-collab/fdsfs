# app/Services/snaptrade_service.py

from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.auth_user_repository import AuthUserRepository
from app.Models.profile import Profile
from app.config import settings
# from snaptrade_python_sdk import SnapTrade # Will be uncommented later
# from snaptrade_python_sdk.apis.tags import authentication_api # Will be uncommented later

class SnapTradeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = AuthUserRepository(db)

    async def register_snaptrade_user(self, user_id: uuid.UUID) -> dict:
        """
        Registers a user with SnapTrade if they don't already have a user secret.
        Saves the secret to the user's profile.
        """
        # 1. Get user
        user = await self.user_repo.get(user_id)
        if not user:
            return {"error": "User not found."}

        # 2. Check for profile, and create it if it doesn't exist.
        if not user.profile:
            print(f"User {user_id} does not have a profile. Creating one now.")
            new_profile = Profile(id=user_id)
            self.db.add(new_profile)
            await self.db.commit()
            await self.db.refresh(user)

        # 3. Check if user is already registered
        if user.profile.snaptrade_user_secret:
            return {"error": "User is already registered with SnapTrade."}

        # 4. Call SnapTrade API to register the user
        try:
            # client = SnapTrade(...)
            # ...
            # user_secret = api_response.body['userSecret']
            print("--- MOCKING SNAPTRADE API CALL ---")
            user_secret = f"mock_secret_for_user_{user_id}"
            print(f"--- Generated mock user secret: {user_secret} ---")
        except Exception as e:
            print(f"Error communicating with SnapTrade API: {e}")
            return {"error": "Failed to register user with SnapTrade."}

        # 5. Save the user secret to the profile
        user.profile.snaptrade_user_secret = user_secret
        await self.db.commit()
        await self.db.refresh(user.profile)

        return {"success": True, "userId": user_id}

    async def generate_connection_link(self, user_id: uuid.UUID) -> dict:
        """
        Generates a SnapTrade Connection Portal URL for a given user.
        """
        # 1. Get user and their SnapTrade secret
        user = await self.user_repo.get(user_id)
        if not user or not user.profile or not user.profile.snaptrade_user_secret:
            return {"error": "User is not registered with SnapTrade or secret is missing."}

        user_secret = user.profile.snaptrade_user_secret

        # 2. Call SnapTrade API to get a redirect URI
        try:
            # client = SnapTrade(...)
            # ...
            # redirect_uri = api_response.body['redirectURI']
            print("--- MOCKING SNAPTRADE LOGIN CALL ---")
            redirect_uri = f"https://app.snaptrade.com/mock-redirect?session_id=12345&user_id={user_id}"
            print(f"--- Generated mock redirect URI: {redirect_uri} ---")
            return {"redirectURI": redirect_uri}
        except Exception as e:
            print(f"Error communicating with SnapTrade API for login link: {e}")
            return {"error": "Failed to generate connection link from SnapTrade."}
