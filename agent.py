"""
LangGraph StateGraph pipeline that fetches raw unstructured order data from a
dummy API, uses an LLM to parse it into structured JSON, validates against
hallucinations, and applies user-requested filters.

"""

import os
import asyncio
import logging
import time
from typing import Optional, TypedDict

import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from models import ParsedOrder, ParsedOrders, predictor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

DUMMY_API_URL = "http://localhost:5001"

# --- LLM Configuration ---
llm = ChatOpenAI(
    model="openai/gpt-oss-120b:exacto",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.0,
    max_tokens=8192,
)

structured_llm = llm.with_structured_output(ParsedOrders)


# --- State ---

class AgentState(TypedDict):
    query: str
    raw_text: str
    raw_orders_list: list[str]
    parsed_orders: list[dict]
    filter_criteria: dict
    validation_warnings: list[str]
    error: Optional[str]
    response: Optional[dict]


# --- Nodes ---

async def fetch_data(state: AgentState) -> dict:
    """Fetch raw order data from the dummy customer API."""
    logger.info("fetch_data: fetching from %s", DUMMY_API_URL)

    last_error = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{DUMMY_API_URL}/api/orders")
                resp.raise_for_status()
                data = resp.json()

                # Resilient key lookup -- handle unpredictable API schema changes
                raw_orders_list = data.get("raw_orders") or data.get("orders") or data.get("data", {}).get("raw_orders")
                if raw_orders_list is None:
                    for v in data.values():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                            raw_orders_list = v
                            logger.warning("fetch_data: used fallback key detection for API response")
                            break
                if not raw_orders_list:
                    return {"error": "API response format unrecognized -- no order list found"}

                raw_text = "\n".join(raw_orders_list)
                logger.info("fetch_data: fetched %d raw orders (%d chars)", len(raw_orders_list), len(raw_text))
                return {
                    "raw_text": raw_text,
                    "raw_orders_list": raw_orders_list,
                    "error": None,
                }
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
            last_error = e
            if attempt < 2:
                logger.warning("fetch_data: attempt %d failed (%s), retrying in 1s...", attempt + 1, e)
                await asyncio.sleep(1)

    error_msg = f"Failed to fetch data after 3 attempts: {last_error}"
    logger.error("fetch_data: %s", error_msg)
    return {"error": error_msg}


async def parse_data(state: AgentState) -> dict:
    """Use LLM with structured output to parse raw text + extract filters."""
    if state.get("error"):
        return {}

    raw_text = state["raw_text"]
    query = state["query"]

    orders_list = state.get("raw_orders_list", [])
    estimated_tokens = len(raw_text) // 4
    logger.info("parse_data: ~%d tokens of raw text, %d orders", estimated_tokens, len(orders_list))

    if estimated_tokens > 4000 and orders_list:
        MAX_TOKENS_PER_CHUNK = 4000
        avg_tokens_per_order = estimated_tokens / len(orders_list)
        orders_per_chunk = max(1, int(MAX_TOKENS_PER_CHUNK / avg_tokens_per_order))
        chunks = [orders_list[i:i + orders_per_chunk] for i in range(0, len(orders_list), orders_per_chunk)]
        logger.info("parse_data: chunking %d orders into %d groups (~%d orders each)",
                    len(orders_list), len(chunks), orders_per_chunk)
        all_orders = []
        filter_criteria = {}

        for i, chunk in enumerate(chunks):
            chunk_text = "\n".join(chunk)
            prompt = _build_parse_prompt(query, chunk_text, is_chunk=True, chunk_num=i + 1, total_chunks=len(chunks))
            try:
                result: ParsedOrders = await asyncio.wait_for(
                    structured_llm.ainvoke(prompt),
                    timeout=120.0,
                )
                all_orders.extend([o.model_dump() for o in result.orders])
                if i == 0:
                    filter_criteria = _extract_filter_dict(result)
            except asyncio.TimeoutError:
                logger.error("parse_data: chunk %d timed out after 60s", i + 1)
            except Exception as e:
                logger.error("parse_data: chunk %d failed: %s", i + 1, e)

        if not all_orders:
            return {"error": "LLM failed to parse any orders from chunked text"}

        logger.info("parse_data: parsed %d orders across %d chunks", len(all_orders), len(chunks))
        return {
            "parsed_orders": all_orders,
            "filter_criteria": filter_criteria,
            "error": None,
        }

    # Single-pass parse
    prompt = _build_parse_prompt(query, raw_text)
    try:
        result: ParsedOrders = await asyncio.wait_for(
            structured_llm.ainvoke(prompt),
            timeout=120.0,
        )
        parsed = [o.model_dump() for o in result.orders]
        filter_criteria = _extract_filter_dict(result)
        logger.info("parse_data: parsed %d orders, filters=%s", len(parsed), filter_criteria)
        return {
            "parsed_orders": parsed,
            "filter_criteria": filter_criteria,
            "error": None,
        }
    except asyncio.TimeoutError:
        logger.error("parse_data: LLM call timed out after 60s")
        return {"error": "LLM parsing timed out after 60s"}
    except Exception as e:
        logger.error("parse_data: LLM parsing failed: %s", e)
        return {"error": f"LLM parsing failed: {str(e)}"}


