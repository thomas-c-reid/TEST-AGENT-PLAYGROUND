import json
import os
from dotenv import load_dotenv
from utils.logger import get_input_logger, get_response_logger
from data.enums.enums import VideoStage
from data.datamodels import (
    VideoConcept,
    VideoPlanningResult,
    ShotList,
    AssetCollectionResult,
    EditingPlan,
    PlanningRequest
    ) 
from pydantic_ai import Agent
from typing import List, Dict, Optional, Type

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from agents.agent_builder import AgentBuilder


load_dotenv()

input_logger = get_input_logger()
response_logger = get_response_logger()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

provider = OpenAIProvider(api_key="ollama", base_url=OLLAMA_BASE_URL)
model = OpenAIModel("qwen2.5-coder:7b", provider=provider)

class App:
    
    CHANNEL_PATH: str = os.getenv("CHANNEL_JSON_PATH")
    SERIES_PATH: str = os.getenv("SERIES_JSON_PATH")
    CHANNELS: list = []
    SERIES: list = []

    def __init__(self):
        self.load_data()
        config = self.load_menu()
        
        self.vm = VideoManager(**config)
        
    async def run(self):
        if not self.vm:
            raise RuntimeError("VideoManager not initialized. Please run the App first.")
        await self.vm.start_pipeline()

    def load_data(self):
        # Load channels
        if not self.CHANNEL_PATH or not os.path.exists(self.CHANNEL_PATH):
            raise FileNotFoundError(f"Channel file not found: {self.CHANNEL_PATH}")
        with open(self.CHANNEL_PATH, "r", encoding="utf-8") as f:
            self.CHANNELS = json.load(f)
        # Load series
        if not self.SERIES_PATH or not os.path.exists(self.SERIES_PATH):
            raise FileNotFoundError(f"Series file not found: {self.SERIES_PATH}")
        with open(self.SERIES_PATH, "r", encoding="utf-8") as f:
            self.SERIES = json.load(f)

    def load_menu(self) -> dict:
        # Display channels
        print("\nAvailable Channels:")
        for idx, ch in enumerate(self.CHANNELS):
            print(f"  [{idx+1}] {ch['name']} - {ch.get('description','')}")
        while True:
            try:
                ch_idx = int(input("Select a channel by number: ")) - 1
                if 0 <= ch_idx < len(self.CHANNELS):
                    chosen_channel = self.CHANNELS[ch_idx]
                    break
                else:
                    print("Invalid selection. Try again.")
            except Exception:
                print("Please enter a valid number.")


        # Filter series for this channel by channel uuid (id)
        channel_uuid = chosen_channel.get("uuid") or chosen_channel.get("id")
        user_series = [s for s in self.SERIES if (s.get("channel")) == channel_uuid]
        if not user_series:
            print("No series found for this channel.")
            chosen_series = None
        else:
            print("\nAvailable Series for this Channel:")
            for idx, s in enumerate(user_series):
                print(f"  [{idx+1}] {s['name']} - {s.get('description','')}")
            while True:
                try:
                    s_idx = int(input("Select a series by number: ")) - 1
                    if 0 <= s_idx < len(user_series):
                        chosen_series = user_series[s_idx]
                        break
                    else:
                        print("Invalid selection. Try again.")
                except Exception:
                    print("Please enter a valid number.")

        # Ask for video description
        video_desc = input("\nEnter a short description for your video: ")

        return {
            "channel": chosen_channel,
            "series": chosen_series,
            "description": video_desc
        }
    
    
class VideoManager:
    """
    We will use this class to manage the agents being loaded in
    """
    CHANNEL: str = None
    SERIES: str = None
    DESCRIPTION: str = None
    
    # PATHS
    SERIES_PATH: str = os.getenv("SERIES_JSON_PATH", "data/json/series")
    CHANNEL_PATH: str = os.getenv("CHANNEL_JSON_PATH", "data/json/channels")
    PROMPTS_PATH: str = os.getenv("PROMPTS_PATH", "data/prompts")
    
    # We will want to change this so load_agent takes a config yaml file to tell what prompt to use at each stage
    # MODEL_NAME: str = os.getenv("MODEL_NAME", "openai:gpt-4o-mini")
    # MODEL_NAME: str = os.getenv("GROK_MODEL_NAME")
    ENV: str = os.getenv("ENV", "DEV")
    
    def __init__(self, channel: dict, series: dict, description: str):
        self.CURRENT_STAGE: VideoStage = VideoStage.VIDEO_CONCEPT
        self.CHANNEL = channel
        self.SERIES = series
        self.DESCRIPTION = description
        
        # Define the order of stages
        self.stage_order: List[VideoStage] = [
            VideoStage.VIDEO_CONCEPT,
            VideoStage.STORYBOARD_AND_SCRIPT,
            VideoStage.SHOTLIST,
            VideoStage.ASSET_COLLECTION,
            VideoStage.EDITING_PLAN,
            VideoStage.FINAL_EDIT,
        ]
        
        # Define each stages input type
        self.input_types: Dict[VideoStage, Optional[Type]] = {
            VideoStage.VIDEO_CONCEPT: None,  # First stage has no input
            VideoStage.STORYBOARD_AND_SCRIPT: VideoConcept,
            VideoStage.SHOTLIST: VideoPlanningResult,
            VideoStage.ASSET_COLLECTION: ShotList,
            VideoStage.EDITING_PLAN: AssetCollectionResult,
            VideoStage.FINAL_EDIT: EditingPlan,
        }
        
        # Initialize the AgentBuilder
        self.agent_builder = AgentBuilder(channel=channel, series=series, description=description)
                
    async def start_pipeline(self):
        """
        This will start the process
        """
        for stage in self.stage_order:
            self.CURRENT_STAGE = stage
            print(f"\nStarting stage: {self.CURRENT_STAGE.name}")
            
            # Load the agent for the current stage
            agent: Agent = self.agent_builder.load_agent(stage)
            enhancement_agent = self.agent_builder.load_agent()
            
            input_logger.info(f"Running agent for stage: {self.CURRENT_STAGE.name}")
            
            enhanced_prompt = await enhancement_agent.run(user_prompt=str(agent.system_prompt))
            result = await agent.run(user_prompt=enhanced_prompt.output)
            
            print('*'*500)
            print(enhanced_prompt)
            print(f"Enhanced Prompt for Stage {self.CURRENT_STAGE.name}:\n{enhanced_prompt.output}")
            print('*'*500)
            print(f'Prompt before: {agent.system_prompt}')
            print('*'*500)
                        
            response_logger.info(f"Stage {self.CURRENT_STAGE.name} \n \n result: {result}")
            
            print(f"\nStage {self.CURRENT_STAGE.name} completed. Result: {result}")

    def build_stage_request(self):
        """
        This function will build the request for the current stage
        """
        input_type = self.input_types.get(self.CURRENT_STAGE)
        if input_type is None:
            raise ValueError(f"No input type defined for stage: {self.CURRENT_STAGE}")
        
        
        