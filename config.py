# Configuration for squit
# Edit these values to customize behavior

# How long an app must be inactive before it's considered stale (seconds)
INACTIVITY_THRESHOLD = 6 * 3600  # 6 hours

# How often to sample the frontmost app (short — keeps timestamps accurate)
OBSERVE_INTERVAL = 5  # 5 seconds

# How often to print the snapshot and potentially close inactive apps
CHECK_INTERVAL = 5 * 60  # 5 minutes

# How long to snooze an app after the user clicks "Keep Open" (seconds)
SNOOZE_DURATION = 60 * 60  # 1 hour

# Apps that will never be closed, regardless of inactivity.
# System processes are already excluded by the filter in utils.py.
# Add any user apps here that you always want to keep open.
WHITELIST = [
    "Finder",
    "Dock",
    "Terminal",
    "Safari",
    "Google Chrome",
    "Cursor",
]
