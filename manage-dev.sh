#!/bin/bash

# ITMS Developer Setup Management Script
# Usage: ./manage-dev.sh [COMMAND] [ARGS...]

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Header
print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║             ITMS Developer Setup                 ║${NC}"
    echo -e "${BLUE}║    Monday.com + GitHub + Context7 Integration    ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Python 3 found${NC}"
    fi
    
    # Check required Python packages
    python3 -c "import requests, dotenv" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Required Python packages installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Installing required Python packages...${NC}"
        pip3 install requests python-dotenv monday
    fi
    
    # Check .env file
    if [ -f .env ]; then
        echo -e "${GREEN}✅ Environment configuration found${NC}"
    else
        echo -e "${RED}❌ .env file not found. Copy .env.template to .env and configure${NC}"
        return 1
    fi
    
    echo ""
}

# Function to test integrations
test_integrations() {
    print_header
    echo -e "${BLUE}🧪 Testing Integrations...${NC}"
    echo ""
    
    # Test Monday.com
    echo -e "${CYAN}📋 Testing Monday.com connection...${NC}"
    python3 "$PYTHON_SCRIPTS_DIR/monday_integration.py" test-connection
    echo ""
    
    # Test GitHub
    echo -e "${CYAN}🐙 Testing GitHub connection...${NC}"
    python3 "$PYTHON_SCRIPTS_DIR/github_integration.py" test-connection
    echo ""
    
    # Test Context7
    echo -e "${CYAN}🧠 Testing Context7 connection...${NC}"
    python3 "$PYTHON_SCRIPTS_DIR/context7_integration.py" test-connection
    echo ""
}

# Function to show current tasks
show_tasks() {
    print_header
    echo -e "${BLUE}📋 Current Development Tasks${NC}"
    echo ""
    
    python3 "$PYTHON_SCRIPTS_DIR/task_manager.py" show-current
}

# Function to pull tasks from Monday
pull_tasks() {
    print_header
    echo -e "${BLUE}📥 Pulling Tasks from Monday.com${NC}"
    echo ""
    
    python3 "$PYTHON_SCRIPTS_DIR/task_manager.py" pull-from-monday
}

# Function to create new task
create_task() {
    print_header
    echo -e "${BLUE}➕ Create New Development Task${NC}"
    echo ""
    
    if [ -z "$2" ]; then
        echo -e "${YELLOW}Usage: $0 create-task \"Task Title\" [description] [priority]${NC}"
        echo ""
        echo -e "${CYAN}Interactive mode:${NC}"
        python3 "$PYTHON_SCRIPTS_DIR/task_manager.py" create-interactive
    else
        TASK_TITLE="$2"
        DESCRIPTION="$3"
        PRIORITY="$4"
        python3 "$PYTHON_SCRIPTS_DIR/task_manager.py" create-task "$TASK_TITLE" "$DESCRIPTION" "$PRIORITY"
    fi
}

# Function to update task progress
update_task() {
    print_header
    echo -e "${BLUE}📝 Update Task Progress${NC}"
    echo ""
    
    if [ -z "$2" ]; then
        echo -e "${CYAN}Interactive mode:${NC}"
        python3 "$PYTHON_SCRIPTS_DIR/task_manager.py" update-interactive
    else
        TASK_ID="$2"
        STATUS="$3"
        PROGRESS="$4"
        NOTES="$5"
        python3 "$PYTHON_SCRIPTS_DIR/task_manager.py" update-task "$TASK_ID" "$STATUS" "$PROGRESS" "$NOTES"
    fi
}

# Function to commit with task linking
commit_to_task() {
    print_header
    echo -e "${BLUE}💾 Commit Changes to Task${NC}"
    echo ""
    
    if [ -z "$2" ]; then
        echo -e "${CYAN}Interactive mode:${NC}"
        python3 "$PYTHON_SCRIPTS_DIR/git_integration.py" commit-interactive
    else
        TASK_ID="$2"
        COMMIT_MESSAGE="$3"
        python3 "$PYTHON_SCRIPTS_DIR/git_integration.py" commit-to-task "$TASK_ID" "$COMMIT_MESSAGE"
    fi
}

# Function to sync Monday and GitHub
sync_platforms() {
    print_header
    echo -e "${BLUE}🔄 Syncing Monday.com ↔ GitHub${NC}"
    echo ""
    
    DIRECTION="${2:-both}"
    python3 "$PYTHON_SCRIPTS_DIR/sync_manager.py" sync "$DIRECTION"
}

# Function to create Odoo module workflow
create_odoo_module() {
    print_header
    echo -e "${BLUE}🔧 Create Odoo Module Workflow${NC}"
    echo ""
    
    if [ -z "$2" ]; then
        echo -e "${CYAN}Interactive mode:${NC}"
        python3 "$PYTHON_SCRIPTS_DIR/odoo_workflow.py" create-interactive
    else
        MODULE_NAME="$2"
        MODULE_TYPE="${3:-enhancement}"
        PRIORITY="${4:-medium}"
        python3 "$PYTHON_SCRIPTS_DIR/odoo_workflow.py" create-module "$MODULE_NAME" "$MODULE_TYPE" "$PRIORITY"
    fi
}

