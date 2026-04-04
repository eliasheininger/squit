import time


class AppTracker:
    """Tracks when each app was last seen as the frontmost (active) window.

    last_seen maps app_name -> unix timestamp of last activity.
    Apps are only tracked after they have been seen at least once.
    """

    def __init__(self):
        self.last_seen: dict[str, float] = {}
        self.started_at: float = time.time()  # when tracking began

    def update(self, app_name: str) -> None:
        """Mark an app as active right now."""
        self.last_seen[app_name] = time.time()

    def seed(self, app_names: list[str]) -> None:
        """Register apps as 'seen now' only if not already tracked.

        Used to initialize the tracker with all currently running apps
        so they start with a fresh timestamp rather than being immediately
        flagged as inactive on first run.
        """
        now = time.time()
        for name in app_names:
            if name not in self.last_seen:
                self.last_seen[name] = now

    def get_inactive(self, threshold: float) -> list[tuple[str, float]]:
        """Return apps that haven't been active for longer than threshold seconds.

        Returns a list of (app_name, inactive_duration_seconds) tuples,
        sorted by longest-inactive first.
        """
        now = time.time()
        inactive = [
            (name, now - last)
            for name, last in self.last_seen.items()
            if (now - last) > threshold
        ]
        return sorted(inactive, key=lambda x: x[1], reverse=True)
