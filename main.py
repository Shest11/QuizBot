import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src")) # src становится путем для импорта, чтобы перейти в bot.main

from bot.main import main as run_bot

if __name__ == "__main__":
    asyncio.run(run_bot())