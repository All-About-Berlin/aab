"""Send the daily digest email."""

import logging

from actions.digest import send_digest
from state import STATE_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def main():
    log.info(f"State directory: {STATE_DIR}")
    send_digest()


if __name__ == "__main__":
    main()
