"""CLI script to query the RAG index.

Usage:
    uv run python scripts/rag_query.py "query text" [--top-k 12] [--db rag/store/rag.db]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import DEFAULT_TOP_K, RAG_DB_PATH
from rag.retrieve.query import rag_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the RAG index")
    parser.add_argument("query", help="Search query text")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help=f"Number of results (default: {DEFAULT_TOP_K})")
    parser.add_argument("--db", default=str(RAG_DB_PATH), help=f"SQLite database path (default: {RAG_DB_PATH})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}. Run rag_ingest.py first.", file=sys.stderr)
        sys.exit(1)

    # Text-based search (no embedding provider)
    hits = rag_query(args.query, top_k=args.top_k, db_path=db_path)

    if not hits:
        print("No results found.")
        return

    print(f"\nTop {len(hits)} results for: {args.query!r}\n")
    for i, hit in enumerate(hits, start=1):
        print(f"  {i}. {hit.path}:{hit.start_line}-{hit.end_line}  [{hit.kind}]  score={hit.score:.3f}")
        # Show first 120 chars of the chunk text
        preview = hit.text[:120].replace("\n", " ").strip()
        print(f"     {preview}...")
        print()


if __name__ == "__main__":
    main()
