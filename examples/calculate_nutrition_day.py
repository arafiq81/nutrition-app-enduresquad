"""
Example: Calculate nutrition for a training day
=================================================
Demonstrates how to use NutritionCalculator directly without the web UI.
Useful for debugging calculations and building scripts.

Usage:
    cd nutrition-app
    source venv/bin/activate
    python examples/calculate_nutrition_day.py
"""

from app import create_app, db
from app.models import User, TrainingSession
from app.calculations import NutritionCalculator
from datetime import date

app = create_app()

with app.app_context():
    # ── Load a user ─────────────────────────────────────────────────────────
    user = User.query.first()
    if not user:
        print("No users found. Run init_db.py first.")
        exit(1)

    print(f"\nAthlete: {user.name}  |  {user.weight_kg}kg  |  Phase: {user.training_phase}")
    print("=" * 60)

    calc = NutritionCalculator(user)

    # ── Baseline ────────────────────────────────────────────────────────────
    rmr  = calc.calculate_rmr()
    neat = calc.calculate_neat(rmr)
    print(f"\nRMR   : {rmr:>6} kcal")
    print(f"NEAT  : {neat:>6} kcal")
    print(f"Baseline (RMR + NEAT): {rmr + neat} kcal")

    # ── Sample training sessions ─────────────────────────────────────────────
    training_scenarios = [
        # (label, sport, duration_min, zone_dist, power_watts)
        ("Morning swim — 3km intervals",  "swim",  55, {1: 10, 2: 20, 3: 0, 4: 70, 5: 0}, None),
        ("Afternoon bike — FTP intervals", "bike",  60, {1: 10, 2: 30, 3: 0, 4: 60, 5: 0}, 230),
        ("Evening run — easy Z2",          "run",   45, {1: 10, 2: 85, 3: 5, 4: 0, 5: 0}, None),
    ]

    total_training_kcal = 0
    total_training_load = 0.0
    training_data_for_hydration = []

    print("\n── Training Sessions ─────────────────────────────────────────────")
    for label, sport, duration, zones, power in training_scenarios:
        energy, load = calc.calculate_training_energy(
            sport=sport,
            duration_minutes=duration,
            zone_distribution=zones,
            average_power_watts=power
        )
        total_training_kcal += energy
        total_training_load += load
        print(f"  {label}")
        print(f"    Energy: {energy} kcal  |  Load: {load:.1f}")
        training_data_for_hydration.append({
            "sport": sport,
            "duration_minutes": duration,
            "zone_distribution": zones,
        })

    # ── TDEE ─────────────────────────────────────────────────────────────────
    tdee_pre_tef = rmr + neat + total_training_kcal
    tef  = calc.calculate_tef(tdee_pre_tef)
    tdee = tdee_pre_tef + tef

    print(f"\n── Energy Summary ────────────────────────────────────────────────")
    print(f"  Training kcal : {total_training_kcal}")
    print(f"  TEF           : {tef}")
    print(f"  TDEE          : {tdee} kcal")
    print(f"  Training Load : {total_training_load:.1f}")

    # ── Macros ───────────────────────────────────────────────────────────────
    macros = calc.calculate_daily_macros(total_training_load, tdee)
    print(f"\n── Macro Targets ─────────────────────────────────────────────────")
    print(f"  Carbs   : {macros['carbs_g']:.0f}g  ({macros['carbs_kcal']} kcal)")
    print(f"  Protein : {macros['protein_g']:.0f}g  ({macros['protein_kcal']} kcal)")
    print(f"  Fat     : {macros['fat_g']:.0f}g  ({macros['fat_kcal']} kcal)")

    # ── Hydration ────────────────────────────────────────────────────────────
    hydration = calc.calculate_hydration_needs(training_data_for_hydration)
    print(f"\n── Hydration ─────────────────────────────────────────────────────")
    print(f"  Total : {hydration['total_ml']} ml  ({hydration['total_ml']/1000:.1f} L)")
    for detail in hydration.get("breakdown", []):
        print(f"    {detail}")
