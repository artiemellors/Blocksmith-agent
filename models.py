"""
Data models for training block generation.
"""
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class PhysiologicalParameters(BaseModel):
    """Physiological parameters for the athlete."""
    hr_max: int = Field(..., description="Maximum heart rate in bpm")
    threshold_t1_pace: str = Field(..., description="T1 threshold pace (mm:ss/km format)")
    threshold_t2_pace: str = Field(..., description="T2 threshold pace (mm:ss/km format)")

    # Heart rate zones (as percentages of HRmax)
    zone1_min: int = 60
    zone1_max: int = 70
    zone2_min: int = 70
    zone2_max: int = 80
    zone3_min: int = 80
    zone3_max: int = 88
    zone4_min: int = 88
    zone4_max: int = 94
    zone5_min: int = 94
    zone5_max: int = 100


class TrainingWeekStructure(BaseModel):
    """Structure and constraints for the training week."""
    training_days: str = "Tuesday → Sunday"
    rest_day: str = "Monday"
    main_sessions_per_week: int = 8
    double_days: str = "Wednesday, Saturday"  # Which days have AM + PM sessions
    runs_per_week: int = 4  # Number of running sessions per week
    long_run_day: str = "Sunday"  # Which day should have the long run
    weekday_session_time_min: int = 45
    weekday_session_time_max: int = 75
    weekend_session_time_min: int = 90
    weekend_session_time_max: int = 105

    def get_num_double_days(self) -> int:
        """Calculate number of double-days from the double_days string."""
        if not self.double_days:
            return 0
        return len([d.strip() for d in self.double_days.split(',') if d.strip()])

    def get_training_days_range(self) -> str:
        """Calculate training days range based on rest day."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        try:
            rest_idx = days.index(self.rest_day)
        except ValueError:
            return "Tuesday → Sunday"  # fallback

        # Training starts day after rest
        start_idx = (rest_idx + 1) % 7
        # Training ends day before rest
        end_idx = (rest_idx - 1) % 7

        return f"{days[start_idx]} → {days[end_idx]}"


class Equipment(BaseModel):
    """Available equipment for training."""
    gym_equipment: List[str] = Field(
        default=["Full HYROX setup"],
        description="Equipment available at gym"
    )
    home_equipment: List[str] = Field(
        default=["exercise bike", "6kg wall ball", "10kg wall ball", "20kg kettlebell", "barbell", "sandbag"],
        description="Equipment available at home"
    )


class InjuryInformation(BaseModel):
    """Current injury status and constraints."""
    active_injuries: List[str] = Field(default=[], description="List of active injuries")
    pain_threshold_during: int = Field(default=2, description="Maximum acceptable pain during session (0-10)")
    pain_threshold_next_day: int = Field(default=3, description="Maximum acceptable pain next day (0-10)")
    soreness_cutoff_hours: int = Field(default=36, description="If soreness exceeds this many hours, reduce volume")
    volume_reduction_percent: int = Field(default=25, description="% to reduce volume if soreness exceeds cutoff")


class HyroxWeights(BaseModel):
    """Official HYROX race weights for specific division."""
    division: str = Field(default="Men", description="HYROX division (Men, Women, Pro Men, Pro Women, Doubles)")
    sled_push_kg: float = Field(default=102, description="Sled push weight in kg")
    sled_pull_kg: float = Field(default=78, description="Sled pull weight in kg")
    wall_ball_kg: float = Field(default=9, description="Wall ball weight in kg")
    wall_ball_target_m: float = Field(default=3.0, description="Wall ball target height in meters")
    sandbag_kg: float = Field(default=20, description="Sandbag lunges weight in kg")
    farmers_carry_kg: List[float] = Field(default=[24, 24], description="Farmer's carry weight per hand in kg")

    @classmethod
    def for_division(cls, division: str) -> "HyroxWeights":
        """Get official HYROX weights for a specific division."""
        weights_by_division = {
            "Men": {
                "sled_push_kg": 102,
                "sled_pull_kg": 78,
                "wall_ball_kg": 9,
                "wall_ball_target_m": 3.0,
                "sandbag_kg": 20,
                "farmers_carry_kg": [24, 24]
            },
            "Women": {
                "sled_push_kg": 78,
                "sled_pull_kg": 56,
                "wall_ball_kg": 6,
                "wall_ball_target_m": 2.7,
                "sandbag_kg": 10,
                "farmers_carry_kg": [16, 16]
            },
            "Pro Men": {
                "sled_push_kg": 152,
                "sled_pull_kg": 103,
                "wall_ball_kg": 12,
                "wall_ball_target_m": 3.0,
                "sandbag_kg": 30,
                "farmers_carry_kg": [32, 32]
            },
            "Pro Women": {
                "sled_push_kg": 102,
                "sled_pull_kg": 78,
                "wall_ball_kg": 9,
                "wall_ball_target_m": 3.0,
                "sandbag_kg": 20,
                "farmers_carry_kg": [24, 24]
            },
            "Doubles": {
                "sled_push_kg": 152,
                "sled_pull_kg": 103,
                "wall_ball_kg": 9,
                "wall_ball_target_m": 3.0,
                "sandbag_kg": 20,
                "farmers_carry_kg": [24, 24]
            }
        }

        config = weights_by_division.get(division, weights_by_division["Men"])
        return cls(division=division, **config)


class BlockObjectives(BaseModel):
    """Objectives and focus areas for the training block."""
    primary_goal: str = Field(..., description="Main goal for this block (e.g., 'BUILD', 'PEAK', 'Base building')")
    running_mileage_week1: int = Field(..., description="Starting weekly mileage in km")
    weekly_progression_percent: int = Field(default=10, description="% increase in mileage per week")
    block_duration_weeks: int = Field(default=4, description="Number of build weeks before deload")
    deload_week: bool = Field(default=True, description="Include a deload week at the end")
    specific_focus_areas: List[str] = Field(
        default=[],
        description="Specific areas to focus on (e.g., 'threshold running', 'sled work', 'wall balls')"
    )


class AthleteProfile(BaseModel):
    """Complete athlete profile."""
    name: str
    age: int
    physiological_params: PhysiologicalParameters
    week_structure: TrainingWeekStructure = Field(default_factory=TrainingWeekStructure)
    equipment: Equipment = Field(default_factory=Equipment)
    injury_info: InjuryInformation = Field(default_factory=InjuryInformation)
    hyrox_weights: HyroxWeights = Field(default_factory=lambda: HyroxWeights.for_division("Men"))


class TrainingBlockInput(BaseModel):
    """Complete input for training block generation."""
    athlete_profile: AthleteProfile
    block_objectives: BlockObjectives
    previous_training_block: Optional[str] = Field(
        None,
        description="Content of the previous training block (markdown format)"
    )
    additional_context: Optional[str] = Field(
        None,
        description="Any additional context or special requests"
    )


class GenerationConfig(BaseModel):
    """Configuration for the generation process."""
    model_name: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 16000
    temperature: float = 1.0
    save_intermediate_layers: bool = Field(
        default=True,
        description="Save output from each layer to separate files"
    )
    output_directory: str = "output"
