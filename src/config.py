import os
import yaml
from dotenv import load_dotenv
load_dotenv()
def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Load the config.yaml into a variable
CONFIG = load_config()

# Get your OpenAI key safely from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
