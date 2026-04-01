"""
AI Chat Bot for Nutrition Coaching
Uses Anthropic Claude API with 3-message daily limit
"""

from anthropic import Anthropic
import os
from datetime import date, datetime, timedelta
from app import db
from app.models import ChatMessage

class NutritionChatBot:
    """AI-powered nutrition coach using Claude"""
    
    DAILY_MESSAGE_LIMIT = 3
    
    def __init__(self, user, daily_nutrition=None, todays_sessions=None):
        """
        Initialize chat bot with user context
        
        Args:
            user: User model instance
            daily_nutrition: DailyNutrition instance for today (optional)
            todays_sessions: List of today's training sessions (optional)
        """
        self.user = user
        self.daily_nutrition = daily_nutrition
        self.todays_sessions = todays_sessions or []
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def check_rate_limit(self):
        """
        Check if user has exceeded daily message limit.
        
        Returns:
            Tuple of (can_send, messages_remaining)
        """
        today_start = datetime.combine(date.today(), datetime.min.time())
        
        # Count messages sent today
        messages_today = ChatMessage.query.filter(
            ChatMessage.user_id == self.user.id,
            ChatMessage.created_at >= today_start
        ).count()
        
        messages_remaining = max(0, self.DAILY_MESSAGE_LIMIT - messages_today)
        can_send = messages_remaining > 0
        
        return can_send, messages_remaining
    
    def get_system_prompt(self):
        """Build context-aware system prompt with athlete's data"""
        
        prompt = f"""You are an expert Ironman triathlon nutrition coach. You provide personalized, actionable nutrition advice.

ATHLETE PROFILE:
- Name: {self.user.name}
- Age: {self.user.age}, Sex: {self.user.sex}
- Weight: {self.user.weight_kg}kg, Height: {self.user.height_cm}cm"""
        
        if self.user.body_fat_percentage:
            prompt += f"\n- Body Fat: {self.user.body_fat_percentage}%"
            prompt += f"\n- Lean Mass: {self.user.lean_body_mass_kg:.1f}kg"
        
        prompt += f"\n- Training Phase: {self.user.training_phase}"
        prompt += f"\n- Activity Level: {self.user.activity_level}"
        
        # Add today's training if available
        if self.todays_sessions:
            prompt += "\n\nTODAY'S TRAINING:"
            for session in self.todays_sessions:
                prompt += f"\n- {session.sport.title()}: {session.duration_minutes} min, {session.energy_expenditure_kcal} kcal, Load: {session.training_load_score:.0f}"
        
        # Add today's nutrition targets if available
        if self.daily_nutrition:
            prompt += f"\n\nTODAY'S NUTRITION TARGETS:"
            prompt += f"\n- Total Energy: {self.daily_nutrition.total_tdee_kcal} kcal"
            prompt += f"\n- Carbs: {self.daily_nutrition.target_carbs_g:.0f}g"
            prompt += f"\n- Protein: {self.daily_nutrition.target_protein_g:.0f}g"
            prompt += f"\n- Fat: {self.daily_nutrition.target_fat_g:.0f}g"
            prompt += f"\n- Hydration: {self.daily_nutrition.target_fluids_ml/1000:.1f}L"
            prompt += f"\n- Training Load: {self.daily_nutrition.daily_training_load_score:.0f}"
        
        prompt += """\n\nYour role:
- Provide specific, actionable nutrition advice
- Reference the athlete's actual data in your responses
- Keep responses concise (2-3 paragraphs max)
- Focus on practical meal/snack suggestions
- Consider training timing and demands
- Be encouraging and supportive"""
        
        return prompt
    
    def send_message(self, user_message):
        """
        Send message to Claude and get response.
        
        Args:
            user_message: User's question/message
            
        Returns:
            Tuple of (success, response_text, error_message)
        """
        # Check rate limit
        can_send, remaining = self.check_rate_limit()
        
        if not can_send:
            return False, None, "You've reached your daily limit of 3 messages. Limit resets at midnight."
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=self.get_system_prompt(),
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            bot_response = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Save to database
            chat_msg = ChatMessage(
                user_id=self.user.id,
                user_message=user_message,
                bot_response=bot_response,
                tokens_used=tokens_used
            )
            db.session.add(chat_msg)
            db.session.commit()
            
            return True, bot_response, None
            
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def get_recent_messages(self, limit=5):
        """
        Get recent chat history for this user.
        
        Args:
            limit: Number of messages to retrieve
            
        Returns:
            List of ChatMessage objects
        """
        return ChatMessage.query.filter_by(
            user_id=self.user.id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(limit).all()
