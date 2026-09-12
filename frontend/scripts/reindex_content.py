#!/usr/bin/env python3

from pathlib import Path
import json
import logging
import meilisearch
import os
import sys


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    index_file = Path(os.environ.get("URSUS_OUTPUT_DIR", "output")) / "search-index.json"
    if not index_file.exists():
        logger.error("search-index.json not found at %s", index_file)
        return 0

    documents = json.loads(index_file.read_text())

    try:
        client = meilisearch.Client(
            "http://search:7700",
            os.environ["MEILI_MASTER_KEY"],
            timeout=5,
        )
        index = client.index("content")
        index.delete_all_documents()
        index.add_documents(documents)
    except Exception:
        logger.exception("Failed to push content documents to Meilisearch")
        return 0

    logger.info("Pushed %d content documents to Meilisearch", len(documents))
    return 0


if __name__ == "__main__":
    sys.exit(main())
