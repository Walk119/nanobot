# nanobot/service/run_bot_chat.py
"""Standalone launcher for bot_chat service."""
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Now import and run
from nanobot.service.bot_chat import create_standalone_app
import uvicorn

if __name__ == "__main__":
    app = create_standalone_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
