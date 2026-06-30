from typing import Dict, List
import os
import re
import numpy as np
import chromadb
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Config
# -----------------------------
CHROMA_COLLECTION = "jira_stories"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Minimum cosine similarity required to consider a past story as "similar"
SIMILARITY_THRESHOLD = 0.3

# OpenAI model (override via env var if you want)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# -----------------------------
# Load embedding model once using Streamlit cache
# Defer import to avoid Python 3.14 threading/shutdown issues
# -----------------------------
@st.cache_resource
def load_embedding_model():
    """Load the embedding model once and cache it across Streamlit reruns."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)

# -----------------------------
# Chroma client (must match your builder)
# -----------------------------
@st.cache_resource
def get_chroma_collection():
    """Get or create Chroma collection, cached across Streamlit reruns."""
    chroma_client = chromadb.PersistentClient(path="./chroma_jira")
    return chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

# Lazy resource accessors; resources are built only when needed.
def get_model():
    return load_embedding_model()

def get_collection():
    return get_chroma_collection()


def call_chatgpt(prompt: str, model_name: str = OPENAI_MODEL) -> str:
    """
    Calls OpenAI Chat Completions and returns response text.
    Requires OPENAI_API_KEY to be set in environment variables (or Streamlit secrets).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")

    client = OpenAI(api_key=api_key)

    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful agile estimation assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content.strip()


def parse_story_points(text: str) -> int | str | None:
    """
    Parse story points from LLM response.
    Returns an integer for valid story points, "NA" if LLM says not enough info, or None if unable to parse.
    """
    text_lower = text.lower()
    tokens = re.findall(r"\bna\b", text_lower)

    # Check if LLM explicitly said not enough information or returned NA
    if "not enough information" in text_lower or "not enough info" in text_lower or tokens:
        return "NA"

    # Fibonacci scale required by your prompt
    allowed = {"1", "2", "3", "5", "8", "13","21","34","55"}
    parts = text.replace("\n", " ").split()
    for p in parts:
        digits = "".join(ch for ch in p if ch.isdigit())
        if digits in allowed:
            return int(digits)

    return None  # Return None instead of defaulting to 3


def estimate_story_points(
    summary: str,
    description: str,
    top_k: int = 5,
    use_llm: bool = True,
) -> Dict:
    """
    Estimate Jira story points using vector similarity + (optional) OpenAI LLM.
    - If use_llm=False -> returns baseline mean from similar stories only.
    - If use_llm=True  -> calls OpenAI using similar stories as context.
    """
    if not summary or not summary.strip():
        raise ValueError("Summary cannot be empty")

    query_text = f"{summary}\n{description}".strip()

    # Embed query
    model = get_model()
    query_embedding = model.encode(query_text).tolist()

    # Query ChromaDB
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "documents", "distances"],
    )

    if not results.get("documents") or not results["documents"][0]:
        raise RuntimeError("Vector DB is empty. Please run build_vector_db.py first.")

    # Parse results
    similar_stories: List[Dict] = []
    story_points: List[float] = []

    for i in range(len(results["documents"][0])):
        metadata = results["metadatas"][0][i] or {}
        dist = results["distances"][0][i]

        raw_sp = metadata.get("story_points", 0)
        sp = float(raw_sp) if raw_sp is not None else 0.0
        story_points.append(sp)

        similar_stories.append(
            {
                "key": metadata.get("key", "UNKNOWN"),
                "summary": metadata.get("summary", ""),
                "story_points": sp,
                "similarity": 1 - dist,  # assuming cosine distance
            }
        )

    baseline_points = int(round(float(np.mean(story_points)))) if story_points else 3

    # Filter similar stories by threshold for LLM context. Chroma will always
    # return nearest neighbors even for unrelated queries; use a threshold to
    # avoid passing noisy context to the LLM. Use strict '>' per requirement
    # (similarity must be above 0.2).
    context_similar = [s for s in similar_stories if s.get("similarity", 0) > SIMILARITY_THRESHOLD]

    # If LLM disabled
    if not use_llm:
        return {
            "story_points": baseline_points,
            "reasoning": f"Estimated using mean of top {len(story_points)} similar stories (no LLM).",
            "similar_stories": context_similar,
            "all_similar_stories": similar_stories,
        }

    # Build prompt using only the sufficiently similar stories as context.
    if context_similar:
        similar_block = "\n".join(
            f"- {s['key']} (SP={int(s['story_points']) if s['story_points'] == int(s['story_points']) else s['story_points']}): {s['summary']}"
            for s in context_similar
        )
        similarity_note = f"Found {len(context_similar)} similar historical stories (similarity > {SIMILARITY_THRESHOLD})."
    else:
        # Do not include low-similarity items as context. We'll still call the LLM
        # but instruct it to treat the story as new and to explicitly state
        # that there were no similarity matches.
        similar_block = "No similar historical stories found above the similarity threshold."
        similarity_note = f"No similar historical stories found (similarity threshold = {SIMILARITY_THRESHOLD}). Estimate using general assessment."

    prompt = f"""
You are an experienced full stack software engineer who has experience in developing .NET applications and using MongoDB, Kafka messaging queues, and microservices. The team follows Agile Scrum. Based on the story information given as input, suggest appropriate story points.

Rules:
- Do not estimate if enough information is not available in the story description, summary and acceptance criteria to make an informed estimate. In that case, respond with "Not enough information to estimate.", and give story points as NA.
- Consider relative complexity, effort, and uncertainty.
- Keep past similar stories in mind while estimating for THIS team.
- If the story is bigger and has story points greater than 8, suggest how to split into multiple stories with max 8 points but dont show the story points for the suggested split. Show it in bullet points.
- Provide justification for the story points.
- Do NOT reveal chain-of-thought or internal deliberation.
- Include effort for unit tests, automation, QA deployment/testing.
- Developer suppose to leverage tools like github copilot for writing unit tests, regression test cases.

New story:
Summary: {summary}
Description:
{description}

Similar past issues (from vector search):
{similar_block}

{('IMPORTANT: No similar stories passed the similarity threshold. BEGIN YOUR RESPONSE with the exact sentence: "There were no similarity matches." Then provide an independent estimate and brief justification. DO NOT reference past stories.' ) if not context_similar else ''}

Return:
- Story Points (choose one: 1,2,3,5,8,13,21,34,55)
- Brief justification
""".strip()

    ai_text = call_chatgpt(prompt)
    llm_points = parse_story_points(ai_text)

    return {
        "story_points": llm_points,
        "reasoning": (
            "Estimated by LLM (OpenAI). "
            + ("Used similar historical stories as context." if context_similar else "No similar historical stories met the similarity threshold; LLM estimated based on the new story alone.")
        ),
        "llm_raw": ai_text,
        "baseline_story_points": baseline_points,
        "similar_stories": context_similar,
        "all_similar_stories": similar_stories,
        "used_similar_stories": context_similar,
        "similarity_threshold": SIMILARITY_THRESHOLD,
    }
