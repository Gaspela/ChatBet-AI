import httpx
import asyncio
from typing import Dict, Any, Optional, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ChatBetClient:
    """
    HTTP client for ChatBet API integration.
    
    Features:
    - Authentication endpoints (generate/validate tokens)
    - Sports data retrieval (sports, tournaments, fixtures)
    - Betting operations (odds, place bets)
    - Async HTTP requests with token-based auth
    """
    
    def __init__(self):
        self.base_url = settings.chatbet_api_base_url
        self.timeout = settings.chatbet_api_timeout
        self._auth_token: Optional[str] = None
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {}
        if self._auth_token:
            default_headers["token"] = self._auth_token
        
        if headers:
            default_headers.update(headers)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=default_headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise
    
    async def generate_token(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/auth/generate_token")
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        headers = {"token": token}
        return await self._make_request("GET", "/auth/validate_token", headers=headers)
    
    async def validate_user(self, user_key: str) -> Dict[str, Any]:
        params = {"userKey": user_key}
        return await self._make_request("GET", "/auth/validate_user", params=params)
    
    async def get_user_balance(self, user_id: str, user_key: str, token: str) -> Dict[str, Any]:
        params = {"userId": user_id, "userKey": user_key}
        headers = {"token": token}
        return await self._make_request("GET", "/auth/get_user_balance", params=params, headers=headers)
    
    async def get_sports(self) -> Dict[str, Any]:
        return await self._make_request("GET", "/sports")
    
    async def get_tournaments(
        self, 
        sport_id: int = 1, 
        language: str = "en", 
        with_active_fixtures: bool = False
    ) -> Dict[str, Any]:
        params = {
            "sport_id": sport_id,
            "language": language,
            "with_active_fixtures": with_active_fixtures
        }
        return await self._make_request("GET", "/sports/tournaments", params=params)
    
    async def get_all_tournaments(
        self, 
        language: str = "en", 
        with_active_fixtures: bool = False
    ) -> Dict[str, Any]:
        params = {
            "language": language,
            "with_active_fixtures": with_active_fixtures
        }
        return await self._make_request("GET", "/sports/all-tournaments", params=params)
    
    async def get_fixtures(
        self,
        tournament_id: int = 566,
        fixture_type: str = "pre_match",
        language: str = "en",
        time_zone: str = "UTC"
    ) -> Dict[str, Any]:
        params = {
            "tournamentId": tournament_id,
            "type": fixture_type,
            "language": language,
            "time_zone": time_zone
        }
        return await self._make_request("GET", "/sports/fixtures", params=params)
    
    async def get_sports_fixtures(
        self,
        sport_id: int = 1,
        fixture_type: str = "pre_match",
        time_zone: str = "UTC",
        language: str = "en"
    ) -> Dict[str, Any]:
        params = {
            "sportId": sport_id,
            "type": fixture_type,
            "time_zone": time_zone,
            "language": language
        }
        return await self._make_request("GET", "/sports/sports-fixtures", params=params)
    
    async def get_odds(
        self,
        sport_id: int = 1,
        tournament_id: int = 566,
        fixture_id: int = 27907678,
        amount: int = 1
    ) -> Dict[str, Any]:
        params = {
            "sportId": sport_id,
            "tournamentId": tournament_id,
            "fixtureId": fixture_id,
            "amount": amount
        }
        return await self._make_request("GET", "/sports/odds", params=params)
    
    async def place_bet(
        self, 
        bet_data: Dict[str, Any],
        accept_language: str = "es",
        country_code: str = "BR",
        token: str = None
    ) -> Dict[str, Any]:
        headers = {
            "accept-language": accept_language,
            "country-code": country_code
        }
        if token:
            headers["token"] = token
        
        return await self._make_request("POST", "/place-bet", json_data=bet_data, headers=headers)
    
    def set_auth_token(self, token: str):
        self._auth_token = token