# Day 2: BrewBerry Café - Coffee Order Barista Agent ☕

A friendly voice-enabled barista that takes complete coffee orders and saves them to a persistent database.

## 🎯 What This Agent Does

The **BrewBerry Café Barista** is a conversational AI agent that:
- Greets customers warmly
- Collects complete coffee orders through natural conversation
- Asks clarifying questions one at a time
- Saves all orders with timestamps to a JSON file
- Uses a clear male English voice (Terrell)

## 🛠️ Tech Stack

- **Framework**: [LiveKit Agents](https://docs.livekit.io/agents)
- **LLM**: [Groq](https://groq.com) (Llama 3.3 70B Versatile)
- **TTS**: [Murf.ai](https://murf.ai) Falcon (Voice: en-US-terrell)
- **STT**: [Deepgram](https://deepgram.com) Nova-3
- **Frontend**: Next.js + LiveKit Components

## 📋 Order Collection Flow

The barista asks these questions in order:

1. **Drink Type**: "What drink would you like?" (latte, cappuccino, espresso, americano, etc.)
2. **Size**: "What size?" (small, medium, large)
3. **Milk**: "Any milk preference?" (whole, skim, oat, almond, soy)
4. **Extras**: "Would you like any extras?" (sugar, chocolate, caramel, whipped cream)
5. **Name**: "Can I get your name for the order?"

After collecting ALL information, the order is automatically saved.

## 💾 Order Storage

Orders are saved to `backend/orders.json` as an array with timestamps:

```json
[
    {
        "drinkType": "latte",
        "size": "medium",
        "milk": "oat",
        "extras": [],
        "name": "Sarah",
        "timestamp": "2025-11-23 14:30:15"
    },
    {
        "drinkType": "cappuccino",
        "size": "large",
        "milk": "whole",
        "extras": ["sugar", "chocolate"],
        "name": "John",
        "timestamp": "2025-11-23 14:35:42"
    }
]
```

## 🚀 Setup & Run

### Prerequisites
- Python 3.9+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node package manager)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Configure environment (.env.local)
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GROQ_API_KEY=your_groq_api_key
MURF_API_KEY=your_murf_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key

# Start backend
uv run python src/agent.py dev
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Configure environment (.env.local with same LiveKit credentials)
# Start frontend
pnpm dev
```

### 3. Run LiveKit Server (Local)

```bash
livekit-server --dev
```

## 🎤 Testing the Agent

1. Open **http://localhost:3000** (Use `localhost`, NOT IP address!)
2. Click the microphone icon
3. Have a conversation:
   - **You**: "Hi!"
   - **Barista**: "Hi! Welcome to BrewBerry Café ☕. I'm your barista today. What can I get started for you?"
   - **You**: "I'd like a latte"
   - **Barista**: "What size would you prefer?"
   - **You**: "Medium"
   - **Barista**: "Any milk preference?"
   - **You**: "Oat milk please"
   - **Barista**: "Would you like any extras like sugar, chocolate, or caramel?"
   - **You**: "No extras"
   - **Barista**: "Can I get your name for the order?"
   - **You**: "Sarah"
   - **Barista**: "Perfect! I've got your order saved, Sarah..."

4. Check `backend/orders.json` to see your saved order!

## 📂 View Saved Orders

```bash
cd backend
Get-Content orders.json  # Windows PowerShell
# or
cat orders.json  # Linux/Mac
```

## 🎙️ Voice Settings

**Current Voice**: Terrell (Clear, friendly American male)

**To change voice**, edit `backend/src/agent.py` line 112:

```python
tts=murf.TTS(
    voice="en-US-terrell",  # Change this
    style="Conversation",
    ...
)
```

**Other male voice options**:
- `en-US-clint` - Professional, warm
- `en-GB-marcus` - Clear British male
- `en-US-wayne` - Mature, confident

After changing, restart backend with `Ctrl+C` then `uv run python src/agent.py dev`

## 🔧 Troubleshooting

### "Accessing media devices..." error
- You're using an IP address instead of localhost
- Solution: Use **http://localhost:3000**

### Agent not responding
- Check backend terminal for errors
- Ensure all 3 services are running (LiveKit, Backend, Frontend)
- Backend must show "registered worker"

### Orders not saving
- Check if `save_order` tool is being called (look for log: "Order #X saved...")
- Ensure backend was restarted after code changes
- File is `orders.json` (plural), not `order.json`

## 🎯 Key Features Implemented

✅ **Friendly Barista Persona** - Warm greeting and conversational style  
✅ **Order State Management** - Tracks all order details  
✅ **Sequential Questions** - Asks one question at a time  
✅ **Function Tool** - `save_order` automatically called when complete  
✅ **Persistent Storage** - All orders saved to `orders.json`  
✅ **Timestamps** - Each order includes when it was placed  
✅ **Male Voice** - Clear English voice (Terrell)

## 📝 Code Structure

```
backend/
├── src/
│   └── agent.py          # Main agent with barista persona & save_order tool
├── orders.json           # All saved orders (created after first order)
└── .env.local           # API keys configuration

frontend/
├── app/                  # Next.js pages
└── .env.local           # LiveKit credentials
```

## 🎓 What You Learned

- Creating persona-driven voice agents
- Managing conversational state
- Implementing function tools in LiveKit Agents
- Sequential question flow design
- Persistent data storage in JSON
- Customizing TTS voices

---

**Built for the AI Voice Agents Challenge** by [Murf.ai](https://murf.ai)
