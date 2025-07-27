import sys

sys.dont_write_bytecode = True

"""
This is a test playground where I will try and build an agent, connect to an MCP server,
and plan-storyboard a video series and then use the tools to connect to DaVinci Resolve
and edit the video.
"""

import asyncio
from data.datamodels import (
    ChannelInfo, 
    SeriesInfo,
    PlanningRequest,
    VideoConcept,
    VideoPlanningResult,
    ShotList,
    AssetCollectionResult,
    EditingPlan,
    FinalEditSummary
)
from data.enums.enums import ContentType
from pydantic_ai import Agent
from dotenv import load_dotenv
import os
from app import App

# ======================================================================================
# SYSTEM PROMPT (top-level)
# ======================================================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def main():
    app = App()
    await app.run()
    
if __name__ == '__main__':
    asyncio.run(main())




































# ======================================================================================
# Pydantic-AI Agents (one per stage)
# ======================================================================================

# Hardcoded chosen channel and series (from main())

# 1) Planning Agent -> VideoConcept
# planning_agent = Agent(
#     model="openai:gpt-4o-mini",
#     system_prompt=build_stage_prompt(
#         "video_concept", chosen_channel, chosen_series
#     ),
#     output_type=VideoConcept,
# )

# # 2) Script + Storyboard Agent -> VideoPlanningResult
# storyboard_agent = Agent(
#     model="openai:gpt-4o-mini",
#     system_prompt=build_stage_prompt(
#         "storyboard_and_script", chosen_channel, chosen_series
#     ),
#     output_type=VideoPlanningResult,
# )

# # 3) Shotlist Agent -> ShotList
# shotlist_agent = Agent(
#     model="openai:gpt-4o-mini",
#     system_prompt=build_stage_prompt(
#         "shotlist", chosen_channel, chosen_series
#     ),
#     output_type=ShotList,
# )


# # 4) Asset Collection Agent -> AssetCollectionResult
# asset_agent = Agent(
#     model="openai:gpt-4o-mini",
#     system_prompt=build_stage_prompt(
#         "asset_collection", chosen_channel, chosen_series
#     ),
#     output_type=AssetCollectionResult,
# )


# # 5) Editing Plan Agent -> EditingPlan
# editing_plan_agent = Agent(
#     model="openai:gpt-4o-mini",
#     system_prompt=build_stage_prompt(
#         "editing_plan", chosen_channel, chosen_series
#     ),
#     output_type=EditingPlan,
# )

# # 6) Final Edit Agent -> FinalEditSummary
# final_edit_agent = Agent(
#     model="openai:gpt-4o-mini",
#     system_prompt=build_stage_prompt(
#         "final_edit", chosen_channel, chosen_series
#     ),
#     output_type=FinalEditSummary,
# )

# ======================================================================================
# Example MCP / Tool placeholders (wire them when ready)
# ======================================================================================

# # Example: search for assets (images, gifs, etc.) via MCP or API
# @asset_agent.tool
# def search_assets(query: str, type: AssetType, max_results: int = 5) -> List[Asset]:
#     """Search assets via MCP/API. (Placeholder implementation)"""
#     # TODO: implement via MCP client
#     return [
#         Asset(
#             id=f"{type}-{i}",
#             type=type,
#             source="placeholder",
#             path_or_url=f"https://assets.example.com/{type}/{i}.mp4" if type == AssetType.VIDEO else f"https://assets.example.com/{type}/{i}.png",
#             license="royalty_free",
#             notes="Mock asset"
#         )
#         for i in range(1, max_results + 1)
#     ]

# # Example: control Resolve (placeholder)
# @final_edit_agent.tool
# def resolve_render(timeline_path: str, preset: str = "YouTube 4K") -> str:
    # """Render the timeline in DaVinci Resolve. (Placeholder implementation)"""
    # # TODO: implement via MCP tool for Resolve
    # return f"/renders/{datetime.now().strftime('%Y%m%d_%H%M%S')}_final.mp4"

# ======================================================================================
# Orchestrator
# ======================================================================================