# Function to create upgrade project
create_upgrade() {
    print_header
    echo -e "${BLUE}🔄 Create Odoo Upgrade Project${NC}"
    echo ""
    
    if [ -z "$2" ]; then
        echo -e "${CYAN}Interactive mode:${NC}"
        python3 "$PYTHON_SCRIPTS_DIR/odoo_workflow.py" upgrade-interactive
    else
        MODULES="$2"
        FROM_VERSION="${3:-18.0}"
        TO_VERSION="${4:-19.0}"
        python3 "$PYTHON_SCRIPTS_DIR/odoo_workflow.py" create-upgrade "$MODULES" "$FROM_VERSION" "$TO_VERSION"
    fi
}

# Function to show development dashboard
show_dashboard() {
    print_header
    echo -e "${BLUE}📊 Development Dashboard${NC}"
    echo ""
    
    python3 "$PYTHON_SCRIPTS_DIR/dashboard.py" show-full
}

# Function to initialize repository
init_repo() {
    print_header
    echo -e "${BLUE}🚀 Initializing ITMS Developer Setup${NC}"
    echo ""
    
    # Check if git repo
    if [ ! -d .git ]; then
        echo -e "${YELLOW}Initializing git repository...${NC}"
        git init
        git add .
        git commit -m "Initial ITMS Developer Setup

🚀 Features:
- Monday.com integration for task management
- GitHub integration for development tracking  
- Context7 intelligent memory
- Odoo workflow automation
- Clear command interface

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
    fi
    
    # Setup Python virtual environment
    if [ ! -d venv ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    
    # Test integrations
    echo -e "${YELLOW}Testing integrations...${NC}"
    source venv/bin/activate
    python3 "$PYTHON_SCRIPTS_DIR/setup_validator.py"
    deactivate
    
    echo -e "${GREEN}✅ ITMS Developer Setup initialized successfully!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "1. Configure .env file with your API tokens"
    echo -e "2. Run: ./manage-dev.sh test"
    echo -e "3. Run: ./manage-dev.sh dashboard"
}

# Function to show usage
show_usage() {
    print_header
    echo -e "${BLUE}Usage: $0 [COMMAND] [ARGS...]${NC}"
    echo ""
    echo -e "${BLUE}🔧 Setup Commands:${NC}"
    echo "  init                 - Initialize ITMS Developer Setup"
    echo "  test                 - Test all integrations"
    echo "  dashboard            - Show development dashboard"
    echo ""
    echo -e "${BLUE}📋 Task Management:${NC}"
    echo "  show-tasks           - Show current tasks"
    echo "  pull-tasks           - Pull tasks from Monday.com"
    echo "  create-task [title]  - Create new task (interactive if no title)"
    echo "  update-task [id]     - Update task progress (interactive if no id)"
    echo ""
    echo -e "${BLUE}💻 Development Workflow:${NC}"
    echo "  commit-task [id]     - Commit changes to specific task"
    echo "  sync [direction]     - Sync Monday ↔ GitHub (both/to-github/to-monday)"
    echo ""
    echo -e "${BLUE}🔧 Odoo Development:${NC}"
    echo "  odoo-module [name]   - Create Odoo module workflow"
    echo "  odoo-upgrade [modules] - Create Odoo upgrade project"
    echo ""
    echo -e "${BLUE}📊 Monitoring:${NC}"
    echo "  status               - Show integration status"
    echo "  logs                 - Show recent activity logs"
    echo ""
    echo -e "${BLUE}🌐 Board URLs:${NC}"
    echo "  Monday.com: https://itmsgroup-squad.monday.com/boards/7970370827"
    echo "  GitHub: https://github.com/itmsgroup-au/itms-developer-setup"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 create-task \"Fix login bug\" \"Security issue\" high"
    echo "  $0 odoo-module itms_new_feature enhancement high"
    echo "  $0 commit-task 12345 \"Implemented user authentication\""
    echo "  $0 sync both"
}

# Function to show logs
show_logs() {
    print_header
    echo -e "${BLUE}📜 Recent Activity Logs${NC}"
    echo ""
    
    python3 "$PYTHON_SCRIPTS_DIR/log_viewer.py" show-recent
}

# Function to show status
show_status() {
    print_header
    echo -e "${BLUE}📊 Integration Status${NC}"
    echo ""
    
    python3 "$PYTHON_SCRIPTS_DIR/status_checker.py"
}

# Main script logic
case "$1" in
    init) init_repo ;;
    test) test_integrations ;;
    dashboard) show_dashboard ;;
    show-tasks) show_tasks ;;
    pull-tasks) pull_tasks ;;
    create-task) create_task "$@" ;;
    update-task) update_task "$@" ;;
    commit-task) commit_to_task "$@" ;;
    sync) sync_platforms "$@" ;;
    odoo-module) create_odoo_module "$@" ;;
    odoo-upgrade) create_upgrade "$@" ;;
    status) show_status ;;
    logs) show_logs ;;
    *) show_usage ;;
esac