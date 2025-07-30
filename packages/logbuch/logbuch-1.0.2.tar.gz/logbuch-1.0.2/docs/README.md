# Logbuch 🌻

A personal CLI app combining journal and task management with mood and sleep tracking, enhanced with powerful convenience features.

## ✨ Key Features

### 📋 Task Management
- Add, list, complete, and delete tasks
- Priority levels (low, medium, high)
- Due dates with **natural language parsing** ("tomorrow", "next week", "monday")
- Multiple boards for organization
- Kanban board visualization
- **Bulk operations** (complete/delete/move multiple tasks)
- **Task templates** for common workflows

### 📝 Journal
- Add journal entries with tags and categories
- View and search entries
- Editor integration for longer entries
- **Journal templates** for reflection prompts

### 😊 Mood Tracking
- Track your daily moods
- **Random mood suggestions** with 50+ mood options
- View mood history and patterns
- **Smart mood categories** (positive, neutral, challenging, complex)

### 😴 Sleep Tracking
- Log sleep hours with notes
- View sleep patterns over time

### 🎯 Goal Setting
- Set goals with target dates
- Track progress (0-100%) with visual progress bars
- View active and completed goals

### ⏰ Time Tracking
- Start/stop time tracking sessions
- Associate time with tasks
- View time entries and reports

### 📊 Dashboard & Analytics
- **Comprehensive dashboard** with overview of all data
- **Quick statistics** and insights
- Recent activity summary
- **Smart suggestions** based on your patterns

### 📅 Calendar & Week Views
- Monthly calendar with task/entry counts
- Weekly task planning view
- Navigate between weeks and months

### 🔍 Smart Search & Filtering
- **Universal search** across all content types
- Filter by date ranges
- **Popular tags** analysis
- Advanced filtering options

### 🚀 Convenience Features
- **Quick add commands** with shortcuts
- **Interactive daily check-in**
- **Natural language date parsing**
- **Task templates** for common workflows
- **Bulk operations** for efficiency
- **Smart suggestions** and insights

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Logbuch

# Install in development mode
pip install -e .
```

## 🚀 Quick Start Guide

### Basic Usage
```bash
# View dashboard (your daily overview)
logbuch dashboard
# or use shortcut
logbuch d

# Quick add anything
logbuch add "Complete project documentation" -t task -p high
logbuch + "Feeling great today!" -t journal
logbuch + -t mood -r  # Random mood

# Natural language dates
logbuch qtask "Call dentist" -d tomorrow
logbuch qtask "Team meeting" -d "next monday"
logbuch qtask "Project deadline" -d "in 2 weeks"
```

### Daily Workflow
```bash
# Start your day with a check-in
logbuch checkin

# Add tasks using templates
logbuch templates --add work
logbuch templates --add health

# Quick stats overview
logbuch stats

# Search across everything
logbuch search "project"
logbuch / "meeting"  # shortcut

# End day with dashboard review
logbuch d
```

## 📋 Commands & Shortcuts

| Command | Shortcut | Description |
|---------|----------|-------------|
| `dashboard` | `d` | Show overview dashboard |
| `add` | `+` | Quick add task/journal/mood |
| `qtask` | `qt` | Quick task with natural dates |
| `search` | `/` | Smart search everything |
| `checkin` | `ci` | Interactive daily check-in |
| `stats` | `st` | Quick statistics |
| `templates` | `tpl` | Task/journal templates |
| `bulk` | `b` | Bulk operations |
| `task` | `t` | Manage tasks |
| `journal` | `j` | Journal entries |
| `mood` | `m` | Track moods |
| `sleep` | `s` | Track sleep |
| `goal` | `g` | Manage goals |
| `calendar` | `c` | Calendar view |
| `week` | `w` | Week view |
| `time` | `ti`, `tr` | Time tracking |
| `kanban` | `k` | Kanban board |

## 🎯 Advanced Features

### Natural Language Dates
```bash
# All of these work!
logbuch qtask "Buy groceries" -d today
logbuch qtask "Doctor appointment" -d tomorrow
logbuch qtask "Team meeting" -d monday
logbuch qtask "Project review" -d "next week"
logbuch qtask "Vacation planning" -d "in 3 days"
logbuch qtask "Annual review" -d "next month"
```

### Task Templates
```bash
# View available templates
logbuch templates

# Add all tasks from a category
logbuch templates --add work
logbuch templates --add health
logbuch templates --add personal

# View journal templates
logbuch templates -t journal
```

### Bulk Operations
```bash
# Complete multiple tasks
logbuch bulk -c "1,2,3"

# Delete multiple tasks
logbuch bulk -d "4,5,6"

# Move tasks to different board
logbuch bulk -m "1,2,3" "urgent"

# Clean up old completed tasks
logbuch bulk --cleanup 30

# Get smart suggestions
logbuch bulk --suggest
```

### Smart Search
```bash
# Search everything
logbuch search "project"

# Search specific content type
logbuch search "meeting" -t tasks
logbuch search "grateful" -t journal
logbuch search "happy" -t moods

# Date range filtering
logbuch search "work" --from-date 2025-06-01 --to-date 2025-06-30

# Show popular tags
logbuch search --tags
```

### Random Mood Features
```bash
# Get one random mood
logbuch mood --random

# Get multiple suggestions
logbuch mood --random-list 5

# Quick add random mood
logbuch + -t mood -r
```

### Interactive Daily Check-in
```bash
# Guided daily check-in
logbuch checkin
# Prompts for: mood, sleep, tasks, journal
```

## 📊 Dashboard Overview

The dashboard shows:
- **Task Summary**: Total, completed, pending tasks
- **Recent Activity**: Latest journal entries and moods  
- **Goals Progress**: Visual progress bars
- **Health Metrics**: Sleep patterns and current mood
- **Quick Actions**: Suggested next steps

## 🔧 Productivity Tips

### Morning Routine
```bash
logbuch checkin          # Daily check-in
logbuch templates --add work  # Add work tasks
logbuch d                # Review dashboard
```

### Throughout the Day
```bash
logbuch + "Quick task" -t task
logbuch mood happy -n "Great meeting!"
logbuch / "project"      # Find related items
```

### Evening Review
```bash
logbuch stats            # Review day's stats
logbuch bulk --suggest   # Get suggestions
logbuch + "Reflection on today" -t journal
logbuch d                # Final dashboard check
```

### Weekly Planning
```bash
logbuch week             # View week layout
logbuch bulk --cleanup 7 # Clean old tasks
logbuch goal -v          # Review goals
logbuch search --tags    # Review popular tags
```

## 🎨 Customization

### Task Templates
Create your own workflows by combining templates:
```bash
logbuch templates --add work
logbuch templates --add health
logbuch qtask "Review weekly goals" -d friday
```

### Smart Boards
Organize tasks by context:
```bash
logbuch qtask "Code review" -b work
logbuch qtask "Grocery shopping" -b personal
logbuch qtask "Exercise" -b health
logbuch kanban show --board work
```

## 📈 Data Management

```bash
# Create backup
logbuch --backup

# Restore from backup
logbuch --restore latest

# Export data
logbuch --export data.json --format json

# Import data
logbuch --import-file data.json

# Database info
logbuch --info
```

## 🧪 Development

```bash
# Run tests
python -m pytest tests/ -v

# Install development dependencies
pip install -e .[dev]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. See LICENSE file for details.

---

**Logbuch** - Your personal productivity companion with the power of convenience! 🌻✨
