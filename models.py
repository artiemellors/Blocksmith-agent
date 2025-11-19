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
    mini_sessions_per_week: int = 3
    weekday_session_time_min: int = 45
    weekday_session_time_max: int = 75
    weekend_session_time_min: int = 90
    weekend_session_time_max: int = 105


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


class BlockObjectives(BaseModel):
    """Objectives and focus areas for the training block."""
    primary_goal: str = Field(..., description="Main goal for this block (e.g., 'REBUILD', 'BUILD', 'PEAK')")
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
