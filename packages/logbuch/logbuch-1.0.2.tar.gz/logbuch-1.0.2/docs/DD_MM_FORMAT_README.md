# 📅 DD:MM Date Format Implementation

Your Logbuch app now supports the **DD:MM** date format for shorter, more convenient date input!

## 🎯 What Changed

Instead of typing long dates like `2024-12-25`, you can now use:
- **`25:12`** for December 25th
- **`05:03`** for March 5th  
- **`31:01`** for January 31st

## 🚀 Quick Start

### **1. Install the DD:MM Support**
```bash
# Run the update script
python update_date_format.py

# Test the implementation
python test_dd_mm_format.py
```

### **2. Use the New Format**
```bash
# Add a task due on Christmas (Dec 25)
logbuch task "Buy Christmas gifts" --due 25:12

# Set a goal for New Year (Jan 1)
logbuch goal "Start exercising" --due 01:01

# Filter mood entries for March 15th
logbuch mood --view --date 15:03
```

## 📋 Supported Date Formats

| Input Format | Example | Meaning |
|--------------|---------|---------|
| **DD:MM** | `25:12` | December 25th (current year) |
| **DD:MM** | `05:03` | March 5th (current year) |
| **Natural Language** | `tomorrow` | Next day |
| **Natural Language** | `next week` | One week from today |
| **Natural Language** | `in 3 days` | Three days from now |
| **ISO Format** | `2024-12-25` | Still supported |

## 🎨 Display Format

All dates are now displayed in the shorter **DD:MM** format:

### **Before (Old Format)**
```
Tasks:
ID  Content              Due Date
1   Christmas shopping   2024-12-25
2   New Year party       2024-01-01
```

### **After (New DD:MM Format)**
```
Tasks:
ID  Content              Due Date
1   Christmas shopping   25:12
2   New Year party       01:01
```

## 🔧 Implementation Details

### **Files Created/Modified**

1. **`logbuch/utils/date_parser.py`** - New date parsing utilities
2. **`logbuch/cli.py`** - Updated to use DD:MM format
3. **`logbuch/storage.py`** - Updated default date format config
4. **`update_date_format.py`** - Installation script
5. **`test_dd_mm_format.py`** - Test suite

### **Key Functions**

```python
# Parse DD:MM format to ISO date
parse_short_date("25:12")  # → "2024-12-25"

# Format ISO date for display  
format_date_for_display("2024-12-25", "short")  # → "25:12"

# Parse natural language dates
parse_natural_date("tomorrow")  # → "2024-01-16" (example)

# Validate date input
validate_date_input("25:12")  # → (True, "")
validate_date_input("32:12")  # → (False, "Invalid day")
```

## 📚 Usage Examples

### **Tasks with DD:MM Dates**
```bash
# Christmas shopping
logbuch task "Buy presents" --due 25:12

# Birthday reminder  
logbuch task "Mom's birthday" --due 15:06

# Project deadline
logbuch task "Submit report" --due 31:03

# Natural language
logbuch task "Doctor appointment" --due tomorrow
```

### **Goals with DD:MM Dates**
```bash
# New Year resolution
logbuch goal "Learn Spanish" --due 31:12

# Summer vacation planning
logbuch goal "Book vacation" --due 01:06

# Natural language
logbuch goal "Finish course" --due "next week"
```

### **Filtering by DD:MM Dates**
```bash
# View mood entries for specific date
logbuch mood --view --date 15:03

# View sleep data for date
logbuch sleep --view --date 20:02

# Search within date range
logbuch search "project" --from-date 01:03 --to-date 31:03
```

## 🎯 Visual Indicators

The new format includes smart visual indicators:

### **Task Due Dates**
- **🔴 Red**: `25:12 (overdue)` - Past due
- **🟡 Yellow**: `16:01 (today)` - Due today  
- **🟠 Orange**: `17:01 (tomorrow)` - Due tomorrow
- **🟢 Green**: `25:12` - Future dates

### **Goal Target Dates**
- **🔴 Red**: `15:01 (overdue)` - Past target
- **🟡 Yellow**: `20:01 (soon)` - Due within 7 days
- **🟢 Green**: `25:12` - Future targets

## 🔍 Validation & Error Handling

The system validates all date inputs:

### **Valid Inputs**
```bash
✅ 25:12  # December 25th
✅ 01:01  # January 1st  
✅ 29:02  # February 29th (leap year)
✅ tomorrow
✅ next week
```

### **Invalid Inputs**
```bash
❌ 32:12  # Invalid day (32)
❌ 25:13  # Invalid month (13)
❌ 00:05  # Invalid day (0)
❌ 15:00  # Invalid month (0)
```

### **Error Messages**
```bash
$ logbuch task "Test" --due 32:12
❌ Invalid date format: Use DD:MM format (e.g., 25:12 for Dec 25) or natural language

💡 Date format examples: 25:12 (December 25th), 05:03 (March 5th), tomorrow
```

