import subprocess


def get_frontmost_app() -> str | None:
    """Return the name of the currently active (frontmost) application.

    Uses AppleScript via osascript to query System Events.
    Returns None if the query fails (e.g. permissions not granted).
    """
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_all_running_apps() -> list[str]:
    """Return names of user-facing running applications only.

    Uses AppleScript with 'background only is false' to restrict to apps
    that have a Dock presence / visible UI — excludes helpers, agents, daemons.
    Then applies an additional name-based filter for anything that slips through.
    Returns an empty list if the query fails.
    """
    # 'background only is false' = app has a Dock icon / visible UI presence
    script = 'tell application "System Events" to get name of every application process whose background only is false'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    names = [name.strip() for name in result.stdout.strip().split(",") if name.strip()]
    return [name for name in names if _is_user_app(name)]


# Name-based blocklist: substrings that indicate a non-user-facing process
_BLOCKED_SUBSTRINGS = ("Helper", "Agent", "Service", "Daemon", "Extension", "XPC")

# Known system process names to always exclude
_BLOCKED_EXACT = {
    "WindowManager", "System Events", "ControlCenter", "loginwindow",
    "SystemUIServer", "ViewBridgeAuxiliary", "AccessibilityUIServer",
    "WallpaperAgent", "TextInputMenuAgent", "TextInputSwitcher",
    "AirPlayUIAgent", "NotificationCenter",
}


def _is_user_app(name: str) -> bool:
    """Return True if the process name looks like a real user-facing app."""
    if name.startswith("com.apple"):
        return False
    if name in _BLOCKED_EXACT:
        return False
    if any(sub in name for sub in _BLOCKED_SUBSTRINGS):
        return False
    return True


def show_dialog(app_name: str, duration_str: str) -> str:
    """Show a macOS confirmation dialog for an inactive app.

    Returns "Close" or "Keep Open" based on what the user clicks.
    Falls back to "Keep Open" (safe default) if the dialog fails or is dismissed.
    """
    msg = f"{app_name} has been inactive for {duration_str}. Close it?"
    script = (
        f'tell application "System Events" to display dialog "{msg}" '
        f'buttons {{"Keep Open", "Close"}} default button "Keep Open" with icon caution'
    )
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return "Keep Open"
    # osascript stdout: "button returned:Close\n"
    return "Close" if "Close" in result.stdout else "Keep Open"


def close_app(app_name: str) -> bool:
    """Gracefully quit an application by name using AppleScript.

    Returns True if the quit command was sent successfully, False otherwise.
    Note: this sends the quit signal; the app may prompt to save unsaved work.
    """
    script = f'tell application "{app_name}" to quit'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as a human-readable string.

    Examples:
        3661 -> "1h 1m"
        300  -> "5m"
        45   -> "45s"
    """
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{secs}s"
