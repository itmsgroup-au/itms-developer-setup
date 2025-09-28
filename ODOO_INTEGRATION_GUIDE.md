# ODOO Integration Guide

## Two Odoo Systems Explained

Your ITMS setup now has **TWO different but complementary** Odoo integrations:

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
- **Enterprise 18**: http://localhost:8018 
- **Community 18**: http://localhost:8019
- **Enterprise 19**: http://localhost:8021
- **Community 19**: http://localhost:8022

### 📊 **2. Odoo MCP Server (`mcp-odoo` from GitHub)**

**Purpose:** Browse and interact with Odoo models/records via AI tools

**What it does:**
- Queries Odoo models and records
- Browses database structure
- Integrates with Claude/Cursor for AI assistance
- Provides read-only access to Odoo data

**Configuration:** `odoo_config.json`
```json
{
  "odoo_url": "http://localhost:8018",
  "odoo_db": "BIGQUERY", 
  "odoo_username": "mark",
  "odoo_password": "mark",
  "odoo_version": "18.0"
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

### ✅ **PostgreSQL MCP Server**
- **Fixed:** Connection string format
- **Now:** `postgresql://postgres@localhost:5432/postgres`
- **Status:** Should show green dot

### ✅ **Odoo Browse MCP Server** 
- **Fixed:** Configuration file path
- **Now:** Uses `odoo_config.json` with correct credentials
- **Status:** Should show green dot

### ✅ **Configuration Sync**
- All MCP servers update automatically when you switch projects
- Odoo configuration updates when you change instances
- PostgreSQL connection matches your Postgres.app setup

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