import logging
import os
import json

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        # Initialize order state
        self.order_state = {
            "drinkType": None,
            "size": None,
            "milk": None,
            "extras": [],
            "name": None
        }
        
        super().__init__(
            instructions="""You are a friendly barista at BrewBerry Café.
                            Start by greeting customers warmly: 'Hi! Welcome to BrewBerry Café ☕. I'm your barista today. What can I get started for you?'
                            
                            Your job is to collect a complete coffee order by asking clarifying questions:
                            1. First ask: What drink would they like? (espresso, latte, cappuccino, americano, etc.)
                            2. Then ask: What size? (small, medium, large)
                            3. Then ask: Any milk preference? (whole, skim, oat, almond, soy)
                            4. Then ask: Would they like any extras? (sugar, chocolate, caramel, whipped cream)
                            5. Finally ask: Can I get their name for the order?
                            
                            After collecting ALL information, use the save_order tool to save the order.
                            Keep your responses short, friendly, and conversational.
                            Ask ONE question at a time and wait for the customer's response.""",
        )

    @function_tool
    async def save_order(self, context: RunContext, drink_type: str, size: str, milk: str, extras: str, name: str):
        """Save the completed coffee order to a JSON file.
        
        Use this tool when you have collected ALL order information from the customer.
        
        Args:
            drink_type: The type of coffee drink (e.g., latte, cappuccino, espresso)
            size: The size of the drink (small, medium, large)
            milk: The type of milk (whole, skim, oat, almond, soy, none)
            extras: Any extras requested (sugar, chocolate, caramel, whipped cream, or 'none')
            name: The customer's name for the order
        """
        
        # Update order state
        self.order_state["drinkType"] = drink_type
        self.order_state["size"] = size
        self.order_state["milk"] = milk
        self.order_state["extras"] = [e.strip() for e in extras.split(',')] if extras.lower() != 'none' else []
        self.order_state["name"] = name
        
        # Add timestamp to order
        from datetime import datetime
        self.order_state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to JSON file (append to list of orders)
        order_file = "orders.json"
        
        # Read existing orders
        try:
            with open(order_file, "r") as f:
                all_orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_orders = []
        
        # Append new order
        all_orders.append(self.order_state.copy())
        
        # Save all orders
        with open(order_file, "w") as f:
            json.dump(all_orders, f, indent=4)
        
        logger.info(f"Order #{len(all_orders)} saved for {name}: {self.order_state}")
        
        return f"Perfect! I've got your order saved, {name}. Your {size} {drink_type} with {milk} milk will be ready shortly. Thank you for visiting BrewBerry Café!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=openai.LLM(
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                api_key=os.environ.get("GROQ_API_KEY"),
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-terrell",  # Clear, friendly American male voice
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