# async def run_pipeline(planning_input: PlanningRequest):
#     # ---------- Stage 1: Concept ----------
#     concept = await planning_agent.run(planning_input.model_dump_json())
#     print("\n=== STAGE 1: VIDEO_CONCEPT ===")
#     print(concept.model_dump_json(indent=2))
#     await wait_for_user()  # STOP for critique

#     # ---------- Stage 2: Storyboard + Script ----------
#     s2_input = {
#         "video_ref": concept.model_dump(),
#         "instructions": "Create Script + Storyboard as per rules."
#     }
#     s2_result = await storyboard_agent.run(s2_input)
#     print("\n=== STAGE 2: STORYBOARD_AND_SCRIPT ===")
#     print(s2_result.model_dump_json(indent=2))
#     await wait_for_user()

#     # ---------- Stage 3: Shotlist ----------
#     s3_input = {
#         "storyboard_ref": s2_result.storyboard.model_dump(),
#         "script_ref": s2_result.script.model_dump(),
#         "instructions": "Create a realistic ShotList for Resolve."
#     }
#     shotlist = await shotlist_agent.run(s3_input)
#     print("\n=== STAGE 3: SHOTLIST ===")
#     print(shotlist.model_dump_json(indent=2))
#     await wait_for_user()

#     # ---------- Stage 4: Asset binding ----------
#     s4_input = {
#         "shotlist": shotlist.model_dump(),
#         "instructions": "Search/bind assets to each shot using tools."
#     }
#     asset_result = await asset_agent.run(s4_input)
#     print("\n=== STAGE 4: ASSET_COLLECTION ===")
#     print(asset_result.model_dump_json(indent=2))
#     await wait_for_user()

#     # ---------- Stage 5: Editing plan ----------
#     s5_input = {
#         "shotlist_ref": asset_result.shotlist.model_dump(),
#         "instructions": "Create EditingPlan with transitions, music, presets."
#     }
#     editing_plan = await editing_plan_agent.run(s5_input)
#     print("\n=== STAGE 5: EDITING_PLAN ===")
#     print(editing_plan.model_dump_json(indent=2))
#     await wait_for_user()

#     # ---------- Stage 6: Final edit ----------
#     s6_input = {
#         "timeline_path": "/projects/my_video/timeline.drptl",
#         # "render_path": resolve_render("/projects/my_video/timeline.drptl", preset=editing_plan.export_preset),
#         "duration_seconds": editing_plan.estimated_total_duration_seconds,
#         "notes": ["Rendered using preset: " + editing_plan.export_preset]
#     }
#     final_edit = await final_edit_agent.run(s6_input)
#     print("\n=== STAGE 6: FINAL_EDIT ===")
#     print(final_edit.model_dump_json(indent=2))
#     print("\nPipeline complete!")

# async def wait_for_user():
#     # Replace this with your interactive gate / CLI confirm if you like
#     print("\n--- Review this stage. Press Enter to continue ---")
#     try:
#         # When running inside notebooks or environments without input, skip.
#         await asyncio.get_event_loop().run_in_executor(None, input)
#     except Exception:
#         pass

# def main():
    # planning_input = PlanningRequest(
    #     request="Make a 60-second short about 3 productivity hacks that actually work.",
    #     channel_info=ChannelInfo(
    #         name="HyperFocus",
    #         description="Actionable productivity hacks for busy creators.",
    #         content_type=ContentType.SHORTS_REEL_TIKTOK,
    #         color_scheme="neon-green on charcoal",
    #         target_audience="18-35 content creators & indie hackers",
    #         typical_video_length_seconds=60,
    #         tone_of_voice="energetic, concise, no-fluff",
    #         brand_tags=["productivity", "routines", "tools"]
    #     ),
    #     series_info=SeriesInfo(
    #         name="60s Hacks",
    #         description="Bite-sized, practical productivity tips.",
    #         episode_number=4
    #     ),
    #     previous_scripts=None,
    # )
    # asyncio.run(run_pipeline(planning_input))

