from enum import Enum

# ======================================================================================
# ENUMS
# ======================================================================================

class VideoStage(Enum):
    VIDEO_CONCEPT = "video_concept"
    STORYBOARD_AND_SCRIPT = "storyboard_and_script"
    SHOTLIST = "shotlist"
    ASSET_COLLECTION = "asset_collection"
    EDITING_PLAN = "editing_plan"
    FINAL_EDIT = "final_edit"

class GoalType(str, Enum):
    NORMAL = "normal"
    RAGE_BAIT = "rage_bait"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PROMOTIONAL = "promotional"

class ContentType(str, Enum):
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    LIVE = "live"
    SHORTS_REEL_TIKTOK = "shorts_reel_tiktok"

class AssetType(str, Enum):
    IMAGE = "image"
    GIF = "gif"
    VIDEO = "video"
    AUDIO = "audio"
    SFX = "sfx"
    MUSIC = "music"
    TEMPLATE = "template"
    FONT = "font"
