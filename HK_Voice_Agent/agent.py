from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    mcp,
    AgentSession
)
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE
import os
import sys
from pathlib import Path

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    news_mcp_server = mcp.MCPServerStdio(
        command=sys.executable,  # Uses the current python path (VA_new)
        args=["LiveNewsServer.py"],
        cwd=str(script_dir),  # Set working directory to script directory
        client_session_timeout_seconds=60 
    )

    maps_mcp_server = mcp.MCPServerStdio(
        command=sys.executable,  # Uses the current python path (VA_new)
        args=["GoogleMapsServer.py"],
        cwd=str(script_dir),  # Set working directory to script directory
        client_session_timeout_seconds=60 
    )
    model = openai.realtime.RealtimeModel(
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"]
    )
    assistant = AssistantFnc(instructions=INSTRUCTIONS, welcome_message=WELCOME_MESSAGE)
    
    session = AgentSession(
        llm=model,
        mcp_servers=[news_mcp_server,maps_mcp_server]
        #mcp_servers=[mcp.MCPServerHTTP(url="https://your-mcp-server-url.com")]
    )
    await session.start(room=ctx.room, agent=assistant)
    
"""
    #### To be added later####
    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)
            
        if assistant_fnc.has_car():
            handle_query(msg)
        else:
            find_profile(msg)
        
    def find_profile(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="system",
                content=LOOKUP_VIN_MESSAGE(msg)
            )
        )
        session.response.create()
        
    def handle_query(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="user",
                content=msg.content
            )
        )
        session.response.create()
      ########################################################
 """

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))