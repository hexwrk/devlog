# DevLog

DevLog is a local-first desktop task manager for IT, computer science, and
cybersecurity students. It combines a fast task board with skill progression,
completion streaks, and a small RPG-style XP system. Your tasks stay in a local
JSON file; there is no account, server, or analytics service.

## What it supports

- Six fixed task categories: `Lab`, `Study`, `Project`, `CTF`, `Reading`, and
	`Revision`
- Skills including Python, Linux, Networking, Web Security, Cryptography, and
	Reverse Engineering
- Task states: Todo, In Progress, Done, and Blocked
- Multiple documentation, GitHub, TryHackMe, Hack The Box, or course links per
	task, validated as `http` or `https` URLs
- Optional local file attachments
- Difficulty-based XP: Easy `10`, Medium `25`, Hard `50`
- An Overview page with weekly progress, XP, recent activity, and a
	today/status/focus summary
- An Analytics page with time tracked, completion rate, streaks, and
	per-category performance
- A Projects page with a workspace per category (progress, task counts,
	scoped task list)
- A Settings page for profile, weekly streak goal, and default board view
- Category, skill, and status filtering on the task board

## Requirements

- Python 3.10 or newer
- A desktop session with Tk support

## Installation

```bash
git clone https://github.com/hexwrk/devlog.git
cd devlog
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
python3 main.py
```

DevLog resolves its images, icon, and data file relative to `main.py`, so it
can be launched from any working directory after installation.

## Data and privacy

Tasks are stored in `tasks.json` beside the application, and preferences in
`settings.json`. The storage layer is the only code that reads or writes
`tasks.json`, and malformed records are skipped instead of crashing the UI.
Resource links are restricted to absolute HTTP(S) URLs. Attachments store
local paths only; file contents are never uploaded.

## Project layout

```text
main.py                  App shell: sidebar + header + page router
theme.py                 Design tokens (colours, spacing, radius, icons)
models/task.py           Validated task schema and taxonomy
models/analytics.py      XP, streak, completion, and velocity calculations
storage.py               Task JSON persistence and legacy-data migration
settings_store.py        Preferences JSON persistence
views/                   Overview, Board, Analytics, Projects, Settings,
                          the task modal, and shared design-system components
tasks.json               Local task data
settings.json            Local preferences data
requirements.txt         Python dependencies
```

## Development checks

Run these from the `devlog` directory:

```bash
python3 -m compileall -q .
python3 -m pip check
```

The analytics and persistence modules are intentionally separated from the
CustomTkinter UI, so they can be tested without opening a window.

## License

MIT
