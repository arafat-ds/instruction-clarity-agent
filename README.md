# Instruction Clarity Agent

A production-grade hybrid AI service that processes natural language instructions and returns structured JSON output — extracting actions, deadlines, and priorities, or asking targeted clarification questions when the instruction is ambiguous.

Built with a rule-based primary pipeline and a Google Gemini LLM fallback, wrapped in a clean FastAPI service layer.

---

## Key Features

- Extracts actionable tasks, deadlines, and priority from natural language
- Asks targeted clarification questions for vague or ambiguous instructions
- Hybrid architecture: rule-based pipeline first, Gemini LLM as fallback
- Automatic noise removal (filler words, polite phrases)
- Uncertainty detection and handling
- Production-safe LLM integration with retry, schema validation, and fallback
- FastAPI service with request timing, request ID tracking, and structured logging
- Smart dev server launcher that auto-detects busy ports
- Docker-ready

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Server | Uvicorn |
| LLM Provider | Google Gemini (`gemini-2.0-flash`) |
| Gemini SDK | `google-genai` |
| Validation | Pydantic v2 |
| Config | pydantic-settings |
| Language | Python 3.11+ |
| Container | Docker |

---

## Project Structure

```
├── agent/                    # Core logic — DO NOT MODIFY
│   ├── agent.py              # Main controller (hybrid pipeline)
│   ├── clarity.py            # Clarity analysis + uncertainty detection
│   ├── extractor.py          # Action, deadline, priority extraction
│   ├── clarifier.py          # Clarification question generation
│   ├── analyzer.py           # Full-instruction clarity analyzer
│   ├── llm.py                # Gemini LLM fallback module
│   └── models.py             # Shared Pydantic models
│
├── api/                      # FastAPI service layer
│   ├── main.py               # App factory, middleware, exception handlers
│   ├── routes/
│   │   ├── process.py        # POST /api/v1/process
│   │   └── health.py         # GET /health, GET /ready
│   ├── schemas/
│   │   ├── request.py        # InstructionRequest model
│   │   └── response.py       # AgentResponse, ErrorResponse models
│   └── core/
│       ├── config.py         # Environment-based settings
│       └── logging.py        # Structured logging setup
│
├── run.py                    # Smart dev server launcher (auto port detection)
├── main.py                   # Terminal CLI entry point
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd instruction-clarity-agent
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=false
PORT=8000
```

> Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## Running the Server

### Development (recommended)

Uses the smart launcher that auto-detects busy ports:

```bash
python run.py
```

With auto-reload:

```bash
python run.py --reload
```

Custom port:

```bash
python run.py --port 9000 --reload
```

### Production

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -t clarity-agent .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key clarity-agent
```

---

## API Endpoints

### `POST /api/v1/process`

Process a natural language instruction.

**Request body:**
```json
{
  "instruction": "string"
}
```

**Response:**
```json
{
  "status": "complete" | "needs_clarification",
  "actions": ["list of action strings"],
  "deadline": "string or null",
  "priority": "high" | "medium" | "low" | null,
  "clarifications": ["list of questions"]
}
```

**Error responses:**

| HTTP Code | Code | Reason |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Empty or missing instruction |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

---

### `GET /health`

Basic liveness check. Always returns `200` if the service is running.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### `GET /ready`

Readiness check. Verifies that required environment variables are configured.

**Response:**
```json
{
  "ready": true,
  "gemini_configured": true
}
```

---

## Example Requests and Responses

### Clear instruction

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"instruction": "fix the login bug and notify the team by tomorrow"}'
```

```json
{
  "status": "complete",
  "actions": ["fix the login bug", "notify the team"],
  "deadline": "tomorrow",
  "priority": "medium",
  "clarifications": []
}
```

---

### Instruction with noise

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"instruction": "hey bro can you like fix the login issue"}'
```

```json
{
  "status": "complete",
  "actions": ["fix the login issue"],
  "deadline": null,
  "priority": "medium",
  "clarifications": []
}
```

---

### Instruction with deadline and high priority

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"instruction": "deploy the updated service to production asap within 2 days"}'
```

```json
{
  "status": "complete",
  "actions": ["deploy the updated service to production asap"],
  "deadline": "2 days",
  "priority": "high",
  "clarifications": []
}
```

---

### Partially ambiguous instruction

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"instruction": "prepare report and send it to the client"}'
```

```json
{
  "status": "complete",
  "actions": ["prepare report", "send it to the client"],
  "deadline": null,
  "priority": "medium",
  "clarifications": ["What does 'it' refer to?"]
}
```

---

### Fully unclear instruction (LLM fallback triggered)

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"instruction": "fix it somehow"}'
```

```json
{
  "status": "needs_clarification",
  "actions": [],
  "deadline": null,
  "priority": null,
  "clarifications": [
    "What specifically needs to be fixed?",
    "What does 'it' refer to?"
  ]
}
```

---

### Empty instruction (validation error)

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"instruction": ""}'
```

```json
{
  "error": {
    "message": "Value error, instruction must not be empty",
    "code": "VALIDATION_ERROR"
  }
}
```

---

## Swagger UI

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

From Swagger UI you can:
- Browse all endpoints with descriptions
- Send test requests directly from the browser
- Inspect request/response schemas
- View example payloads

ReDoc (alternative docs):
```
http://localhost:8000/redoc
```

---

## How the Pipeline Works

```
Raw instruction
      ↓
1. Noise removal        strips "hey", "bro", "can you", "please", etc.
      ↓
2. Uncertainty removal  strips "maybe", "if possible", "possibly", etc.
      ↓
3. Action extraction    splits into actions, detects deadline + priority
      ↓
4. Action validation    checks each action for vague pronouns, missing verbs
      ↓
5. Decision
      ├── All actions pronoun-only?  → needs_clarification
      ├── Valid actions exist?       → complete
      └── No actions at all?        → needs_clarification
      ↓
6. Hybrid check
      ├── No actions OR ≥2 clarifications? → Gemini LLM fallback
      └── Rule-based result sufficient?    → return rule-based result
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `DEBUG` | No | `false` | Enable debug logging |
| `PORT` | No | `8000` | Preferred server port |

---

## Response Headers

Every response includes:

| Header | Example | Description |
|---|---|---|
| `X-Request-ID` | `a1b2c3d4` | Unique ID for request tracing |
| `X-Response-Time` | `42.5ms` | Total processing time |

---

## Design Principles

- **Hybrid architecture** — rule-based pipeline runs first; LLM is a fallback, not the default
- **Stateless** — every request is fully independent with no shared state
- **Non-destructive validation** — actions are never dropped due to ambiguity
- **Production-safe LLM** — retry (×2), schema validation, safe defaults, and fallback on every call
- **Clean separation** — `agent/` (core logic) and `api/` (service layer) are fully decoupled
- **No external NLP libraries** — rule-based layer uses only Python stdlib and regex
