"""
Unit tests for NutritionCalculator.
"""
import pytest
from app.calculations import NutritionCalculator


# ── RMR ────────────────────────────────────────────────────────────────────────

class TestRMR:
    def test_mifflin_male(self, athlete):
        athlete.body_fat_percentage = None
        calc = NutritionCalculator(athlete)
        rmr = calc.calculate_rmr()
        # (10 × 78) + (6.25 × 180) - (5 × 35) + 5 = 780 + 1125 - 175 + 5 = 1735
        assert rmr == 1735

    def test_mifflin_female(self, athlete):
        athlete.body_fat_percentage = None
        athlete.sex = "female"
        calc = NutritionCalculator(athlete)
        rmr = calc.calculate_rmr()
        # (10 × 78) + (6.25 × 180) - (5 × 35) - 161 = 1569
        assert rmr == 1569

    def test_cunningham_used_when_body_fat_present(self, athlete):
        athlete.body_fat_percentage = 12.0  # lbm = 78 × 0.88 = 68.64 kg
        calc = NutritionCalculator(athlete)
        rmr = calc.calculate_rmr()
        # 500 + (22 × 68.64) = 500 + 1510 = 2010
        assert rmr == pytest.approx(2010, abs=5)

    def test_rmr_positive(self, athlete):
        calc = NutritionCalculator(athlete)
        assert calc.calculate_rmr() > 0


# ── NEAT ───────────────────────────────────────────────────────────────────────

class TestNEAT:
    def test_sedentary(self, athlete):
        athlete.activity_level = "sedentary"
        calc = NutritionCalculator(athlete)
        rmr = calc.calculate_rmr()
        neat = calc.calculate_neat(rmr)
        assert neat == int(rmr * 0.15)

    def test_moderate(self, athlete):
        athlete.activity_level = "moderate"
        calc = NutritionCalculator(athlete)
        rmr = calc.calculate_rmr()
        neat = calc.calculate_neat(rmr)
        assert neat == int(rmr * 0.25)

    def test_unknown_level_falls_back_to_moderate(self, athlete):
        athlete.activity_level = "extreme_commuter"
        calc = NutritionCalculator(athlete)
        rmr = calc.calculate_rmr()
        neat_unknown = calc.calculate_neat(rmr)
        athlete.activity_level = "moderate"
        neat_moderate = calc.calculate_neat(rmr)
        assert neat_unknown == neat_moderate


# ── Training Energy ─────────────────────────────────────────────────────────────

class TestTrainingEnergy:
    def test_run_zone2_returns_positive(self, athlete):
        calc = NutritionCalculator(athlete)
        energy, load = calc.calculate_training_energy(
            sport="run",
            duration_minutes=60,
            zone_distribution={2: 100},
        )
        assert energy > 0
        assert load > 0

    def test_power_based_bike(self, athlete):
        calc = NutritionCalculator(athlete)
        energy, load = calc.calculate_training_energy(
            sport="bike",
            duration_minutes=60,
            zone_distribution={3: 100},
            average_power_watts=200,
        )
        # 200W × 1h × 3.6 / 4.18 ≈ 172 kcal (mechanical) — gross including efficiency
        assert energy > 100

    def test_swim_higher_energy_than_strength(self, athlete):
        calc = NutritionCalculator(athlete)
        swim_energy, _ = calc.calculate_training_energy(
            sport="swim", duration_minutes=60, zone_distribution={3: 100}
        )
        strength_energy, _ = calc.calculate_training_energy(
            sport="strength_mobility", duration_minutes=60, zone_distribution={3: 100}
        )
        assert swim_energy > strength_energy

    def test_empty_zone_distribution(self, athlete):
        calc = NutritionCalculator(athlete)
        energy, load = calc.calculate_training_energy(
            sport="run",
            duration_minutes=30,
            zone_distribution={},
        )
        assert energy >= 0


# ── TEF ────────────────────────────────────────────────────────────────────────

class TestTEF:
    def test_tef_is_10_percent(self, athlete):
        calc = NutritionCalculator(athlete)
        tef = calc.calculate_tef(2000)
        assert tef == pytest.approx(200, abs=5)


# ── Macros ─────────────────────────────────────────────────────────────────────

class TestMacros:
    def test_high_load_gives_more_carbs(self, athlete):
        calc = NutritionCalculator(athlete)
        low_load_macros  = calc.calculate_daily_macros(training_load_score=20,  total_tdee=2500)
        high_load_macros = calc.calculate_daily_macros(training_load_score=200, total_tdee=3500)
        assert high_load_macros["carbs_g"] > low_load_macros["carbs_g"]

    def test_macros_returned_keys(self, athlete):
        calc = NutritionCalculator(athlete)
        macros = calc.calculate_daily_macros(100, 2800)
        for key in ("carbs_g", "protein_g", "fat_g"):
            assert key in macros

    def test_protein_scales_with_weight(self, athlete):
        calc = NutritionCalculator(athlete)
        macros = calc.calculate_daily_macros(100, 2800)
        # Protein should be roughly 1.6–2.2 g/kg
        per_kg = macros["protein_g"] / athlete.weight_kg
        assert 1.4 <= per_kg <= 2.5
