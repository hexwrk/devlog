# DevLog 🖥️

> A desktop task manager built specifically for IT & Cybersecurity students.

## Features
- Task categories: Lab, Study, Project, CTF, Reading, Revision
- Skill tracking: Python, Networking, Linux, Web Security, and more
- Link resources (docs, GitHub repos, courses) to tasks
- Progress dashboard with streaks and completion stats

## Stack
- Python 3.x
- CustomTkinter (UI)
- JSON (local persistence)

## Getting Started
```bash
git clone https://github.com/hexwrk/devlog.git
cd devlog
pip install -r requirements.txt
python main.py
```

## Project Structure
```
devlog/
├── main.py              # Entry point
├── views/               # UI screens (dashboard, board, stats)
├── models/              # Task data model + JSON persistence
├── assets/              # Icons, fonts
├── data/                # tasks.json lives here (auto-created)
└── requirements.txt
```

## License
MIT
