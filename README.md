# ITMS Developer Setup

**Complete Monday.com + GitHub + Context7 Integration for ITMS Development Team**

A comprehensive development workflow automation tool that integrates Monday.com project management, GitHub development tracking, and Context7 intelligent memory following the proven patterns of ITMS Odoo management scripts.

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/itmsgroup-au/itms-developer-setup.git
cd itms-developer-setup
./manage-dev.sh init
```

### 2. Configure Environment
```bash
cp .env.template .env
# Edit .env with your API tokens and settings
```

### 3. Test Integration
```bash
./manage-dev.sh test
```

### 4. Start Development
```bash
./manage-dev.sh dashboard
```

## 📋 Main Interface - `manage-dev.sh`

Following the proven pattern of `manage-odoo.sh`, this script provides a clear command interface:

### 🔧 Setup Commands
```bash
./manage-dev.sh init                 # Initialize ITMS Developer Setup
./manage-dev.sh test                 # Test all integrations
./manage-dev.sh dashboard            # Show development dashboard
```

### 📋 Task Management
```bash
./manage-dev.sh show-tasks           # Show current tasks
./manage-dev.sh pull-tasks           # Pull tasks from Monday.com
./manage-dev.sh create-task [title]  # Create new task (interactive if no title)
./manage-dev.sh update-task [id]     # Update task progress (interactive if no id)
```

### 💻 Development Workflow
```bash
./manage-dev.sh commit-task [id]     # Commit changes to specific task
./manage-dev.sh sync [direction]     # Sync Monday ↔ GitHub
```

### 🔧 Odoo Development
```bash
./manage-dev.sh odoo-module [name]   # Create Odoo module workflow
./manage-dev.sh odoo-upgrade [modules] # Create Odoo upgrade project
```

### 📊 Monitoring
```bash
./manage-dev.sh status               # Show integration status
./manage-dev.sh logs                 # Show recent activity logs
```

## 🎯 Key Features

### ✅ **Clear Task Management**
- Pull tasks from Monday.com board
- Interactive task creation and updates
- Status tracking with progress indicators
- Priority and type classification

### ✅ **Git Commit Integration**
- Link commits directly to Monday.com tasks
- Automatic task updates with commit information
- Interactive commit workflow
- Commit history tracking by task

### ✅ **Monday.com Board Integration**
- **Board**: [Development Tasks](https://itmsgroup-squad.monday.com/boards/7970370827/views/171097174)
- Automated task creation and updates
- Status synchronization
- Progress tracking with notes

### ✅ **GitHub Repository Integration**
- **Repository**: [itmsgroup-au/itms-developer-setup](https://github.com/itmsgroup-au/itms-developer-setup)
- Issue creation and linking
- Pull request tracking
- Bidirectional sync with Monday.com

### ✅ **Context7 Intelligent Memory**
- ITMS development standards integration
- Workflow pattern memory
- Intelligent assistance via Claude Code

## 📊 Examples

### Create and Work on a Task
```bash
# Create new task
./manage-dev.sh create-task "Fix user authentication bug" "Security issue in login" high

# Work on the task...
# Make code changes

# Commit to task
./manage-dev.sh commit-task 12345 "Implemented secure password validation"

# Update task progress
./manage-dev.sh update-task 12345 "In Review" 90 "Ready for testing"
```

### Odoo Module Development
```bash
# Create complete Odoo module workflow
./manage-dev.sh odoo-module itms_customer_portal enhancement high

# This creates:
# ✅ Monday.com task with timeline
# ✅ GitHub issues for development phases
# ✅ Local module structure
# ✅ Testing checklist
```

### Sync Platforms
```bash
# Sync Monday tasks to GitHub issues
./manage-dev.sh sync to-github

# Sync GitHub issues to Monday tasks
./manage-dev.sh sync to-monday

# Bidirectional sync
./manage-dev.sh sync both
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Monday.com Configuration - Development Board
MONDAY_API_TOKEN=your_monday_api_token
MONDAY_BOARD_ID=7970370827
MONDAY_BOARD_URL=https://itmsgroup-squad.monday.com/boards/7970370827/views/171097174

