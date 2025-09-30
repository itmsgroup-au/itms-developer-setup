# 🚀 Quick Start Guide - Smart Development Features

## ✅ Fixed Issues

The code review system had overly aggressive rules that flagged normal CLI `print()` statements as debug code. This has been fixed with:

1. **Better rule specificity** - Only flags actual debug statements like `pdb.set_trace()`
2. **File type awareness** - Differentiates between Odoo modules and CLI tools
3. **Smart filtering** - Excludes workflow/setup files by default
4. **Odoo-focused analysis** - Performance rules only apply to Odoo-specific files

## 🎯 Quick Usage

### 1. Install Git Hooks (One-time setup)
```bash
./itms hooks install
```
This enables automatic code review on every commit.

### 2. Daily Workflow
```bash
# Start the main workflow
./itms workflow

# Or use individual commands:
./itms review           # AI code review (Odoo files only)
./itms setup            # Smart environment setup  
./itms workspace        # Create contextual workspace
```

### 3. For Active Development

1. **Select a task** in the workflow menu (option 2)
2. **Run smart setup** (option 11 or `./itms setup`)
3. **Develop** in the generated Cursor workspace
4. **Commit changes** - code review runs automatically

## 🔍 Code Review Options

```bash
# Review only Odoo files (recommended)
./itms review

# Review specific files
./itms review models/my_model.py views/my_views.xml

# Include all files (including setup scripts)
python3 code_review_integration.py --include-setup-files

# Review commit range
python3 code_review_integration.py --commit-range HEAD~3..HEAD
```

## 🏗️ Environment Setup Options

```bash
# Setup for current active task
./itms setup

# Setup for specific Monday.com task
./itms setup 123456789

# Just analyze requirements (no setup)
python3 contextual_dev_environment.py --analyze

# Open existing workspace
python3 contextual_dev_environment.py --open-workspace
```

## 🎯 What Gets Analyzed

### Code Review Focuses On:
- **Security**: Hardcoded passwords, SQL injection, dangerous sudo usage
- **Performance**: N+1 queries, missing field optimization (Odoo files only)
- **Odoo Patterns**: Model naming, required fields, view patterns (Odoo files only)
- **Quality**: Actual debug code (not normal CLI prints)

### Automatically Excluded:
- Workflow/setup scripts (`itms_workflow.py`, `itms_setup.py`, etc.)
- Archive folders and git files
- Node modules and Python cache files

### Environment Setup Detects:
- **Task types** from Monday.com descriptions (reporting, accounting, inventory, etc.)
- **Required dependencies** based on task content
- **Appropriate module structure** for the task type
- **Related tasks** in the same Monday.com group

## 💡 Pro Tips

1. **Use Git hooks** for seamless integration - they catch issues before code reaches the repository
2. **Start with task analysis** (`./itms analyze`) to understand scope before coding
3. **Let the system generate workspaces** - they include proper Odoo configurations
4. **Review suggestions** - the system finds related tasks and dependencies you might miss
5. **Trust the filtering** - by default, only relevant files are analyzed

## 🛠️ Troubleshooting

### Code Review Issues
```bash
# If too many false positives:
python3 code_review_integration.py --odoo-only

# If missing important files:
python3 code_review_integration.py --include-setup-files

# Check what files are being analyzed:
python3 code_review_integration.py --files path/to/your/file.py
```

### Environment Setup Issues
```bash
# Check Monday.com connection:
python3 itms_workflow.py  # Try option 1

# Verify active task:
cat .active_task.json

# Check project context:
cat .project_context.json
```

### Git Hooks Issues
```bash
# Check status:
./itms hooks status

# Reinstall:
./itms hooks uninstall
./itms hooks install
```

## 🎉 What's Working Now

- ✅ **Code review** analyzes only relevant files with appropriate rules
- ✅ **Environment setup** creates contextual workspaces based on Monday.com tasks  
- ✅ **Git integration** automatically updates Monday.com with commit info
- ✅ **Task analysis** intelligently categorizes and suggests dependencies
- ✅ **CLI tools** provide quick access to all features
- ✅ **Smart filtering** reduces noise and focuses on what matters

The system now provides intelligent development assistance without overwhelming you with false positives!

---

*Next time you start working on a Monday.com task, just run `./itms setup` and let the AI configure everything for you.*