async def validate(state: AgentState) -> dict:
    """Cross-reference parsed orders against raw text to catch hallucinations."""
    if state.get("error"):
        return {}

    raw_text = state["raw_text"].lower()
    parsed = state["parsed_orders"]
    warnings = []
    validated = []

    logger.info("validate: checking %d parsed orders against raw text", len(parsed))

    for order in parsed:
        order_id = str(order["order_id"])
        buyer = order["buyer"]
        total = order["total"]

        # Extract numeric portion of order_id for flexible matching
        numeric_id = "".join(c for c in order_id if c.isdigit())

        checks = {
            "order_id": order_id.lower() in raw_text or numeric_id in raw_text,
            "buyer": buyer.lower() in raw_text,
            "total": str(total) in raw_text or f"${total}" in raw_text,
        }

        if all(checks.values()):
            validated.append(order)
        else:
            failed = [k for k, v in checks.items() if not v]
            warning = f"Order {order_id}: removed (could not verify {', '.join(failed)} in raw text)"
            logger.warning("validate: %s", warning)
            warnings.append(warning)

    logger.info("validate: %d/%d orders passed", len(validated), len(parsed))

    return {
        "parsed_orders": validated,
        "validation_warnings": warnings,
    }


async def filter_and_respond(state: AgentState) -> dict:
    """Apply filters, enrich with ML predictions, and assemble final response."""

    if state.get("error"):
        return {
            "response": {
                "success": False,
                "error": state["error"],
                "orders": [],
                "total_parsed": 0,
                "total_matched": 0,
                "filters_applied": {},
                "validation_warnings": state.get("validation_warnings", []),
                "ml_predictions": [],
            }
        }

    orders = state["parsed_orders"]
    filters = state.get("filter_criteria", {})

    filtered = list(orders)

    if filters.get("state"):
        target = filters["state"].upper()
        filtered = [o for o in filtered if o["state"].upper() == target]

    if filters.get("min_total") is not None:
        filtered = [o for o in filtered if o["total"] >= filters["min_total"]]

    if filters.get("max_total") is not None:
        filtered = [o for o in filtered if o["total"] <= filters["max_total"]]

    if filters.get("item_keyword"):
        raw_keyword = filters["item_keyword"].lower()
        keywords = [k.strip() for k in raw_keyword.replace(",", " or ").split(" or ") if k.strip()]
        filtered = [
            o for o in filtered
            if any(kw in item.lower() for item in o["items"] for kw in keywords)
        ]

    active_filters = {k: v for k, v in filters.items() if v is not None}
    logger.info("filter_and_respond: %d/%d orders match filters %s", len(filtered), len(orders), active_filters)

    ml_predictions = []
    for order in filtered:
        try:
            parsed_order = ParsedOrder(**order)
            prediction = predictor.predict_order(parsed_order)
            ml_predictions.append({
                "order_id": order["order_id"],
                **prediction,
            })
        except Exception as e:
            logger.warning("filter_and_respond: ML prediction failed for %s: %s", order.get("order_id"), e)

    return {
        "response": {
            "success": True,
            "orders": filtered,
            "total_parsed": len(orders),
            "total_matched": len(filtered),
            "filters_applied": active_filters,
            "validation_warnings": state.get("validation_warnings", []),
            "ml_predictions": ml_predictions,
        },
    }


# --- Build Graph ---

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("fetch_data", fetch_data)
    graph.add_node("parse_data", parse_data)
    graph.add_node("validate", validate)
    graph.add_node("filter_and_respond", filter_and_respond)

    graph.set_entry_point("fetch_data")
    graph.add_edge("fetch_data", "parse_data")
    graph.add_edge("parse_data", "validate")
    graph.add_edge("validate", "filter_and_respond")
    graph.add_edge("filter_and_respond", END)

    return graph.compile()


compiled_graph = build_graph()


# --- Helpers ---

def _build_parse_prompt(query: str, raw_text: str, is_chunk: bool = False,
                        chunk_num: int = 0, total_chunks: int = 0) -> str:
    chunk_note = ""
    if is_chunk:
        chunk_note = f"\n\nNote: This is chunk {chunk_num} of {total_chunks}. Parse all orders in this chunk."

    return f"""You are a data extraction assistant. Given raw order text and a user query, do two things:

1. Parse ALL orders from the raw text into structured data.
2. Extract any filter criteria from the user's query.

User query: "{query}"

Raw order data:
{raw_text}
{chunk_note}

Instructions:
- Extract every order completely and accurately
- For state, convert full names to 2-letter codes (e.g., "Ohio" -> "OH")
- For total, extract the numeric value without the $ sign
- For items, extract as a list of strings
- Do NOT invent orders that aren't in the text
- For filters, identify state, min/max total, and item keywords from the query"""


def _extract_filter_dict(result: ParsedOrders) -> dict:
    return {
        "state": result.filter_state,
        "min_total": result.filter_min_total,
        "max_total": result.filter_max_total,
        "item_keyword": result.filter_item_keyword,
    }


# --- Public Interface ---

async def run_agent(query: str) -> dict:
    """Execute the LangGraph pipeline with a natural language query."""
    logger.info("run_agent: query=%r", query)
    start = time.time()

    initial_state: AgentState = {
        "query": query,
        "raw_text": "",
        "raw_orders_list": [],
        "parsed_orders": [],
        "filter_criteria": {},
        "validation_warnings": [],
        "error": None,
        "response": None,
    }

    result = await compiled_graph.ainvoke(initial_state)

    elapsed = time.time() - start
    logger.info("run_agent: completed in %.2fs", elapsed)

    return result["response"]


if __name__ == "__main__":
    import subprocess
    import sys
    from pathlib import Path

    # Start dummy API so the pipeline has something to fetch from
    dummy_proc = subprocess.Popen(
        [sys.executable, "dummy_customer_api.py"],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(1)

    try:
        query = sys.argv[1] if len(sys.argv) > 1 else "Show me all orders"
        print(f"\nQuery: {query}\n")
        import json
        result = asyncio.run(run_agent(query))
        print(json.dumps(result, indent=2))
    finally:
        dummy_proc.terminate()
        dummy_proc.wait(timeout=5)