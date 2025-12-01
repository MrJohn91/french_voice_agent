#!/usr/bin/env python3
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def delete_agent():
    url = os.getenv("LIVEKIT_URL").replace("wss://", "https://")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    from livekit import api
    
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=api_key,
        api_secret=api_secret
    )
    
    try:
        # Delete the agent
        await lkapi.agent.delete_job("CA_NDS9Tpsmncgg")
        print("✅ Agent CA_NDS9Tpsmncgg deleted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await lkapi.aclose()

asyncio.run(delete_agent())
