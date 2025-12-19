"""
Data models for training block generation.
"""
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class PhysiologicalParameters(BaseModel):
    """Physiological parameters for the athlete."""
    hr_max: int = Field(..., description="Maximum heart rate in bpm")
    threshold_t1_pace: str = Field(..., description="T1 threshold pace (mm:ss/km format)")
    threshold_t2_pace: str = Field(..., description="T2 threshold pace (mm:ss/km format)")
    vo2_max: Optional[int] = Field(None, description="VO2 max in ml/kg/min")

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


class TrainingPhase(str, Enum):
    """Training periodization phases."""
    BASE = "BASE"
    BUILD = "BUILD"
    PEAK = "PEAK"
    TAPER = "TAPER"
    TRANSITION = "TRANSITION"


class VolumeProgressionStrategy(BaseModel):
    """Volume progression rates for different training phases."""
    base_percent: float = Field(default=10.0, description="Weekly volume increase during base phase (%)")
    build_percent: float = Field(default=5.0, description="Weekly volume increase during build phase (%)")
    peak_percent: float = Field(default=2.5, description="Weekly volume increase during peak phase (%)")
    taper_percent: float = Field(default=-20.0, description="Weekly volume decrease during taper phase (%)")
    transition_percent: float = Field(default=0.0, description="Volume change during transition phase (%)")
    deload_percent: float = Field(default=-40.0, description="Volume reduction during deload weeks (%)")

    def get_progression_for_phase(self, phase: TrainingPhase) -> float:
        """Get the progression percentage for a given training phase."""
        progression_map = {
            TrainingPhase.BASE: self.base_percent,
            TrainingPhase.BUILD: self.build_percent,
            TrainingPhase.PEAK: self.peak_percent,
            TrainingPhase.TAPER: self.taper_percent,
            TrainingPhase.TRANSITION: self.transition_percent,
        }
        return progression_map.get(phase, 0.0)

    def calculate_weekly_volumes(
        self,
        phase: TrainingPhase,
        starting_volume: int,
        num_weeks: int,
        include_deload: bool = True
    ) -> List[int]:
        """
        Calculate weekly volume targets with phase-appropriate progression.

        Args:
            phase: The training phase
            starting_volume: Starting weekly volume in km
            num_weeks: Total number of weeks (including deload if applicable)
            include_deload: Whether to include a deload week at the end

        Returns:
            List of weekly volumes in km
        """
        progression_rate = self.get_progression_for_phase(phase)
        volumes = []
        current_volume = starting_volume

        # Calculate build weeks
        build_weeks = num_weeks - 1 if include_deload else num_weeks

        for week in range(build_weeks):
            volumes.append(round(current_volume))
            current_volume *= (1 + progression_rate / 100)

        # Add deload week if requested
        if include_deload:
            peak_volume = volumes[-1] if volumes else starting_volume
            deload_volume = round(peak_volume * (1 + self.deload_percent / 100))
            volumes.append(deload_volume)

        return volumes


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
    primary_goal: TrainingPhase = Field(
        ...,
        description="The specific periodization phase: BASE (Capacity), BUILD (Threshold), PEAK (Race Specificity), TAPER (Freshness), or TRANSITION (Recovery)"
    )
    running_mileage_week1: int = Field(..., description="Starting weekly mileage in km")
    volume_progression: VolumeProgressionStrategy = Field(
        default_factory=VolumeProgressionStrategy,
        description="Volume progression strategy based on training phase"
    )
    weekly_progression_override: Optional[float] = Field(
        None,
        description="Optional manual override for weekly progression %. If None, uses phase-appropriate default."
    )
    block_duration_weeks: int = Field(default=4, description="Number of build weeks before deload")
    deload_week: bool = Field(default=True, description="Include a deload week at the end")
    specific_focus_areas: List[str] = Field(
        default=[],
        description="Specific areas to focus on (e.g., 'threshold running', 'sled work', 'wall balls')"
    )
    target_race_date: Optional[str] = Field(None, description="Target race date (YYYY-MM-DD)")
    race_type: Optional[str] = Field(
        None,
        description="Race category for HYROX weights (Men, Women, Pro Men, Pro Women, Doubles)"
    )
    weeks_to_race: Optional[int] = Field(None, description="Number of weeks until race")

    # Maintain backward compatibility
    @property
    def weekly_progression_percent(self) -> float:
        """Get the progression percentage (for backward compatibility)."""
        return self.get_progression_percent()

    def get_progression_percent(self) -> float:
        """Get the progression percentage for this block's training phase."""
        # Use manual override if provided, otherwise use phase-based default
        if self.weekly_progression_override is not None:
            return self.weekly_progression_override
        return self.volume_progression.get_progression_for_phase(self.primary_goal)

    def get_weekly_volumes(self) -> List[int]:
        """
        Calculate the weekly volume schedule for this training block.

        Returns:
            List of weekly volumes in km, including deload week if applicable
        """
        # Create a custom progression rate if override is provided
        if self.weekly_progression_override is not None:
            # Temporarily override the phase-specific rate
            custom_strategy = VolumeProgressionStrategy(
                base_percent=self.weekly_progression_override,
                build_percent=self.weekly_progression_override,
                peak_percent=self.weekly_progression_override,
                taper_percent=self.weekly_progression_override,
                transition_percent=self.weekly_progression_override,
                deload_percent=self.volume_progression.deload_percent  # Keep deload as-is
            )
            return custom_strategy.calculate_weekly_volumes(
                phase=self.primary_goal,
                starting_volume=self.running_mileage_week1,
                num_weeks=self.block_duration_weeks + (1 if self.deload_week else 0),
                include_deload=self.deload_week
            )

        # Use phase-based progression
        return self.volume_progression.calculate_weekly_volumes(
            phase=self.primary_goal,
            starting_volume=self.running_mileage_week1,
            num_weeks=self.block_duration_weeks + (1 if self.deload_week else 0),
            include_deload=self.deload_week
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
    race_category: Optional[str] = Field(
        None,
        description="HYROX race category (Men, Women, Pro Men, Pro Women, Doubles) - automatically sets hyrox_weights if provided"
    )

    def __init__(self, **data):
        """Initialize athlete profile and auto-set HYROX weights if race_category provided."""
        # If race_category is provided but hyrox_weights is not, auto-load weights
        if 'race_category' in data and data['race_category'] and 'hyrox_weights' not in data:
            data['hyrox_weights'] = HyroxWeights.for_division(data['race_category'])
        super().__init__(**data)


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
    skip_qa_validation: bool = Field(
        default=False,
        description="Skip QA validation stage (faster generation)"
    )
    output_directory: str = "output"
