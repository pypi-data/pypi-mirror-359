# 🔥 Logbuch Template Tools

## Your Professional Template

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on ${DATE}, ${TIME}.
# Last modified: ${MONTH_NAME_SHORT}.
# Copyright (c) ${YEAR}. All rights reserved.
```

## 🛠️ Available Tools

### 1. **apply_template.py** - Update ALL files at once
```bash
python3.11 apply_template.py
```
- Updates ALL Python files in the project
- Creates backups automatically
- Shows progress and summary

### 2. **update_core_files.py** - Update just the important files
```bash
python3.11 update_core_files.py
```
- Updates only the core 12 files
- Quick and safe
- Perfect for testing

### 3. **update_file_headers.py** - Full control with options
```bash
# Dry run to see what would change
python3.11 update_file_headers.py --dry-run --verbose

# Update all files
python3.11 update_file_headers.py

# Update specific directory
python3.11 update_file_headers.py --directory logbuch/commands
```

### 4. **quick_header_update.py** - Interactive selection
```bash
python3.11 quick_header_update.py
```
- Interactive menu
- Choose specific files or directories
- Perfect for selective updates

## 🎯 Quick Commands

```bash
# Apply template to ALL files (recommended)
python3.11 apply_template.py

# Clean up backup files after you're happy
find . -name "*.backup" -delete

# Check a specific file
head -10 logbuch/cli.py
```

## ✨ Features

- ✅ **Preserves original creation dates** if they exist
- ✅ **Updates "Last modified" month** automatically
- ✅ **Creates backups** before making changes
- ✅ **Handles encoding properly** with UTF-8
- ✅ **Skips system directories** (.git, __pycache__, etc.)
- ✅ **Professional shebang** for all Python files
- ✅ **Consistent copyright** format

## 🎉 Result

Every Python file will have your clean, professional header:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.
```

**Your Logbuch codebase will look absolutely professional and consistent!** 🚀
