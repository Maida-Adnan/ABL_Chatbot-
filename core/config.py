import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")