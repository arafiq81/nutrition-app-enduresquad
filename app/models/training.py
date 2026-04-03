from app import db
from datetime import datetime

class TrainingSession(db.Model):
    """Individual training session - planned and actual workout data."""
    __tablename__ = 'training_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('nutrition_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Session Info
    date = db.Column(db.Date, nullable=False)
    sport = db.Column(db.String(20), nullable=False)  # 'swim', 'bike', 'run'
    session_type = db.Column(db.String(20), default='planned')  # 'planned' or 'actual'
    
    # Timing
    start_time = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False)
    
    # Zone Distribution (percentage of time in each zone)
    zone1_percent = db.Column(db.Float, default=0)
    zone2_percent = db.Column(db.Float, default=0)
    zone3_percent = db.Column(db.Float, default=0)
    zone4_percent = db.Column(db.Float, default=0)
    zone5_percent = db.Column(db.Float, default=0)
    
    # Optional: Power/Pace Data
    average_power_watts = db.Column(db.Integer, nullable=True)
    average_pace = db.Column(db.String(10), nullable=True)
    distance_km = db.Column(db.Float, nullable=True)
    
    # Calculated Fields
    energy_expenditure_kcal = db.Column(db.Integer, nullable=True)
    training_load_score = db.Column(db.Float, nullable=True)
    
    # External Integration
    strava_id = db.Column(db.String(50), nullable=True)
    
    # Notes
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Training {self.sport} - {self.date} ({self.session_type})>'
    
    @property
    def total_zone_percent(self):
        """Validate zone distribution adds up to ~100%"""
        return (self.zone1_percent + self.zone2_percent + 
                self.zone3_percent + self.zone4_percent + self.zone5_percent)
    
    def calculate_training_load_score(self):
        """Calculate training load score based on duration and intensity."""
        zone_factors = {1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0, 5: 2.5}
        
        score = 0
        score += (self.duration_minutes * self.zone1_percent / 100) * zone_factors[1]
        score += (self.duration_minutes * self.zone2_percent / 100) * zone_factors[2]
        score += (self.duration_minutes * self.zone3_percent / 100) * zone_factors[3]
        score += (self.duration_minutes * self.zone4_percent / 100) * zone_factors[4]
        score += (self.duration_minutes * self.zone5_percent / 100) * zone_factors[5]
        
        self.training_load_score = score
        return score
