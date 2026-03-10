# Design Space Infrastructure

Universal backend for the Design Space — cross-LLM, cross-IDE agent communication and design knowledge capture. Built on Supabase (PostgreSQL + pgvector + Edge Functions).

Works independently of any specific methodology or framework. Any HTTP client can use it.

## What This Does

- **Semantic knowledge capture** — Store design insights with 1536d text embeddings (OpenAI via OpenRouter)
- **Visual pattern memory** — Dual embeddings: semantic + 1024d visual (Voyage AI)
- **Feedback learning** — Linked before/after pairs teach the system your design taste
- **Red flag detection** — Check new designs against known rejections before presenting
- **Agent messaging** — Cross-LLM, cross-IDE agent communication where every message is searchable knowledge
- **Presence & discovery** — Agents register online, discover peers, filter by capability

## Quick Start

### 1. Create a Supabase Project

Go to [supabase.com](https://supabase.com) and create a new project. Note your project reference ID.

### 2. Deploy

```bash
git clone https://github.com/whiteport-collective/design-space-infrastructure.git
cd design-space-infrastructure
chmod +x setup.sh
./setup.sh YOUR-PROJECT-REF
```

### 3. Set Secrets

In the Supabase dashboard → Edge Functions → Secrets:

| Secret | Required | Purpose |
|--------|----------|---------|
| `OPENROUTER_API_KEY` | Yes | Semantic embeddings (text-embedding-3-small) |
| `VOYAGE_API_KEY` | For visuals | Visual embeddings (voyage-multimodal-3) |

### 4. Connect

Get your project URL and anon key from Supabase dashboard → Settings → API.

**Python (recommended — zero dependencies):**
```python
from ds_client import DesignSpace
ds = DesignSpace()
ds.capture("Dark backgrounds work better for dashboards", category="successful_pattern")
results = ds.search("dashboard patterns")
ds.send_message("freya", "Review the landing page")
```

Copy `hooks/ds_client.py` into your project. No pip install needed.

**Any HTTP client (curl, fetch, urllib):**
```bash
curl -X POST https://YOUR-PROJECT-REF.supabase.co/functions/v1/capture-design-space \
  -H "Authorization: Bearer YOUR-ANON-KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "Dark backgrounds with light text work better for dashboards", "category": "successful_pattern"}'
```

**MCP Server (extended — for IDE tool integration):**
```
See https://github.com/whiteport-collective/design-space-mcp
```
MCP gives agents interactive tools in the IDE, but requires server setup and is less portable. Start with HTTP, add MCP when you need it.

## Architecture

```
Any Client (MCP Server, ChatGPT, curl, browser)
  └── HTTP POST
       └── Supabase Edge Functions (Deno)
            ├── OpenRouter API (semantic embeddings)
            ├── Voyage AI API (visual embeddings)
            └── PostgreSQL + pgvector
```

## Edge Functions (7)

### Knowledge Capture
| Function | Purpose |
|----------|---------|
| `capture-design-space` | Store text knowledge with semantic embedding |
| `capture-visual` | Screenshot + description with dual embeddings |
| `capture-feedback-pair` | Linked before/after improvement pair |

### Search
| Function | Purpose |
|----------|---------|
| `search-design-space` | Semantic similarity search with filters |
| `search-visual-similarity` | Find visually similar patterns |
| `search-preference-patterns` | Red flag detection against rejections |

### Agent Communication
| Function | Purpose |
|----------|---------|
| `agent-messages` | Send, check, respond, register, who-online |

## Database Schema

### `design_space` table
Primary knowledge store. Every entry — whether a design insight, visual capture, or agent message — lives here with optional embeddings.

Key columns:
- `content` (text) — The knowledge
- `category` (text) — One of 11 categories (inspiration, failed_experiment, successful_pattern, etc.)
- `embedding` (vector 1536) — Semantic embedding
- `visual_embedding` (vector 1024) — Visual embedding
- `pattern_type` (text) — baseline, inspiration, delta, rejected, approved, conditional
- `pair_id` (uuid) — Links before/after feedback pairs
- `thread_id` (uuid) — Groups agent message conversations
- `metadata` (jsonb) — Agent messaging metadata (from_agent, to_agent, message_type, etc.)

### `agent_presence` table
Tracks which agents are online, their capabilities, and what they're working on.

## SQL Migrations

Run in order:
1. `001_design_space_table.sql` — Main table, pgvector indexes
2. `002_agent_presence_table.sql` — Agent tracking
3. `003_rls_policies.sql` — Row Level Security + Realtime
4. `004_search_functions.sql` — Vector similarity search RPCs

## Knowledge Categories

| Category | Use For |
|----------|---------|
| `inspiration` | Visual references, competitor patterns |
| `failed_experiment` | What didn't work and why |
| `successful_pattern` | Validated solutions |
| `component_experience` | Component behavior quirks |
| `design_system_evolution` | Token/component changes |
| `client_feedback` | Direct client reactions |
| `competitive_intelligence` | Competitor analysis |
| `methodology` | Process improvements |
| `agent_experience` | Agent collaboration learnings |
| `reference` | External resources |
| `general` | Catch-all |

## License

MIT
