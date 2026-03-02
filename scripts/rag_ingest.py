"""CLI script to ingest the repository into the RAG index.

Usage:
    uv run python scripts/rag_ingest.py [--root .] [--ref worktree] [--db rag/store/rag.db]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import RAG_DB_PATH
from rag.ingest.embed import ZeroVectorProvider
from rag.ingest.index import ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest repository into the RAG index")
    parser.add_argument("--root", default=".", help="Repository root directory (default: .)")
    parser.add_argument("--ref", default="worktree", help="Repo reference label (default: worktree)")
    parser.add_argument("--db", default=str(RAG_DB_PATH), help=f"SQLite database path (default: {RAG_DB_PATH})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Ensure the database directory exists
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    provider = ZeroVectorProvider()
    result = ingest(
        root_dir=args.root,
        repo_ref=args.ref,
        embedding_provider=provider,
        db_path=db_path,
    )

    print(f"\nIngest complete:")
    print(f"  Files processed: {result.files_processed}")
    print(f"  Files skipped:   {result.files_skipped}")
    print(f"  Chunks created:  {result.chunks_created}")


if __name__ == "__main__":
    main()
