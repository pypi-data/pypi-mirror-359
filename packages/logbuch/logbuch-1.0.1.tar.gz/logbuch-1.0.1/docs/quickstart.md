# 🚀 Quick Start Guide

Get up and running with Logbuch in 5 minutes!

## 📦 Installation

### Option 1: pip (Recommended)
```bash
pip install logbuch
```

### Option 2: From Source
```bash
git clone https://github.com/yourusername/logbuch.git
cd logbuch
pip install -e .
```

## 🎯 First-Time Setup

Run the interactive setup to get started:

```bash
logbuch setup --first-time
```

This will:
- Welcome you to Logbuch
- Show you the key features
- Create your first task
- Set up your profile

## ⚡ Essential Commands

### Task Management
```bash
# Add a task
logbuch task "Finish the presentation"
logbuch t "Quick task"                    # Short version

# List tasks
logbuch task --list
logbuch t -l                              # Short version

# Complete a task
logbuch task --complete 1
logbuch t -c 1                            # Short version
```

### Dashboard
```bash
# View your productivity dashboard
logbuch dashboard
logbuch d                                 # Short version
logbuch .                                 # Ultra-short version
```

### AI Coach
```bash
# Get AI productivity coaching
logbuch coach
logbuch co                                # Short version
```

### Journal & Mood
```bash
# Add journal entry
logbuch journal "Today was productive!"
logbuch j "Great day!"                    # Short version

# Track mood
logbuch mood happy
logbuch m excited                         # Short version
```

## 🎮 Gamification

Check your progress and achievements:

```bash
# View your profile
logbuch profile
logbuch me                                # Short version

# See achievements
logbuch achievements
logbuch ach                               # Short version
```

## 🚂 Commuter Assistant

Set up your commute route:

```bash
# Add your commute route
logbuch add-route --name "Work" --from "Central Station" --to "Downtown" --mode train --departure "08:15" --duration 45 --default

# Quick delay check
logbuch late
```

## 🚽 ASCII Art Celebrations

Celebrate your wins:

```bash
# Create ASCII art
logbuch toilet "SUCCESS"
logbuch art "DONE"                        # Short version

# Celebration mode
logbuch toilet --celebrate "TASK COMPLETED"
```

## ⚡ Lightning Shortcuts

Logbuch has 50+ shortcuts for maximum speed:

```bash
logbuch shortcuts                         # See all shortcuts
```

**Most used shortcuts:**
- `t` - tasks
- `j` - journal  
- `m` - mood
- `d` - dashboard
- `.` - quick dashboard
- `late` - train delays
- `co` - AI coach
- `me` - profile

## 🔧 Configuration

Logbuch works great out of the box, but you can customize it:

```bash
# View current settings
logbuch config

# Clean up test data
logbuch cleanup --test-data

# Export your data
logbuch export my-data.json
```

## 🆘 Getting Help

```bash
# General help
logbuch --help
logbuch ?                                 # Short version

# Command-specific help
logbuch task --help
logbuch coach --help
```

## 🎯 Next Steps

Now that you're set up:

1. **Add some tasks** - Start with `logbuch t "My first task"`
2. **Check your dashboard** - Use `logbuch d` to see your overview
3. **Get AI coaching** - Try `logbuch co` for productivity insights
4. **Explore features** - Use `logbuch shortcuts` to see everything
5. **Celebrate wins** - Use `logbuch art "WIN"` when you complete tasks

## 🚀 Pro Tips

- Use `logbuch .` for instant dashboard access
- Set up your commute with `logbuch add-route` to never be surprised by delays
- Use `logbuch + "Quick idea"` for lightning-fast capture
- Try `logbuch toilet --celebrate "ACHIEVEMENT"` for epic celebrations
- Use shortcuts everywhere - they make you incredibly fast

## 🆘 Troubleshooting

### Common Issues

**Command not found**
```bash
# Make sure Logbuch is installed
pip install logbuch

# Or add to PATH if installed from source
export PATH=$PATH:~/.local/bin
```

**Permission errors**
```bash
# Use user installation
pip install --user logbuch
```

**Database issues**
```bash
# Clean up and reset
logbuch cleanup --test-data
```

## 📚 Learn More

- [Complete Manual](manual.md) - Comprehensive guide
- [Configuration](configuration.md) - Customize Logbuch
- [Integrations](integrations.md) - Connect external services
- [API Reference](api.md) - Developer documentation

---

**Ready to be incredibly productive? Let's go! 🚀**
