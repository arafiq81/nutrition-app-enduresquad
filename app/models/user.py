from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """
    User profile - stores athlete's basic information and preferences.
    Now includes authentication fields.
    """
    # Separate table from the training app's 'users' table (same Supabase DB).
    # Linked to the training app user via training_user_id (UUID).
    __tablename__ = 'nutrition_users'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link to training app's users.id (UUID) — used to query completed_sets
    # for daily training load → calorie calculations.
    training_user_id = db.Column(db.String(36), nullable=True, index=True)

    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Physical Metrics (for RMR calculation)
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.String(10), nullable=True)  # 'male' or 'female'
    weight_kg = db.Column(db.Float, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    body_fat_percentage = db.Column(db.Float, nullable=True)  # Optional
    
    # Activity Level (for NEAT calculation)
    activity_level = db.Column(db.String(20), default='moderate')
    
    # Training Phase (affects carb recommendations)
    training_phase = db.Column(db.String(20), default='base')
    
    # Heart Rate Zones (for training calculations)
    hr_max = db.Column(db.Integer, nullable=True)
    hr_zone1_max = db.Column(db.Integer, nullable=True)
    hr_zone2_max = db.Column(db.Integer, nullable=True)
    hr_zone3_max = db.Column(db.Integer, nullable=True)
    hr_zone4_max = db.Column(db.Integer, nullable=True)
    
    # Power/Pace Thresholds
    ftp_watts = db.Column(db.Integer, nullable=True)
    run_threshold_pace = db.Column(db.String(10), nullable=True)
    swim_css_pace = db.Column(db.String(10), nullable=True)
    
    # Profile completion status
    profile_complete = db.Column(db.Boolean, default=False)
    # Admin approval (NEW)
    approved = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)  # admin user_id    
   
    # Relationships
    training_sessions = db.relationship('TrainingSession', backref='athlete', lazy=True, cascade='all, delete-orphan')
    meal_logs = db.relationship('MealLog', backref='athlete', lazy=True, cascade='all, delete-orphan')
    daily_nutrition = db.relationship('DailyNutrition', backref='athlete', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def lean_body_mass_kg(self):
        """Calculate lean body mass if body fat % is available"""
        if self.body_fat_percentage:
            return self.weight_kg * (1 - self.body_fat_percentage / 100)
        return None

    @property
    def is_admin(self):
        """True for the first registered user (id=1).
        Replace with a dedicated is_admin column when multiple admins are needed."""
        return self.id == 1