## 🔄 Migration from Old Format

### **Automatic Migration**
- Existing data remains unchanged in storage (ISO format)
- Only display format changes to DD:MM
- All old commands still work

### **Manual Migration** (if needed)
```bash
# Run the migration script
python migrate_dates.py
```

## 🧪 Testing

### **Run the Test Suite**
```bash
python test_dd_mm_format.py
```

### **Expected Output**
```
🧪 Testing DD:MM Date Parsing
========================================
✅ 25:12       → 2024-12-25  (December 25th)
✅ 01:01       → 2024-01-01  (January 1st)
✅ 31:03       → 2024-03-31  (March 31st)
❌ 32:12       → Invalid     (Invalid day)
❌ 25:13       → Invalid     (Invalid month)

🎨 Testing Date Display Formatting
========================================
  2024-12-25 → 25:12 (short) / 25-12 (display)
  2024-01-01 → 01:01 (short) / 01-01 (display)
```

## 🎨 Customization

### **Change Date Format**
```python
# In your code, you can customize the format
from logbuch.utils.date_parser import format_date_for_display

# Different display formats
format_date_for_display("2024-12-25", "short")   # → "25:12"
format_date_for_display("2024-12-25", "display") # → "25-12"  
format_date_for_display("2024-12-25", "long")    # → "2024-12-25"
```

### **Add Custom Date Patterns**
You can extend the `parse_natural_date()` function to support more patterns:

```python
# Add to logbuch/utils/date_parser.py
elif "next month" in date_input:
    next_month = today + datetime.timedelta(days=30)
    return next_month.strftime("%Y-%m-%d")
```

## 🚀 Advanced Features

### **Smart Date Interpretation**
```bash
# The system shows what it interpreted
$ logbuch task "Meeting" --due 25:12
📅 Interpreted '25:12' as 25:12
✅ Task added: Meeting
📅 Due: 25:12
```

### **Context-Aware Validation**
```bash
# Validates against calendar rules
$ logbuch task "Test" --due 29:02
✅ Valid (leap year 2024)

$ logbuch task "Test" --due 30:02  
❌ Invalid date format: February doesn't have 30 days
```

### **Natural Language Support**
```bash
# All these work
logbuch task "Task 1" --due tomorrow
logbuch task "Task 2" --due "next week"  
logbuch task "Task 3" --due "in 3 days"
logbuch task "Task 4" --due 25:12
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Import Errors**
```bash
❌ ImportError: No module named 'logbuch.utils.date_parser'

# Solution: Run the update script
python update_date_format.py
```

#### **Date Not Parsing**
```bash
❌ Invalid date format: Use DD:MM format

# Check your input format
✅ Correct: 25:12
❌ Wrong: 25/12, 25-12, 12/25
```

#### **Leap Year Issues**
```bash
# February 29th only valid in leap years
✅ 29:02 in 2024 (leap year)
❌ 29:02 in 2023 (not leap year)
```

### **Debug Mode**
```python
# Test date parsing manually
from logbuch.utils.date_parser import parse_short_date, validate_date_input

# Test your date
result = parse_short_date("25:12")
print(f"Parsed: {result}")

# Check validation
is_valid, error = validate_date_input("25:12")
print(f"Valid: {is_valid}, Error: {error}")
```

## 🎉 Benefits

### **Shorter Input**
- **Before**: `logbuch task "Gift" --due 2024-12-25`
- **After**: `logbuch task "Gift" --due 25:12`

### **More Intuitive**
- DD:MM matches how people think about dates
- Natural language support for flexibility
- Visual indicators for urgency

### **Backward Compatible**
- All existing commands still work
- Existing data is preserved
- ISO format still supported

## 📖 Reference

### **Date Format Cheat Sheet**
| What You Want | Input Format | Example |
|---------------|--------------|---------|
| Christmas | `25:12` | December 25th |
| New Year | `01:01` | January 1st |
| Valentine's Day | `14:02` | February 14th |
| Halloween | `31:10` | October 31st |
| Tomorrow | `tomorrow` | Next day |
| Next Week | `next week` | 7 days from now |
| In 3 Days | `in 3 days` | 3 days from now |

### **Command Examples**
```bash
# Tasks
logbuch task "Christmas party" --due 25:12
logbuch task "Tax deadline" --due 15:04
logbuch task "Vacation" --due tomorrow

# Goals  
logbuch goal "Learn Python" --due 31:12
logbuch goal "Run marathon" --due 15:06

# Filtering
logbuch mood --view --date 20:03
logbuch history --date tomorrow
logbuch search "project" --from-date 01:01 --to-date 31:12
```

---

🎉 **Congratulations!** Your Logbuch app now supports the convenient **DD:MM** date format. Enjoy shorter, more intuitive date input! 

For questions or issues, check the troubleshooting section or run the test suite to verify everything is working correctly.