# GitHub Configuration - ITMS Group
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username
GITHUB_ORG=itmsgroup-au
GITHUB_REPO=itmsgroup-au/itms-developer-setup

# Context7 Configuration
CONTEXT7_API_KEY=your_context7_api_key

# Developer Settings
DEVELOPER_NAME=Your Name
DEVELOPER_EMAIL=your.email@itmsgroup.com.au
```

### Required API Tokens

#### Monday.com API Token
1. Go to [Monday.com API](https://auth.monday.com/oauth2/authorize?client_id=YOUR_CLIENT_ID)
2. Generate API token with read/write permissions
3. Add to `.env` as `MONDAY_API_TOKEN`

#### GitHub Personal Access Token
1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Generate token with `repo`, `issues`, and `pull_requests` permissions
3. Add to `.env` as `GITHUB_TOKEN`

#### Context7 API Key
1. Visit [Context7 Dashboard](https://context7.com/dashboard)
2. Create account and generate API key
3. Add to `.env` as `CONTEXT7_API_KEY`

## 📁 Project Structure

```
itms-developer-setup/
├── manage-dev.sh              # Main management script (like manage-odoo.sh)
├── .env                       # Environment configuration
├── .env.template              # Configuration template
├── requirements.txt           # Python dependencies
├── scripts/                   # Python integration scripts
│   ├── monday_integration.py  # Monday.com API client
│   ├── task_manager.py        # Task management interface
│   ├── git_integration.py     # Git commit to task linking
│   ├── github_integration.py  # GitHub API client
│   └── status_checker.py      # Integration status checker
└── README.md                  # This file
```

## 🎯 ITMS Development Standards

This setup enforces ITMS quality standards:

### **Code Quality**
- Black formatting: 100% compliance
- Pylint score: 8.5+ target
- Security scanning: 0 high/critical vulnerabilities
- Test coverage: 70%+ for critical modules

### **Testing Hierarchy**
1. **Installation** (100% automated) - Module loads without errors
2. **Functionality** (85% automated) - Core features work correctly
3. **Integration** (60% automated) - Cross-module compatibility  
4. **UI/UX** (30% automated) - User interface validation

### **Workflow Standards**
- Every commit linked to a Monday.com task
- Task progress tracked automatically
- Quality validation on every change
- Documentation following OCA standards

## 🌐 Access URLs

- **Monday.com Board**: https://itmsgroup-squad.monday.com/boards/7970370827/views/171097174
- **GitHub Repository**: https://github.com/itmsgroup-au/itms-developer-setup

## 🔧 Troubleshooting

### Common Issues

**Monday.com Connection Issues**
```bash
./manage-dev.sh test
# Check MONDAY_API_TOKEN in .env
```

**GitHub Authentication Issues**
```bash
# Check GITHUB_TOKEN in .env
# Ensure token has correct permissions
```

**Git Integration Issues**
```bash
# Ensure you're in a git repository
git status
# Check for uncommitted changes
```

### Support

For issues with this setup:
1. Check the status: `./manage-dev.sh status`
2. Test integrations: `./manage-dev.sh test`
3. Review logs: `./manage-dev.sh logs`
4. Create issue in GitHub repository

## 🚀 Benefits

### **For Developers**
- **Clear Interface**: Single script for all operations (like manage-odoo.sh)
- **Integrated Workflow**: Seamless Monday.com + GitHub + Git integration
- **Quality Enforcement**: ITMS standards built into every step
- **Time Saving**: Automated task creation and updates

### **For Project Management**
- **Real-time Tracking**: Automatic task updates from commits
- **Clear Visibility**: Development progress in Monday.com
- **Quality Metrics**: Built-in quality and progress tracking
- **Team Collaboration**: Integrated GitHub and Monday.com workflows

### **For Code Quality**
- **ITMS Standards**: Enforced automatically
- **Testing Integration**: 4-level testing hierarchy
- **Documentation**: OCA-compliant documentation generation
- **Security**: Built-in vulnerability scanning

---

**🎉 Ready to transform your ITMS development workflow!**

This setup provides the same clear, organized approach as the proven `manage-odoo.sh` script, but extended to cover complete project management and development workflow automation.