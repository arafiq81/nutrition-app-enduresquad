"""
Nutrition Calculation Engine for Ironman Athletes

This module contains all the core calculations for:
- Resting Metabolic Rate (RMR)
- Non-Exercise Activity Thermogenesis (NEAT)
- Training Energy Expenditure
- Thermic Effect of Food (TEF)
- Macro Distribution
- Hydration Requirements
"""

from typing import Dict, Optional, Tuple
from datetime import date


class NutritionCalculator:
    """
    Main calculator class for athlete nutrition needs.
    
    Based on research from:
    - Mifflin-St Jeor equation (RMR)
    - Cunningham equation (RMR with body fat)
    - Zone-based energy expenditure (Jeukendrup, Burke)
    - Dynamic carbohydrate periodization (Thomas, Burke, Stellingwerff)
    """
    
    # Activity multipliers for NEAT calculation
    ACTIVITY_MULTIPLIERS = {
        'sedentary': 0.15,      # Desk job, minimal movement
        'light': 0.20,          # Some walking, light activity
        'moderate': 0.25,       # Active job, regular movement
        'very_active': 0.30     # Physical job, constantly moving
    }
    
    # Zone-specific energy costs (kcal/min) for 70kg athlete
    # These are adjusted by athlete weight
    ZONE_ENERGY_RATES = {
        'swim': {
            1: 7.0,   # Z1 - Easy swimming
            2: 9.0,   # Z2 - Aerobic
            3: 11.0,  # Z3 - Tempo
            4: 13.0,  # Z4 - Threshold
            5: 16.0   # Z5 - VO2max
        },
        'bike': {
            1: 8.0,   # Z1 - Recovery
            2: 10.0,  # Z2 - Endurance
            3: 12.0,  # Z3 - Tempo
            4: 14.0,  # Z4 - Threshold
            5: 17.0   # Z5 - VO2max
        },
        'run': {
            1: 10.0,  # Z1 - Easy
            2: 12.0,  # Z2 - Aerobic
            3: 14.0,  # Z3 - Tempo
            4: 16.0,  # Z4 - Threshold
            5: 19.0   # Z5 - VO2max
        },
        'strength_core': {
            1: 4.0,   # Light core work
            2: 4.5,   # Moderate intensity
            3: 5.0,   # High intensity
            4: 5.5,   # Very intense
            5: 6.0    # Maximum effort
        },
        'strength_functional': {
            1: 5.0,   # Light functional
            2: 6.0,   # Moderate
            3: 7.0,   # High
            4: 7.5,   # Very high
            5: 8.0    # Maximum
        },
        'strength_power': {
            1: 6.0,   # Light plyometrics
            2: 7.0,   # Moderate
            3: 8.0,   # High
            4: 9.0,   # Very high
            5: 10.0   # Maximum effort
        },
        'strength_mobility': {
            1: 2.0,   # Gentle stretching
            2: 2.5,   # Active recovery
            3: 3.0,   # Intensive yoga
            4: 3.5,   # Power yoga
            5: 4.0    # Very intense
        },
        'strength_heavy': {
            1: 5.0,   # Light weights
            2: 6.0,   # Moderate
            3: 7.0,   # Heavy
            4: 8.0,   # Very heavy
            5: 9.0    # Maximum effort
        }
    }
    
    def __init__(self, user):
        """
        Initialize calculator with user profile.
        
        Args:
            user: User model instance with athlete data
        """
        self.user = user
    
    def calculate_rmr(self) -> int:
        """
        Calculate Resting Metabolic Rate.
        
        Uses Cunningham equation if body fat % is available (more accurate),
        otherwise uses Mifflin-St Jeor equation.
        
        Returns:
            RMR in kcal/day
        """
        if self.user.body_fat_percentage and self.user.lean_body_mass_kg:
            # Cunningham equation (uses lean body mass)
            # RMR = 500 + (22 × LBM in kg)
            rmr = 500 + (22 * self.user.lean_body_mass_kg)
        else:
            # Mifflin-St Jeor equation
            # Male: RMR = (10 × weight) + (6.25 × height) - (5 × age) + 5
            # Female: RMR = (10 × weight) + (6.25 × height) - (5 × age) - 161
            
            rmr = (10 * self.user.weight_kg) + (6.25 * self.user.height_cm) - (5 * self.user.age)
            
            if self.user.sex == 'male':
                rmr += 5
            else:
                rmr -= 161
        
        return int(rmr)
    
    def calculate_neat(self, rmr: int) -> int:
        """
        Calculate Non-Exercise Activity Thermogenesis.
        
        Based on daily activity level (desk job vs. active job).
        
        Args:
            rmr: Resting metabolic rate
            
        Returns:
            NEAT in kcal/day
        """
        multiplier = self.ACTIVITY_MULTIPLIERS.get(
            self.user.activity_level, 
            self.ACTIVITY_MULTIPLIERS['moderate']
        )
        
        neat = rmr * multiplier
        return int(neat)
    
    def calculate_training_energy(
        self, 
        sport: str, 
        duration_minutes: int,
        zone_distribution: Dict[int, float],
        average_power_watts: Optional[int] = None
    ) -> Tuple[int, float]:
        """
        Calculate energy expenditure for a training session.
        
        Args:
            sport: 'swim', 'bike', 'run', or strength variants
            duration_minutes: Session duration
            zone_distribution: Dict mapping zone (1-5) to percentage (0-100)
            average_power_watts: Optional power data for cycling
            
        Returns:
            Tuple of (energy_kcal, training_load_score)
        """
        
        # If we have power data for cycling, use it (more accurate)
        if sport == 'bike' and average_power_watts:
            return self._calculate_power_based_energy(
                average_power_watts, 
                duration_minutes
            )
        
        # Otherwise use HR zone-based estimation
        return self._calculate_zone_based_energy(
            sport, 
            duration_minutes, 
            zone_distribution
        )
    
    def _calculate_power_based_energy(
        self, 
        average_watts: int, 
        duration_minutes: int
    ) -> Tuple[int, float]:
        """
        Calculate cycling energy from power data.
        
        Formula:
        Energy (kJ) = Power (W) × Time (hours) × 3.6
        Energy (kcal) = kJ (approximately)
        """
        duration_hours = duration_minutes / 60
        
        # Energy in kilojoules
        energy_kj = average_watts * duration_hours * 3.6
        
        # Convert to kcal (for cycling, kJ ≈ kcal due to efficiency)
        energy_kcal = energy_kj
        
        # Estimate training load score from power
        if self.user.ftp_watts and self.user.ftp_watts > 0:
            intensity_factor = average_watts / self.user.ftp_watts
            training_load_score = duration_minutes * intensity_factor * 1.5
        else:
            training_load_score = duration_minutes * 1.5
        
        return int(energy_kcal), training_load_score
    
    def _calculate_zone_based_energy(
        self,
        sport: str,
        duration_minutes: int,
        zone_distribution: Dict[int, float]
    ) -> Tuple[int, float]:
        """
        Calculate energy expenditure based on HR zones.
        
        Args:
            sport: Sport type
            duration_minutes: Total duration
            zone_distribution: Percentage of time in each zone
            
        Returns:
            Tuple of (energy_kcal, training_load_score)
        """
        if sport not in self.ZONE_ENERGY_RATES:
            raise ValueError(f"Unknown sport: {sport}")
        
        zone_rates = self.ZONE_ENERGY_RATES[sport]
        
        # Adjust rates for athlete's weight (base rates are for 70kg)
        weight_factor = self.user.weight_kg / 70.0
        
        total_energy = 0
        training_load = 0
        
        # Training load zone factors (how demanding each zone is)
        zone_load_factors = {1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0, 5: 2.5}
        
        for zone, percentage in zone_distribution.items():
            if zone not in zone_rates:
                continue
            
            # Calculate time in this zone
            minutes_in_zone = duration_minutes * (percentage / 100)
            
            # Calculate energy for this zone
            base_rate = zone_rates[zone]
            adjusted_rate = base_rate * weight_factor
            zone_energy = adjusted_rate * minutes_in_zone
            
            total_energy += zone_energy
            
            # Calculate training load contribution
            zone_load = minutes_in_zone * zone_load_factors[zone]
            training_load += zone_load
        
        # Apply metabolic drift for sessions > 3 hours
        if duration_minutes > 180:
            hours_over_3 = (duration_minutes - 180) / 60
            drift_factor = 1 + (hours_over_3 * 0.05)  # 5% per hour
            total_energy *= drift_factor
        
        return int(total_energy), training_load
    
    def calculate_tef(self, total_intake_kcal: int) -> int:
        """
        Calculate Thermic Effect of Food.
        
        TEF is approximately 10% of total caloric intake.
        
        Args:
            total_intake_kcal: Total daily caloric intake
            
        Returns:
            TEF in kcal
        """
        return int(total_intake_kcal * 0.10)
    
    def calculate_daily_macros(
        self, 
        training_load_score: float,
        total_tdee: int
    ) -> Dict[str, float]:
        """
        Calculate macro distribution based on training load.
        
        Uses dynamic carbohydrate periodization:
        - Low demand: 3-5 g/kg
        - Moderate: 5-7 g/kg
        - High: 7-10 g/kg
        - Very high: 10-12 g/kg
        
        Args:
            training_load_score: Calculated training load for the day
            total_tdee: Total daily energy expenditure
            
        Returns:
            Dict with carbs_g, protein_g, fat_g
        """
        weight = self.user.weight_kg
        
        # Determine carbohydrate needs based on training load (MORE GRANULAR)
        if training_load_score < 50:
            carbs_per_kg = 4.0  # Low demand (rest/easy day)
        elif training_load_score < 80:
            carbs_per_kg = 5.5  # Moderate-low demand
        elif training_load_score < 110:
            carbs_per_kg = 6.5  # Moderate demand
        elif training_load_score < 140:
            carbs_per_kg = 7.5  # Moderate-high demand
        elif training_load_score < 180:
            carbs_per_kg = 9.0  # High demand
        else:
            carbs_per_kg = 11.0  # Very high demand / race day
        
        carbs_g = weight * carbs_per_kg
        
        # Protein: 2.0 g/kg for endurance athletes (recovery + adaptation)
        protein_g = weight * 2.0
        
        # Fat: Remaining calories after carbs and protein
        carbs_kcal = carbs_g * 4
        protein_kcal = protein_g * 4
        remaining_kcal = total_tdee - carbs_kcal - protein_kcal
        
        # Ensure minimum fat intake (20% of TDEE minimum for hormonal health)
        min_fat_kcal = total_tdee * 0.20
        fat_kcal = max(remaining_kcal, min_fat_kcal)
        
        fat_g = fat_kcal / 9
        
        return {
            'carbs_g': round(carbs_g, 1),
            'protein_g': round(protein_g, 1),
            'fat_g': round(fat_g, 1)
        }
    
    def calculate_hydration_needs(
        self,
        training_sessions: list,
        baseline: bool = True
    ) -> Dict[str, int]:
        """
        Calculate daily hydration requirements.
        
        Args:
            training_sessions: List of training sessions for the day
            baseline: Include baseline daily hydration
            
        Returns:
            Dict with baseline_ml, training_ml, total_ml
        """
        # Baseline hydration: 35 ml/kg body weight
        baseline_ml = int(self.user.weight_kg * 35) if baseline else 0
        
        training_ml = 0
        
        for session in training_sessions:
            sport = session.get('sport')
            duration_minutes = session.get('duration_minutes')
            zone_distribution = session.get('zone_distribution', {})
            
            # Calculate average zone (weighted)
            avg_zone = 0
            total_pct = 0
            for zone, pct in zone_distribution.items():
                avg_zone += zone * pct
                total_pct += pct
            
            if total_pct > 0:
                avg_zone = avg_zone / total_pct
            else:
                avg_zone = 2  # Default to Z2
            
            # Fluid needs per hour by intensity
            if avg_zone < 2:
                ml_per_hour = 500
            elif avg_zone < 3:
                ml_per_hour = 700
            else:
                ml_per_hour = 900
            
            # Sport adjustments
            if sport == 'swim':
                ml_per_hour *= 0.8  # Less sweating in water
            elif sport == 'run':
                ml_per_hour *= 1.1  # More sweating while running
            
            session_ml = int((duration_minutes / 60) * ml_per_hour)
            
            # Post-workout rehydration (150% of losses)
            session_ml = int(session_ml * 1.5)
            
            training_ml += session_ml
        
        return {
            'baseline_ml': baseline_ml,
            'training_ml': training_ml,
            'total_ml': baseline_ml + training_ml
        }
