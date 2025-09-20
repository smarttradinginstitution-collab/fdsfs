# app/Services/snaptrade_service.py

from __future__ import annotations
import uuid
from typing import Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.auth_user_repository import AuthUserRepository
from app.Repositories.brokerage_connection_repository import BrokerageConnectionRepository
from app.Models.profile import Profile
from app.config import settings
from snaptrade_client import SnapTrade

class SnapTradeConnectionError(Exception):
    """Custom exception for SnapTrade connection errors."""
    pass

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

    async def list_all_snaptrade_users(self) -> Union[list[str], dict]:
        """
        Lists all user IDs registered with SnapTrade.
        """
        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID,
            )
            api_response = client.authentication.list_snap_trade_users()
            return api_response.body
        except Exception as e:
            print("--- SNAPTRADE LIST USERS API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("------------------------------------")
            return {"error": "Failed to list SnapTrade users. Check backend logs for details."}

    async def delete_snaptrade_user(self, user_id: str) -> dict:
        """
        Deletes a user from SnapTrade and clears their secret from the profile.
        """
        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID,
            )
            # This call is asynchronous on SnapTrade's side
            api_response = client.authentication.delete_snap_trade_user(user_id=user_id)

            # If SnapTrade accepts the request, we clear the secret locally.
            if api_response.body.get("status") == "deleted":
                user_uuid = uuid.UUID(user_id)
                user = await self.user_repo.get(user_uuid)
                if user and user.profile:
                    user.profile.snaptrade_user_secret = None
                    await self.db.commit()
                    await self.db.refresh(user.profile)

            return api_response.body
        except Exception as e:
            print("--- SNAPTRADE DELETE USER API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("-------------------------------------")
            return {"error": "Failed to delete SnapTrade user. Check backend logs for details."}

    async def rotate_snaptrade_user_secret(self, user_id: str) -> dict:
        """
        Rotates a user's SnapTrade secret and saves the new one to their profile.
        """
        user_uuid = uuid.UUID(user_id)
        user = await self.user_repo.get(user_uuid)
        if not user or not user.profile or not user.profile.snaptrade_user_secret:
            return {"error": "User is not registered with SnapTrade or secret is missing."}

        current_secret = user.profile.snaptrade_user_secret

        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID,
            )
            api_response = client.authentication.reset_snap_trade_user_secret(
                user_id=user_id,
                user_secret=current_secret
            )

            new_secret = api_response.body.get("userSecret")
            if new_secret:
                user.profile.snaptrade_user_secret = new_secret
                await self.db.commit()
                await self.db.refresh(user.profile)
            else:
                return {"error": "SnapTrade API did not return a new userSecret."}

            return api_response.body
        except Exception as e:
            print("--- SNAPTRADE ROTATE SECRET API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("---------------------------------------")
            return {"error": "Failed to rotate SnapTrade user secret. Check backend logs for details."}

    async def synchronize_connections(self, user_id: str) -> bool:
        """
        Fetches connections from SnapTrade and upserts them into the local database.
        """
        from sqlalchemy.dialects.postgresql import insert
        from app.Models.brokerage_connection import BrokerageConnection

        user_uuid = uuid.UUID(user_id)
        user = await self.user_repo.get(user_uuid)
        if not user or not user.profile or not user.profile.snaptrade_user_secret:
            return False

        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID,
            )
            connections = client.connections.list_brokerage_authorizations(
                user_id=user_id,
                user_secret=user.profile.snaptrade_user_secret
            )

            if not connections.body:
                return True

            values_to_upsert = []
            for conn in connections.body:
                created_at_str = conn['created_date']
                created_at_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))

                disabled_date_str = conn.get('disabled_date')
                disabled_date_dt = None
                if disabled_date_str:
                    disabled_date_dt = datetime.fromisoformat(disabled_date_str.replace('Z', '+00:00'))

                values_to_upsert.append({
                    'id': conn['id'],
                    'user_id': user_uuid,
                    'brokerage_name': conn['brokerage']['name'],
                    'brokerage_display_name': conn['brokerage'].get('display_name'),
                    'brokerage_logo_url': conn['brokerage'].get('aws_s3_logo_url'),
                    'connection_type': conn['type'],
                    'disabled': conn['disabled'],
                    'disabled_date': disabled_date_dt,
                    'created_at': created_at_dt,
                })

            stmt = insert(BrokerageConnection).values(values_to_upsert)
            update_dict = {
                c.name: c for c in stmt.excluded if c.name not in ['id', 'user_id', 'created_at', 'deleted_at']
            }
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=update_dict,
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception as e:
            print("--- SNAPTRADE SYNC CONNECTIONS API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("------------------------------------------")
            return False

    async def generate_reconnect_link(self, user_id: uuid.UUID, connection_id: str) -> dict:
        """
        Generates a SnapTrade Connection Portal URL for a given user to reconnect a specific connection.
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
                body={"customRedirect": "http://localhost:5173/connections?status=success", "reconnect": connection_id}
            )

            redirect_uri = api_response.body.get('redirectURI')

            if not redirect_uri:
                print("SnapTrade API did not return a redirectURI.")
                return {"error": "SnapTrade API did not return a redirectURI."}

            return {"redirectURI": redirect_uri}

        except Exception as e:
            print("--- SNAPTRADE RECONNECT LINK API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("----------------------------------------")
            return {"error": "Failed to generate reconnect link from SnapTrade. Check backend logs for details."}

    async def delete_connection(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> None:
        """
        Deletes a brokerage connection from SnapTrade and soft-deletes it locally.
        """
        repo = BrokerageConnectionRepository(self.db)
        connection = await repo.get_by_id(connection_id)

        # Security check: Ensure connection exists and belongs to the user
        if not connection or connection.user_id != user_id:
            raise SnapTradeConnectionError("Connection not found or permission denied.")

        # Get user's SnapTrade secret
        user = await self.user_repo.get(user_id)
        if not user or not user.profile or not user.profile.snaptrade_user_secret:
            raise SnapTradeConnectionError("User profile or SnapTrade secret not found.")

        user_secret = user.profile.snaptrade_user_secret

        try:
            client = SnapTrade(
                consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
                client_id=settings.SNAPTRADE_CLIENT_ID
            )
            # This is a synchronous call, a 204 response means success.
            client.connections.remove_brokerage_authorization(
                authorization_id=str(connection_id),
                user_id=str(user_id),
                user_secret=user_secret
            )

            # Soft-delete the connection locally after successful deletion from SnapTrade
            await repo.soft_delete(connection)

        except Exception as e:
            print("--- SNAPTRADE DELETE CONNECTION API ERROR ---")
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print("-------------------------------------------")
            # Re-raise as a custom exception for the controller to handle
            raise SnapTradeConnectionError("Failed to delete connection from SnapTrade.")
