# log_util.py
# Lightweight logger for KM-Waechter. Modernized 2024.

import time

LOG_LINES: list[str] = []     # module-level buffer; cleared after each flush


def log(message: str) -> None:
    """Timestamp and buffer a message, and print it immediately."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Append all buffered lines to the log file, then clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
