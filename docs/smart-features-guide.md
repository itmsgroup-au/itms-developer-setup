# 🤖 ITMS Smart Development Features

## Overview

The ITMS Developer Setup now includes two powerful AI-powered features that transform your development workflow:

1. **Smart Code Review Integration** - AI-powered code review with Odoo pattern recognition
2. **Contextual Development Environment** - Auto-configure IDE workspace based on Monday.com tasks

## 🔍 Smart Code Review Integration

### Features
- **AI-powered code analysis** with Odoo-specific patterns
- **Security vulnerability detection** (hardcoded passwords, SQL injection risks, etc.)
- **Performance optimization suggestions** (N+1 queries, batch operations)
- **Odoo convention compliance** (model naming, view patterns, security rules)
- **Automatic Monday.com task updates** with review results
- **Pre-commit hooks** that prevent bad code from being committed

### Usage

#### Manual Code Review
```bash
# Review current changes
python3 code_review_integration.py

# Review specific files
python3 code_review_integration.py --files models/my_model.py views/my_views.xml

# Review commit range
python3 code_review_integration.py --commit-range HEAD~3..HEAD

# Save report and update Monday.com
python3 code_review_integration.py --save-report --update-monday
```

#### Through Workflow Menu
Use option `12. 🔍 AI Code Review` in the main workflow menu.

#### Git Hooks (Recommended)
```bash
# Install smart Git hooks
python3 setup_git_hooks.py install

# Check status
python3 setup_git_hooks.py status

# Uninstall if needed
python3 setup_git_hooks.py uninstall
```

### Security Rules Detected
- Hardcoded passwords and API keys
- SQL injection vulnerabilities
- Dangerous sudo() usage
- Debug code in production
- Exposed system fields

### Performance Rules
- N+1 query detection in loops
- Missing field selection optimizations
- Large recordset queries without limits
- Inefficient computed field patterns

### Odoo-Specific Rules
- Missing `_name` field in models
- Dangerous XPath patterns in views
- Missing required attributes in records
- Security access violations

## 🏗️ Contextual Development Environment

### Features
- **Intelligent task analysis** from Monday.com task descriptions
- **Auto-generated module structures** based on task requirements
- **Smart dependency detection** (accounting, inventory, sales, etc.)
- **Contextual Cursor workspaces** with proper Odoo configuration
- **Related task suggestions** and dependency analysis
- **One-click environment setup** for any Monday.com task

### Usage

#### Complete Environment Setup
```bash
# Setup environment for active task
python3 contextual_dev_environment.py --setup

# Setup for specific task
python3 contextual_dev_environment.py --task-id 123456789 --setup

# Open existing workspace
python3 contextual_dev_environment.py --open-workspace
```

#### Analysis Only
```bash
# Analyze current task requirements
python3 contextual_dev_environment.py --analyze

# Analyze specific task
python3 contextual_dev_environment.py --task-id 123456789 --analyze
```

#### Through Workflow Menu
- `11. 🤖 Smart Environment Setup` - Complete one-click setup
- `13. 📋 Analyze Task Requirements` - Analysis only
- `14. 🏗️ Create Contextual Workspace` - Workspace generation only
- `15. 🎯 Smart Task Suggestions` - Related tasks and dependencies

### Task Type Detection

The system automatically detects task types and configures accordingly:

#### 📊 Reporting Tasks
- **Keywords**: report, reporting, dashboard
- **Dependencies**: report_xlsx, web
- **Structure**: report/, wizard/ directories
- **Odoo Apps**: base, web

#### 💰 Accounting Tasks
- **Keywords**: invoice, billing, accounting
- **Dependencies**: account, account_invoicing
- **Odoo Apps**: account, sale, purchase

#### 📦 Inventory Tasks
- **Keywords**: inventory, stock, warehouse
- **Dependencies**: stock, stock_account
- **Odoo Apps**: stock, purchase, sale

#### 💼 Sales Tasks
- **Keywords**: sale, sales, crm, customer
- **Dependencies**: sale, crm
- **Odoo Apps**: sale_management, crm

#### 🛒 Purchase Tasks
- **Keywords**: purchase, vendor, supplier
- **Dependencies**: purchase
- **Odoo Apps**: purchase

#### 👥 HR Tasks
- **Keywords**: hr, employee, payroll
- **Dependencies**: hr, hr_payroll
- **Odoo Apps**: hr, hr_payroll

#### 🌐 Website Tasks
- **Keywords**: website, portal, web
- **Dependencies**: website, portal
- **Structure**: controllers/, static/src/ directories
- **Odoo Apps**: website

