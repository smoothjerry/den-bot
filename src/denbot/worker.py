"""Root entrypoint for the Temporal worker process.

Runs as its own container/process — separate from the Discord bot. Both share
the same Docker image and codebase; only the entrypoint differs.
"""

import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from denbot.temporal.worker import main  # noqa: E402  (import after load_dotenv)

if __name__ == "__main__":
    main()
