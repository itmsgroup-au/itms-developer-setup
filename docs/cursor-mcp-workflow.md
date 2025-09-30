# ITMS Cursor MCP Workflow Guide

## Overview

Your enhanced ITMS workflow is now fully integrated with Cursor via MCP (Model Context Protocol). This creates a powerful AI-assisted development environment that combines Monday.com task management, Context7 memories, Odoo guidelines, and intelligent sub-task creation.

## MCP Servers Available in Cursor

After restarting Cursor, you'll have access to these MCP servers:

### 1. 🚀 **itms-task-master** (NEW!)
**Your intelligent task management system**
- Get assigned Monday.com tasks
- Create intelligent sub-tasks using Context7 + Odoo guidelines
- Execute sub-tasks with AI assistance
- Auto-update Monday.com status

### 2. 🗄️ **postgresql**
- Query your PostgreSQL databases
- Execute SQL commands safely

### 3. 🔧 **odoo & odoo-browse**
- Browse Odoo models and records
- Query Odoo data directly from Cursor

### 4. 📚 **context7**
- Search documentation and memories
- Access past implementations and patterns

### 5. ⚙️ **itms-workflow** (Original)
- Basic Monday.com integration
- GitHub repository management

## Your Enhanced Daily Workflow

### Phase 1: Task Assignment & Analysis

1. **In Cursor, use the itms-task-master tools:**

```
Ask Claude: "Show me my assigned Monday.com tasks"
```

This triggers: `get_assigned_tasks()` 
- Fetches tasks assigned to "Mark Shaw"
- Shows task names, IDs, priorities, and latest updates

2. **Select your active task:**

```
Ask Claude: "Set task [TASK_ID] as my active task"
```

This triggers: `select_active_task(task_id)`
- Pulls full task details from Monday.com
- Shows description, updates, and context
- Marks as active for sub-task creation

### Phase 2: Intelligent Sub-task Creation

3. **Create intelligent sub-tasks:**

```
Ask Claude: "Analyze my active task and create sub-tasks"
```

This triggers: `create_subtasks()`
- **Analyzes task content** using Context7 memories
- **Applies Odoo development guidelines** from your docs
- **References past implementations** and patterns
- **Creates structured sub-tasks** in Monday.com:
  - `[Analysis]` - Research and requirements
  - `[Design]` - Technical design and planning  
  - `[Development]` - Core implementation
  - `[Testing]` - Testing and validation
  - `[Documentation]` - Documentation updates

**Sub-tasks are automatically created with:**
- Proper priorities (Critical/High/Medium)
- Estimated hours
- Detailed descriptions
- Links to parent task

### Phase 3: AI-Assisted Execution

4. **Execute sub-tasks with AI assistance:**

```
Ask Claude: "Help me execute sub-task [SUBTASK_ID]"
```

This triggers: `execute_subtask(subtask_id)`
- Updates Monday.com status to "Working on it"
- Provides **context-aware guidance** based on task type
- Suggests specific next steps and best practices
- Ready for AI agent collaboration

5. **Complete sub-tasks:**

```
Ask Claude: "Mark sub-task [SUBTASK_ID] as complete with notes: [COMPLETION_NOTES]"
```

This triggers: `complete_subtask(subtask_id, completion_notes)`
- Updates Monday.com status to "Done"
- Adds completion notes and timestamps
- Tracks progress automatically

## Example Conversation Flow

```
You: "Show me my assigned tasks"

Claude: 📋 Your Assigned Tasks (3):

1. **[Odoo] Implement inventory tracking module** (ID: 12345)
   Status: Not Started
   Priority: High
   Latest: Need to integrate with existing warehouse system...

2. **[Bug] Fix user authentication timeout** (ID: 12346)
   Status: Working on it  
   Priority: Critical
   Latest: Users reporting session timeouts after 15 minutes...

---

You: "Set task 12345 as my active task"

Claude: 🎯 Active Task Set: [Odoo] Implement inventory tracking module

**ID**: 12345
**Status**: Not Started
**Board**: ITMS Development

**Details**:
- Priority: High
- Assignee: Mark Shaw
- Due Date: Next Friday

**Recent Updates** (2):
- **Product Manager** (2024-09-29): Need integration with warehouse system
- **Team Lead** (2024-09-28): This should follow our standard Odoo patterns

✅ Task is now active and ready for sub-task creation using `create_subtasks`

---

You: "Analyze this task and create intelligent sub-tasks"

Claude: ✅ Created 5 Sub-tasks for: [Odoo] Implement inventory tracking module

1. **[Analysis] Research requirements for inventory tracking** (ID: 12350)
2. **[Design] Create technical design for inventory tracking** (ID: 12351)  
3. **[Development] Implement core functionality for inventory tracking** (ID: 12352)
4. **[Testing] Test and validate inventory tracking** (ID: 12353)
5. **[Documentation] Document inventory tracking** (ID: 12354)

🎯 Sub-tasks are ready for execution using `execute_subtask`
📋 View all tasks on Monday.com board: 18059344134

---

You: "Help me execute the analysis sub-task 12350"

Claude: 🚀 Executing Subtask: [Analysis] Research requirements for inventory tracking

**ID**: 12350
**Status**: Updated to 'Working on it'

**Description**: Analyze task requirements, review existing code, and plan implementation approach

**Guidance**:
1. Review existing codebase and related files
2. Check Monday.com for additional requirements  
3. Research similar implementations
4. Document findings in task updates

💡 Use `complete_subtask` when finished to update status and commit changes
```

## Integration with Context7 & Odoo Guidelines

The system automatically leverages:

- **Context7 memories**: Past implementations, solutions, and patterns
- **Odoo integration guide**: Your development best practices
- **Project context**: Current board, repo, and environment settings
- **PRD information**: Product requirements and specifications

## Advanced Features

### Workflow Status
```
Ask Claude: "What's my current workflow status?"
```
Shows active tasks, configuration, and next recommended actions.

### Custom Task Types
The system recognizes task patterns:
- **Odoo tasks**: Gets Odoo-specific sub-task breakdown
- **Bug fixes**: Focuses on debugging and testing steps  
- **Features**: Emphasizes design and implementation phases

### Auto-context Updates
When you switch projects (boards/repos), all task assignments automatically update to reflect the new context.

## Setup Required

1. **Restart Cursor** to load the new MCP servers
2. **Verify green status** for all MCP servers in Cursor settings
3. **Start using** the task-master tools in your conversations

## Quick Reference Commands

| Action | Ask Claude |
|--------|------------|
| View assigned tasks | "Show me my assigned Monday.com tasks" |
| Set active task | "Set task [ID] as active" |
| Create sub-tasks | "Create sub-tasks for my active task" |
| Execute sub-task | "Help me execute sub-task [ID]" |
| Complete sub-task | "Mark sub-task [ID] as complete" |
| Check workflow status | "What's my current workflow status?" |

## Benefits

✅ **Intelligent task breakdown** based on past experience
✅ **Context-aware guidance** for each development phase  
✅ **Automatic Monday.com updates** and progress tracking
✅ **AI-assisted execution** with Claude's full capabilities
✅ **Seamless integration** with your existing tools and workflows
✅ **Knowledge retention** via Context7 and Odoo guidelines

Your development workflow is now supercharged with AI! 🚀