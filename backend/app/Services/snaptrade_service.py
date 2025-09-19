# app/Services/snaptrade_service.py

from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.auth_user_repository import AuthUserRepository
from app.Models.profile import Profile  # Import the Profile model
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
        # This makes the system robust for users created before the profile trigger was active.
        if not user.profile:
            print(f"User {user_id} does not have a profile. Creating one now.")
            new_profile = Profile(id=user_id)
            self.db.add(new_profile)
            await self.db.commit()
            await self.db.refresh(user) # Refresh the user object to load the new profile

        # 3. Check if user is already registered
        if user.profile.snaptrade_user_secret:
            return {"error": "User is already registered with SnapTrade."}

        # 4. Call SnapTrade API to register the user
        #    (This part is mocked as the SDK is not installed)
        try:
            # client = SnapTrade(
            #     consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
            #     client_id=settings.SNAPTRADE_CLIENT_ID,
            # )
            # api_response = client.authentication.register_snap_trade_user(
            #     body={ "userId": str(user_id) }
            # )
            # user_secret = api_response.body['userSecret']

            # Mocked response for now
            print("--- MOCKING SNAPTRADE API CALL ---")
            user_secret = f"mock_secret_for_user_{user_id}"
            print(f"--- Generated mock user secret: {user_secret} ---")

        except Exception as e:
            # In a real scenario, you would log the error from the SnapTrade API
            print(f"Error communicating with SnapTrade API: {e}")
            return {"error": "Failed to register user with SnapTrade."}

        # 5. Save the user secret to the profile
        user.profile.snaptrade_user_secret = user_secret
        await self.db.commit()
        await self.db.refresh(user.profile)

        return {"success": True, "userId": user_id}
