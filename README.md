# python_multithreading
Python Multithreading Repo

What is journalctl_watcher.py?

This script demonstrates how to run two threads with a queue used like an input/output queue.

 ┌───────────────────────────────────────────────┐
 │              Main Program (.py)               │
 └───────────────────────────────────────────────┘
                 │
                 │   (1) main allocates
                 ▼
        ┌───────────────────────┐
        │      auth_queue        │
        │  (queue.Queue object) │
        └───────────────────────┘
                 │
                 │   (1) main spawns watcher thread
                 ▼
        ┌───────────────────────┐
        │     auth_watcher       │
        │  - tails auth.log     │
        │  - parse line item    │
        └───────────────────────┘
                 │
                 │   (2) watcher thread puts processed results onto
                 ▼
        ┌───────────────────────┐
        │     auth_queue         │
        │  (queue.Queue object) │
        └───────────────────────┘
                 │
                 │   (1) main spawns processing thread
                 ▼
        ┌───────────────────────┐
        │   auth_to_te_worker    │
        │  - processor_thread   │
        │  - gets queue item    │
        │  - (3) prints item    │
        └───────────────────────┘
                 │
                 │   (4) waits for ctrl+c shutdown request
                 ▼
      ┌───────────────────────────────────────────┐
      │              Shutdown Output              │
      └───────────────────────────────────────────┘

How to run journalctl_watcher.py:

1. Run it: ./journalctl_watcher.py
2. Open a new terminal tab
3. Run: sudo su
4. Go back to terminal tab running python script
5. Inspect the logs.
