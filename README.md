# Day 3: Health & Wellness Voice Companion 🌿

A supportive AI wellness companion that conducts daily emotional check-ins, remembers past conversations, and helps users set achievable daily goals.

## 🎯 What This Agent Does

The **Health & Wellness Companion** provides:
- **Daily emotional check-ins** with empathetic conversation
- **Memory of past sessions** for continuity and personalization
- **Practical, non-medical advice** tailored to user's state
- **Goal-setting support** for daily intentions
- **Persistent wellness tracking** saved to JSON

### Core Principles
✅ Supportive & empathetic (not clinical)  
✅ One question at a time  
✅ References past check-ins naturally  
✅ Provides simple, practical suggestions  
❌ No medical diagnosis or clinical terms

## 🛠️ Tech Stack

- **Framework**: [LiveKit Agents](https://docs.livekit.io/agents)
- **LLM**: [Groq](https://groq.com) (Llama 3.3 70B Versatile)
- **TTS**: [Murf.ai](https://murf.ai) Falcon (Voice: en-US-matthew)
- **STT**: [Deepgram](https://deepgram.com) Nova-3
- **Frontend**: Next.js + LiveKit Components
- **Data**: JSON-based wellness log with memory

## 📋 Check-In Flow (7 Steps)

The companion follows a structured conversation flow:

1. **Greet Warmly**
   - References past data if available
   - Makes user feel remembered

2. **Ask About Mood & Energy**
   - "How are you feeling today?"
   - "What's your energy like right now?"
   - "Anything stressing you out?"

3. **Ask About Goals/Intentions**
   - "What are 1–3 things you'd like to get done today?"
   - "Is there anything you want to do just for yourself?"

4. **Offer Simple, Practical Advice**
   - "Maybe start with the easiest task first."
   - "A 5–10 minute walk could help."
   - Non-medical suggestions only

5. **Recap & Confirm**
   - "So today you're feeling [mood], your energy is [energy], and your goals are [goals]. Sound right?"

6. **Save the Check-in**
   - Uses `save_wellness_checkin` tool
   - Persists to `wellness_log.json`

7. **End with Encouragement**
   - "You've got this! 💪"
   - "Be kind to yourself today."

## 💾 Data Structure

### wellness_log.json

```json
[
  {
    "timestamp": "2025-11-24T09:15:30+05:30",
    "date": "2025-11-24",
    "time": "09:15:30",
    "mood": "stressed",
    "energy": "low",
    "stressors": "didn't sleep well, work deadline",
    "objectives": [
      "finish project report",
      "get some exercise"
    ],
    "summary": "Mood: stressed, Energy: low"
  },
  {
    "timestamp": "2025-11-24T14:22:15+05:30",
    "date": "2025-11-24",
    "time": "14:22:15",
    "mood": "relieved",
    "energy": "medium",
    "stressors": "",
    "objectives": [
      "go for a walk",
      "catch up on reading"
    ],
    "summary": "Mood: relieved, Energy: medium"
  }
]
```

## 🧠 Memory & Personalization

### How Memory Works

1. **On Start**: Agent loads last 5 check-ins from `wellness_log.json`
2. **Context Injection**: Adds memory to system prompt
3. **Natural Reference**: Mentions past goals in greeting

**Example Greeting with Memory:**
> "Hey! Welcome back. Last time you mentioned you wanted to finish a project report. How did that go?"

### Memory Context Example

```python
if self.past_checkins:
    last_checkin = self.past_checkins[-1]
    memory_context = f"""
    MEMORY: Last check-in was on {last_checkin['date']} at {last_checkin['time']}.
    They felt {last_checkin['mood']} with {last_checkin['energy']} energy.
    Their goals were: {', '.join(last_checkin['objectives'])}.
    """
```

## 🚀 Setup & Run

### Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Configure .env.local
LIVEKIT_URL=ws://127.0.0.1:7880
GROQ_API_KEY=your_key
MURF_API_KEY=your_key
DEEPGRAM_API_KEY=your_key

# Start agent
uv run python src/agent.py dev
```

### Frontend Setup

```bash
cd frontend
pnpm install
pnpm dev
```

### LiveKit Server

```bash
livekit-server --dev
```

## 🎤 Testing the Agent

### Test in Voice Mode

1. Open `http://localhost:3000`
2. Click microphone icon
3. Have a wellness check-in:
   - **You**: "Hi"
   - **Agent**: "Hi! How are you feeling today?"
   - **You**: "I'm feeling a bit stressed"
   - **Agent**: "I hear you. What's your energy like?"
   - Continue the conversation...

### Test in Console Mode

```bash
cd backend
uv run python src/agent.py console
```

Great for quick testing without voice interface!

## 📂 View Saved Check-ins

```bash
cd backend
Get-Content wellness_log.json  # Windows
# or
cat wellness_log.json  # Linux/Mac
```

## 🎨 Conversation Examples

### Example 1: First Check-in (No Memory)

```
Agent: Hi! Welcome. I'm your wellness companion. How are you feeling today?
You: I'm feeling stressed.
Agent: I hear you. What's your energy like right now?
You: Pretty low. I didn't sleep well.
Agent: That's tough. What are 1–3 things you'd like to get done today?
You: Finish a project report and maybe exercise.
Agent: Those sound like good goals. Maybe start with the easiest task first.
Agent: So you're feeling stressed, energy is low, and your goals are 
       finishing the report and exercise. Does that sound right?
You: Yes.
Agent: Perfect! I've saved your check-in. You've got this! 💪
```

### Example 2: Second Check-in (With Memory)

```
Agent: Hey! Welcome back. Last time you wanted to finish a project 
       report and exercise. How did that go?
You: I finished the report! But didn't exercise.
Agent: That's great you got the report done! How are you feeling today?
You: Much better. More relieved.
Agent: Wonderful! What's your energy like today?
You: Medium, better than yesterday.
Agent: That's progress! Any goals for today?
You: Go for that walk I missed, and catch up on reading.
Agent: Nice! A 5–10 minute walk could help. Sound good?
You: Perfect!
Agent: *(saves)* Remember: walk, reading. You're doing great! 💪
```

## 🎯 Key Features

### Core Functionality
✅ **Empathetic Conversation** - Validates feelings naturally  
✅ **Memory Integration** - References past check-ins  
✅ **Practical Advice** - Simple, non-medical suggestions  
✅ **Goal Tracking** - Helps set 1-3 daily objectives  
✅ **Data Persistence** - All check-ins saved with timestamps

### Function Tools
1. **`save_wellness_checkin`** - Saves after user confirmation
2. **Helper functions**: `load_wellness_log()`, `save_wellness_log()`, `create_log_entry()`

### What the Agent Avoids
❌ Medical diagnosis ("You might be depressed")  
❌ Clinical terms ("That sounds like burnout")  
❌ Prescriptive commands ("You must exercise")  
❌ Judgmental responses  
❌ Multiple questions at once

## 📁 Project Structure

```
backend/
├── src/
│   └── agent.py                    # Wellness companion implementation
├── wellness_log.json               # Saved check-ins (auto-created)
├── IMPLEMENTATION_SUMMARY.md       # Technical documentation
├── CONVERSATION_EXAMPLES.md        # Example conversations
└── .env.local                      # API keys

frontend/
├── app/                            # Next.js pages
└── .env.local                      # LiveKit credentials
```

## 🔧 Troubleshooting

### Agent not remembering past check-ins
- Ensure `wellness_log.json` exists in backend directory
- Check backend logs for "Loaded X past check-ins"
- File should be created after first successful check-in

### Check-in not saving
- Look for "✓ Wellness check-in #X saved" in backend logs
- Ensure user confirms before save (agent recaps first)
- Check file permissions on `wellness_log.json`

### Agent giving medical advice
- This shouldn't happen - check system prompt
- Agent is designed to avoid clinical/medical terms
- If it does, please report the conversation

## 🎓 What You Learned (Day 3)

- **State management** with memory across sessions
- **Function tools** for data persistence
- **Conversational AI** with empathetic design
- **JSON data handling** for wellness tracking
- **Context injection** for personalized greetings
- **Helper functions** for code organization

## 📝 Additional Resources

- [IMPLEMENTATION_SUMMARY.md](backend/IMPLEMENTATION_SUMMARY.md) - Complete technical details
- [CONVERSATION_EXAMPLES.md](backend/CONVERSATION_EXAMPLES.md) - More conversation flows

---

**Built for the AI Voice Agents Challenge - Day 3** by [Murf.ai](https://murf.ai)
