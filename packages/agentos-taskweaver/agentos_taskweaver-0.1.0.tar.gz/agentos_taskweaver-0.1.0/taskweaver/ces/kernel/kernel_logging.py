import logging
import os
import sys

use_console_logging = os.environ.get(
    "TASKWEAVER_USE_CONSOLE_LOGGING",
    "true"
).lower() == "true"

if use_console_logging:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
else:
    log_file_path = os.environ.get(
        "TASKWEAVER_LOGGING_FILE_PATH",
        "ces-runtime.log"
    )
    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

logger = logging.getLogger(__name__)
