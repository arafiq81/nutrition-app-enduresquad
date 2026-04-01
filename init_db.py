"""Initialize database and create your user profile"""

import os
from pathlib import Path
from app import create_app, db
from app.models import User
from datetime import datetime

def init_database():
    """Create all tables and add initial user"""
    
    # Ensure data directory exists and is writable
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Set proper permissions
    os.chmod(data_dir, 0o755)
    
    print(f"Database directory: {data_dir}")
    print(f"Directory exists: {data_dir.exists()}")
    print(f"Directory writable: {os.access(data_dir, os.W_OK)}")
    
    app = create_app()
    
    with app.app_context():
        # Print the actual database path being used
        print(f"\nDatabase URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Drop all tables (fresh start)
        print("\nDropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create YOUR user profile
        print("\n=== Creating Your Athlete Profile ===\n")
        
        name = input("Name: ")
        email = input("Email: ")
        age = int(input("Age: "))
        sex = input("Sex (male/female): ").lower()
        weight = float(input("Weight (kg): "))
        height = float(input("Height (cm): "))
        
        body_fat = input("Body fat % (press Enter to skip): ")
        body_fat = float(body_fat) if body_fat else None
        
        print("\nActivity level: sedentary, light, moderate, very_active")
        activity = input("Activity level (default: moderate): ") or "moderate"
        
        print("\nTraining phase: base, build, peak, race, recovery")
        phase = input("Training phase (default: build): ") or "build"
        
        print("\nHeart rate zones (press Enter to skip any):")
        hr_max = input("HR Max: ")
        hr_max = int(hr_max) if hr_max else None
        
        hr_z1 = input("Zone 1 max (e.g., 142): ")
        hr_z1 = int(hr_z1) if hr_z1 else None
        
        hr_z2 = input("Zone 2 max (e.g., 155): ")
        hr_z2 = int(hr_z2) if hr_z2 else None
        
        hr_z3 = input("Zone 3 max (e.g., 165): ")
        hr_z3 = int(hr_z3) if hr_z3 else None
        
        hr_z4 = input("Zone 4 max (e.g., 175): ")
        hr_z4 = int(hr_z4) if hr_z4 else None
        
        # Create user
        user = User(
            name=name,
            email=email,
            age=age,
            sex=sex,
            weight_kg=weight,
            height_cm=height,
            body_fat_percentage=body_fat,
            activity_level=activity,
            training_phase=phase,
            hr_max=hr_max,
            hr_zone1_max=hr_z1,
            hr_zone2_max=hr_z2,
            hr_zone3_max=hr_z3,
            hr_zone4_max=hr_z4
        )
        
        db.session.add(user)
        db.session.commit()
        
        db_file = data_dir / 'nutrition.db'
        print(f"\n{'='*50}")
        print(f"✓ Database initialized successfully!")
        print(f"✓ User created: {user.name} (ID: {user.id})")
        print(f"✓ Database location: {db_file}")
        print(f"✓ Database file exists: {db_file.exists()}")
        print(f"\nYou can now run: python run.py")
        print(f"{'='*50}\n")

if __name__ == '__main__':
    init_database()
