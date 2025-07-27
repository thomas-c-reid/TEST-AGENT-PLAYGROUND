import logging
import os
from dotenv import load_dotenv

load_dotenv()

INPUT_PROMPT_LOG_PATH = os.getenv("INPUT_PROMPT_LOG_PATH")
RESPONSE_LOG_PATH = os.getenv("RESPONSE_LOG_PATH")

# Ensure log directories exist
for log_path in [INPUT_PROMPT_LOG_PATH, RESPONSE_LOG_PATH]:
    if log_path and not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    # Clear previous log
    if log_path:
        with open(log_path, 'w'):
            pass

def get_input_logger() -> logging.Logger:
    """
    Returns a logger for input prompts.
    """
    logger = logging.getLogger("input_prompt")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler(INPUT_PROMPT_LOG_PATH, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - INPUT - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

def get_response_logger() -> logging.Logger:
    """
    Returns a logger for responses.
    """
    logger = logging.getLogger("response")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler(RESPONSE_LOG_PATH, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - RESPONSE - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger