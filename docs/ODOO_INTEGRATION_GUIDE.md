# Odoo Integration Guide

Complete guide for ITMS Odoo development environment with AI integration.

## Overview

Your ITMS setup has **two complementary** Odoo integrations working together:

### 🔧 **1. Your Daily Odoo Management (`manage-odoo.sh`)**

**Purpose:** Start, stop, and manage your actual Odoo server instances

**What it does:**

- Starts/stops Odoo 18/19 Enterprise/Community
- Manages different ports (8018, 8019, 8021, 8022)
- Handles virtual environments and configurations
- Shows server status and logs

**Access:**

- Direct: `/Users/markshaw/Desktop/git/odoo/manage-odoo.sh status`
- Via workflow: `python3 itms_workflow.py` → Option 15: 🔧 Manage Odoo instances

**Instances:**

- **Enterprise 18**: <http://localhost:8018>
- **Community 18**: <http://localhost:8019>
- **Enterprise 19**: <http://localhost:8021>
- **Community 19**: <http://localhost:8022>

### 📊 **2. Odoo MCP Server (`mcp-odoo` from GitHub)**

**Purpose:** Browse and interact with Odoo models/records via AI tools

**What it does:**

- Queries Odoo models and records via XML-RPC
- Browses database structure
- Integrates with Claude/Cursor for AI assistance
- Provides read-only access to Odoo data

### ⚠️ CRITICAL: XML-RPC Configuration Required

For XML-RPC to work in Odoo 18 Enterprise, you MUST include `base` in server_wide_modules:

```ini
# In your odoo18-enterprise.conf
server_wide_modules = web,queue_job,base
xmlrpc = True
xmlrpc_interface = 0.0.0.0
```

**Configuration:** `odoo_config.json`

```json
{
  "url": "http://localhost:8018",
  "db": "BIGQUERY",
  "username": "mark",
  "password": "mark",
  "version": "18.0"
}
```

**MCP Server Status:** Should show green dot in Cursor

## How They Work Together

1. **Start Odoo Instance** (using `manage-odoo.sh`)

   ```bash
   ./manage-odoo.sh start-enterprise18
   ```

2. **MCP Server Connects** (automatically via Cursor)

   - Connects to the running Odoo instance
   - Allows AI tools to browse your data
   - Uses credentials from `odoo_config.json`

3. **Switch Instances** (via workflow)

   - Use Option 10: Switch Odoo instance
   - Updates MCP configuration automatically
   - MCP server connects to new instance

## Fixed MCP Issues

### ✅ PostgreSQL MCP Server

- **Fixed:** Connection string format
- **Now:** `postgresql://postgres@localhost:5432/postgres`
- **Status:** Should show green dot

### ✅ Odoo Browse MCP Server

- **Fixed:** Configuration file path
- **Now:** Uses `odoo_config.json` with correct credentials
- **Status:** Should show green dot

### ✅ Configuration Sync

- All MCP servers update automatically when you switch projects
- Odoo configuration updates when you change instances
- PostgreSQL connection matches your Postgres.app setup

## 🚨 **Troubleshooting XML-RPC Issues**

### **Problem: MCP Odoo servers show red dots, XML-RPC returns 404 errors**

**Root Cause:** Odoo 18 Enterprise requires the `base` module in `server_wide_modules` for XML-RPC endpoints to be available.

**Solution:**

1. **Edit your Odoo configuration:**

   ```bash
   nano /Users/markshaw/Desktop/git/odoo/config/odoo18-enterprise.conf
   ```

2. **Update server_wide_modules line:**

   ```ini
   # Change from:
   server_wide_modules = web,queue_job

   # To:
   server_wide_modules = web,queue_job,base

   # Also ensure XML-RPC is enabled:
   xmlrpc = True
   xmlrpc_interface = 0.0.0.0
   ```

3. **Restart Odoo:**

   ```bash
   /Users/markshaw/Desktop/git/odoo/manage-odoo.sh restart-enterprise18
   ```

4. **Test XML-RPC is working:**

   ```python
   import xmlrpc.client
   common = xmlrpc.client.ServerProxy('http://localhost:8018/xmlrpc/2/common')
   print(common.version())  # Should return version info

   # Test authentication
   uid = common.authenticate('BIGQUERY', 'mark', 'mark', {})
   print(f'UID: {uid}')  # Should return user ID (e.g., 2)
   ```

5. **Restart Claude/Cursor** to refresh MCP server connections

**Expected Result:** Odoo MCP servers should now show green dots and be fully functional.

## Troubleshooting

### Red Dots on MCP Servers?

1. **Restart Cursor** (most common fix)
2. **Check Odoo is running:** `./manage-odoo.sh status`
3. **Verify PostgreSQL:** Should have Postgres.app running
4. **Check credentials:** Ensure `mark/mark` works for your Odoo

### Update Configurations

```bash
# Update all MCP configs
python3 project_context.py --update

# Or via workflow
python3 itms_workflow.py → Option 6: Complete Project Setup Wizard
```

## Summary

- **`manage-odoo.sh`** = Your daily Odoo server management
- **`mcp-odoo`** = AI integration for browsing Odoo data
- Both work together seamlessly
- Switch between instances easily
- All configurations sync automatically