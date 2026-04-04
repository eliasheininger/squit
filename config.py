# Configuration for focus-cleaner
# Edit these values to customize behavior

# How long an app must be inactive before it's considered stale (seconds)
INACTIVITY_THRESHOLD = 6 * 3600  # 6 hours

# How often to sample the frontmost app (short — keeps timestamps accurate)
OBSERVE_INTERVAL = 5  # 5 seconds

# How often to print the snapshot and potentially close inactive apps
CHECK_INTERVAL = 5 * 60  # 5 minutes

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
