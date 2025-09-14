#!/usr/bin/env python3
"""
Assessment classes for streetlifting program generation
Separated to avoid heavy model imports in API server
"""

from dataclasses import dataclass

@dataclass
class StreetliftingAssessment:
    # Core streetlifting movements
    weighted_pullups_max: int  # kg
    weighted_dips_max: int     # kg
    muscle_ups: int            # max reps
    
    # Compound bodybuilding movements
    rows_max: int             # kg for weighted rows
    pushups_max: int          # max reps
    squats_max: int           # kg for weighted squats
    
    # Training parameters
    training_days_per_week: int
    mesocycle_week: int       # Current week in mesocycle
    primary_goal: str         # "strength", "muscle_ups", "hypertrophy", "power"
    athlete_description: str = ""  # Optional athlete description