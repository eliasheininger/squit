#!/usr/bin/env python3
"""focus-cleaner: close apps that haven't been active for too long.

Usage:
    python3 main.py            # dry-run (safe, just logs what would be closed)
    python3 main.py --close    # actually quit inactive apps
    python3 main.py --threshold 3600  # override inactivity threshold (seconds)
    python3 main.py --interval 60     # override check interval (seconds)
"""

import argparse
import time
from datetime import datetime

import config
from tracker import AppTracker
from utils import close_app, format_duration, get_all_running_apps, get_frontmost_app


def log(msg: str) -> None:
    """Print a timestamped log line."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def print_snapshot(tracker: AppTracker, threshold: float) -> None:
    """Print a table of all tracked apps and their current inactivity status."""
    now = time.time()
    if not tracker.last_seen:
        print("  (no apps tracked yet)")
        return

    tracking_age = format_duration(now - tracker.started_at)
    print(f"  Tracking for: {tracking_age}  |  threshold: {format_duration(threshold)}")
    print()

    # Sort by inactive duration, longest first
    rows = sorted(tracker.last_seen.items(), key=lambda x: now - x[1], reverse=True)

    print(f"  {'APP':<35} {'INACTIVE':<12} {'STATUS'}")
    print(f"  {'-'*35} {'-'*12} {'-'*20}")
    for app_name, last_ts in rows:
        inactive_secs = now - last_ts
        duration_str = format_duration(inactive_secs)
        if app_name in config.WHITELIST:
            status = "whitelisted"
        elif inactive_secs > threshold:
            status = "*** WOULD CLOSE ***"
        else:
            status = "ok"
        print(f"  {app_name:<35} {duration_str:<12} {status}")
    print()


def run_check(tracker: AppTracker, dry_run: bool, threshold: float) -> None:
    """Full check: print snapshot and close inactive apps if enabled.

    Frontmost app sampling happens in the main loop — this only handles
    the snapshot display and close logic.
    """
    # Print snapshot of all tracked apps
    log(f"Tracked apps ({len(tracker.last_seen)}):")
    print_snapshot(tracker, threshold)

    # 4. Find apps that have been inactive longer than the threshold
    inactive = tracker.get_inactive(threshold)
    flagged = [(n, d) for n, d in inactive if n not in config.WHITELIST]
    if not flagged:
        log("No apps to close.")
        return

    for app_name, duration in flagged:
        duration_str = format_duration(duration)

        if dry_run:
            log(f"[DRY RUN] Would close '{app_name}' (inactive for {duration_str})")
        else:
            log(f"Closing '{app_name}' (inactive for {duration_str})...")
            success = close_app(app_name)
            if success:
                log(f"  -> Quit signal sent to '{app_name}'")
                # Remove from tracker so it doesn't get targeted again immediately
                tracker.last_seen.pop(app_name, None)
            else:
                log(f"  -> Failed to quit '{app_name}' (app may not support AppleScript quit)")


def main():
    parser = argparse.ArgumentParser(
        description="Close apps that haven't been active for a while."
    )
    parser.add_argument(
        "--close",
        action="store_true",
        help="Actually close inactive apps (default is dry-run, logs only)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=config.INACTIVITY_THRESHOLD,
        help=f"Inactivity threshold in seconds (default: {config.INACTIVITY_THRESHOLD})",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=config.CHECK_INTERVAL,
        help=f"Check interval in seconds (default: {config.CHECK_INTERVAL})",
    )
    args = parser.parse_args()

    dry_run = not args.close
    threshold = args.threshold
    interval = args.interval

    mode = "DRY RUN" if dry_run else "LIVE (will close apps)"
    print(f"\nfocus-cleaner starting in {mode} mode")
    print(f"  Inactivity threshold : {format_duration(threshold)}")
    print(f"  Check interval       : {format_duration(interval)}")
    print(f"  Whitelist            : {config.WHITELIST or 'none'}")
    print(f"  Press Ctrl+C to stop\n")

    tracker = AppTracker()

    # Seed all currently running apps with 'now' so nothing gets flagged
    # immediately just because it hasn't been seen as frontmost yet
    running = get_all_running_apps()
    tracker.seed(running)
    log(f"Initialized tracker with {len(running)} running apps")
    log(f"Observing every {config.OBSERVE_INTERVAL}s, full check every {format_duration(interval)}")

    last_check = time.time()

    while True:
        # Observe the frontmost app frequently so timestamps stay accurate
        time.sleep(config.OBSERVE_INTERVAL)
        frontmost = get_frontmost_app()
        if frontmost:
            tracker.update(frontmost)

        # Also seed any newly opened apps
        tracker.seed(get_all_running_apps())

        # Full snapshot + close check only on the longer interval
        if time.time() - last_check >= interval:
            print()
            run_check(tracker, dry_run=dry_run, threshold=threshold)
            log(f"Next check in {format_duration(interval)}...")
            last_check = time.time()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nfocus-cleaner stopped.")
