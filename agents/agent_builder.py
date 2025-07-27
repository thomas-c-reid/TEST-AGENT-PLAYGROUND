from data.enums.enums import (
    VideoStage,
)
from data.datamodels import (
    VideoConcept,
    VideoPlanningResult,
    ShotList,
    AssetCollectionResult,
    EditingPlan
)

from pydantic_ai.agent import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import requests
import os
import json
from typing import Dict, Optional, Type
from dotenv import load_dotenv
from utils.logger import get_input_logger, get_response_logger

load_dotenv()

response_logger = get_response_logger()

class AgentBuilder:
    """
    A class to build agents based on the current stage of the video production process.
    It uses the pydantic_ai library to create agents with specific prompts and output types.
    """
    
    SERIES_PATH: str = os.getenv("SERIES_JSON_PATH", "data/json/series")
    CHANNEL_PATH: str = os.getenv("CHANNEL_JSON_PATH", "data/json/channels")
    PROMPTS_PATH: str = os.getenv("PROMPTS_PATH", "data/prompts")
    
    ENV: str = os.getenv("ENV", "DEV")
    
    def __init__(self, channel: dict, series: dict, description: str):
        self.channel = channel
        self.series = series
        self.description = description
        
        # Define each stages output type
        self.output_types: Dict[VideoStage, Optional[Type]] = {
            VideoStage.VIDEO_CONCEPT: VideoConcept,
            VideoStage.STORYBOARD_AND_SCRIPT: VideoPlanningResult,
            VideoStage.SHOTLIST: ShotList,
            VideoStage.ASSET_COLLECTION: AssetCollectionResult,
            VideoStage.EDITING_PLAN: EditingPlan,
            VideoStage.FINAL_EDIT: None,
        }
        
        # Define output types for each stage
        self.LLM_PER_STAGE = {
            'DEV': {
                VideoStage.VIDEO_CONCEPT: "openai:gpt-4o-mini",
                VideoStage.STORYBOARD_AND_SCRIPT: "openai:gpt-4o-mini",
                VideoStage.SHOTLIST: "openai:gpt-4o-mini",
                VideoStage.ASSET_COLLECTION: "openai:gpt-4o-mini",
                VideoStage.EDITING_PLAN: "openai:gpt-4o-mini",
                VideoStage.FINAL_EDIT: "openai:gpt-4o-mini"
        },  'PROD': {
                VideoStage.VIDEO_CONCEPT: "openai:gpt-4o-mini",
                VideoStage.STORYBOARD_AND_SCRIPT: "openai:gpt-4o-mini",
                VideoStage.SHOTLIST: "openai:gpt-4o-mini",
                VideoStage.ASSET_COLLECTION: "openai:gpt-4o-mini",
                VideoStage.EDITING_PLAN: "openai:gpt-4o-mini",
                VideoStage.FINAL_EDIT: "openai:gpt-4o-mini"
                       }
        }
        
        self.available_models = self.request_available_models()
        
    def load_agent(self, stage: VideoStage = None) -> Agent:
        """
        Load an agent based on the current stage of the video production process.
        
        Args:
            stage (VideoStage): The current stage of the video production process.
        
        Returns:
            Agent: An instance of the Agent class configured for the specified stage.
        """
        
        if not stage:
            prompt = self.build_prompt_enhancement_system_prompt()
            
            model = self.load_llm_model(VideoStage.VIDEO_CONCEPT)
            
            return Agent(
                model=model,
                system_prompt=prompt,
                output_type=str,
            )
            
        else:
            prompt = self.build_system_prompt(stage)
            
            # Determine the output type for the current stage
            output_type = self.output_types.get(stage)
            
            # Load the appropriate LLM model based on the environment and stage
            model = self.load_llm_model(stage)
            
            return Agent(
                model=model,
                system_prompt=prompt,
                output_type=output_type,
            )
        
    def load_llm_model(self, current_stage: VideoStage):
        # check if the current stage and env has a model defined
        # if it does, load it properly for that provider
        # else, default to one of the available models
        chosen_model = self.LLM_PER_STAGE.get(self.ENV, {}).get(current_stage, os.getenv("DEFAULT_MODEL"))
        print(chosen_model)
        print(self.available_models)
        if chosen_model not in self.available_models:
            chosen_model = os.getenv("DEFAULT_MODEL")
            
        # will need to check between who owns the model so we can test out different ones more dynamically
        provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
        return OpenAIModel(model_name=chosen_model, provider=provider)
        
    def build_system_prompt(self, current_stage: VideoStage) -> str:
        # Map VideoStage enum to prompt file
        stage_prompt_files = {
            VideoStage.VIDEO_CONCEPT: "stage_one_prompt.txt",
            VideoStage.STORYBOARD_AND_SCRIPT: "stage_two_prompt.txt",
            VideoStage.SHOTLIST: "stage_three_prompt.txt",
            VideoStage.ASSET_COLLECTION: "stage_four_prompt.txt",
            VideoStage.EDITING_PLAN: "stage_five_prompt.txt",
            VideoStage.FINAL_EDIT: "stage_six_prompt.txt",
        }
        
        system_prompt_path = os.path.join(self.PROMPTS_PATH, "system_prompt.txt") 
        stage_prompt_file = stage_prompt_files.get(current_stage)
        if not stage_prompt_file:
            raise RuntimeError(f"No prompt file mapping for stage: {current_stage}")
        stage_prompt_path = os.path.join(self.PROMPTS_PATH, stage_prompt_file)

        # Read system prompt
        try:
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except Exception as e:
            raise RuntimeError(f"Could not read system prompt: {e}")

        # Read stage prompt
        if not os.path.exists(stage_prompt_path):
            raise RuntimeError(f"Stage prompt file not found for stage: {current_stage}")
        with open(stage_prompt_path, "r", encoding="utf-8") as f:
            stage_prompt = f.read().strip()

        # Load channel and series dicts from JSON files
        if self.channel is None:
            raise ValueError("No CHANNEL provided!")
        if self.series is None:
            raise ValueError("No SERIES provided!")

        # Load all channels
        if not os.path.exists(self.CHANNEL_PATH):
            raise FileNotFoundError(f"Channel file not found: {self.CHANNEL_PATH}")
        with open(self.CHANNEL_PATH, "r", encoding="utf-8") as f:
            all_channels = json.load(f)
        # Load all series
        if not os.path.exists(self.SERIES_PATH):
            raise FileNotFoundError(f"Series file not found: {self.SERIES_PATH}")
        with open(self.SERIES_PATH, "r", encoding="utf-8") as f:
            all_series = json.load(f)

        # Find the dict for the selected channel
        channel_id = self.channel if isinstance(self.channel, str) else self.channel.get("uuid") or self.channel.get("id")
        channel_dict = next((c for c in all_channels if c.get("uuid") == channel_id or c.get("id") == channel_id), None)
        if not channel_dict:
            raise ValueError(f"Channel with id '{channel_id}' not found in {self.CHANNEL_PATH}")

        # Find the dict for the selected series
        series_id = self.series if isinstance(self.series, str) else self.series.get("uuid") or self.series.get("id")
        series_dict = next((s for s in all_series if s.get("uuid") == series_id or s.get("id") == series_id), None)
        if not series_dict:
            raise ValueError(f"Series with id '{series_id}' not found in {self.SERIES_PATH}")

        channel_str = f"CHANNEL JSON:\n{json.dumps(channel_dict, indent=2)}"
        series_str = f"SERIES JSON:\n{json.dumps(series_dict, indent=2)}"
        
        return f"{system_prompt}\n\n{stage_prompt}\n\n{channel_str}\n\n{series_str}\n\n Main Intended Subject of this Video: [DESC] -> {self.description}\n\n <- THIS IS THE MAIN SUBJECT OF THE VIDEO, DO NOT DEVIATE FROM THIS! ->\n\n"
        
    def build_prompt_enhancement_system_prompt(self) -> str:
        return f'''
                You are an AI assistant that helps enhance prompts for video production agents. 
                Your task is to take a user-provided prompt and enhance it with additional context, details, and structure to make it more suitable for video production tasks. 
                The enhanced prompt should be clear, concise, and provide all necessary information for the agent to perform its task effectively.
                You will be given a Channel, Series and video description and your job is to enhance the prompt for the agent.
                
                ## Channel Information
                {self.channel}
                
                ## Series Information
                {self.series}
                
                ## Video Description
                {self.description}
                '''
        ...
        
    # TODO: Implement this but make the whole class work for multiple LLM Tenants
    @staticmethod
    def request_available_models() -> list:
        return []