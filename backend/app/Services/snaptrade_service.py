# app/Services/snaptrade_service.py

from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.auth_user_repository import AuthUserRepository
from app.Models.profile import Profile
from app.config import settings
from snaptrade_client import SnapTrade

class SnapTradeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = AuthUserRepository(db)

    async def register_snaptrade_user(self, user_id: uuid.UUID) -> dict:
        """
        Registers a user with SnapTrade if they don't already have a user secret.
        Saves the secret to the user's profile.
        """
        user = await self.user_repo.get(user_id)
        if not user:
            return {"error": "User not found."}

        if not user.profile:
            print(f"User {user_id} does not have a profile. Creating one now.")
            new_profile = Profile(id=user_id)
            self.db.add(new_profile)
            await self.db.commit()
            await self.db.refresh(user)

        if user.profile.snaptrade_user_secret:
            return {"error": "User is already registered with SnapTrade."}

        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID,
            )
            api_response = client.authentication.register_snap_trade_user(
                body={ "userId": str(user_id) }
            )
            user_secret = api_response.body.get('userSecret')
            if not user_secret:
                return {"error": "SnapTrade API did not return a userSecret."}
        except Exception as e:
            print("--- SNAPTRADE REGISTRATION API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("------------------------------------")
            return {"error": "Failed to register user with SnapTrade. Check backend logs for details."}

        user.profile.snaptrade_user_secret = user_secret
        await self.db.commit()
        await self.db.refresh(user.profile)

        return {"success": True, "userId": user_id}

    async def generate_connection_link(self, user_id: uuid.UUID) -> dict:
        """
        Generates a SnapTrade Connection Portal URL for a given user.
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.profile or not user.profile.snaptrade_user_secret:
            return {"error": "User is not registered with SnapTrade or secret is missing."}

        user_secret = user.profile.snaptrade_user_secret

        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID
            )
            api_response = client.authentication.login_snap_trade_user(
                user_id=str(user_id),
                user_secret=user_secret,
                body={"customRedirect": "http://localhost:5173/connections?status=success"}
            )

            redirect_uri = api_response.body.get('redirectURI')

            if not redirect_uri:
                print("SnapTrade API did not return a redirectURI.")
                return {"error": "SnapTrade API did not return a redirectURI."}

            return {"redirectURI": redirect_uri}

        except Exception as e:
            print("--- SNAPTRADE CONNECTION LINK API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("---------------------------------------")
            return {"error": "Failed to generate connection link from SnapTrade. Check backend logs for details."}
