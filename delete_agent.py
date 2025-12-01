#!/usr/bin/env python3
"""Delete LiveKit agent from cloud"""

import os
from livekit import api
from dotenv import load_dotenv

load_dotenv()

def delete_agent(agent_id: str):
    """Delete agent by ID"""
    livekit_api = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )
    
    # Delete the agent
    livekit_api.agent.delete_worker(agent_id)
    print(f"✅ Agent {agent_id} deleted successfully")

def list_agents():
    """List all agents"""
    livekit_api = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )
    
    workers = livekit_api.agent.list_workers()
    print("\n📋 Available agents:")
    for worker in workers:
        print(f"  - ID: {worker.id}, Name: {worker.name}")
    return workers

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        agent_id = sys.argv[1]
        delete_agent(agent_id)
    else:
        print("Usage: python delete_agent.py <agent-id>")
        print("\nOr list agents first:")
        list_agents()
