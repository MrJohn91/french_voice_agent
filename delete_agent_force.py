#!/usr/bin/env python3
import os
import asyncio
from livekit import api
from dotenv import load_dotenv

load_dotenv()

async def delete_agent():
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )
    
    try:
        # List all dispatches first
        dispatches = await lkapi.agent_dispatch.list_dispatch()
        print(f"Found {len(dispatches)} dispatches")
        
        for dispatch in dispatches:
            print(f"Deleting dispatch: {dispatch.id}")
            await lkapi.agent_dispatch.delete_dispatch(dispatch.id, "")
        
        print("✅ All agents deleted")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await lkapi.aclose()

asyncio.run(delete_agent())
