import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.config import settings
from app.models.schemas import ChatMessage, ChatResponse, UserContext
from app.services.chatbet_client import ChatBetClient
from app.services.data_service import DataService
from app.ai.prompt_builder import PromptBuilder
from app.ai.analyzers import APIAnalyzer
import json
import logging
from datetime import datetime, timedelta
import re
import uuid

logger = logging.getLogger(__name__)


class ChatBotService:
    """
    Chatbot service with AI integration and sports data processing.
    
    Features:
    - Google AI integration for natural language processing
    - ChatBet API integration for sports data
    - Smart caching and data optimization
    - Conversational context management
    - Betting simulation and analysis
    """
    
    def __init__(self):
        genai.configure(api_key=settings.google_ai_api_key)
        self.model = genai.GenerativeModel(settings.google_ai_model)
        
        self.chatbet_client = ChatBetClient()
        self.data_service = DataService(self.chatbet_client)
        self.api_analyzer = APIAnalyzer(self.data_service, self._ensure_auth_token)
        
        self.user_contexts: Dict[str, UserContext] = {}
        
        self._auth_token: Optional[str] = None
    
    async def _ensure_auth_token(self):
        if not self._auth_token:
            try:
                token_response = await self.chatbet_client.generate_token()
                self._auth_token = token_response.get("token")
                self.chatbet_client.set_auth_token(self._auth_token)
                logger.info("Generated new authentication token")
            except Exception as e:
                logger.error(f"Error generating auth token: {e}")
    
    def _get_system_prompt(self) -> str:
        return PromptBuilder.get_system_prompt()
    
    async def _get_user_context(self, session_id: str) -> UserContext:
        if session_id not in self.user_contexts:
            self.user_contexts[session_id] = UserContext(session_id=session_id)
        return self.user_contexts[session_id]
    
    def _update_user_context(self, context: UserContext, message: str, response_data: Dict):
        context.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": response_data.get("response", ""),
            "intent": response_data.get("intent")
        })
        
        if len(context.conversation_history) > settings.max_conversation_history:
            context.conversation_history = context.conversation_history[-settings.max_conversation_history:]
        
        entities = response_data.get("entities", {})
        if "teams" in entities:
            context.mentioned_teams.extend(entities["teams"])
            context.mentioned_teams = list(set(context.mentioned_teams))
        
        context.last_intent = response_data.get("intent")
    
    def _build_context_prompt(self, context: UserContext, current_message: str) -> str:
        return PromptBuilder.build_context_prompt(context, current_message)
    
    async def _execute_api_actions(self, actions: List[str], entities: Dict, context: UserContext) -> Dict[str, Any]:
        return await self.api_analyzer.execute_api_actions(actions, entities, context)
    
    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """Process user message and generate response with real data"""
        try:
            context = await self._get_user_context(message.session_id or "default")
            context.user_key = message.user_key
            
            full_prompt = self._build_context_prompt(context, message.message)
            system_prompt = self._get_system_prompt()
            
            prompt = f"{system_prompt}\n\n{full_prompt}"
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            try:
                if "```json" in response_text:
                    json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
                    if json_match:
                        response_text = json_match.group(1)
                
                response_data = json.loads(response_text)
            except (json.JSONDecodeError, AttributeError):
                response_data = {
                    "intent": "general",
                    "entities": {},
                    "api_actions": [],
                    "response": response_text,
                    "needs_api_data": False,
                    "confidence": 0.8
                }
            
            if response_data.get("needs_api_data", False):
                logger.info(f"Need API data: {response_data.get('api_actions', [])}")
                entities = response_data.get("entities", {})
                entities["_original_message"] = message.message
                
                api_data = await self._execute_api_actions(
                    response_data.get("api_actions", []), 
                    entities,
                    context
                )
                logger.info(f"API data result: {api_data is not None}")
                if api_data:
                    logger.info(f"API data keys: {list(api_data.keys())}")
                
                if api_data and not api_data.get("error"):
                    if api_data.get("betting_recommendations"):
                        betting_recommendations = api_data.get("betting_recommendations", [])
                        if betting_recommendations:
                            top_recommendation = betting_recommendations[0]
                            recommendations_prompt = f"""
                            USER QUESTION: {message.message}
                            
                            BETTING RECOMMENDATIONS ANALYSIS:
                            BEST RECOMMENDATION:
                            - Match: {top_recommendation.get('match')}
                            - Bet type: {top_recommendation.get('recommendation_type')}
                            - Recommended option: {top_recommendation.get('option')}
                            - Recommended odds: {top_recommendation.get('odds')}
                            - Tournament: {top_recommendation.get('tournament')}
                            
                            OTHER OPTIONS:"""
                            
                            for rec in betting_recommendations[1:3]:
                                recommendations_prompt += f"""
                            - {rec.get('match')}: {rec.get('option')} (odds {rec.get('odds')}) - {rec.get('recommendation_type')}"""
                            
                            recommendations_prompt += f"""
                            
                            INSTRUCTIONS:
                            - Respond in English with a super friendly and enthusiastic tone, like an expert buddy
                            - Start with something like "Hey! I've got the perfect recommendation for you" or "Check out what I found!"
                            - Present the BEST bet with excitement: "This match is awesome!" or "What a game!"
                            - Explain the bet type in casual language: "safe bet", "value play", "interesting risk"
                            - Mention the specific odds with enthusiasm: "Wow, those odds look great!"
                            - Include 1-2 alternatives with phrases like "If you're feeling adventurous..." or "By the way, you also have..."
                            - ALWAYS mention these are SIMULATED bets but in a fun way: "We're simulating the play!" or "Playing with virtual money!"
                            - Give a responsible gambling reminder but keep the positive vibe
                            - Maximum 5-6 sentences, full of energy
                            - End with something like "What do you think?" or "Let me know your thoughts!"
                            
                            Respond ONLY with the final text, no JSON format.
                            """
                            enhanced_response = await self.model.generate_content_async(recommendations_prompt)
                            response_data["response"] = enhanced_response.text
                            response_data["data"] = api_data
                    elif api_data.get("simulation_options"):
                        simulation_options = api_data.get("simulation_options", [])
                        bet_amount = api_data.get("bet_amount", 0)
                        
                        if simulation_options:
                            simulation_prompt = f"""
                            USER QUESTION: {message.message}
                            
                            BET SIMULATION WITH ${bet_amount}:
                            """
                            
                            for option in simulation_options[:5]:
                                simulation_prompt += f"""
                            - {option.get('match')}: {option.get('bet_option')} (odds {option.get('odds')}) → Profit ${option.get('profit')} (Total ${option.get('potential_return')})"""
                            
                            simulation_prompt += f"""
                            
                            INSTRUCTIONS:
                            - Respond in English with tons of excitement, like a buddy who loves betting
                            - Start with something like "Hey! With ${bet_amount} you've got some awesome options" or "That's a great amount to play with!"
                            - Explain the available options with enthusiasm: "Check out these spectacular plays"
                            - Mention the potential profits with excitement: "You could win up to $X!" or "Wow, that profit looks amazing!"
                            - Highlight the best options: "My favorite is this one", "If it were me, I'd go for..."
                            - ALWAYS emphasize these are simulations in a fun way: "We're playing with Monopoly money!" or "Just for fun, but how exciting!"
                            - Include a responsible gambling reminder but keep the positive energy
                            - Maximum 6-8 sentences, full of energy
                            - End by asking their opinion: "Which one catches your eye?" or "Which would you go for?"
                            
                            Respond ONLY with the final text, no JSON format.
                            """
                            enhanced_response = await self.model.generate_content_async(simulation_prompt)
                            response_data["response"] = enhanced_response.text
                            response_data["data"] = api_data
                    elif api_data.get("competitive_matches"):
                        competitive_matches = api_data.get("competitive_matches", [])
                        if competitive_matches:
                            most_competitive = competitive_matches[0]
                            competitive_prompt = f"""
                            USER QUESTION: {message.message}
                            
                            MOST COMPETITIVE MATCHES ANALYSIS:
                            MOST COMPETITIVE MATCH:
                            - Match: {most_competitive.get('fixture', {}).get('homeCompetitorName', {}).get('en', '')} vs {most_competitive.get('fixture', {}).get('awayCompetitorName', {}).get('en', '')}
                            - Home odds: {most_competitive.get('home_win_odds')}
                            - Away odds: {most_competitive.get('away_win_odds')}
                            - Draw odds: {most_competitive.get('draw_odds')}
                            - Competitiveness score: {most_competitive.get('competitiveness_score', 0):.3f}
                            
                            OTHER COMPETITIVE MATCHES:"""
                            
                            for match in competitive_matches[1:3]:
                                home_team = match.get('fixture', {}).get('homeCompetitorName', {}).get('en', '')
                                away_team = match.get('fixture', {}).get('awayCompetitorName', {}).get('en', '')
                                competitive_prompt += f"""
                            - {home_team} vs {away_team} (score: {match.get('competitiveness_score', 0):.3f})"""
                            
                            competitive_prompt += f"""
                            
                            INSTRUCTIONS:
                            - Respond in English with tons of excitement, like a passionate sports fan
                            - Start with something like "Wow! I've got the most balanced match for you" or "Wait till you see this, it's going to be epic!"
                            - Highlight the MOST COMPETITIVE match with enthusiasm: "This game is going to be a nail-biter!"
                            - Mention the teams and main odds with excitement: "The odds are super close!"
                            - Explain why it's competitive in an exciting way: "It's so evenly matched that anything could happen!"
                            - Briefly mention 1-2 other competitive matches: "And if that's not enough, check out these too..."
                            - Use sporty language: "thriller", "super close", "edge-of-your-seat", "intense"
                            - Maximum 4-5 sentences, packed with energy
                            - End with anticipation: "Get ready for a show!" or "This is going to be epic!"
                            
                            Respond ONLY with the final text, no JSON format.
                            """
                            enhanced_response = await self.model.generate_content_async(competitive_prompt)
                            response_data["response"] = enhanced_response.text
                            response_data["data"] = api_data
                    elif api_data.get("team_odds") and api_data.get("comparison_type") == "favorite_teams":
                        team_odds = api_data.get("team_odds", {})
                        favorite_team = api_data.get("favorite_team")
                        
                        comparison_prompt = f"""
                        USER QUESTION: {message.message}
                        
                        TEAMS COMPARISON BASED ON ODDS:
                        """
                        for team, data in team_odds.items():
                            comparison_prompt += f"""
                        - {team}: odds {data.get('odds')} (in {data.get('match')})"""
                        
                        if favorite_team:
                            comparison_prompt += f"""
                        
                        FAVORITE IDENTIFIED: {favorite_team} with odds {team_odds[favorite_team].get('odds')}
                        """
                        
                        comparison_prompt += f"""
                        
                        INSTRUCTIONS:
                        - Respond in English with a super friendly and enthusiastic tone, like an expert buddy
                        - Start with excitement: "Hey! I checked the odds and here's what I found" or "Wow, this is interesting!"
                        - DIRECTLY identify which team has the LOWEST odds (the favorite)
                        - Mention the specific odds with excitement: "Check out these odds!"
                        - Explain simply that lower odds = higher probability
                        - Use energetic language: "clear favorite", "the bookmakers are sure", "no doubt about it"
                        - Add emotional context: "It's super obvious!" or "The odds don't lie!"
                        - Maximum 2-3 sentences, full of energy
                        - DO NOT mention date details
                        - End with confidence: "There's your answer!" or "Crystal clear!"
                        
                        Respond ONLY with the final text, no JSON format.
                        """
                        enhanced_response = await self.model.generate_content_async(comparison_prompt)
                        response_data["response"] = enhanced_response.text
                        response_data["data"] = api_data
                    else:
                        enhanced_prompt = f"""
                        REAL DATA OBTAINED FROM CHATBET API:
                        {json.dumps(api_data, indent=2, ensure_ascii=False)}
                        
                        USER'S ORIGINAL MESSAGE: {message.message}
                        
                        INSTRUCTIONS:
                        - Hey! Use ONLY the real data provided above 
                        - Respond in a super natural and friendly way in English, like a buddy who's passionate about betting
                        - If it's about matches, mention specific teams, dates, and tournaments with excitement 
                        - If it's about odds, mention the exact values with enthusiasm 
                        - If it's about balance, mention the exact available amount with energy 
                        - For bet simulations, calculate potential winnings and get excited 
                        - ALWAYS clarify that the bets are SIMULATED but do it in a fun, positive way 
                        - Use expressions like: "Hey!", "Check this out!", "Awesome!", "That's fire!", "So cool!", "This is wild!"
                        
                        
                        Respond ONLY with the final friendly text, no JSON format.
                        """
                        
                        enhanced_response = await self.model.generate_content_async(enhanced_prompt)
                        response_data["response"] = enhanced_response.text
                        response_data["data"] = api_data
                else:
                    response_data["response"] = "Sorry, I couldn't get the requested information at this moment. Can you try with another query?"

            self._update_user_context(context, message.message, response_data)
            
            return ChatResponse(
                response=response_data.get("response", "Oops! I couldn't process your message. Want to try again? I'm here to help!"),
                intent=response_data.get("intent"),
                confidence=response_data.get("confidence", 0.8),
                data=response_data.get("data")
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                response="Hey there! There was a little error processing your message. But don't worry, try again and it should work!",
                intent="error",
                confidence=0.0
            )