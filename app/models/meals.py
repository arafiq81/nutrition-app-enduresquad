from app import db
from datetime import datetime

class MealLog(db.Model):
    """Individual meal/snack entry."""
    __tablename__ = 'meal_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # When
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    
    # What (meal timing context)
    meal_type = db.Column(db.String(20), nullable=True)
    
    # Macros (in grams)
    carbs_g = db.Column(db.Float, nullable=False)
    protein_g = db.Column(db.Float, nullable=False)
    fat_g = db.Column(db.Float, nullable=False)
    
    # Optional: Hydration
    fluids_ml = db.Column(db.Integer, nullable=True)
    
    # Description
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Meal {self.date} {self.time}>'
    
    @property
    def calories(self):
        """Calculate total calories from macros"""
        return (self.carbs_g * 4) + (self.protein_g * 4) + (self.fat_g * 9)
