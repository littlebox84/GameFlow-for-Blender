"""Shared runtime state for GameFlow."""
import time

running = False
stop_requested = False
restart_after_load = False
last_heartbeat = 0.0


def mark_alive():
    global running, last_heartbeat
    running = True
    last_heartbeat = time.monotonic()


def clear_running():
    global running, stop_requested, last_heartbeat
    running = False
    stop_requested = False
    last_heartbeat = 0.0


def is_alive(timeout=1.5):
    if not running or last_heartbeat <= 0.0:
        return False
    return (time.monotonic() - last_heartbeat) <= timeout
