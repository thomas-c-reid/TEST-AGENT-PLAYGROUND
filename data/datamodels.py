
# ======================================================================================
# CORE DATA MODELS
# ======================================================================================

from typing import List, Optional
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt
from data.enums.enums import ContentType, GoalType, AssetType
from uuid import uuid4

# ---------- Inputs ----------

class ChannelInfo(BaseModel):
    name: str
    description: str
    content_type: ContentType
    color_scheme: Optional[str] = None
    target_audience: str
    typical_video_length_seconds: PositiveInt
    tone_of_voice: str = "energetic, concise, authoritative"
    brand_tags: List[str] = []
    uuid: uuid4 = uuid4()

class SeriesInfo(BaseModel):
    name: str
    description: str
    episode_number: Optional[int] = None
    overall_arc: Optional[str] = None
    channel: uuid4

class PlanningRequest(BaseModel):
    """
    Input for (1) Planning Stage
    """
    request: str = Field(..., description="High-level user request for the video")
    channel_info: ChannelInfo
    series_info: Optional[SeriesInfo] = None
    # previous_scripts: Optional[List[str]] = None

# ---------- Stage 1 Output ----------

class VideoConcept(BaseModel):
    """
    Result from (1) Planning Stage -> Used in (2) Storyboard & Script creation
    """
    title: str
    description: str
    goal: GoalType
    target_audience: str
    estimated_duration_seconds: PositiveInt
    content_type: ContentType

# ---------- Stage 2 Output ----------

class StoryBeat(BaseModel):
    id: PositiveInt
    timecode_in: NonNegativeInt
    timecode_out: NonNegativeInt
    objective: str
    visual_brief: str
    audio_brief: str
    on_screen_text: Optional[str] = None

class StoryBoard(BaseModel):
    """
    Storyboard portion
    """
    tagline: str
    beats: List[StoryBeat]
    outro: str
    channel_plug: str
    notes: List[str] = []
    video_ref: VideoConcept

class Script(BaseModel):
    """
    Script portion
    """
    full_text: str
    hooks: List[str]
    cta: str
    disclaimers: List[str] = []
    video_ref: VideoConcept

class VideoPlanningResult(BaseModel):
    """
    Response from (2) Storyboard and Script creation
    """
    script: Script
    storyboard: StoryBoard

# ---------- Stage 3 Output ----------

class Asset(BaseModel):
    id: str
    type: AssetType
    source: Optional[str] = None  # API, MCP tool, local path, stock site
    path_or_url: Optional[str] = None
    notes: Optional[str] = None

class Shot(BaseModel):
    """
    For each section of the storyboard, break down how we will achieve it in DaVinci Resolve
    and what assets are needed for each.
    """
    id: PositiveInt
    related_beat_id: PositiveInt
    video_editing_prompt: str
    script_excerpt: str
    duration_seconds: float
    assets_needed: List[str] = Field(default_factory=list)  # logical names
    bound_assets: List[Asset] = Field(default_factory=list) # resolved concrete assets

class ShotList(BaseModel):
    """
    A more in-depth look at how we can achieve this
    """
    shots: List[Shot]
    storyboard_ref: StoryBoard

# ---------- Stage 4 Output ----------

class AssetCollectionResult(BaseModel):
    shotlist: ShotList

# ---------- Stage 5 Output ----------

class EditingPlan(BaseModel):
    shotlist_ref: ShotList
    music_tracks: List[Asset] = []
    color_grading_notes: str = ""
    fx_notes: str = ""
    export_preset: str = "YouTube 4K"
    timeline_fps: int = 30
    estimated_total_duration_seconds: PositiveInt

# ---------- Stage 6 Output ----------

class FinalEditSummary(BaseModel):
    timeline_path: str
    render_path: str
    duration_seconds: PositiveInt
    notes: List[str] = []
