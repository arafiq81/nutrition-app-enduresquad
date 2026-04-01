from app import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class DailyNutrition(db.Model):
    """Daily nutrition summary - targets and actuals."""
    __tablename__ = 'daily_nutrition'
    __table_args__ = (UniqueConstraint('user_id', 'date', name='uq_daily_nutrition_user_date'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Calculated Targets
    rmr_kcal = db.Column(db.Integer, nullable=True)
    neat_kcal = db.Column(db.Integer, nullable=True)
    training_kcal = db.Column(db.Integer, nullable=True)
    tef_kcal = db.Column(db.Integer, nullable=True)
    total_tdee_kcal = db.Column(db.Integer, nullable=True)
    
    # Macro Targets (in grams)
    target_carbs_g = db.Column(db.Float, nullable=True)
    target_protein_g = db.Column(db.Float, nullable=True)
    target_fat_g = db.Column(db.Float, nullable=True)
    
    # Hydration Target
    target_fluids_ml = db.Column(db.Integer, nullable=True)
    
    # Training Load
    daily_training_load_score = db.Column(db.Float, nullable=True)
    
    # Actual Consumed
    consumed_carbs_g = db.Column(db.Float, default=0)
    consumed_protein_g = db.Column(db.Float, default=0)
    consumed_fat_g = db.Column(db.Float, default=0)
    consumed_fluids_ml = db.Column(db.Integer, default=0)
    
    # Status
    recalculated_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<DailyNutrition {self.date}>'
    
    @property
    def consumed_calories(self):
        """Total calories consumed today"""
        return (self.consumed_carbs_g * 4 + 
                self.consumed_protein_g * 4 + 
                self.consumed_fat_g * 9)
    
    @property
    def remaining_carbs(self):
        """Carbs remaining to hit target"""
        if self.target_carbs_g:
            return max(0, self.target_carbs_g - self.consumed_carbs_g)
        return None
    
    @property
    def remaining_protein(self):
        """Protein remaining to hit target"""
        if self.target_protein_g:
            return max(0, self.target_protein_g - self.consumed_protein_g)
        return None
    
    @property
    def remaining_fat(self):
        """Fat remaining to hit target"""
        if self.target_fat_g:
            return max(0, self.target_fat_g - self.consumed_fat_g)
        return None
    
    @property
    def carbs_percentage(self):
        """Percentage of carb target consumed"""
        if self.target_carbs_g and self.target_carbs_g > 0:
            return (self.consumed_carbs_g / self.target_carbs_g) * 100
        return 0
