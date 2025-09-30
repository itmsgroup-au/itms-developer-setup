# 🎯 Project Nickname System

## Overview

The Project Nickname System allows you to switch between different projects using simple nicknames that automatically configure:

- **Monday.com Board & Group**
- **GitHub Repository**
- **Odoo Database & URL**
- **Cursor Workspace**
- **Environment Variables**

Instead of manually switching between configurations, just say **"switch to Canbrax"** and everything is configured automatically!

## 🚀 Quick Usage

### Switch to a Project
```bash
# Using CLI
./itms project canbrax

# Using workflow menu (option 5)
python3 itms_workflow.py
```

### List Available Projects
```bash
./itms project list
```

### Set Up New Project
```bash
./itms project setup
```

## 🛠️ Setup Example

Let's say you want to set up a project called "Canbrax":

```bash
./itms project setup
```

The wizard will ask for:
- **Nickname**: `canbrax`
- **Description**: `Canbrax Property Management System`
- **Monday Board ID**: `123456789`
- **Monday Board Name**: `Canbrax Development Board`
- **GitHub Repo**: `canbrax-odoo`
- **GitHub Owner**: `itmsgroup-au` (default)
- **Odoo Database**: `odoo_canbrax` (default)
- **Odoo URL**: `http://localhost:8018` (default)

## 🎯 What Gets Configured

When you switch to a project nickname, the system automatically:

### 1. Updates `.env` file
```bash
MONDAY_BOARD_ID=123456789
MONDAY_GROUP_ID=
MONDAY_GROUP_NAME=
GITHUB_REPO=canbrax-odoo
GITHUB_ORG=itmsgroup-au
ODOO_URL=http://localhost:8018
ODOO_DB=odoo_canbrax
```

### 2. Creates Project Context
```json
{
  "project_nickname": "canbrax",
  "board_id": "123456789",
  "board_name": "Canbrax Development Board",
  "repo_full_name": "itmsgroup-au/canbrax-odoo",
  "database": "odoo_canbrax",
  "updated_at": "2025-09-30T10:09:00"
}
```

### 3. Generates Cursor Workspace
- **Location**: `/Users/markshaw/Desktop/cursor-workspaces/canbrax.code-workspace`
- **Folders**: Project repo, Odoo core, Custom modules
- **Settings**: Python paths, Odoo configuration, extensions
- **Tasks**: Start Odoo for this specific project/database

### 4. Clears Active Task
- Switches project context completely
- Ready for new project work

## 🏗️ Advanced Features

### CLI Commands
```bash
# Quick project switching
./itms project canbrax
./itms project bigquery
./itms project test

# Management
./itms project list           # List all projects
./itms project setup          # Interactive setup wizard

# Direct CLI setup (advanced)
python3 src/project_nicknames.py add canbrax \
  --board-id 123456789 \
  --repo canbrax-odoo \
  --description "Canbrax Property Management"
```

### Workflow Integration
- **Option 5**: 🎯 Switch Project (by nickname)
- Shows available projects
- Interactive switching
- Automatic configuration reload

### Smart Environment Features
All smart development features now work with project context:
- **Smart Environment Setup** (option 12) uses project database
- **AI Code Review** (option 13) understands project context
- **Contextual Workspace** (option 15) creates project-specific workspaces

## 📋 Project Configuration Structure

Each project nickname stores:

```json
{
  "nickname": "canbrax",
  "description": "Canbrax Property Management System",
  "monday_board_id": "123456789",
  "monday_board_name": "Canbrax Development Board", 
  "monday_group_id": "",
  "monday_group_name": "",
  "github_repo": "canbrax-odoo",
  "github_owner": "itmsgroup-au",
  "odoo_database": "odoo_canbrax",
  "odoo_url": "http://localhost:8018",
  "workspace_path": "/Users/markshaw/Desktop/cursor-workspaces/canbrax.code-workspace",
  "created_at": "2025-09-30T10:00:00",
  "last_used": "2025-09-30T10:09:00"
}
```

## 🎉 Benefits

### 1. **One-Command Project Switching**
No more manually updating multiple configuration files

### 2. **Consistent Workspace Setup**
Every project gets a properly configured Cursor workspace

### 3. **Context Awareness**
All smart development features understand your current project

### 4. **Team Collaboration**
Share project nicknames across team members

### 5. **Mistake Prevention**
No more accidentally working on wrong database/repo

## 💡 Best Practices

### Naming Convention
- Use lowercase, descriptive nicknames
- Examples: `canbrax`, `bigquery`, `stairmaster`, `qlm`

### Project Setup
1. Set up the project nickname first
2. Switch to the project: `./itms project projectname`
3. Select an active task in the workflow
4. Use smart environment setup (option 12)
5. Start developing with contextual workspace

### Workspace Organization
- All workspaces are stored in `/Users/markshaw/Desktop/cursor-workspaces/`
- Each project gets its own `.code-workspace` file
- Workspaces include project-specific Odoo configurations

## 🔄 Migration from Manual Setup

If you have existing cursor workspaces, you can:

1. **Set up project nicknames** for your existing projects
2. **Migrate existing workspaces** to the new naming convention
3. **Use the new system** for consistent project switching

The system integrates seamlessly with your existing development workflow while adding powerful automation on top.

---

*This system transforms project switching from a manual, error-prone process into a single command that configures everything correctly.*