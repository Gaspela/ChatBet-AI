from typing import List, Dict, Any
import logging
from .models import UserContext

logger = logging.getLogger(__name__)

class APIAnalyzer:
    """
    API analyzer for intelligent sports betting data processing and analysis.
    
    Features:
    - Betting recommendations based on odds analysis
    - Match competitiveness evaluation
    - Bet simulation with profit calculations
    - Team favorite comparison analysis
    - Real-time odds processing and filtering
    - Integration with ChatBet API through data service
    - Context-aware response generation
    """
    
    def __init__(self, data_service, ensure_auth_callback):
        self.data_service = data_service
        self.ensure_auth_callback = ensure_auth_callback

    async def execute_api_actions(self, actions: List[str], entities: Dict, context: UserContext) -> Dict[str, Any]:
        api_data = {}
        logger.info(f"Executing actions: {actions} with entities: {entities}")
        
        try:
            await self.ensure_auth_callback()
            
            for action in actions:
                if action == "get_fixtures":
                    api_data.update(await self._get_fixtures(entities))
                
                elif action == "get_odds":
                    api_data.update(await self._get_odds(entities, api_data, context))
                
                elif action == "get_balance":
                    api_data.update(await self._get_balance())
            
            return api_data
        
        except Exception as e:
            logger.error(f"Error executing API actions: {str(e)}")
            return {"error": f"Error accessing sports data: {str(e)}"}

    async def _get_fixtures(self, entities: Dict) -> Dict[str, Any]:
        fixtures = await self.data_service.get_fixtures_for_sport(sport_id=1)
        
        if entities.get("teams"):
            filtered_fixtures = []
            for team in entities["teams"]:
                team_fixtures = self.data_service.find_team_in_fixtures(team, fixtures)
                filtered_fixtures.extend(team_fixtures)
            fixtures = filtered_fixtures
        
        if entities.get("dates"):
            for date in entities["dates"]:
                fixtures = self.data_service.find_fixtures_by_date(fixtures, date)
        
        return {"fixtures": fixtures[:10]}

    async def _get_odds(self, entities: Dict, api_data: Dict, context: UserContext) -> Dict[str, Any]:
        fixtures = api_data.get("fixtures", [])
        
        if not fixtures:
            logger.info("Getting fixtures for odds calculation")
            fixtures = await self.data_service.get_fixtures_for_sport(sport_id=1)
            
            if entities.get("teams"):
                filtered_fixtures = []
                for team in entities["teams"]:
                    team_fixtures = self.data_service.find_team_in_fixtures(team, fixtures)
                    filtered_fixtures.extend(team_fixtures)
                fixtures = filtered_fixtures
            
            if entities.get("dates"):
                for date in entities["dates"]:
                    fixtures = self.data_service.find_fixtures_by_date(fixtures, date)
        
        if not fixtures:
            return {"odds": [], "error": "No fixtures found for the specified criteria"}
        
        message_lower = entities.get("_original_message", "").lower()
        
        if self._is_recommendation_query(message_lower) and not entities.get("teams"):
            return await self._process_betting_recommendations(entities, fixtures)
        elif self._is_competitive_query(message_lower):
            return await self._process_competitive_analysis(entities, fixtures)
        elif self._is_favorite_query(message_lower) and entities.get("teams"):
            return await self._process_favorite_comparison(entities, fixtures)
        elif entities.get("amount", 0) > 0:
            return await self._process_bet_simulation(entities, fixtures)
        else:
            return await self._process_standard_odds(fixtures)

    async def _get_balance(self) -> Dict[str, Any]:
        try:
            balance_data = await self.data_service.chatbet_client.get_user_balance()
            return {"user_balance": balance_data.get("balance", 0)}
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return {"user_balance": 1000, "balance_note": "Using demo balance"}

    def _is_recommendation_query(self, message: str) -> bool:
        return any(word in message for word in ["recommend", "suggestion", "best bet", "should I bet"])
    
    def _is_competitive_query(self, message: str) -> bool:
        return any(word in message for word in ["competitive", "balanced", "close", "tight"])
    
    def _is_favorite_query(self, message: str) -> bool:
        return any(word in message for word in ["favorite", "favored", "between"])

    async def _process_betting_recommendations(self, entities: Dict, fixtures: List) -> Dict[str, Any]:
        logger.info("Processing betting recommendation query")
        all_odds = []
        analyzed_fixtures = []
        betting_recommendations = []
        
        if not entities.get("dates"):
            today_fixtures = self.data_service.find_fixtures_by_date(fixtures, "today")
            tomorrow_fixtures = self.data_service.find_fixtures_by_date(fixtures, "tomorrow")
            recent_fixtures = today_fixtures + tomorrow_fixtures
        else:
            recent_fixtures = fixtures
        
        for fixture in recent_fixtures[:5]:
            try:
                fixture_id = fixture.get("id")
                if not fixture_id:
                    continue
                
                odds_data = await self.data_service.get_odds_for_fixture(fixture_id)
                
                if odds_data and odds_data.get("data"):
                    extracted_odds = self.data_service.extract_main_odds(odds_data["data"])
                    
                    if extracted_odds:
                        home_win_odds = None
                        away_win_odds = None
                        draw_odds = None
                        
                        for odd in extracted_odds:
                            if odd.get("bet_type") == "home_win":
                                home_win_odds = odd.get("odds")
                            elif odd.get("bet_type") == "away_win":
                                away_win_odds = odd.get("odds")
                            elif odd.get("bet_type") == "draw":
                                draw_odds = odd.get("odds")
                        
                        if home_win_odds and away_win_odds:
                            home_team = fixture.get("homeCompetitorName", {}).get("en", "")
                            away_team = fixture.get("awayCompetitorName", {}).get("en", "")
                            tournament = fixture.get("tournament_name", {}).get("en", "")
                            
                            recommendation = self._analyze_betting_recommendation(
                                home_team, away_team, tournament,
                                home_win_odds, away_win_odds, draw_odds
                            )
                            
                            if recommendation["score"] > 0:
                                betting_recommendations.append(recommendation)
                                analyzed_fixtures.append({
                                    "fixture": fixture,
                                    "odds": extracted_odds,
                                    "recommendation": recommendation
                                })
            
            except Exception as e:
                logger.error(f"Error processing fixture {fixture.get('id')}: {str(e)}")
                continue
        
        betting_recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "odds": all_odds,
            "analyzed_fixtures": analyzed_fixtures,
            "betting_recommendations": betting_recommendations[:3]
        }

    def _analyze_betting_recommendation(self, home_team: str, away_team: str, tournament: str,
                                      home_win_odds: float, away_win_odds: float, draw_odds: float = None) -> Dict:
        safe_bet_score = 0
        safe_bet_option = ""
        if home_win_odds < 2.0:
            safe_bet_score = 1 / home_win_odds
            safe_bet_option = f"{home_team} to win"
        elif away_win_odds < 2.0:
            safe_bet_score = 1 / away_win_odds
            safe_bet_option = f"{away_team} to win"
        
        value_score = 0
        value_option = ""
        if 2.0 <= home_win_odds <= 3.5:
            value_score = home_win_odds / 3.0
            value_option = f"{home_team} to win"
        elif 2.0 <= away_win_odds <= 3.5:
            value_score = away_win_odds / 3.0
            value_option = f"{away_team} to win"
        elif draw_odds and 3.0 <= draw_odds <= 4.0:
            value_score = draw_odds / 4.0
            value_option = "Draw"
        
        risk_reward_score = 0
        risk_reward_option = ""
        if home_win_odds >= 3.5:
            risk_reward_score = min(home_win_odds / 6.0, 1.0)
            risk_reward_option = f"{home_team} to win (underdog)"
        elif away_win_odds >= 3.5:
            risk_reward_score = min(away_win_odds / 6.0, 1.0)
            risk_reward_option = f"{away_team} to win (underdog)"
        
        best_score = max(safe_bet_score, value_score, risk_reward_score)
        
        if best_score > 0:
            if best_score == safe_bet_score:
                recommendation_type = "Safe Bet"
                option = safe_bet_option
                odds = home_win_odds if "home" in safe_bet_option.lower() else away_win_odds
            elif best_score == value_score:
                recommendation_type = "Value Bet"
                option = value_option
                odds = home_win_odds if "home" in value_option.lower() else (away_win_odds if "away" in value_option.lower() else draw_odds)
            else:
                recommendation_type = "High Risk/High Reward"
                option = risk_reward_option
                odds = home_win_odds if "home" in risk_reward_option.lower() else away_win_odds
            
            return {
                "match": f"{home_team} vs {away_team}",
                "tournament": tournament,
                "recommendation_type": recommendation_type,
                "option": option,
                "odds": odds,
                "score": best_score
            }
        
        return {"score": 0}

    async def _process_competitive_analysis(self, entities: Dict, fixtures: List) -> Dict[str, Any]:
        logger.info("Processing competitive analysis query")
        competitive_matches = []
        
        target_fixtures = fixtures[:8] if not entities.get("dates") else fixtures
        
        for fixture in target_fixtures:
            try:
                fixture_id = fixture.get("id")
                if not fixture_id:
                    continue
                
                odds_data = await self.data_service.get_odds_for_fixture(fixture_id)
                
                if odds_data and odds_data.get("data"):
                    extracted_odds = self.data_service.extract_main_odds(odds_data["data"])
                    
                    if extracted_odds:
                        home_win_odds = None
                        away_win_odds = None
                        draw_odds = None
                        
                        for odd in extracted_odds:
                            if odd.get("bet_type") == "home_win":
                                home_win_odds = odd.get("odds")
                            elif odd.get("bet_type") == "away_win":
                                away_win_odds = odd.get("odds")
                            elif odd.get("bet_type") == "draw":
                                draw_odds = odd.get("odds")
                        
                        if home_win_odds and away_win_odds:
                            competitiveness_score = self._calculate_competitiveness(
                                home_win_odds, away_win_odds, draw_odds
                            )
                            
                            competitive_matches.append({
                                "fixture": fixture,
                                "home_win_odds": home_win_odds,
                                "away_win_odds": away_win_odds,
                                "draw_odds": draw_odds,
                                "competitiveness_score": competitiveness_score,
                                "odds": extracted_odds
                            })
            
            except Exception as e:
                logger.error(f"Error analyzing competitiveness for fixture {fixture.get('id')}: {str(e)}")
                continue
        
        competitive_matches.sort(key=lambda x: x["competitiveness_score"], reverse=True)
        
        return {
            "competitive_matches": competitive_matches[:5],
            "most_competitive": competitive_matches[0] if competitive_matches else None
        }

    def _calculate_competitiveness(self, home_odds: float, away_odds: float, draw_odds: float = None) -> float:
        odds_diff = abs(home_odds - away_odds)
        base_competitiveness = 1 / (1 + odds_diff)
        
        if draw_odds and draw_odds <= 3.5:
            draw_factor = 1.2
        else:
            draw_factor = 1.0
        
        avg_odds = (home_odds + away_odds) / 2
        if 1.8 <= avg_odds <= 2.5:
            balance_bonus = 0.2
        else:
            balance_bonus = 0
        
        return base_competitiveness * draw_factor + balance_bonus

    async def _process_favorite_comparison(self, entities: Dict, fixtures: List) -> Dict[str, Any]:
        logger.info("Processing favorite comparison query")
        team_odds = {}
        
        for team in entities["teams"]:
            team_fixtures = self.data_service.find_team_in_fixtures(team, fixtures)
            
            if team_fixtures:
                for fixture in team_fixtures[:1]:
                    try:
                        fixture_id = fixture.get("id")
                        if not fixture_id:
                            continue
                        
                        odds_data = await self.data_service.get_odds_for_fixture(fixture_id)
                        
                        if odds_data and odds_data.get("data"):
                            extracted_odds = self.data_service.extract_main_odds(odds_data["data"])
                            
                            home_team = fixture.get("homeCompetitorName", {}).get("en", "")
                            away_team = fixture.get("awayCompetitorName", {}).get("en", "")
                            
                            if team.lower() in home_team.lower():
                                for odd in extracted_odds:
                                    if odd.get("bet_type") == "home_win":
                                        team_odds[team] = {
                                            "odds": odd.get("odds"),
                                            "match": f"{home_team} vs {away_team}",
                                            "fixture": fixture,
                                            "all_odds": extracted_odds
                                        }
                                        break
                            elif team.lower() in away_team.lower():
                                for odd in extracted_odds:
                                    if odd.get("bet_type") == "away_win":
                                        team_odds[team] = {
                                            "odds": odd.get("odds"),
                                            "match": f"{home_team} vs {away_team}",
                                            "fixture": fixture,
                                            "all_odds": extracted_odds
                                        }
                                        break
                    
                    except Exception as e:
                        logger.error(f"Error getting odds for team {team}: {str(e)}")
                        continue
        
        favorite_team = None
        if len(team_odds) >= 2:
            favorite_team = min(team_odds.keys(), key=lambda t: team_odds[t]["odds"])
        
        return {
            "team_odds": team_odds,
            "favorite_team": favorite_team,
            "comparison_type": "favorite_teams"
        }

    async def _process_bet_simulation(self, entities: Dict, fixtures: List) -> Dict[str, Any]:
        logger.info("Processing bet simulation query")
        bet_amount = entities.get("amount", 0)
        simulation_options = []
        
        target_fixtures = fixtures[:6]
        
        for fixture in target_fixtures:
            try:
                fixture_id = fixture.get("id")
                if not fixture_id:
                    continue
                
                odds_data = await self.data_service.get_odds_for_fixture(fixture_id)
                
                if odds_data and odds_data.get("data"):
                    extracted_odds = self.data_service.extract_main_odds(odds_data["data"])
                    
                    if extracted_odds:
                        home_team = fixture.get("homeCompetitorName", {}).get("en", "")
                        away_team = fixture.get("awayCompetitorName", {}).get("en", "")
                        
                        for odd in extracted_odds:
                            bet_type = odd.get("bet_type")
                            odds_value = odd.get("odds")
                            
                            if bet_type in ["home_win", "away_win", "draw"] and odds_value:
                                potential_return = bet_amount * odds_value
                                profit = potential_return - bet_amount
                                
                                bet_description = ""
                                if bet_type == "home_win":
                                    bet_description = f"{home_team} to win"
                                elif bet_type == "away_win":
                                    bet_description = f"{away_team} to win"
                                else:
                                    bet_description = "Draw"
                                
                                simulation_options.append({
                                    "match": f"{home_team} vs {away_team}",
                                    "bet_option": bet_description,
                                    "odds": odds_value,
                                    "bet_amount": bet_amount,
                                    "potential_return": round(potential_return, 2),
                                    "profit": round(profit, 2),
                                    "fixture": fixture
                                })
            
            except Exception as e:
                logger.error(f"Error simulating bet for fixture {fixture.get('id')}: {str(e)}")
                continue
        
        simulation_options.sort(key=lambda x: x["profit"], reverse=True)
        
        return {
            "simulation_options": simulation_options[:10],
            "bet_amount": bet_amount
        }

    async def _process_standard_odds(self, fixtures: List) -> Dict[str, Any]:
        all_odds = []
        
        for fixture in fixtures[:5]:
            try:
                fixture_id = fixture.get("id")
                if not fixture_id:
                    continue
                
                odds_data = await self.data_service.get_odds_for_fixture(fixture_id)
                
                if odds_data and odds_data.get("data"):
                    extracted_odds = self.data_service.extract_main_odds(odds_data["data"])
                    all_odds.extend(extracted_odds)
            
            except Exception as e:
                logger.error(f"Error getting odds for fixture {fixture.get('id')}: {str(e)}")
                continue
        
        return {"odds": all_odds}