## 🚀 Integration with Existing Workflow

### Menu Changes
The main workflow menu now includes a dedicated "SMART DEVELOPMENT" section:

```
🚀 SMART DEVELOPMENT:
11. 🤖 Smart Environment Setup (AI-powered)
12. 🔍 AI Code Review  
13. 📋 Analyze Task Requirements
14. 🏗️ Create Contextual Workspace
15. 🎯 Smart Task Suggestions

✅ CODE QUALITY:
21. Format & lint code
22. Install Git hooks (Smart Review)
23. Quality check
```

### Automatic Integrations

#### Git Hooks
When installed, Git hooks automatically:
- Run code review on every commit attempt
- Validate commit message format
- Update Monday.com tasks with commit information
- Block commits with critical security issues

#### Monday.com Integration
- Code review results are automatically posted to active tasks
- Commit messages are enhanced with task information
- Task updates include code review summaries and commit links

#### Cursor Workspace Generation
Generated workspaces include:
- Proper Odoo addon paths
- Task-specific folder structure  
- Debugging configurations
- Recommended extensions
- Custom build/test tasks

## 📋 Best Practices

### Development Workflow
1. **Select active task** in workflow menu (option 2)
2. **Run smart environment setup** (option 11)
3. **Develop in generated workspace**
4. **Run code review** before committing (option 12)
5. **Commit changes** (hooks will handle the rest)

### Code Review Workflow
1. **Install Git hooks** once per repository (option 22)
2. Code review runs automatically on every commit
3. Fix any critical issues before commit succeeds
4. Monday.com tasks update automatically

### Task Analysis Workflow
1. **Analyze task requirements** (option 13) to understand scope
2. **Check smart suggestions** (option 15) for related work
3. **Create contextual workspace** (option 14) for focused development

## 🔧 Configuration

### Environment Variables
All existing environment variables in `.env` are respected. New features use:
- `MONDAY_API_TOKEN` - For task analysis and updates
- `GITHUB_TOKEN` - For repository integration
- Odoo paths from `config.yaml`

### Customization
Modify these files to customize behavior:
- `code_review_integration.py` - Add custom security/performance rules
- `contextual_dev_environment.py` - Add new task type detection
- `setup_git_hooks.py` - Customize hook behavior

## 🎯 Impact

### Smart Code Review Benefits
- **Higher code quality** through automated pattern detection
- **Automated compliance** with Odoo and security standards  
- **Better traceability** with automatic Monday.com updates
- **Reduced review time** by catching issues early

### Contextual Environment Benefits
- **Faster context switching** between different task types
- **Reduced setup time** with one-click environment configuration
- **Increased focus** with task-specific workspace configurations
- **Better project organization** with intelligent module structuring

## 🛠️ Troubleshooting

### Code Review Issues
```bash
# Check if tools are installed
pip install black ruff requests pyyaml python-dotenv

# Test code review manually
python3 code_review_integration.py --help
```

### Environment Setup Issues  
```bash
# Check Monday.com connection
python3 itms_workflow.py
# Select option 1 to verify task loading

# Check Odoo paths in config.yaml
cat config.yaml | grep -A5 paths
```

### Git Hook Issues
```bash
# Check hook status
python3 setup_git_hooks.py status

# Reinstall hooks
python3 setup_git_hooks.py uninstall
python3 setup_git_hooks.py install
```

## 📚 Examples

### Example: Setting up for Inventory Report Task

1. Task: "Create inventory aging report with Excel export"
2. System detects: `reporting` + `inventory` task types
3. Auto-generates:
   - `itms_inventory_aging_report/` module
   - Dependencies: `['base', 'stock', 'report_xlsx']`  
   - Workspace with report/ and wizard/ folders
   - Cursor tasks for testing and development

### Example: Code Review Results

```markdown
# 🔍 Smart Code Review Report
**Generated:** 2024-01-15T10:30:00
**Files Analyzed:** 3

## 📊 Summary
- 🔴 Critical: 1
- 🟠 High: 2  
- 🟡 Medium: 3
- 🔵 Low: 1
- **Total Issues:** 7

## 🔍 Detailed Findings
### 📄 models/inventory_report.py
**🔴 Critical Issues:**
- Line 45: Hardcoded password detected. Use environment variables.
  ```python
  password = "admin123"
  ```

**🟠 High Issues:**
- Line 67: Dangerous sudo usage. Verify security implications.
  ```python
  self.sudo().write({'status': 'done'})
  ```
```

---

*These smart features represent a significant advancement in the ITMS development workflow, providing AI-powered assistance that understands both your codebase and your Monday.com project management.*