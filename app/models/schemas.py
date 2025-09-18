from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

"""
ChatBet AI Models - Pydantic Data Models

Data models and structures for ChatBet AI Assistant application.
All models use Pydantic for automatic validation, serialization, and type safety.

Model Categories:
- Chat & Communication: ChatMessage, ChatResponse for API interactions
- User Management: UserContext for session and conversation state
- Betting Operations: SimulatedBet, BetSimulation, BetResult for bet tracking
- Sports Data: SportEvent, OddsInfo, Sport, Tournament, Fixture for API data
- Financial: UserBalance for account management
- API Integration: OddsData for external API responses

Features:
- Type validation with Pydantic BaseModel
- Optional fields with default values
- DateTime handling for timestamps
- Nested dictionaries for complex data structures
- List typing for collections
"""

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_key: Optional[str] = "1"

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    data: Optional[Dict[str, Any]] = None

class UserContext(BaseModel):
    user_id: Optional[str] = None
    session_id: str
    conversation_history: List[Dict[str, Any]] = []
    last_intent: Optional[str] = None
    mentioned_teams: List[str] = []
    mentioned_tournaments: List[str] = []
    user_balance: Optional[float] = None
    user_key: Optional[str] = None
    auth_token: Optional[str] = None
    simulated_bets: List[Dict[str, Any]] = []

class SimulatedBet(BaseModel):
    bet_id: str
    fixture_id: str
    bet_type: str
    amount: float
    odds: float
    potential_payout: float
    potential_profit: float
    team: str
    match_info: str
    timestamp: str
    status: str = "pending"
    confirmed: bool = False

class BetSimulation(BaseModel):
    fixture_id: str
    bet_type: str
    amount: float
    odds: float
    potential_profit: float
    teams: List[str]
    match_info: str

class SportEvent(BaseModel):
    fixture_id: str
    sport_name: str
    tournament_name: str
    team_home: str
    team_away: str
    start_time: Optional[datetime] = None
    status: Optional[str] = None

class OddsInfo(BaseModel):
    fixture_id: str
    bet_type: str
    odds_value: float
    description: str

class Sport(BaseModel):
    id: str
    name: str
    alias: str
    name_es: str
    name_en: str
    name_pt_br: str

class Tournament(BaseModel):
    tournament_id: str
    tournament_name: str
    sport_name: Dict[str, str]

class Fixture(BaseModel):
    id: str
    start_time: str
    sport_id: str
    tournament: Dict[str, str]
    home_competitor: Dict[str, str]
    away_competitor: Dict[str, str]

class OddsData(BaseModel):
    status: str
    main_market: str
    result: Dict[str, Dict[str, Any]]
    both_teams_to_score: Optional[Dict[str, Dict[str, Any]]] = None
    double_chance: Optional[Dict[str, Dict[str, Any]]] = None
    over_under: Optional[Dict[str, Dict[str, Any]]] = None

class UserBalance(BaseModel):
    flag: int
    money: float
    playable_balance: float
    withdrawable_balance: float
    bonus_balance: float
    redeemed_bonus: float

class BetResult(BaseModel):
    message: str
    bet_id: str
    possible_win: float