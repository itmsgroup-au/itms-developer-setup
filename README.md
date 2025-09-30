# 🚀 ITMS Developer Setup

> **Production-ready Odoo development environment with AI integration**

## ⚡ Quick Start

### 1. Setup (One-time)
```bash
git clone <this-repo>
cd itms-developer-setup
python3 itms_setup.py
```

### 2. Configure
```bash
# Copy and edit environment file
cp templates/.env.template .env
# Edit .env with your paths and API tokens
```

### 3. Daily Workflow
```bash
# Launch workflow assistant
python3 itms_workflow.py
```

## 🔧 Features

- ✅ **Monday.com Integration** - Task management and auto-updates
- ✅ **AI Tool Support** - Claude, Cursor, KiloCode MCP
- ✅ **Code Quality** - Black + Ruff-Odoo + AI-powered code review
- ✅ **Git Automation** - Smart hooks and commits with Monday.com sync
- ✅ **Team Ready** - Shareable configurations
- 🆕 **Smart Code Review** - AI-powered security, performance, and Odoo pattern analysis
- 🆕 **Contextual Environment** - Auto-configure workspaces based on Monday.com tasks

## 📋 Daily Workflow

1. **Check Tasks**: View Monday.com tasks
2. **Smart Setup**: AI-powered environment configuration for tasks
3. **Create Module**: Auto-generate Odoo modules with contextual structure
4. **Code Quality**: AI-powered review with security and performance analysis
5. **Git Integration**: Smart commits with automatic Monday.com updates

## 🚀 New Smart Features

### Quick CLI Access
```bash
# Quick access to any feature
./itms workflow              # Main menu
./itms review               # AI code review  
./itms setup                # Smart environment setup
./itms hooks install        # Install Git hooks
```

### Smart Code Review Integration
- **AI-powered analysis** of security, performance, and Odoo patterns
- **Pre-commit hooks** that prevent bad code
- **Automatic Monday.com updates** with review results
- **Contextual suggestions** based on your codebase

### Contextual Development Environment  
- **Intelligent task analysis** from Monday.com descriptions
- **Auto-generated workspaces** with proper Odoo configuration
- **Smart dependency detection** (accounting, inventory, sales, etc.)
- **One-click environment setup** for any task context

## 🤖 AI Integration

The setup automatically configures:
- **Claude Desktop** MCP servers
- **Cursor** with ITMS guidelines
- **KiloCode** Fast-Grok integration
- **Context7** memory system

## 🏢 Team Sharing

Each developer:
1. Clones this repository
2. Runs `python3 itms_setup.py`
3. Customizes their `.env` file
4. Starts with `python3 itms_workflow.py`

## 📁 Project Structure

```
itms-developer-setup/
├── src/                    # Smart development features
│   ├── code_review_integration.py     # AI code review
│   ├── contextual_dev_environment.py  # Smart environments  
│   └── setup_git_hooks.py             # Git integration
├── utils/                  # Utility scripts
│   ├── project_context.py             # Context management
│   ├── project_setup_wizard.py        # Setup wizard
│   └── odoo_log_viewer.py             # Log viewer
├── config/                 # Configuration files
│   ├── config.yaml                    # Main configuration
│   ├── .env                          # Personal settings
│   └── pyproject.toml                # Python config
├── docs/                   # Documentation
│   ├── SMART_FEATURES.md             # New AI features guide
│   ├── QUICK_START_GUIDE.md          # Usage guide
│   └── ...                          # Other docs
├── itms                    # CLI entry point
├── itms_workflow.py        # Main workflow assistant
├── itms_setup.py          # Initial setup tool
└── itms_mcp_server.py     # MCP server
```

## 🛠️ Core Files

- `itms` - CLI for quick access to all features
- `itms_workflow.py` - Main daily workflow assistant
- `itms_setup.py` - Intelligent initial setup tool
- `src/` - Smart AI-powered development features
- `config/config.yaml` - Team shared settings

## 🆘 Support

For issues:
1. Check your `.env` file configuration
2. Run `python3 itms_setup.py` to re-setup
3. Verify API tokens are valid

---

*Built for ITMS Group development workflow*
