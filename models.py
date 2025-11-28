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
    rest_days: str = "Monday"  # Comma-separated list of rest days
    main_sessions_per_week: int = 8  # Total number of sessions per week
    double_days: str = "Wednesday, Saturday"  # Which days have AM + PM sessions
    runs_per_week: int = 4  # Number of running sessions per week
    long_run_day: str = "Sunday"  # Which day should have the long run
    weekday_session_time_min: int = 45
    weekday_session_time_max: int = 75
    weekend_session_time_min: int = 90
    weekend_session_time_max: int = 105

    def get_rest_days_list(self) -> list[str]:
        """Get list of rest days from the comma-separated string."""
        if not self.rest_days:
            return []
        return [d.strip() for d in self.rest_days.split(',') if d.strip()]

    def get_num_rest_days(self) -> int:
        """Calculate number of rest days."""
        return len(self.get_rest_days_list())

    def get_num_training_days(self) -> int:
        """Calculate number of training days (7 - rest days)."""
        return 7 - self.get_num_rest_days()

    def get_num_double_days(self) -> int:
        """Calculate number of double-days from the double_days string."""
        if not self.double_days:
            return 0
        return len([d.strip() for d in self.double_days.split(',') if d.strip()])

    def get_training_days_range(self) -> str:
        """Calculate training days range based on rest days."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        rest_list = self.get_rest_days_list()

        if not rest_list:
            return "Monday → Sunday"

        # If only one rest day, return range
        if len(rest_list) == 1:
            try:
                rest_idx = days.index(rest_list[0])
            except ValueError:
                return "Tuesday → Sunday"  # fallback

            # Training starts day after rest
            start_idx = (rest_idx + 1) % 7
            # Training ends day before rest
            end_idx = (rest_idx - 1) % 7

            return f"{days[start_idx]} → {days[end_idx]}"

        # Multiple rest days - just list training days
        rest_set = set(rest_list)
        training_days_list = [d for d in days if d not in rest_set]
        if len(training_days_list) <= 3:
            return ", ".join(training_days_list)
        else:
            return f"{training_days_list[0]} → {training_days_list[-1]} (with rest on {', '.join(rest_list)})"


class PerformanceBenchmarks(BaseModel):
    """Performance benchmarks and HYROX-specific data."""
    last_hyrox_date: Optional[str] = Field(None, description="Date of last HYROX race")
    last_hyrox_time: Optional[str] = Field(None, description="Last HYROX time (HH:MM:SS format)")
    goal_hyrox_time: Optional[str] = Field(None, description="Goal HYROX time (HH:MM:SS format)")
    races_completed: int = Field(default=0, description="Number of HYROX races completed")
    strong_stations: List[str] = Field(default=[], description="Stations where athlete excels")
    weak_stations: List[str] = Field(default=[], description="Stations needing improvement")


class Equipment(BaseModel):
    """Available equipment for training."""
    primary_location: str = Field(
        default="Full HYROX Gym",
        description="Primary training location"
    )
    available_equipment: List[str] = Field(
        default=[
            "SkiErg", "Sled", "Sled Track", "Burpee Broad Jump space", "Rowing Machine",
            "Farmers Carry handles", "Sandbag lunges space", "Wall Balls", "Full barbell setup"
        ],
        description="Equipment available for training"
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
    primary_goal: str = Field(..., description="Main goal for this block (e.g., 'BUILD', 'PEAK', 'Base building')")
    running_mileage_week1: int = Field(..., description="Starting weekly mileage in km")
    weekly_progression_percent: int = Field(default=10, description="% increase in mileage per week")
    block_duration_weeks: int = Field(default=4, description="Number of build weeks before deload")
    deload_week: bool = Field(default=True, description="Include a deload week at the end")
    specific_focus_areas: List[str] = Field(
        default=[],
        description="Specific areas to focus on (e.g., 'threshold running', 'sled work', 'wall balls')"
    )
    target_race_date: Optional[str] = Field(None, description="Target race date")
    race_type: Optional[str] = Field(None, description="Race type (Open/Pro/Doubles/Doubles Pro/Mixed Relay)")
    weeks_to_race: Optional[int] = Field(None, description="Number of weeks until race")


class AthleteProfile(BaseModel):
    """Complete athlete profile."""
    name: str
    age: int
    physiological_params: PhysiologicalParameters
    week_structure: TrainingWeekStructure = Field(default_factory=TrainingWeekStructure)
    equipment: Equipment = Field(default_factory=Equipment)
    injury_info: InjuryInformation = Field(default_factory=InjuryInformation)
    performance_benchmarks: PerformanceBenchmarks = Field(default_factory=PerformanceBenchmarks)


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
