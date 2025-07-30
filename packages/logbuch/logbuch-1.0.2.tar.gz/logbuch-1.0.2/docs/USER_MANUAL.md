# 📖 Logbuch User Manual

> **Think Locally, Act Globally** - Your Personal Productivity Logbook

## 🎯 Table of Contents

1. [Getting Started](#getting-started)
2. [Core Features](#core-features)
3. [Task Management](#task-management)
4. [Productivity Features](#productivity-features)
5. [Advanced Features](#advanced-features)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Tricks](#tips--tricks)

---

## 🚀 Getting Started

### First Launch

When you first run `logbuch`, you'll see the epic ASCII art logo and welcome screen:

```bash
logbuch
```

This displays:
- 🎨 **Epic ASCII Logo** - Beautiful speed font with your terminal colors
- 📖 **Tagline** - "Think Locally, Act Globally"
- 🚀 **Quick guidance** - Next steps to get started

### Interactive Setup

For new users, run the welcome wizard:

```bash
logbuch welcome
```

This will guide you through:
- ⚙️ **Personal preferences** - Name, time format, default priority
- 📋 **Initial tasks** - Sample tasks to get you started
- 🎮 **Feature configuration** - Enable/disable features you want

### Quick Setup

For experienced users who want defaults:

```bash
logbuch welcome --quick
```

---

## 🎯 Core Features

### Task Management

#### Adding Tasks

```bash
# Basic task
logbuch t "Complete project documentation"

# Task with priority
logbuch t "Fix critical bug" --priority high

# Task with due date
logbuch t "Submit report" --due "2024-01-15"

# Task with tags
logbuch t "Review code" --tags work,urgent
```

#### Viewing Tasks

```bash
# List all active tasks
logbuch list

# List with specific status
logbuch list --status pending

# List with priority filter
logbuch list --priority high

# List recent tasks
logbuch list --recent 5
```

#### Completing Tasks

```bash
# Complete by ID
logbuch complete 1

# Complete by partial title match
logbuch complete "documentation"

# Bulk complete multiple tasks
logbuch complete 1,2,3
```

### Dashboard

Get an overview of your productivity:

```bash
logbuch d
```

The dashboard shows:
- 📊 **Task statistics** - Total, completed, pending
- 🎯 **Goals progress** - Current goals and completion
- 📈 **Recent activity** - What you've been working on
- 🏆 **Achievements** - Recent unlocks and progress
- ⚡ **Quick actions** - Common next steps

---

## 🎮 Productivity Features

### Gamification System

Logbuch includes a comprehensive gamification system to make productivity fun:

#### Experience Points (XP)
- 📋 **Task completion**: 10-50 XP based on priority
- 🎯 **Goal achievement**: 100-500 XP based on complexity
- ⚡ **Daily streaks**: Bonus XP for consistency
- 🏆 **Achievements**: Special XP bonuses

#### Levels and Progression
```bash
# Check your current level
logbuch level

# View XP breakdown
logbuch xp
```

#### Achievements System
```bash
# View all achievements
logbuch achievements

# Check progress on specific achievement
logbuch achievement "Task Master"
```

**Achievement Categories:**
- 🏁 **Completion** - Task completion milestones
- ⚡ **Speed** - Fast task completion
- 🎯 **Focus** - Concentration and consistency
- 🚀 **Productivity** - Overall productivity metrics
- 🌟 **Special** - Unique accomplishments

### AI Coach

Get intelligent suggestions and insights:

```bash
# Get personalized suggestions
logbuch coach

# Analyze productivity patterns
logbuch insights

# Get smart task recommendations
logbuch suggestions
```

The AI Coach provides:
- 📊 **Pattern analysis** - Identifies your productivity patterns
- 💡 **Smart suggestions** - Personalized recommendations
- 🎯 **Goal optimization** - Helps refine your goals
- ⚡ **Efficiency tips** - Ways to improve your workflow

---

## 🚂 Advanced Features

### Commuter Assistant

Perfect for daily commuters:

```bash
# Check train delays
logbuch late

# Add your regular route
logbuch route add "Berlin Hbf to Munich Hbf"

# Get travel optimization suggestions
logbuch commute optimize
```

### ASCII Art Celebrations

Celebrate your achievements in style:

```bash
# Basic celebration
logbuch toilet "SUCCESS!"

# With different fonts
logbuch toilet "AMAZING!" --font big

# Epic celebrations
logbuch toilet "LEGENDARY!" --celebrate
```

### Time Tracking

Track time spent on tasks:

```bash
# Start tracking time for a task
logbuch track start 1

# Stop tracking
logbuch track stop

# View time reports
logbuch time report
```

### Smart Shortcuts

Lightning-fast productivity commands:

```bash
# View all shortcuts
logbuch shortcuts

# Quick add (interactive)
logbuch s

# Quick complete
logbuch c

# Quick dashboard
logbuch d
```

---

## 🔧 Customization

### Preferences

Configure Logbuch to match your workflow:

```bash
# View current preferences
logbuch config show

# Set default priority
logbuch config set default_priority high

# Set time format
logbuch config set time_format 12h

# Set theme
logbuch config set theme dark
```

### Feature Toggles

Enable or disable features:

```bash
# Enable gamification
logbuch config set feature_gamification true

# Disable AI coach
logbuch config set feature_ai_coach false

# Enable commuter assistant
logbuch config set feature_commuter_assistant true
```

### Custom Commands

Create your own shortcuts:

```bash
# Add custom alias
logbuch alias add "w" "logbuch t 'Work task'"

# List custom aliases
logbuch alias list

# Remove alias
logbuch alias remove "w"
```

---

## 🛠️ Maintenance

### Database Cleanup

Keep your Logbuch database optimized:

```bash
# Check database health
logbuch maintenance stats

# Clean up duplicate and invalid data
logbuch maintenance cleanup

# Dry run (see what would be cleaned)
logbuch maintenance cleanup --dry-run

# Create backup
logbuch maintenance backup
```

### Performance Optimization

```bash
# View performance statistics
logbuch perf stats

# Clear performance cache
logbuch perf clear-cache

# Optimize database
logbuch optimize
```

---

## 🆘 Troubleshooting

### Common Issues

#### Command Not Found
```bash
# If 'logbuch' command is not found:
python3.11 -m logbuch

# Or set up aliases:
./setup_alias.sh
source ~/.zshrc
```

#### Database Issues
```bash
# Reset database (WARNING: loses data)
logbuch reset --confirm

# Repair database
logbuch maintenance repair

# Check database integrity
logbuch maintenance check
```

#### Performance Issues
```bash
# Clear caches
logbuch maintenance cleanup
logbuch perf clear-cache

# Optimize database
logbuch optimize

# Check for large datasets
logbuch maintenance stats
```

### Error Messages

Logbuch provides helpful error messages with suggestions:

- 🔍 **Validation errors** - Clear explanation of what's wrong
- 💡 **Suggestions** - Specific steps to fix the issue
- 📚 **Documentation links** - References to relevant help

### Getting Help

```bash
# General help
logbuch --help

# Command-specific help
logbuch task --help

# Interactive tour
logbuch tour

# Show version and system info
logbuch --version --info
```

---

## 💡 Tips & Tricks

### Productivity Hacks

1. **Use Short Aliases**
   ```bash
   alias lb='logbuch'
   alias lbt='logbuch t'
   alias lbd='logbuch d'
   ```

2. **Batch Operations**
   ```bash
   # Add multiple tasks at once
   logbuch batch add "Task 1" "Task 2" "Task 3"
   
   # Complete multiple tasks
   logbuch complete 1,2,3
   ```

3. **Smart Filtering**
   ```bash
   # Tasks due today
   logbuch list --due today
   
   # High priority pending tasks
   logbuch list --priority high --status pending
   
   # Tasks with specific tags
   logbuch list --tags work,urgent
   ```

### Workflow Integration

1. **Morning Routine**
   ```bash
   logbuch d                    # Check dashboard
   logbuch late                 # Check commute
   logbuch coach               # Get daily suggestions
   ```

2. **End of Day Review**
   ```bash
   logbuch achievements        # Check progress
   logbuch time report         # Review time spent
   logbuch t "Plan tomorrow"   # Add planning task
   ```

3. **Weekly Cleanup**
   ```bash
   logbuch maintenance cleanup  # Clean database
   logbuch archive completed    # Archive old tasks
   logbuch backup              # Create backup
   ```

### Advanced Usage

1. **Scripting with Logbuch**
   ```bash
   #!/bin/bash
   # Daily productivity script
   logbuch d --format json | jq '.pending_tasks'
   logbuch coach --format json | jq '.suggestions[]'
   ```

2. **Integration with Other Tools**
   ```bash
   # Export to calendar
   logbuch export --format ical > tasks.ics
   
   # Import from other tools
   logbuch import --format csv tasks.csv
   ```

---

## 🎉 Conclusion

Logbuch is designed to be your ultimate productivity companion. With its combination of powerful features, beautiful interface, and intelligent assistance, it adapts to your workflow and helps you achieve more.

**Remember the philosophy: Think Locally, Act Globally**

Start with your personal productivity, but let Logbuch help you make a bigger impact on the world.

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/logbuch/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/logbuch/discussions)
- 📚 **Documentation**: [Online Docs](https://logbuch.readthedocs.io)
- 💬 **Community**: [Discord Server](https://discord.gg/logbuch)

**Happy productivity!** 🚀📖✨
