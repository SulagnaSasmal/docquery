#!/usr/bin/env python3
"""
DocQuery CLI — Interactive query interface.

Usage:
    python query_cli.py --collection vaultpay
"""

import argparse
import os

from dotenv import load_dotenv

load_dotenv()

from query.chain import RAGChain
from query.memory import init_memory_db


def main():
    parser = argparse.ArgumentParser(description="DocQuery — Ask questions about your docs")
    parser.add_argument("--collection", default="default", help="ChromaDB collection to query")
    parser.add_argument("--session", default="cli", help="Session ID for conversation memory")
    args = parser.parse_args()

    init_memory_db()

    chain = RAGChain(
        collection_name=args.collection,
        site_name=args.collection,
    )

    print(f"\nDocQuery — Ask questions about '{args.collection}' docs")
    print(f"Type 'quit' to exit, 'clear' to reset conversation.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if question.lower() == "clear":
            from query.memory import clear_history
            clear_history(args.session)
            print("Conversation cleared.\n")
            continue

        result = chain.query(
            question=question,
            session_id=args.session,
        )

        print(f"\nAnswer: {result.answer}\n")

        if result.sources:
            print("Sources:")
            for i, src in enumerate(result.sources, 1):
                print(f"  [{i}] {src['title']} > {src.get('section', '')} (score: {src['score']})")
                print(f"      {src['url']}")
            print()

        confidence_emoji = {"high": "GREEN", "medium": "AMBER", "low": "RED"}
        print(f"Confidence: {result.confidence.upper()} ({result.confidence_score:.2f})\n")


if __name__ == "__main__":
    main()
