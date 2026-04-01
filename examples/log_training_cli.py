"""
Example: Log a training session from the command line
=====================================================
Demonstrates how to programmatically add a TrainingSession record
and trigger nutrition recalculation.

Usage:
    cd nutrition-app
    source venv/bin/activate
    python examples/log_training_cli.py
"""

from app import create_app, db
from app.models import User, TrainingSession, DailyNutrition
from app.calculations import NutritionCalculator
from datetime import date, datetime

app = create_app()

SESSION = {
    "date": date.today(),
    "sport": "bike",
    "session_type": "actual",
    "duration_minutes": 90,
    "zone1_percent": 0,
    "zone2_percent": 60,
    "zone3_percent": 20,
    "zone4_percent": 20,
    "zone5_percent": 0,
    "average_power_watts": 210,
    "description": "Long endurance ride — Z2 base with 2×15min tempo",
}

with app.app_context():
    user = User.query.first()
    if not user:
        print("No users found. Run init_db.py first.")
        exit(1)

    calc = NutritionCalculator(user)
    zone_dist = {
        1: SESSION["zone1_percent"],
        2: SESSION["zone2_percent"],
        3: SESSION["zone3_percent"],
        4: SESSION["zone4_percent"],
        5: SESSION["zone5_percent"],
    }

    energy, load = calc.calculate_training_energy(
        sport=SESSION["sport"],
        duration_minutes=SESSION["duration_minutes"],
        zone_distribution=zone_dist,
        average_power_watts=SESSION.get("average_power_watts"),
    )

    session = TrainingSession(
        user_id=user.id,
        date=SESSION["date"],
        sport=SESSION["sport"],
        session_type=SESSION["session_type"],
        duration_minutes=SESSION["duration_minutes"],
        zone1_percent=SESSION["zone1_percent"],
        zone2_percent=SESSION["zone2_percent"],
        zone3_percent=SESSION["zone3_percent"],
        zone4_percent=SESSION["zone4_percent"],
        zone5_percent=SESSION["zone5_percent"],
        average_power_watts=SESSION.get("average_power_watts"),
        energy_expenditure_kcal=energy,
        training_load_score=load,
        description=SESSION.get("description", ""),
    )
    db.session.add(session)
    db.session.commit()

    print(f"✓ Session logged: {SESSION['sport']} {SESSION['duration_minutes']} min")
    print(f"  Energy: {energy} kcal  |  Load: {load:.1f}")

    # Recalculate daily nutrition
    calc_date = SESSION["date"]
    all_sessions = TrainingSession.query.filter_by(user_id=user.id, date=calc_date).all()

    rmr  = calc.calculate_rmr()
    neat = calc.calculate_neat(rmr)
    total_energy = sum(s.energy_expenditure_kcal or 0 for s in all_sessions)
    total_load   = sum(s.training_load_score or 0 for s in all_sessions)
    tef  = calc.calculate_tef(rmr + neat + total_energy)
    tdee = rmr + neat + total_energy + tef
    macros = calc.calculate_daily_macros(total_load, tdee)

    daily = DailyNutrition.query.filter_by(user_id=user.id, date=calc_date).first()
    if not daily:
        daily = DailyNutrition(user_id=user.id, date=calc_date, recalculated_count=0)
        db.session.add(daily)

    daily.rmr_kcal = rmr
    daily.neat_kcal = neat
    daily.training_kcal = total_energy
    daily.tef_kcal = tef
    daily.total_tdee_kcal = tdee
    daily.target_carbs_g = macros["carbs_g"]
    daily.target_protein_g = macros["protein_g"]
    daily.target_fat_g = macros["fat_g"]
    daily.daily_training_load_score = total_load
    daily.recalculated_count = (daily.recalculated_count or 0) + 1
    db.session.commit()

    print(f"\n✓ Nutrition targets updated for {calc_date}")
    print(f"  TDEE   : {tdee} kcal")
    print(f"  Carbs  : {macros['carbs_g']:.0f}g")
    print(f"  Protein: {macros['protein_g']:.0f}g")
    print(f"  Fat    : {macros['fat_g']:.0f}g")
