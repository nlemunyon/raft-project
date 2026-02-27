# Raft AI Agent — LangGraph Pipeline

An AI agent that fetches raw unstructured order data from an API, uses an LLM to parse it into structured JSON, validates against hallucinations, and returns filtered results enriched with ML predictions. Built with LangGraph, OpenRouter, and a polished React UI.

## Architecture

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────┐
│                  LangGraph Pipeline                   │
│                                                       │
│  FETCH ──► PARSE ──► VALIDATE ──► FILTER + RESPOND   │
│    │         │          │              │               │
│  Dummy     LLM w/     Cross-ref    Python filters     │
│  API       structured  parsed vs   + ML predictions   │
│  (:5001)   output      raw text         │              │
│                                         ▼              │
│                                   JSON Response        │
└──────────────────────────────────────────────────────┘
    │
    ▼
React Frontend (Chat UI + Results + ML Stats)
```

**Flow:** `User Query → Fetch (API) → Parse (LLM) → Validate → Filter + Respond`

## Quick Start

```bash
# 1. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Build the frontend
cd frontend
npm install
npm run build
cd ..

# 3. Set your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-..." > .env

# 4. Run everything (one command)
python main.py
```

Open http://localhost:8000 in your browser.



## Edge Cases

| Scenario | Behavior |
|----------|----------|
| API down | Retries 3 times with 1s delay, then returns error |
| LLM fails to parse | Returns error with details |
| Hallucinated order | Validation removes it, logs warning |
| Large payload (>6000 tokens) | Chunks orders into groups, parses separately, merges |

## ML Predictions

A logistic regression model trained on 5,000 synthetic orders (`data/training_data.csv`) predicts whether each customer is likely to reorder. Features:

| Feature | Signal |
|---------|--------|
| `num_items` | More items → more engaged buyer |
| `has_electronics` | Electronics buyers return for accessories |
| `state_reorder_score` | Regional reorder pattern (OH, TX, CA, IL, FL highest) |
| `total_normalized` | Moderate spend correlates with repeat purchases |
| `electronics_x_spend` | Interaction: electronics + high spend compounds reorder likelihood |
| `avg_item_price` | Average price per item (normalized) |

The model trains at startup in <1 second and achieves ~87% accuracy on synthetic data.

To regenerate training data: `python generate_data.py`

## Example Queries

- "Show me all orders from Ohio"
- "Orders over $500"
- "Find orders with laptops"
- "Show me everything"
- "Orders under $100"
- "Who ordered electronics?"

## Project Structure

```
raft-project/
├── main.py                    # Entry point: starts dummy API + FastAPI
├── dummy_customer_api.py      # Flask API (port 5001) - 20 raw text orders
├── agent.py                   # LangGraph StateGraph pipeline
├── models.py                  # Pydantic schemas + logistic regression
├── generate_data.py           # Generates data/training_data.csv
├── data/training_data.csv     # 5K synthetic orders (committed)
├── server.py                  # FastAPI routes + serves React build
├── requirements.txt
├── .env                       # OPENROUTER_API_KEY
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx            # Two-panel layout
        ├── index.css          # Dark minimal design system
        ├── utils/motion.js    # Framer Motion variants
        ├── components/
        │   ├── ChatPanel.jsx  # Message list + input + suggestions
        │   ├── Message.jsx    # User/agent bubbles with result tables
        │   ├── ResultsPanel.jsx  # Structured results + raw JSON
        │   └── StatsPanel.jsx    # ML model stats + feature importance
        └── services/api.js    # API client

6 Python files, 4 React components.
```

## Tech Stack

- **Backend**: Python, FastAPI, LangGraph, LangChain, OpenRouter (gpt-oss-120b:exacto), scikit-learn
- **Frontend**: React 18, Vite, Tailwind CSS v4, Framer Motion, Lucide icons
- **Design**: Dark minimal aesthetic (#0a0a0a background, #3b82f6 blue accent, Inter + JetBrains Mono)
