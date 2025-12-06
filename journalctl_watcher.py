#!/usr/bin/env python3
import os
import time
import threading
import queue
import re

last_activity_timestamp = time.time()
timeout_seconds = 600

AUTH_LOG = "/var/log/auth.log"
auth_queue = queue.Queue()
STOP = False

# ------------------------------------------------------------
# Thread 1: Watch auth.log for auth denials and push to queue
# ------------------------------------------------------------
def auth_watcher(logfile, q):
    global last_activity_timestamp
    global STOP
    """Open auth.log using a file descriptor and push parsed auths into queue."""

    print("[Watcher] Starting auth watcher...")

    # Open file descriptor
    fd = os.open(logfile, os.O_RDONLY)
    f = os.fdopen(fd, "r")

    # Seek to end for tail -F behavior
    f.seek(0, os.SEEK_END)

    auth_regex = re.compile(r"pam_unix.*", re.IGNORECASE)

    while not STOP:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            current_time = time.time()
            time_since_last_activity = current_time - last_activity_timestamp
            if time_since_last_activity > timeout_seconds:
                print(f"Inactivity detected! Last activity {time_since_last_activity:.2f} seconds ago.")
                # Perform actions for idle timeout, e.g., terminate the worker thread
                STOP = True
                break
            else:
                continue
        else:
            last_activity_timestamp = time.time()

        if "pam" in line.lower():
            m = auth_regex.search(line)
            if m:
                auth_text = m.group(0)
                parsed = {"raw": line.strip(), "pam": auth_text.strip()}
                q.put(parsed)

    f.close()
    print("[Watcher] Stopped.")


# -----------------------------------------------------------------
# Thread 2: Consume auths from queue
# -----------------------------------------------------------------
def auth_to_te_worker(q, NoneType):
    """Take parsed auths from the queue and run audit2allow."""
    print("[Processor] Starting auth processor...")

    while not STOP:
        try:
            auth = q.get(timeout=0.5)
        except queue.Empty:
            continue

        print(auth)

        q.task_done()

    print("[Processor] Stopped.")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    global STOP

    print("[Main] Starting SELinux auth monitor system.")

    watcher_thread = threading.Thread(
        target=auth_watcher,
        args=(AUTH_LOG, auth_queue),
        daemon=True
    )

    processor_thread = threading.Thread(
        target=auth_to_te_worker,
        args=(auth_queue, None),
        daemon=True
    )

    watcher_thread.start()
    processor_thread.start()

    print("[Main] Running. Press Ctrl+C to stop.")

    try:
        while STOP is not True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Shutdown requested...")
        STOP = True

    watcher_thread.join()
    processor_thread.join()

    print("[Main] Shutdown complete.")


if __name__ == "__main__":
    main()
