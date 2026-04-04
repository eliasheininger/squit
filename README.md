# squit

A minimal macOS CLI tool that tracks which apps you've been using and closes ones that have been inactive (not frontmost) for too long.

**Default: 6 hours inactivity threshold, checks every 5 minutes.**

---

## Requirements

- macOS 10.15+
- Python 3.10+ (uses `str | None` syntax; no pip installs needed)

---

## macOS Permissions (required)

squit uses AppleScript via `osascript` to detect the active app and close inactive ones. macOS requires explicit permission for this.

### 1. Accessibility (required to detect frontmost app)

1. Open **System Settings → Privacy & Security → Accessibility**
2. Click the **+** button
3. Add **Terminal** (or your terminal app: iTerm2, Warp, etc.)
4. Make sure the toggle is **on**

### 2. Automation (prompted automatically)

When you first run the script, macOS will show a dialog:

> *"Terminal" wants to control "System Events"*

Click **OK**. If you accidentally denied it:

1. Open **System Settings → Privacy & Security → Automation**
2. Find **Terminal** and enable **System Events**

---

## Usage

```bash
cd path/to/windowcleaner

# Dry-run mode (safe — logs only, nothing is closed)
python3 main.py

# Live mode (actually quits inactive apps)
python3 main.py --close

# Custom threshold: close after 1 hour of inactivity
python3 main.py --threshold 3600

# Custom check interval: check every 60 seconds (useful for testing)
python3 main.py --interval 60

# Combine flags
python3 main.py --close --threshold 3600 --interval 60
```

### Sample output

```
squit starting in DRY RUN mode
  Inactivity threshold : 6h 0m
  Check interval       : 5m
  Whitelist            : ['Finder', 'SystemUIServer', 'Dock', 'loginwindow']
  Press Ctrl+C to stop

[10:00:00] Initialized tracker with 12 running apps

[10:00:00] Active app: Visual Studio Code
[10:00:00] No inactive apps found.
[10:00:00] Next check in 5m...

[10:05:00] Active app: Safari
[10:05:00] [DRY RUN] Would close 'Slack' (inactive for 6h 3m)
[10:05:00] [DRY RUN] Would close 'Spotify' (inactive for 7h 12m)
[10:05:00] Next check in 5m...
```

---

## Configuration

Edit `config.py` to change defaults:

```python
INACTIVITY_THRESHOLD = 6 * 3600   # seconds before an app is considered stale
CHECK_INTERVAL       = 5 * 60     # how often to check
WHITELIST            = ["Finder", "SystemUIServer", "Dock", "loginwindow"]
```

Add any app name to `WHITELIST` to protect it from ever being closed (use the exact name as shown in Activity Monitor).

---

## How It Works

1. Every `CHECK_INTERVAL` seconds, squit calls `osascript` to find the frontmost app
2. It records a timestamp for that app (`tracker.py`)
3. It also seeds any newly opened apps with the current time
4. Any app not seen as frontmost for longer than `INACTIVITY_THRESHOLD` is flagged
5. In dry-run mode it logs; in live mode it sends AppleScript `quit` to each flagged app

---

## Project Structure

```
windowcleaner/
  main.py      # Entry point — arg parsing, main loop
  tracker.py   # AppTracker class — timestamp storage and inactive detection
  utils.py     # osascript helpers — frontmost app, list running, close app
  config.py    # Constants — threshold, interval, whitelist
  README.md    # This file
```

---

## Next Steps / Roadmap

| Feature | How |
|---|---|
| Whitelist from CLI | `--whitelist "Slack,Notion"` arg in `main.py` |
| Menu bar app | Wrap with [`rumps`](https://github.com/jaredks/rumps): `pip install rumps` |
| Background daemon | Add `~/Library/LaunchAgents/com.squit.plist` |
| Persist state across restarts | Save `tracker.last_seen` to JSON on disk |
| Notifications | Use `osascript` to send macOS notifications before closing |

### launchd daemon (run on login, background)

Create `~/Library/LaunchAgents/com.squit.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.squit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/windowcleaner/main.py</string>
        <string>--close</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/squit.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/squit.err</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.squit.plist
```
