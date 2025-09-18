from typing import Dict, List, Any, Optional, Tuple
from app.services.chatbet_client import ChatBetClient
from app.models.schemas import Sport, Tournament, Fixture, OddsData, UserBalance
import asyncio
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class DataService:
    """
    Data service with caching and intelligent sports data processing.
    
    Features:
    - Smart caching system with expiration times
    - Sports data retrieval (sports, tournaments, fixtures)
    - Odds processing and analysis
    - Team and date-based filtering
    - User balance management
    """
    
    def __init__(self, chatbet_client: ChatBetClient):
        self.client = chatbet_client
        
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
        self.cache_durations = {
            "sports": 60,
            "tournaments": 30,
            "fixtures": 10,
            "odds": 2,
            "user_balance": 5,
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache_expiry:
            return False
        return datetime.now() < self._cache_expiry[key]
    
    def _set_cache(self, key: str, data: Any, cache_type: str) -> None:
        self._cache[key] = data
        expiry_minutes = self.cache_durations.get(cache_type, 10)
        self._cache_expiry[key] = datetime.now() + timedelta(minutes=expiry_minutes)
    
    async def get_sports(self) -> List[Dict[str, Any]]:
        cache_key = "all_sports"
        
        if self._is_cache_valid(cache_key):
            logger.info("Using cached sports data")
            return self._cache[cache_key]
        
        try:
            sports_data = await self.client.get_sports()
            self._set_cache(cache_key, sports_data, "sports")
            logger.info(f"Fetched {len(sports_data)} sports from API")
            return sports_data
        except Exception as e:
            logger.error(f"Error fetching sports: {e}")
            return []
    
    async def get_all_tournaments(self) -> List[Dict[str, Any]]:
        cache_key = "all_tournaments"
        
        if self._is_cache_valid(cache_key):
            logger.info("Using cached tournaments data")
            return self._cache[cache_key]
        
        try:
            tournaments_data = await self.client.get_all_tournaments()
            self._set_cache(cache_key, tournaments_data, "tournaments")
            logger.info(f"Fetched tournaments for {len(tournaments_data)} sports")
            return tournaments_data
        except Exception as e:
            logger.error(f"Error fetching tournaments: {e}")
            return []
    
    async def get_fixtures_for_sport(self, sport_id: int = 1) -> List[Dict[str, Any]]:
        cache_key = f"fixtures_sport_{sport_id}"
        
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached fixtures for sport {sport_id}")
            return self._cache[cache_key]
        
        try:
            fixtures_data = await self.client.get_sports_fixtures(sport_id=sport_id)
            if fixtures_data and isinstance(fixtures_data[0], dict) and "totalResults" in fixtures_data[0]:
                fixtures_data = fixtures_data[1:]
            
            self._set_cache(cache_key, fixtures_data, "fixtures")
            logger.info(f"Fetched {len(fixtures_data)} fixtures for sport {sport_id}")
            return fixtures_data
        except Exception as e:
            logger.error(f"Error fetching fixtures for sport {sport_id}: {e}")
            return []
    
    async def get_odds_for_fixture(self, sport_id: int, tournament_id: int, fixture_id: int) -> Dict[str, Any]:
        cache_key = f"odds_{sport_id}_{tournament_id}_{fixture_id}"
        
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached odds for fixture {fixture_id}")
            return self._cache[cache_key]
        
        try:
            odds_data = await self.client.get_odds(
                sport_id=sport_id,
                tournament_id=tournament_id,
                fixture_id=fixture_id
            )
            self._set_cache(cache_key, odds_data, "odds")
            logger.info(f"Fetched odds for fixture {fixture_id}")
            return odds_data
        except Exception as e:
            logger.error(f"Error fetching odds for fixture {fixture_id}: {e}")
            return {}
    
    async def get_user_balance(self, user_id: str, user_key: str, token: str) -> Dict[str, Any]:
        cache_key = f"balance_{user_id}"
        
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached balance for user {user_id}")
            return self._cache[cache_key]
        
        try:
            balance_data = await self.client.get_user_balance(user_id, user_key, token)
            self._set_cache(cache_key, balance_data, "user_balance")
            logger.info(f"Fetched balance for user {user_id}: ${balance_data.get('money', 0)}")
            return balance_data
        except Exception as e:
            logger.error(f"Error fetching balance for user {user_id}: {e}")
            return {}
    
    def find_team_in_fixtures(self, team_name: str, fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        team_name_lower = team_name.lower()
        matching_fixtures = []
        
        for fixture in fixtures:
            try:
                home_team = ""
                away_team = ""
                
                if "homeCompetitor" in fixture:
                    home_team = fixture.get("homeCompetitor", {}).get("name", "").lower()
                    away_team = fixture.get("awayCompetitor", {}).get("name", "").lower()

                if not home_team and "home_team_data" in fixture:
                    home_team = fixture.get("home_team_data", {}).get("name", {}).get("en", "").lower()
                    away_team = fixture.get("away_team_data", {}).get("name", {}).get("en", "").lower()

                if (team_name_lower in home_team or team_name_lower in away_team or
                    home_team in team_name_lower or away_team in team_name_lower):
                    matching_fixtures.append(fixture)
                    
            except (AttributeError, KeyError) as e:
                logger.warning(f"Error processing fixture for team search: {e}")
                continue
        
        return matching_fixtures
    
    def find_fixtures_by_date(self, fixtures: List[Dict[str, Any]], target_date: str) -> List[Dict[str, Any]]:
        today = datetime.now()
        target_dates = []
        
        if target_date.lower() == "today":
            target_dates = [today.strftime("%m-%d")]
        elif target_date.lower() == "tomorrow":
            tomorrow = today + timedelta(days=1)
            target_dates = [tomorrow.strftime("%m-%d")]
        elif target_date.lower() == "sunday":

            days_ahead = 6 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_sunday = today + timedelta(days_ahead)
            target_dates = [next_sunday.strftime("%m-%d")]
        elif target_date.lower() in ["weekend", "fin de semana"]:
            days_to_saturday = 5 - today.weekday()
            if days_to_saturday <= 0:
                days_to_saturday += 7
            saturday = today + timedelta(days=days_to_saturday)
            sunday = saturday + timedelta(days=1)
            target_dates = [saturday.strftime("%m-%d"), sunday.strftime("%m-%d")]
            logger.info(f"Weekend dates: {target_dates}")
        else:
            date_to_use = target_date
            if "-" in target_date and len(target_date) == 5:
                parts = target_date.split("-")
                if len(parts) == 2 and len(parts[0]) == 2 and len(parts[1]) == 2:
                    if int(parts[0]) > 12:
                        date_to_use = f"{parts[1]}-{parts[0]}"
            target_dates = [date_to_use]
        
        matching_fixtures = []
        for fixture in fixtures:
            try:
                start_time = fixture.get("startTime", "")
                for date in target_dates:
                    if date in start_time:
                        matching_fixtures.append(fixture)
                        break
            except (AttributeError, KeyError):
                continue
        
        logger.info(f"Found {len(matching_fixtures)} fixtures for date(s) {target_dates}")
        return matching_fixtures
    
    def extract_best_odds(self, odds_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not odds_data or "result" not in odds_data:
            return []
        
        best_odds = []
        result_odds = odds_data["result"]
        
        if "homeTeam" in result_odds:
            home_odds = result_odds["homeTeam"]
            best_odds.append({
                "bet_type": "home_win",
                "team": home_odds.get("name", "Home"),
                "odds": home_odds.get("odds", 0),
                "bet_id": home_odds.get("betId", "")
            })
        
        if "tie" in result_odds:
            draw_odds = result_odds["tie"]
            best_odds.append({
                "bet_type": "draw",
                "team": draw_odds.get("name", "Draw"),
                "odds": draw_odds.get("odds", 0),
                "bet_id": draw_odds.get("betId", "")
            })
        
        if "awayTeam" in result_odds:
            away_odds = result_odds["awayTeam"]
            best_odds.append({
                "bet_type": "away_win",
                "team": away_odds.get("name", "Away"),
                "odds": away_odds.get("odds", 0),
                "bet_id": away_odds.get("betId", "")
            })
        
        if "over_under" in odds_data:
            over_under = odds_data["over_under"]
            if "over" in over_under:
                over_odds = over_under["over"]
                best_odds.append({
                    "bet_type": "over",
                    "team": over_odds.get("name", "Over"),
                    "odds": over_odds.get("odds", 0),
                    "bet_id": over_odds.get("betId", "")
                })
        
        return best_odds
    
    def format_fixture_summary(self, fixture: Dict[str, Any]) -> str:
        try:
            home_team = fixture.get("homeCompetitor", {}).get("name", "Team A")
            away_team = fixture.get("awayCompetitor", {}).get("name", "Team B")
            start_time = fixture.get("startTime", "TBD")
            tournament = fixture.get("tournament", {}).get("name", "Unknown Tournament")
            
            return f"{home_team} vs {away_team} - {start_time} ({tournament})"
        except Exception:
            return "Fixture information not available"
    
    def calculate_potential_win(self, amount: float, odds: float) -> float:
        return round(amount * odds, 2)