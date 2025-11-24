import logging
import os
import json
from pathlib import Path

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

# Wellness log helper functions
LOG_FILE = Path("wellness_log.json")

def load_wellness_log():
    """Load all wellness check-in entries from the JSON log file."""
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning(f"Could not decode {LOG_FILE}, returning empty list")
        return []

def save_wellness_log(entries):
    """Save wellness check-in entries to the JSON log file."""
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)
    logger.info(f"✓ Saved {len(entries)} wellness check-in(s) to {LOG_FILE}")

def create_log_entry(mood_text, energy_text, stressors_text, objectives_list, summary_text):
    """Create a wellness log entry dict with all required fields.
    
    Args:
        mood_text: How the user is feeling emotionally
        energy_text: Their energy level description
        stressors_text: What's stressing them out (can be empty string)
        objectives_list: List of 1-3 goals for the day
        summary_text: Overall summary of the check-in
        
    Returns:
        dict: Complete wellness log entry
    """
    from datetime import datetime
    
    now = datetime.now()
    
    return {
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "mood": mood_text,
        "energy": energy_text,
        "stressors": stressors_text,
        "objectives": objectives_list,
        "summary": summary_text,
    }




class WellnessCompanion(Agent):
    """Health & Wellness Voice Companion that conducts daily check-ins"""
    
    def __init__(self) -> None:
        # Initialize wellness state (will be populated during check-in)
        self.wellness_state = {
            "timestamp": None,
            "date": None,
            "time": None,
            "mood": None,
            "energy": None,
            "stressors": None,
            "objectives": [],
            "summary": None
        }
        
        # Load past check-ins for context
        self.past_checkins = self._load_past_checkins()
        
        # Create dynamic system prompt with memory
        base_prompt = """You are a calm, supportive, realistic health and wellness companion.

Your role is to conduct brief daily check-ins with users. You are NOT a doctor or therapist.
Avoid medical diagnosis or clinical terms. Focus on being a caring, practical friend.

CONVERSATION FLOW:

1. GREET WARMLY
   - If there's past data, reference it naturally (e.g., "Last time you mentioned wanting to exercise - how did that go?")
   - If first time, just greet warmly

2. ASK ABOUT MOOD AND ENERGY
   Examples:
   - "How are you feeling today?"
   - "What's your energy like right now?"
   - "Anything stressing you out?"
   - "How are you doing emotionally?"
   
   Listen to their response. Be empathetic.

3. ASK ABOUT GOALS/INTENTIONS
   Examples:
   - "What are 1–3 things you'd like to get done today?"
   - "Is there anything you want to do just for yourself today? Maybe rest, a walk, or a hobby?"
   - "Any goals for today, big or small?"
   
   Encourage achievable goals. It's okay if goals are simple.

4. OFFER SIMPLE, PRACTICAL ADVICE
   Based on what they shared, offer ONE small suggestion:
   - "Maybe start with the easiest task first."
   - "A 5–10 minute walk could help clear your head."
   - "Sounds like you could use a break - even 5 minutes helps."
   - "Breaking that big task into smaller steps might feel less overwhelming."
   
   Keep it practical and non-medical. No diagnosis. No prescriptions.

5. RECAP AND CONFIRM
   Summarize what they told you:
   "So today you're feeling [mood], your energy is [energy], and your main goals are [goal 1], [goal 2]. Does that sound right?"
   
   Wait for confirmation (yes, correct, that's right, etc.)

6. SAVE THE CHECK-IN
   Once they confirm, use the save_wellness_checkin tool to save their check-in.
   
7. END WITH ENCOURAGEMENT
   - "You've got this!"
   - "Remember to be kind to yourself today."
   - "One step at a time - you're doing great."

IMPORTANT RULES:
- Keep responses SHORT and conversational (1-2 sentences max)
- Ask ONE question at a time
- Wait for their response before moving to the next step
- Be supportive but realistic
- Celebrate small wins
- Never diagnose or give medical advice"""

        # Add memory context if there are past check-ins
        if self.past_checkins:
            last_checkin = self.past_checkins[-1]
            memory_context = f"""

MEMORY: Last check-in was on {last_checkin.get('date')} at {last_checkin.get('time')}.
They felt {last_checkin.get('mood', 'N/A')} with {last_checkin.get('energy', 'N/A')} energy.
Their goals were: {', '.join(last_checkin.get('objectives', []))}.
Reference this naturally in your greeting to show continuity."""

            base_prompt += memory_context
        
        super().__init__(instructions=base_prompt)
    
    def _load_past_checkins(self, max_recent: int = 5) -> list:
        """Load recent wellness check-ins from JSON file"""
        all_checkins = load_wellness_log()
        # Return the most recent check-ins
        return all_checkins[-max_recent:] if len(all_checkins) > max_recent else all_checkins
    
    @function_tool
    async def save_wellness_checkin(
        self, 
        context: RunContext, 
        mood: str, 
        energy: str, 
        objectives: str,
        stressors: str = "",
        summary: str = ""
    ):
        """Save the daily wellness check-in to wellness_log.json.
        
        Use this tool AFTER you have:
        1. Asked about their mood
        2. Asked about their energy level  
        3. Asked about any stressors
        4. Asked about their objectives/goals for the day
        5. Summarized what they shared and got confirmation
        
        Args:
            mood: How the user is feeling emotionally (e.g., "good", "stressed", "calm", "excited")
            energy: Their energy level (e.g., "low", "medium", "high", "tired but motivated")
            objectives: Their 1-3 goals for the day, comma-separated (e.g., "exercise 30min, finish project, drink more water")
            stressors: What's stressing them out or bothering them (optional, can be empty string)
            summary: Overall summary of the check-in conversation (optional)
        """
        # Parse objectives into a list
        objectives_list = [obj.strip() for obj in objectives.split(',') if obj.strip()]
        
        # Create the log entry using the helper function
        entry = create_log_entry(
            mood_text=mood,
            energy_text=energy,
            stressors_text=stressors,
            objectives_list=objectives_list,
            summary_text=summary if summary else f"Mood: {mood}, Energy: {energy}"
        )
        
        # Save to JSON file using helper functions
        all_checkins = load_wellness_log()
        all_checkins.append(entry)
        save_wellness_log(all_checkins)
        
        logger.info(f"✓ Wellness check-in #{len(all_checkins)} saved: {entry}")
        
        return f"Perfect! I've saved your check-in. Remember: {', '.join(objectives_list)}. You've got this! 💪"

    
    @function_tool
    async def get_past_checkins(self, context: RunContext, count: int = 3):
        """Retrieve recent wellness check-ins for reference.
        
        Use this tool if you want to look up specific past check-ins during the conversation.
        
        Args:
            count: Number of recent check-ins to retrieve (default: 3, max: 10)
        """
        count = min(count, 10)  # Cap at 10
        
        all_checkins = load_wellness_log()
        if not all_checkins:
            return "No past check-ins found."
        
        recent = all_checkins[-count:] if len(all_checkins) > count else all_checkins
        
        summary = []
        for checkin in recent:
            summary.append(
                f"• {checkin['date']}: {checkin['mood']} mood, "
                f"{checkin['energy']} energy, "
                f"goals: {', '.join(checkin['objectives'])}"
            )
        
        return "\n".join(summary)



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
        agent=WellnessCompanion(),
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
