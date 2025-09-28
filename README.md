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

- ✅ **Monday.com Integration** - Task management
- ✅ **AI Tool Support** - Claude, Cursor, KiloCode MCP
- ✅ **Code Quality** - Black + Ruff-Odoo
- ✅ **Git Automation** - Smart hooks and commits
- ✅ **Team Ready** - Shareable configurations

## 📋 Daily Workflow

1. **Check Tasks**: View Monday.com tasks
2. **Create Module**: Auto-generate Odoo modules with proper structure
3. **Code Quality**: Automatic formatting and linting
4. **Git Integration**: Smart commits linked to tasks

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

## 🛠️ Configuration Files

- `itms_setup.py` - Intelligent setup tool
- `itms_workflow.py` - Daily workflow assistant
- `config.yaml` - Team shared settings
- `.env` - Personal developer settings

## 📚 Documentation

See `docs/` folder for:
- Odoo upgrade framework
- Git commit guidelines
- Development standards

## 🆘 Support

For issues:
1. Check your `.env` file configuration
2. Run `python3 itms_setup.py` to re-setup
3. Verify API tokens are valid

---

*Built for ITMS Group development workflow*
