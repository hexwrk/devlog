"""
models/analytics.py — Derived metrics computed from stored tasks
=================================================================
This module is READ-ONLY. It never writes to disk.
It takes a list of Task objects and returns computed values.

Call chain:  View → analytics.py → (tasks already loaded by view)

Why a separate analytics module?
---------------------------------
The dashboard view should not contain business logic — it should only
display results. If you put the streak calculation inside the view,
you can't test it independently, and you can't reuse it elsewhere.
Keeping it here means: one place to fix, one place to test.
"""


from datetime import date, timedelta
from collections import Counter
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import Task

def get_streak(tasks: list[Task]) -> int:
    """
    Count consecutive days ending today (or yesterday) where at least
    one task was completed.

    Logic:
    1. Collect all completed_at dates where status == "Done"
    2. Put them in a set for O(1) lookup
    3. Walk backwards from today, day by day
    4. Stop the moment a day has no completion

    Edge cases handled:
    - completed_at is None → skip (task has no date)
    - No done tasks at all → return 0
    - Today has no completion but yesterday does → count from yesterday
      (user hasn't completed anything today yet, streak still alive)
    """
    done_dates: set[date] = set()

    for task in tasks:
        if task.status == "Done" and task.completed_at:
            try:
                done_dates.add(date.fromisoformat(task.completed_at))
            except ValueError:
                pass   # malformed date string — skip it

    if not done_dates:
        return 0

    today = date.today()

    # Start from today; if today has no completion, try yesterday.
    # This prevents the streak from resetting the moment you open the app
    # on a new day before completing anything.
    cursor = today if today in done_dates else today - timedelta(days=1)

    if cursor not in done_dates:
        return 0   # neither today nor yesterday — streak is broken

    streak = 0
    while cursor in done_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


def get_status_counts(tasks: list[Task]) -> dict[str, int]:
    """Return a count of tasks per status."""
    counts = {"Todo": 0, "In Progress": 0, "Done": 0, "Blocked": 0}
    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
    return counts


def get_most_active_skill(tasks: list[Task]) -> str:
    """
    Return the skill with the most completed tasks.
    Returns "—" if no tasks are done yet.
    """
    done = [t.skill for t in tasks if t.status == "Done" and t.skill]
    if not done:
        return "—"
    return Counter(done).most_common(1)[0][0]


def get_due_today(tasks: list[Task]) -> list[Task]:
    """
    Return tasks whose due_date == today.
    Tasks with no due_date are excluded.
    """
    today = date.today().isoformat()
    return [t for t in tasks if t.due_date == today and t.status != "Done"]


def get_completion_rate(tasks: list[Task]) -> int:
    """Return percentage of tasks that are Done (0-100)."""
    if not tasks:
        return 0
    done = sum(1 for t in tasks if t.status == "Done")
    return round((done / len(tasks)) * 100)
