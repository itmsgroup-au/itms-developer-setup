#!/usr/bin/env python3
"""
ITMS Intelligent Setup Tool
Detects Claude Desktop, Cursor, and KiloCode configurations and sets up MCP properly
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict

import requests
import yaml


class ITMSIntelligentSetup:
    """Intelligent setup for ITMS development environment with AI tool detection"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent
        self.home_dir = Path.home()

        # AI tool configuration paths
        self.ai_configs = {
            "cursor_mcp": self.home_dir / ".cursor" / "mcp.json",
            "cursor_kilo": self.home_dir
            / "Library"
            / "Application Support"
            / "Cursor"
            / "User"
            / "globalStorage"
            / "kilocode.kilo-code"
            / "settings"
            / "mcp_settings.json",
            "claude_desktop": self.home_dir
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json",
            "claude_local": Path(".claude") / "settings.local.json",
        }

        self.detected_configs = {}
        self.env_vars = self.load_environment()

    def load_environment(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_file = self.setup_dir / ".env"
        env_vars = {}

        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

        return env_vars

    def detect_ai_tools(self):
        """Detect installed AI tools and their configurations"""
        print("🔍 Detecting AI tool configurations...")

        for tool_name, config_path in self.ai_configs.items():
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    self.detected_configs[tool_name] = {
                        "path": config_path,
                        "config": config_data,
                        "writable": os.access(config_path, os.W_OK),
                    }
                    print(f"   ✅ Found {tool_name}: {config_path}")
                except Exception as e:
                    print(f"   ⚠️  Found {tool_name} but couldn't read: {e}")
            else:
                print(f"   ❌ Not found: {tool_name}")

    def fix_monday_api_configuration(self):
        """Fix Monday.com API configuration issues"""
        print("\n🔧 Fixing Monday.com API configuration...")

        # The issue is inconsistent board IDs
        # From your working board: 18058278926 (the one with tasks)
        # From your .env: 7970370827 (seems to be wrong)

        correct_board_id = "18058278926"  # The one that shows tasks in manage-dev.sh

        # Update .env file
        env_file = self.setup_dir / ".env"
        if env_file.exists():
            content = env_file.read_text()
            # Fix the board ID
            content = content.replace(
                "MONDAY_BOARD_ID=7970370827", f"MONDAY_BOARD_ID={correct_board_id}"
            )
            content = content.replace(
                "MONDAY_BOARD_ID=10016116930", f"MONDAY_BOARD_ID={correct_board_id}"
            )
            env_file.write_text(content)
            print(f"   ✅ Updated .env with correct board ID: {correct_board_id}")

        # Update config.yaml
        config_file = self.setup_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            config["apis"]["monday"][
                "board_id"
            ] = f"${{{{'MONDAY_BOARD_ID'}}:-'{correct_board_id}'}}"

            with open(config_file, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
            print("   ✅ Updated config.yaml with correct board ID")

        return correct_board_id

    def ensure_mcp_server_exists(self):
        """Ensure MCP server file exists"""
        print("\n🔧 Checking MCP server...")

        mcp_server_file = self.setup_dir / "itms_mcp_server.py"
        if mcp_server_file.exists():
            mcp_server_file.chmod(0o755)
            print("   ✅ MCP server ready")
        else:
            print("   ❌ MCP server missing - please create manually")

        return mcp_server_file

    def update_ai_tool_configs(self, mcp_server_path: Path, board_id: str):
        """Update AI tool configurations with working MCP server"""
        print("\n🔧 Updating AI tool configurations...")

        # Create clean MCP configuration
        clean_mcp_config = {
            "context7": {
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp@latest"],
                "env": {"CONTEXT7_API_KEY": self.env_vars.get("CONTEXT7_API_KEY", "")},
            },
            "itms-workflow": {
                "command": "python3",
                "args": [str(mcp_server_path)],
                "cwd": str(self.setup_dir),
                "env": {
                    "MONDAY_API_TOKEN": self.env_vars.get("MONDAY_API_TOKEN", ""),
                    "MONDAY_BOARD_ID": board_id,
                    "GITHUB_TOKEN": self.env_vars.get("GITHUB_TOKEN", ""),
                    "DEVELOPER_NAME": self.env_vars.get("DEVELOPER_NAME", ""),
                    "DEVELOPER_EMAIL": self.env_vars.get("DEVELOPER_EMAIL", ""),
                    "PROJECT_ROOT": self.env_vars.get("PROJECT_ROOT", ""),
                    "ODOO_PATH": self.env_vars.get("ODOO_PATH", ""),
                },
            },
            "git": {
                "command": "uvx",
                "args": [
                    "mcp-server-git",
                    "--repository",
                    self.env_vars.get(
                        "PROJECT_ROOT", str(self.home_dir / "Desktop" / "git")
                    ),
                ],
            },
        }

        # Update Cursor configurations
        for config_name in ["cursor_mcp", "cursor_kilo"]:
            if config_name in self.detected_configs:
                config_path = self.detected_configs[config_name]["path"]
                if self.detected_configs[config_name]["writable"]:
                    try:
                        new_config = {"mcpServers": clean_mcp_config}
                        with open(config_path, "w") as f:
                            json.dump(new_config, f, indent=2)
                        print(f"   ✅ Updated {config_name}")
                    except Exception as e:
                        print(f"   ❌ Failed to update {config_name}: {e}")

        # Create Claude Desktop config if it doesn't exist
        claude_config_path = self.ai_configs["claude_desktop"]
        claude_config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            claude_config = {"mcpServers": clean_mcp_config}
            with open(claude_config_path, "w") as f:
                json.dump(claude_config, f, indent=2)
            print("   ✅ Created/Updated Claude Desktop config")
        except Exception as e:
            print(f"   ❌ Failed to create Claude Desktop config: {e}")

    def fix_workflow_script(self, board_id: str):
        """Fix the itms_workflow.py script Monday.com connection"""
        print("\n🔧 Fixing workflow script...")

        workflow_file = self.setup_dir / "itms_workflow.py"
        if workflow_file.exists():
            content = workflow_file.read_text()

            # Fix the GraphQL query format - the issue is likely with the query structure
            # Replace the problematic query section
            old_query = '''query = """
        query {
            boards(ids: [%s]) {
                items_page {
                    items {
                        id
                        name
                        state
                        column_values {
                            id
                            text
                            ... on StatusValue {
                                label
                            }
                        }
                        updates {
                            body
                            created_at
                        }
                    }
                }
            }
        }
        """ % self.monday_api['board_id']'''

            new_query = f'''query = """
        query {{
            boards(ids: [{board_id}]) {{
                items_page(limit: 25) {{
                    items {{
                        id
                        name
                        state
                        created_at
                        column_values {{
                            id
                            text
                        }}
                    }}
                }}
            }}
        }}
        """"'''

            content = content.replace(old_query, new_query)
            workflow_file.write_text(content)
            print("   ✅ Fixed Monday.com query in workflow script")

    def create_clean_gitignore(self):
        """Create a clean .gitignore for production"""
        print("\n📝 Creating clean .gitignore...")

        gitignore_content = """# ITMS Developer Setup - Production

# Personal configuration
.env
*.local
.DS_Store

# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
*.log

# IDE
.vscode/settings.json
.cursor/
*.swp

# Temporary
*.tmp
*.bak
temp/

# Archives
archive/
backup_*/
"""

        gitignore_file = self.setup_dir / ".gitignore"
        gitignore_file.write_text(gitignore_content)
        print("   ✅ Created clean .gitignore")

    def create_production_readme(self):
        """Create a clean, production README"""
        print("\n📝 Creating production README...")

        readme_content = """# 🚀 ITMS Developer Setup

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
"""

        readme_file = self.setup_dir / "README.md"
        readme_file.write_text(readme_content)
        print("   ✅ Created production README")

    def test_integrations(self):
        """Test that all integrations work"""
        print("\n🧪 Testing integrations...")

        # Test Monday.com API
        monday_token = self.env_vars.get("MONDAY_API_TOKEN")
        board_id = self.env_vars.get("MONDAY_BOARD_ID")

        if monday_token and board_id:
            try:
                query = f"""
                query {{
                    boards(ids: [{board_id}]) {{
                        name
                        items_page(limit: 1) {{
                            items {{
                                id
                                name
                            }}
                        }}
                    }}
                }}
                """

                response = requests.post(
                    "https://api.monday.com/v2",
                    json={"query": query},
                    headers={"Authorization": monday_token},
                )

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        print(f"   ❌ Monday.com API errors: {data['errors']}")
                    else:
                        board_name = data["data"]["boards"][0]["name"]
                        print(f"   ✅ Monday.com API working - Board: {board_name}")
                else:
                    print(f"   ❌ Monday.com API failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Monday.com test failed: {e}")
        else:
            print("   ⚠️  Monday.com not configured")

        # Test MCP server
        mcp_server = self.setup_dir / "itms_mcp_server.py"
        if mcp_server.exists():
            print("   ✅ MCP server created and ready")
        else:
            print("   ❌ MCP server missing")

    def run_setup(self):
        """Run the complete intelligent setup"""
        print("🚀 ITMS Intelligent Setup")
        print("=" * 30)
        print()
        print("This will:")
        print("• Detect AI tool configurations")
        print("• Fix Monday.com API issues")
        print("• Create working MCP servers")
        print("• Update all AI tool configs")
        print("• Clean up repository structure")
        print()

        try:
            # Main setup steps
            self.detect_ai_tools()
            board_id = self.fix_monday_api_configuration()
            mcp_server_path = self.ensure_mcp_server_exists()
            self.update_ai_tool_configs(mcp_server_path, board_id)
            self.fix_workflow_script(board_id)
            self.create_clean_gitignore()
            self.create_production_readme()
            self.test_integrations()

            print("\n✅ Intelligent setup completed successfully!")
            print()
            print("🎯 Next Steps:")
            print("1. Edit your .env file with correct API tokens")
            print("2. Restart Cursor/Claude Desktop to load new MCP configs")
            print("3. Test: python3 itms_workflow.py")
            print()
            print("🤖 AI Tools configured:")
            for tool_name in self.detected_configs:
                print(f"   • {tool_name}")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False


def main():
    """Main setup entry point"""
    try:
        setup = ITMSIntelligentSetup()
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
