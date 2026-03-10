#!/usr/bin/env python3
"""
SessionStart hook — Load recent agent experiences from Design Space.
Gives the agent instant context about what happened in previous sessions.
"""

import json
import sys
import os
import urllib.request

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SUPABASE_URL = os.environ.get("DESIGN_SPACE_URL", "https://uztngidbpduyodrabokm.supabase.co")
SUPABASE_KEY = os.environ.get("DESIGN_SPACE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6dG5naWRicGR1eW9kcmFib2ttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyNjI0MzksImV4cCI6MjA1NjgzODQzOX0.L1XMXA3EBFlW-8ZPFaJO3suMOakJPBGKCyMpy6A3UjE")


def load_context():
    """Fetch recent experiences from Design Space to prime the agent."""

    # Search for recent agent experiences
    payload = json.dumps({
        "query": "recent agent session activity",
        "category": "agent_experience",
        "limit": 10,
        "threshold": 0.3
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{SUPABASE_URL}/functions/v1/search-design-space",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
    except Exception:
        return  # Silent fail — agent works fine without context

    results = data.get("results", [])
    if not results:
        return

    # Also check for unread messages
    msg_payload = json.dumps({
        "action": "check",
        "agent_id": os.environ.get("AGENT_ID", "claude-code"),
        "include_broadcast": True,
        "limit": 5
    }).encode("utf-8")

    msg_req = urllib.request.Request(
        f"{SUPABASE_URL}/functions/v1/agent-messages",
        data=msg_payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },
        method="POST"
    )

    messages = []
    try:
        with urllib.request.urlopen(msg_req, timeout=3) as resp:
            msg_data = json.loads(resp.read())
            messages = msg_data.get("messages", [])
    except Exception:
        pass

    # Output context for the agent
    print("\n--- DESIGN SPACE CONTEXT (auto-loaded) ---")
    print("Recent sessions:")
    for r in results[:7]:
        content = r.get("content", "")[:150]
        print(f"  - {content}")

    if messages:
        print(f"\nUnread messages ({len(messages)}):")
        for msg in messages:
            meta = msg.get("metadata", {})
            from_agent = meta.get("from_agent", "unknown")
            print(f"  [{from_agent}]: {msg.get('content', '')[:120]}")

    print("---\n")


if __name__ == "__main__":
    load_context()
