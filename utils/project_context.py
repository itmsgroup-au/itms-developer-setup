#!/usr/bin/env python3
"""
ITMS Project Context Manager
Centralized management of Monday.com boards and GitHub repos
Automatically syncs all MCP configurations when context changes
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProjectContextManager:
    """Manages active project context (Monday board + GitHub repo)"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent
        self.context_file = self.setup_dir / ".project_context.json"
        self.session = requests.Session()

        # API tokens
        self.monday_token = os.getenv("MONDAY_API_TOKEN")
        self.github_token = os.getenv("GITHUB_TOKEN")

        # MCP config file paths
        self.mcp_configs = {
            "cursor_mcp": Path.home() / ".cursor" / "mcp.json",
            "cursor_kilo": Path.home()
            / "Library"
            / "Application Support"
            / "Cursor"
            / "User"
            / "globalStorage"
            / "kilocode.kilo-code"
            / "settings"
            / "mcp_settings.json",
            "augment": Path.home()
            / "Library"
            / "Application Support"
            / "Cursor"
            / "User"
            / "globalStorage"
            / "augment.vscode-augment"
            / "augment-global-state"
            / "mcpServers.json",
            "claude_local": Path(".claude") / "settings.local.json",
        }

        # Current context
        self.current_context = self.load_context()

        # Set up API headers
        self.session.headers.update(
            {"User-Agent": "ITMS-Context-Manager/1.0", "Accept": "application/json"}
        )

    def load_context(self) -> Optional[Dict]:
        """Load current project context"""
        if self.context_file.exists():
            try:
                with open(self.context_file, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_context(self, context: Dict):
        """Save project context and update all MCP configs"""
        with open(self.context_file, "w") as f:
            json.dump(context, f, indent=2)

        self.current_context = context
        self.update_all_mcp_configs()
        self.update_env_file()
        self.update_odoo_server_configs()

        # Update Odoo MCP config if this context has Odoo info
        if hasattr(context, "get") and context.get("odoo"):
            self.update_odoo_config_file(context)

    def get_monday_boards(self) -> List[Dict]:
        """Fetch available Monday.com boards"""
        print("🔍 Fetching Monday.com boards...")

        query = """
        query {
            boards(limit: 50) {
                id
                name
                description
                board_kind
                state
                items_count
                updated_at
            }
        }
        """

        try:
            response = self.session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers={"Authorization": self.monday_token},
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"❌ GraphQL errors: {data['errors']}")
                    return []

                boards = data["data"]["boards"]
                # Filter out Subitems boards as they're not selectable project boards
                filtered_boards = [
                    board
                    for board in boards
                    if not board["name"].startswith("Subitems of")
                ]
                print(
                    f"✅ Found {len(filtered_boards)} boards (filtered out {len(boards) - len(filtered_boards)} Subitems boards)"
                )
                return filtered_boards
            else:
                print(f"❌ API Error: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error fetching boards: {e}")
            return []

    def get_github_repos(self) -> List[Dict]:
        """Fetch available GitHub repositories"""
        print("🔍 Fetching GitHub repositories...")

        try:
            # Get user's repos
            response = self.session.get(
                "https://api.github.com/user/repos",
                headers={"Authorization": f"token {self.github_token}"},
                params={"per_page": 50, "sort": "updated"},
            )

            repos = []
            if response.status_code == 200:
                user_repos = response.json()
                repos.extend(user_repos)

            # Get organization repos
            github_org = os.getenv("GITHUB_ORG", "itmsgroup-au")
            if github_org:
                response = self.session.get(
                    f"https://api.github.com/orgs/{github_org}/repos",
                    headers={"Authorization": f"token {self.github_token}"},
                    params={"per_page": 50, "sort": "updated"},
                )

                if response.status_code == 200:
                    org_repos = response.json()
                    repos.extend(org_repos)

            print(f"✅ Found {len(repos)} repositories")
            return repos

        except Exception as e:
            print(f"❌ Error fetching repos: {e}")
            return []

    def select_board(self) -> Optional[Dict]:
        """Interactive Monday board selection"""
        boards = self.get_monday_boards()

        if not boards:
            print("❌ No boards found")
            return None

        print("\n📋 Available Monday.com Boards:")
        print("-" * 60)

        current_board_id = (
            self.current_context.get("board_id") if self.current_context else None
        )

        for i, board in enumerate(boards, 1):
            board_id = str(board["id"])
            current_marker = " ⭐ (CURRENT)" if board_id == current_board_id else ""

            print(f"{i:2d}. {board['name']}{current_marker}")
            print(f"    ID: {board_id}")
            print(f"    Items: {board.get('items_count', 0)}")
            print(f"    State: {board.get('state', 'unknown')}")
            if board.get("description"):
                print(f"    Description: {board['description']}")
            print()

        try:
            choice = input(f"Select board number (1-{len(boards)}) or ID: ").strip()

            # Check if it's a number (board selection) or ID
            if choice.isdigit() and 1 <= int(choice) <= len(boards):
                return boards[int(choice) - 1]
            else:
                # Try to find by ID
                for board in boards:
                    if str(board["id"]) == choice:
                        return board

                print("❌ Invalid selection")
                return None

        except ValueError:
            print("❌ Invalid input")
            return None

    def select_repo(self) -> Optional[Dict]:
        """Interactive GitHub repo selection"""
        repos = self.get_github_repos()

        if not repos:
            print("❌ No repositories found")
            return None

        print("\n🐙 Available GitHub Repositories:")
        print("-" * 60)

        current_repo = (
            self.current_context.get("repo_full_name") if self.current_context else None
        )

        for i, repo in enumerate(repos, 1):
            repo_name = repo["full_name"]
            current_marker = " ⭐ (CURRENT)" if repo_name == current_repo else ""

            print(f"{i:2d}. {repo_name}{current_marker}")
            print(f"    Description: {repo.get('description', 'No description')}")
            print(f"    Language: {repo.get('language', 'Unknown')}")
            print(f"    Updated: {repo.get('updated_at', 'Unknown')}")
            print()

        try:
            choice = input(f"Select repo number (1-{len(repos)}): ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(repos):
                return repos[int(choice) - 1]
            else:
                print("❌ Invalid selection")
                return None

        except ValueError:
            print("❌ Invalid input")
            return None

    def update_env_file(self):
        """Update .env file with current context"""
        if not self.current_context:
            return

        env_file = self.setup_dir / ".env"
        if not env_file.exists():
            print("❌ .env file not found")
            return

        content = env_file.read_text()
        lines = content.split("\n")

        # Update relevant lines
        updates = {
            "MONDAY_BOARD_ID": self.current_context.get("board_id"),
            "GITHUB_REPO": self.current_context.get("repo_full_name"),
            "GITHUB_ORG": self.current_context.get("repo_owner"),
        }

        for key, value in updates.items():
            if value:
                found = False
                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = f"{key}={value}"
                        found = True
                        break

                if not found:
                    lines.append(f"{key}={value}")

        env_file.write_text("\n".join(lines))

    def update_odoo_server_configs(self):
        """Update Odoo server config files with default database from .env"""
        try:
            # Get database name from .env
            env_file = self.setup_dir / ".env"
            if not env_file.exists():
                return

            content = env_file.read_text()
            db_name = None

            for line in content.split("\n"):
                if line.strip().startswith("ODOO_DB="):
                    db_name = line.split("=", 1)[1].strip()
                    break

            if not db_name:
                return

            # Update all Odoo config files
            odoo_config_paths = [
                "/Users/markshaw/Desktop/git/odoo/config/odoo18-enterprise.conf",
                "/Users/markshaw/Desktop/git/odoo/config/odoo18-community.conf",
                "/Users/markshaw/Desktop/git/odoo/config/odoo19-enterprise.conf",
                "/Users/markshaw/Desktop/git/odoo/config/odoo19-community.conf",
            ]

            updated_count = 0
            for config_path in odoo_config_paths:
                config_file = Path(config_path)
                if config_file.exists():
                    # Read current config
                    content = config_file.read_text()
                    lines = content.split("\n")

                    # Update db_name line
                    for i, line in enumerate(lines):
                        if line.strip().startswith("db_name ="):
                            old_value = line.split("=", 1)[1].strip()
                            lines[i] = f"db_name = {db_name}"
                            if old_value != db_name:
                                print(
                                    f"✅ Updated {config_file.name}: db_name = {db_name}"
                                )
                                updated_count += 1
                            break

                    # Write back the config
                    config_file.write_text("\n".join(lines))

            if updated_count > 0:
                print(
                    f"✅ Updated {updated_count} Odoo server config files with default database"
                )

        except Exception as e:
            print(f"⚠️  Failed to update Odoo server configs: {e}")

    def update_odoo_config_file(self, config: Dict):
        """Update odoo_config.json file with current project configuration"""
        odoo_config = {
            "odoo_url": config.get("odoo", {}).get("url", "http://localhost:8018"),
            "odoo_db": config.get("odoo", {}).get("database", ""),
            "odoo_username": config.get("odoo", {}).get("username", "odoo"),
            "odoo_password": config.get("odoo", {}).get("password", ""),
            "odoo_version": "18.0",  # Default to 18, could be dynamic
        }

        odoo_config_file = self.setup_dir / "odoo_config.json"
        with open(odoo_config_file, "w") as f:
            json.dump(odoo_config, f, indent=2)

        print(
            f"✅ Updated Odoo MCP config: {odoo_config['odoo_url']} / {odoo_config['odoo_db']}"
        )

    def update_all_mcp_configs(self):
        """Update all MCP configuration files with current context"""
        if not self.current_context:
            print("❌ No context to update")
            return

        board_id = self.current_context.get("board_id")
        repo_full_name = self.current_context.get("repo_full_name")
        repo_owner = self.current_context.get("repo_owner")

        updated_count = 0

        for config_name, config_path in self.mcp_configs.items():
            try:
                if config_path.exists():
                    self.update_mcp_config_file(
                        config_path, config_name, board_id, repo_full_name, repo_owner
                    )
                    updated_count += 1
                else:
                    print(f"⚠️  Config not found: {config_path}")
            except Exception as e:
                print(f"❌ Failed to update {config_name}: {e}")

        print(f"✅ Updated {updated_count} MCP configuration files")

    def update_mcp_config_file(
        self,
        config_path: Path,
        config_name: str,
        board_id: str,
        repo_full_name: str,
        repo_owner: str,
    ):
        """Update a specific MCP config file"""
        with open(config_path, "r") as f:
            config = json.load(f)

        # Different config formats
        if config_name == "augment":
            # Augment uses array format
            self.update_augment_config(config, board_id, repo_full_name, repo_owner)
        else:
            # Standard MCP format
            self.update_standard_mcp_config(
                config, board_id, repo_full_name, repo_owner
            )

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"   ✅ Updated {config_name}")

    def update_augment_config(
        self, config: list, board_id: str, repo_full_name: str, repo_owner: str
    ):
        """Update Augment MCP config with all servers"""
        # Remove old servers and add new ones
        config.clear()

        # Context7 server
        config.append(
            {
                "name": "context7",
                "command": "npx -y @upstash/context7-mcp@latest",
                "arguments": "",
                "useShellInterpolation": True,
                "env": {"CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", "")},
                "id": "688ae864-7588-4c19-a1ed-3222d6c98aa4",
                "tools": ["resolve-library-id", "get-library-docs"],
                "disabledTools": [],
            }
        )

        # PostgreSQL server (Augment format with proper arguments)
        config.append(
            {
                "name": "postgresql",
                "command": "npx -y @modelcontextprotocol/server-postgres postgresql://postgres@localhost:5432/postgres",
                "arguments": "",
                "useShellInterpolation": True,
                "env": {
                    "PG_PATH": "/Applications/Postgres.app/Contents/Versions/17/bin"
                },
                "id": "postgres-mcp-server",
                "tools": [],
                "disabledTools": [],
            }
        )

        # Chrome DevTools MCP server for web performance testing (requires Node 22.12.0+)
        config.append(
            {
                "name": "chrome-devtools",
                "command": "npx -y chrome-devtools-mcp@latest",
                "arguments": "",
                "useShellInterpolation": True,
                "env": {},
                "id": "chrome-devtools-mcp-server",
                "tools": [],
                "disabledTools": [],
            }
        )

        # Odoo MCP server (GitHub mcp-odoo for browsing models/records)
        config.append(
            {
                "name": "odoo",
                "command": "npx -y mcp-odoo",
                "arguments": "",
                "useShellInterpolation": True,
                "env": {
                    "ODOO_URL": os.getenv("ODOO_URL", "http://localhost:8018"),
                    "ODOO_DB": os.getenv("ODOO_DB", "BIGQUERY"),
                    "ODOO_USERNAME": os.getenv("ODOO_USERNAME", "mark"),
                    "ODOO_PASSWORD": os.getenv("ODOO_PASSWORD", "mark"),
                    "ODOO_ADMIN_PASSWD": os.getenv("ODOO_ADMIN_PASSWD", "itmsadmin"),
                    "ODOO_PATH": os.getenv(
                        "ODOO_PATH", "/Users/markshaw/Desktop/git/odoo"
                    ),
                },
                "id": "odoo-mcp-server",
                "tools": [],
                "disabledTools": [],
                "alwaysAllow": ["execute_method", "search_employee", "search_holidays"],
            }
        )

        # ITMS Task Master (Enhanced workflow with task-master integration)
        config.append(
            {
                "name": "itms-task-master",
                "command": f"python3 {Path(__file__).parent / 'itms_mcp_server.py'}",
                "arguments": "",
                "useShellInterpolation": True,
                "env": {
                    "MONDAY_API_TOKEN": os.getenv("MONDAY_API_TOKEN", ""),
                    "MONDAY_BOARD_ID": board_id,
                    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
                    "GITHUB_REPO": repo_full_name,
                    "GITHUB_ORG": repo_owner,
                    "DEVELOPER_NAME": os.getenv("DEVELOPER_NAME", ""),
                    "DEVELOPER_EMAIL": os.getenv("DEVELOPER_EMAIL", ""),
                    "PROJECT_ROOT": os.getenv("PROJECT_ROOT", ""),
                    "ODOO_PATH": os.getenv("ODOO_PATH", ""),
                    "CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", ""),
                },
                "id": "itms-task-master",
                "tools": [],
                "disabledTools": [],
                "alwaysAllow": [
                    "get_assigned_tasks",
                    "select_active_task",
                    "create_subtasks",
                    "get_monday_tasks",
                    "create_monday_task",
                    "workflow_status",
                    "set_working_group",
                    "clear_working_group",
                ],
            }
        )

    def update_standard_mcp_config(
        self, config: dict, board_id: str, repo_full_name: str, repo_owner: str
    ):
        """Update standard MCP config with all servers"""
        # Clear existing servers and regenerate from scratch
        config["mcpServers"] = {}
        servers = config["mcpServers"]

        # Context7 server
        servers["context7"] = {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp@latest"],
            "env": {"CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", "")},
        }

        # PostgreSQL server (fixed connection string format)
        servers["postgresql"] = {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-postgres",
                "postgresql://postgres@localhost:5432/postgres",
            ],
            "env": {"PG_PATH": "/Applications/Postgres.app/Contents/Versions/17/bin"},
        }

        # Odoo MCP server (GitHub mcp-odoo for browsing models/records)
        servers["odoo"] = {
            "command": "npx",
            "args": ["-y", "mcp-odoo"],
            "env": {
                "ODOO_URL": os.getenv("ODOO_URL", "http://localhost:8018"),
                "ODOO_DB": os.getenv("ODOO_DB", "BIGQUERY"),
                "ODOO_USERNAME": os.getenv("ODOO_USERNAME", "mark"),
                "ODOO_PASSWORD": os.getenv("ODOO_PASSWORD", "mark"),
                "ODOO_ADMIN_PASSWD": os.getenv("ODOO_ADMIN_PASSWD", "itmsadmin"),
                "ODOO_PATH": os.getenv("ODOO_PATH", "/Users/markshaw/Desktop/git/odoo"),
            },
        }

        # Chrome DevTools MCP server for web performance testing (requires Node 22.12.0+)
        servers["chrome-devtools"] = {
            "command": "npx",
            "args": ["-y", "chrome-devtools-mcp@latest"],
        }

        # ITMS Task Master (Enhanced workflow with task-master integration)
        servers["itms-task-master"] = {
            "command": "python3",
            "args": [str(Path(__file__).parent / "itms_mcp_server.py")],
            "cwd": str(Path(__file__).parent),
            "env": {
                "MONDAY_API_TOKEN": os.getenv("MONDAY_API_TOKEN", ""),
                "MONDAY_BOARD_ID": board_id,
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
                "GITHUB_REPO": repo_full_name,
                "GITHUB_ORG": repo_owner,
                "DEVELOPER_NAME": os.getenv("DEVELOPER_NAME", ""),
                "DEVELOPER_EMAIL": os.getenv("DEVELOPER_EMAIL", ""),
                "PROJECT_ROOT": os.getenv("PROJECT_ROOT", ""),
                "ODOO_PATH": os.getenv("ODOO_PATH", ""),
                "CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", ""),
            },
        }

        # Git server (keep existing)
        if "git" not in servers:
            servers["git"] = {
                "command": "uvx",
                "args": [
                    "mcp-server-git",
                    "--repository",
                    os.getenv("PROJECT_ROOT", "/Users/markshaw/Desktop/git"),
                ],
            }

    def show_current_context(self):
        """Display current project context"""
        if not self.current_context:
            print("❌ No project context set")
            return

        print("\n🎯 Current Project Context:")
        print("=" * 40)
        print(f"📋 Monday Board: {self.current_context.get('board_name')}")
        print(f"   ID: {self.current_context.get('board_id')}")
        print(f"🐙 GitHub Repo: {self.current_context.get('repo_full_name')}")
        print(f"   Owner: {self.current_context.get('repo_owner')}")
        print(f"⏰ Last Updated: {self.current_context.get('updated_at')}")
        print()

    def set_project_context(self):
        """Interactive project context setup"""
        print("\n🎯 Set Project Context (Board + Repo)")
        print("=" * 40)

        # Select Monday board
        print("\n1️⃣ Select Monday.com Board:")
        board = self.select_board()
        if not board:
            print("❌ Board selection cancelled")
            return

        # Select GitHub repo
        print("\n2️⃣ Select GitHub Repository:")
        repo = self.select_repo()
        if not repo:
            print("❌ Repo selection cancelled")
            return

        # Create context
        context = {
            "board_id": str(board["id"]),
            "board_name": board["name"],
            "repo_full_name": repo["full_name"],
            "repo_owner": repo["owner"]["login"],
            "repo_name": repo["name"],
            "updated_at": __import__("datetime").datetime.now().isoformat(),
        }

        # Save and update all configs
        print(f"\n💾 Saving context: {board['name']} + {repo['full_name']}")
        self.save_context(context)

        print("✅ Project context updated!")
        print("🔄 Restart Cursor/Claude Desktop to apply MCP changes")

    def main_menu(self):
        """Main interactive menu"""
        while True:
            print("\n🎯 ITMS Project Context Manager")
            print("=" * 40)

            self.show_current_context()

            print("1. 🎯 Set Project Context (Board + Repo)")
            print("2. 📋 Change Monday Board Only")
            print("3. 🐙 Change GitHub Repo Only")
            print("4. 🔄 Refresh Current Context")
            print("5. 📋 View All Boards")
            print("6. 🐙 View All Repos")
            print("0. ❌ Exit")

            try:
                choice = input("\nSelect option (0-6): ").strip()

                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.set_project_context()
                elif choice == "2":
                    board = self.select_board()
                    if board and self.current_context:
                        self.current_context["board_id"] = str(board["id"])
                        self.current_context["board_name"] = board["name"]
                        self.current_context["updated_at"] = (
                            __import__("datetime").datetime.now().isoformat()
                        )
                        self.save_context(self.current_context)
                        print("✅ Monday board updated!")
                elif choice == "3":
                    repo = self.select_repo()
                    if repo and self.current_context:
                        self.current_context["repo_full_name"] = repo["full_name"]
                        self.current_context["repo_owner"] = repo["owner"]["login"]
                        self.current_context["repo_name"] = repo["name"]
                        self.current_context["updated_at"] = (
                            __import__("datetime").datetime.now().isoformat()
                        )
                        self.save_context(self.current_context)
                        print("✅ GitHub repo updated!")
                elif choice == "4":
                    if self.current_context:
                        self.update_all_mcp_configs()
                        self.update_env_file()
                        print("✅ Context refreshed!")
                elif choice == "5":
                    self.get_monday_boards()
                elif choice == "6":
                    self.get_github_repos()
                else:
                    print("❌ Invalid option")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point"""
    try:
        manager = ProjectContextManager()

        # Check if run with arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--set":
                manager.set_project_context()
            elif sys.argv[1] == "--show":
                manager.show_current_context()
            elif sys.argv[1] == "--update":
                manager.update_all_mcp_configs()
                manager.update_env_file()
            else:
                print("Usage: python3 project_context.py [--set|--show|--update]")
        else:
            manager.main_menu()

    except Exception as e:
        print(f"❌ Failed to start project context manager: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
