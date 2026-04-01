from app import db
from datetime import datetime

class ChatMessage(db.Model):
    """
    Track chat messages for rate limiting and history
    """
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Message content
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    
    # Metadata
    tokens_used = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ChatMessage user_id={self.user_id} at {self.created_at}>'
