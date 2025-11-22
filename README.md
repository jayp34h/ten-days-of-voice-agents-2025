# Day 1: Personal Voice Agent (Nova)

Welcome to **Day 1** of the AI Voice Agents Challenge! Today's task is to build your own personal voice assistant named **Nova**.

## Tech Stack

- **Framework**: [LiveKit Agents](https://docs.livekit.io/agents)
- **LLM**: [Groq](https://groq.com) (Llama 3.3 70B Versatile) - *Fast inference!*
- **TTS**: [Murf.ai](https://murf.ai) (Falcon) - *High-quality voice*
- **STT**: [Deepgram](https://deepgram.com) (Nova-3) - *Accurate transcription*
- **Frontend**: Next.js + LiveKit Components

## Prerequisites

- Python 3.9+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node package manager)
- LiveKit Server (Local or Cloud)

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install dependencies (including livekit-plugins-openai for Groq)
uv sync

# Configure environment
cp .env.example .env.local
```

Edit `.env.local` and add your API keys:
```bash
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
GROQ_API_KEY=...      # Required for Llama 3.3
MURF_API_KEY=...      # Required for Falcon TTS
DEEPGRAM_API_KEY=...  # Required for STT
```

**Start the Backend:**
```bash
uv run python src/agent.py dev
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Configure environment
cp .env.example .env.local
```

Edit `.env.local` with your LiveKit credentials (same as backend).

**Start the Frontend:**
```bash
pnpm dev
```

### 3. Run LiveKit Server (Local Dev)

If you are not using LiveKit Cloud, run the local server:
```bash
livekit-server --dev
```

## Usage

1.  Ensure all 3 services are running (LiveKit Server, Backend, Frontend).
2.  Open your browser to **[http://localhost:3000](http://localhost:3000)**.
    > **IMPORTANT:** Do not use the network IP (e.g., `192.168.x.x`). Browsers block microphone access on non-secure (non-HTTPS) IP addresses. Always use `localhost`.
3.  Click the microphone icon and say "Hello Nova!"

## Troubleshooting

-   **"Accessing media devices is available only in secure contexts"**: You are likely accessing the app via an IP address (e.g., `192.168.1.111:3000`). Switch to `http://localhost:3000`.
-   **Agent not responding**: Check the backend terminal. If you see `ImportError: cannot import name 'openai'`, run `uv sync` in the `backend` directory to install the missing dependency.
-   **Connection issues**: Ensure `LIVEKIT_URL` matches between backend, frontend, and your running server (usually `ws://127.0.0.1:7880` for local).

## License

MIT
