# ITMS MCP Server Configuration

## Quick Setup for Cursor

To configure the ITMS Task Master MCP server in Cursor:

1. **Open Cursor Settings**
   - Go to `Cursor > Settings` (or `Ctrl/Cmd + ,`)

2. **Navigate to MCP Servers**
   - Search for "MCP" in settings
   - Find "MCP Servers" section

3. **Add the ITMS Task Master Server**
   ```json
   {
     "itms-task-master": {
       "command": "python3",
       "args": ["/Users/markshaw/Desktop/git/itms-developer-setup/itms_mcp_server.py"],
       "env": {}
     }
   }
   ```

   **Note:** The `itms_mcp_server.py` file is in the **root directory**, not in `utils/`.

4. **Restart Cursor**
   - Close and reopen Cursor for the MCP server to be available

## Environment Variables Required

Make sure your `.env` file contains:
```
MONDAY_API_TOKEN=your_monday_token
MONDAY_BOARD_ID=your_board_id
GITHUB_TOKEN=your_github_token
```

## Available Tools

Once configured, the following tools will be available in Claude:

- `get_monday_tasks` - Get assigned Monday.com tasks
- `select_active_task` - Set a task as active for workflow
- `create_subtasks` - Create intelligent sub-tasks
- `execute_subtask` - Execute specific sub-tasks with AI guidance
- `complete_subtask` - Mark sub-tasks as complete
- `workflow_status` - Get current workflow status
- `set_working_board` - Set active Monday board
- `set_working_group` - Filter tasks by group
- `set_working_repo` - Set active GitHub repo

## Troubleshooting

If you see a red dot (disconnected):
1. Check that Python 3 is available in your PATH
2. Verify the file path is correct
3. Ensure .env file exists with required tokens
4. Check Cursor's developer console for error messages