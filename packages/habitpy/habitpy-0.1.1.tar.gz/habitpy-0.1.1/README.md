
---

# HabitPy

**Track your habits, analyze your progress, and stay motivated—all from your terminal!**

## Features

- 📅 **Daily & Weekly Tracking:** Log your habits (only numbers)
- ✏️ **Custom Habits:** Add, show, or delete any habit you want to track.
- 📈 **Visualize Progress:** Instantly generate beautiful graphs (with dark mode!) for your week, month, or year.
- 🎉 **Motivational Cheers:** Get random motivational messages to keep you going.
- 📤 **Export Data:** Export all your habit data to CSV for use in Excel, Sheets, or anywhere else.
- 🛠️ **Easy Reset:** Reset your data and start fresh anytime.

## Installation

```bash
pip install .
```
or, for development:
```bash
git clone https://github.com/Asunt70/habitpy.git
cd habits-py
pip install -e .
```

## Usage

First, set up your tracker:
```bash
habitpy setup
```

Then, use these commands:
- `habitpy track` — Log today’s habits
- `habitpy create <habit_name>` — Add a new habit
- `habitpy show` — List your habits
- `habitpy delete <habit_name>` — Remove a habit
- `habitpy graph week|month|year` — See your progress in graphs
- `habitpy export` — Export your data to CSV
- `habitpy reset` — Delete all data and start over

---

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W318WNN8)
