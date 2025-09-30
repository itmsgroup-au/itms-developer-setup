#!/usr/bin/env python3
"""
ITMS Project Setup Wizard
Complete project initialization: Monday board + GitHub repo + Odoo + Database + PostgreSQL
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psycopg2
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProjectSetupWizard:
    """Complete project setup wizard for ITMS development"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent
        self.session = requests.Session()

        # API tokens
        self.monday_token = os.getenv("MONDAY_API_TOKEN")
        self.github_token = os.getenv("GITHUB_TOKEN")

        # Odoo configurations from manage-odoo.sh
        self.odoo_instances = {
            "enterprise18": {
                "name": "Odoo 18 Enterprise",
                "url": "http://localhost:8018/odoo",
                "config": "/Users/markshaw/Desktop/git/odoo/config/odoo18-enterprise.conf",
                "pid": "/Users/markshaw/Desktop/git/odoo/odoo18-enterprise.pid",
            },
            "community18": {
                "name": "Odoo 18 Community",
                "url": "http://localhost:8019/odoo",
                "config": "/Users/markshaw/Desktop/git/odoo/config/odoo18-community.conf",
                "pid": "/Users/markshaw/Desktop/git/odoo/odoo18-community.pid",
            },
            "enterprise19": {
                "name": "Odoo 19 Enterprise",
                "url": "http://localhost:8021/odoo",
                "config": "/Users/markshaw/Desktop/git/odoo/config/odoo19-enterprise.conf",
                "pid": "/Users/markshaw/Desktop/git/odoo/odoo19-enterprise.pid",
            },
            "community19": {
                "name": "Odoo 19 Community",
                "url": "http://localhost:8022/odoo",
                "config": "/Users/markshaw/Desktop/git/odoo/config/odoo19-community.conf",
                "pid": "/Users/markshaw/Desktop/git/odoo/odoo19-community.pid",
            },
        }

        # PostgreSQL connection
        self.pg_path = "/Applications/Postgres.app/Contents/Versions/17/bin"
        os.environ["PATH"] = f"{self.pg_path}:{os.environ['PATH']}"

        # Set up API headers
        self.session.headers.update(
            {"User-Agent": "ITMS-Setup-Wizard/1.0", "Accept": "application/json"}
        )

    def run_wizard(self):
        """Main setup wizard"""
        print("🚀 ITMS Project Setup Wizard")
        print("=" * 50)
        print("This wizard will configure:")
        print("1. 📋 Monday.com board")
        print("2. 🐙 GitHub repository")
        print("3. 🔧 Odoo instance (version/edition)")
        print("4. 🗄️  Database setup")
        print("5. 🐘 PostgreSQL access")
        print("6. 🔗 MCP server configuration")
        print()

        if input("Continue? (y/n) [y]: ").strip().lower() == "n":
            print("❌ Setup cancelled")
            return

        # Step 1: Monday Board
        print("\n" + "=" * 50)
        print("📋 STEP 1: Monday.com Board Selection")
        print("=" * 50)
        board = self.select_monday_board()
        if not board:
            print("❌ Setup cancelled - no board selected")
            return

        # Step 1b: Monday.com Group Selection
        print("\n" + "=" * 50)
        print("👥 STEP 1b: Monday.com Group Selection (Optional)")
        print("=" * 50)
        group = self.select_monday_group(board["id"])

        # Step 2: GitHub Repo
        print("\n" + "=" * 50)
        print("🐙 STEP 2: GitHub Repository Selection")
        print("=" * 50)
        repo = self.select_github_repo()
        if not repo:
            print("❌ Setup cancelled - no repo selected")
            return

        # Step 3: Odoo Instance
        print("\n" + "=" * 50)
        print("🔧 STEP 3: Odoo Instance Configuration")
        print("=" * 50)
        odoo_config = self.select_odoo_instance()
        if not odoo_config:
            print("❌ Setup cancelled - no Odoo instance selected")
            return

        # Step 4: Database Setup
        print("\n" + "=" * 50)
        print("🗄️  STEP 4: Database Configuration")
        print("=" * 50)
        db_config = self.setup_database(odoo_config)
        if not db_config:
            print("❌ Setup cancelled - database setup failed")
            return

        # Step 5: Odoo Credentials
        print("\n" + "=" * 50)
        print("🔐 STEP 5: Odoo User Credentials")
        print("=" * 50)
        odoo_user_config = self.setup_odoo_credentials(odoo_config, db_config)
        if not odoo_user_config:
            print("❌ Setup cancelled - Odoo credentials setup failed")
            return

        # Step 6: PostgreSQL Access
        print("\n" + "=" * 50)
        print("🐘 STEP 6: PostgreSQL Access Verification")
        print("=" * 50)
        pg_config = self.verify_postgresql_access()

        # Step 7: Save Configuration
        print("\n" + "=" * 50)
        print("💾 STEP 7: Saving Project Configuration")
        print("=" * 50)
        project_config = self.save_project_config(
            board, group, repo, odoo_config, db_config, odoo_user_config, pg_config
        )

        # Step 8: Update MCP Servers
        print("\n" + "=" * 50)
        print("🔗 STEP 8: Updating MCP Server Configurations")
        print("=" * 50)
        self.update_mcp_configurations(project_config)

        # Step 8: Update Odoo MCP config files
        print("\n" + "=" * 50)
        print("📝 STEP 8: Updating Odoo Configuration Files")
        print("=" * 50)
        self.update_odoo_config_files(project_config)
        self.update_odoo_server_config(project_config)

        # Step 9: Verify Odoo connectivity
        print("\n" + "=" * 50)
        print("🔍 STEP 9: Verifying Odoo Connection")
        print("=" * 50)
        self.verify_odoo_connection(project_config)

        # Step 10: Create project nickname
        print("\n" + "=" * 50)
        print("🎯 STEP 10: Creating Project Nickname")
        print("=" * 50)
        self.create_project_nickname(project_config)

        # Step 11: Create Cursor workspace
        print("\n" + "=" * 50)
        print("💼 STEP 11: Creating Cursor Workspace")
        print("=" * 50)
        self.create_cursor_workspace(project_config)

        print("\n" + "=" * 50)
        print("✅ PROJECT SETUP COMPLETE!")
        print("=" * 50)
        self.show_project_summary(project_config)

    def select_monday_board(self) -> Optional[Dict]:
        """Select Monday.com board"""
        boards = self.get_monday_boards()
        if not boards:
            return None

        print("\nAvailable Monday.com boards:")
        for i, board in enumerate(boards, 1):
            print(
                f"{i:2d}. {board['name']} (ID: {board['id']}, Items: {board.get('items_count', 0)})"
            )

        try:
            choice = input(f"\nSelect board (1-{len(boards)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(boards):
                selected = boards[int(choice) - 1]
                print(f"✅ Selected: {selected['name']}")
                return selected
        except:
            pass

        print("❌ Invalid selection")
        return None

    def select_monday_group(self, board_id: str) -> Optional[Dict]:
        """Select Monday.com group within the board"""
        groups = self.get_monday_groups(board_id)
        if not groups:
            print("No groups found on this board - proceeding with all tasks")
            return None

        print("\nAvailable groups on this board:")
        print("0. All groups (no filter)")
        for i, group in enumerate(groups, 1):
            print(
                f"{i:2d}. {group['title']} (ID: {group['id']}, Color: {group.get('color', 'default')})"
            )

        try:
            choice = input(f"\nSelect group (0-{len(groups)}) [0]: ").strip()
            if not choice or choice == "0":
                print("✅ Selected: All groups (no filter)")
                return None
            elif choice.isdigit() and 1 <= int(choice) <= len(groups):
                selected = groups[int(choice) - 1]
                print(f"✅ Selected group: {selected['title']}")
                return selected
        except:
            pass

        print("❌ Invalid selection - proceeding with all groups")
        return None

    def select_github_repo(self) -> Optional[Dict]:
        """Select GitHub repository"""
        repos = self.get_github_repos()
        if not repos:
            return None

        print("\nAvailable GitHub repositories:")
        for i, repo in enumerate(repos, 1):
            print(f"{i:2d}. {repo['full_name']} ({repo.get('language', 'Unknown')})")

        try:
            choice = input(f"\nSelect repository (1-{len(repos)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(repos):
                selected = repos[int(choice) - 1]
                print(f"✅ Selected: {selected['full_name']}")
                return selected
        except:
            pass

        print("❌ Invalid selection")
        return None

    def select_odoo_instance(self) -> Optional[Dict]:
        """Select and configure Odoo instance"""
        print("\nAvailable Odoo instances:")
        instances = list(self.odoo_instances.items())

        for i, (key, config) in enumerate(instances, 1):
            status = (
                "🟢 Running" if self.is_odoo_running(config["pid"]) else "🔴 Stopped"
            )
            print(f"{i}. {config['name']} ({config['url']}) {status}")

        try:
            choice = input(f"\nSelect Odoo instance (1-{len(instances)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(instances):
                key, config = instances[int(choice) - 1]

                # Check if running, offer to start
                if not self.is_odoo_running(config["pid"]):
                    start = (
                        input(f"Start {config['name']}? (y/n) [y]: ").strip().lower()
                    )
                    if start != "n":
                        self.start_odoo_instance(key)

                print(f"✅ Selected: {config['name']}")
                return {"key": key, **config}
        except:
            pass

        print("❌ Invalid selection")
        return None

    def setup_database(self, odoo_config: Dict) -> Optional[Dict]:
        """Setup database for the project"""
        print(f"\n🗄️  Database setup for {odoo_config['name']}")

        # Get database name
        db_name = input("Database name for this project: ").strip()
        if not db_name:
            print("❌ Database name required")
            return None

        # Get database user (default: odoo)
        db_user = input("Database username [odoo]: ").strip() or "odoo"

        # Get database password
        db_password = input("Database password (leave empty for no password): ").strip()

        # Check if database exists
        if self.database_exists(db_name):
            print(f"✅ Database '{db_name}' already exists")
            use_existing = input("Use existing database? (y/n) [y]: ").strip().lower()
            if use_existing == "n":
                return None
        else:
            # Create database
            create = input(f"Create database '{db_name}'? (y/n) [y]: ").strip().lower()
            if create != "n":
                if self.create_database(db_name, db_user):
                    print(f"✅ Database '{db_name}' created")
                else:
                    print(f"❌ Failed to create database '{db_name}'")
                    return None

        return {
            "name": db_name,
            "user": db_user,
            "password": db_password,
            "host": "localhost",
            "port": 5432,
        }

    def setup_odoo_credentials(
        self, odoo_config: Dict, db_config: Dict
    ) -> Optional[Dict]:
        """Setup Odoo user credentials for database access"""
        print(f"\n🔐 Odoo credentials for database: {db_config['name']}")
        print(
            "These credentials will be used by the Odoo MCP server to access your Odoo instance."
        )

        # Get Odoo username
        default_username = "admin"
        odoo_username = (
            input(f"Odoo username [{default_username}]: ").strip() or default_username
        )

        # Get Odoo password
        import getpass

        try:
            odoo_password = getpass.getpass("Odoo password: ").strip()
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled")
            return None

        if not odoo_password:
            print("❌ Odoo password required for MCP server access")
            return None

        # Test connection to Odoo (optional)
        test_connection = input("Test Odoo connection? (y/n) [y]: ").strip().lower()
        if test_connection != "n":
            try:
                import requests

                login_url = f"{odoo_config['url']}/web/session/authenticate"
                login_data = {
                    "db": db_config["name"],
                    "login": odoo_username,
                    "password": odoo_password,
                }
                response = requests.post(login_url, json=login_data, timeout=10)
                if response.status_code == 200 and "session_id" in response.cookies:
                    print("✅ Odoo connection test successful")
                else:
                    print(
                        "⚠️  Could not verify Odoo connection - credentials will be saved anyway"
                    )
            except Exception as e:
                print(f"⚠️  Could not test Odoo connection: {e}")

        return {
            "username": odoo_username,
            "password": odoo_password,
            "url": odoo_config["url"],
            "database": db_config["name"],
        }

    def verify_postgresql_access(self) -> Dict:
        """Verify PostgreSQL access and configuration"""
        print("\n🐘 Verifying PostgreSQL access...")

        try:
            # Test connection
            conn = psycopg2.connect(
                host="localhost", port=5432, user="postgres", database="postgres"
            )
            conn.close()
            print("✅ PostgreSQL connection successful")

            # Check if odoo user exists
            odoo_user_exists = self.postgresql_user_exists("odoo")
            if not odoo_user_exists:
                create_user = (
                    input("Create 'odoo' PostgreSQL user? (y/n) [y]: ").strip().lower()
                )
                if create_user != "n":
                    if self.create_postgresql_user("odoo"):
                        print("✅ PostgreSQL user 'odoo' created")
                    else:
                        print("❌ Failed to create PostgreSQL user 'odoo'")
            else:
                print("✅ PostgreSQL user 'odoo' exists")

            return {
                "host": "localhost",
                "port": 5432,
                "path": self.pg_path,
                "connection_string": "postgresql://localhost:5432/postgres",
            }

        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return {}

    def save_project_config(
        self,
        board: Dict,
        group: Optional[Dict],
        repo: Dict,
        odoo_config: Dict,
        db_config: Dict,
        odoo_user_config: Dict,
        pg_config: Dict,
    ) -> Dict:
        """Save complete project configuration"""
        config = {
            "project_name": repo["name"],
            "created_at": datetime.now().isoformat(),
            "monday": {
                "board_id": str(board["id"]),
                "board_name": board["name"],
                "group_id": str(group["id"]) if group else None,
                "group_name": group["title"] if group else None,
            },
            "github": {
                "repo_full_name": repo["full_name"],
                "repo_owner": repo["owner"]["login"],
                "repo_name": repo["name"],
            },
            "odoo": {
                "instance_key": odoo_config["key"],
                "instance_name": odoo_config["name"],
                "url": odoo_config["url"],
                "database": db_config["name"],
                "username": odoo_user_config["username"],
                "password": odoo_user_config["password"],
            },
            "database": {
                "name": db_config["name"],
                "user": db_config["user"],
                "password": db_config["password"],
                "host": db_config["host"],
                "port": db_config["port"],
            },
            "postgresql": pg_config,
        }

        # Save to project context
        context_file = self.setup_dir / ".project_context.json"
        with open(context_file, "w") as f:
            json.dump(config, f, indent=2)

        # Update .env file
        self.update_env_file(config)

        print("✅ Project configuration saved")
        return config

    def update_mcp_configurations(self, config: Dict):
        """Update all MCP server configurations"""
        try:
            from project_context import ProjectContextManager

            manager = ProjectContextManager()

            # Create compatible context for existing system
            context = {
                "board_id": config["monday"]["board_id"],
                "board_name": config["monday"]["board_name"],
                "group_id": config["monday"]["group_id"],
                "group_name": config["monday"]["group_name"],
                "repo_full_name": config["github"]["repo_full_name"],
                "repo_owner": config["github"]["repo_owner"],
                "repo_name": config["github"]["repo_name"],
                "updated_at": config["created_at"],
            }

            manager.save_context(context)
            print("✅ MCP configurations updated")

        except Exception as e:
            print(f"❌ Failed to update MCP configurations: {e}")

    def update_odoo_config_files(self, config: Dict):
        """Update odoo_config.json files for mcp-odoo compatibility"""
        try:
            # Create odoo_config.json in current directory
            odoo_config = {
                "url": config["odoo"]["url"],
                "db": config["odoo"]["database"],
                "username": config["odoo"]["username"],
                "password": config["odoo"]["password"],
                "version": "18.0",
            }

            # Save to current directory
            config_file = self.setup_dir / "odoo_config.json"
            with open(config_file, "w") as f:
                json.dump(odoo_config, f, indent=2)
            print(f"✅ Created {config_file}")

            # Also save to home directory as fallback
            home_config = Path.home() / ".odoo_config.json"
            with open(home_config, "w") as f:
                json.dump(odoo_config, f, indent=2)
            print(f"✅ Created {home_config}")

            print("✅ Odoo MCP configuration files updated")

        except Exception as e:
            print(f"❌ Failed to update Odoo config files: {e}")

    def update_odoo_server_config(self, config: Dict):
        """Update Odoo server configuration file with default database"""
        try:
            instance_key = config["odoo"]["instance_key"]
            db_name = config["odoo"]["database"]

            # Find the config file for this instance
            config_file = None
            for key, instance_config in self.odoo_instances.items():
                if key == instance_key:
                    config_file = Path(instance_config["config"])
                    break

            if not config_file or not config_file.exists():
                print(f"⚠️  Odoo config file not found for {instance_key}")
                return

            # Read current config
            content = config_file.read_text()
            lines = content.split("\n")

            # Update db_name line
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith("db_name ="):
                    lines[i] = f"db_name = {db_name}"
                    updated = True
                    print(f"✅ Set default database to: {db_name}")
                    break

            if updated:
                # Write back the config
                config_file.write_text("\n".join(lines))
                print(f"✅ Updated Odoo server config: {config_file}")
            else:
                print(f"⚠️  Could not find db_name setting in {config_file}")

        except Exception as e:
            print(f"❌ Failed to update Odoo server config: {e}")

    def verify_odoo_connection(self, config: Dict):
        """Verify Odoo connection and provide setup guidance"""
        try:
            odoo_url = config["odoo"]["url"]
            db_name = config["odoo"]["database"]
            username = config["odoo"]["username"]

            print(f"🔍 Testing connection to {odoo_url}...")

            # Test basic HTTP connectivity first
            import requests

            try:
                response = requests.get(f"{odoo_url}/web/database/selector", timeout=5)
                if response.status_code == 200:
                    print("✅ Odoo server is running and accessible")

                    # Test MCP-Odoo configuration
                    print("🔍 Testing MCP-Odoo configuration...")
                    result = subprocess.run(
                        ["npx", "-y", "mcp-odoo"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        input="",  # Provide empty input to avoid hanging
                    )

                    if "Authentication error" in result.stderr:
                        print("⚠️  MCP-Odoo config created but authentication failed")
                        print(
                            f"   This is normal if database '{db_name}' doesn't exist yet or user '{username}' needs setup"
                        )
                        print("   📝 Next steps:")
                        print(f"   1. Start Odoo: Open {odoo_url} in browser")
                        print(
                            f"   2. Create database '{db_name}' or verify user '{username}' exists"
                        )
                        print("   3. Restart Claude/Cursor to reload MCP servers")
                    elif "Error starting server" not in result.stderr:
                        print("✅ MCP-Odoo configuration working!")
                    else:
                        print("⚠️  MCP-Odoo configuration may need adjustment")

                else:
                    print(
                        f"⚠️  Odoo server responded with status {response.status_code}"
                    )
                    self.show_odoo_start_instructions(config)

            except requests.exceptions.ConnectionError:
                print("❌ Cannot connect to Odoo server")
                self.show_odoo_start_instructions(config)
            except requests.exceptions.Timeout:
                print("⏱️  Odoo server connection timeout")
                self.show_odoo_start_instructions(config)

        except Exception as e:
            print(f"⚠️  Connection verification failed: {e}")
            self.show_odoo_start_instructions(config)

    def show_odoo_start_instructions(self, config: Dict):
        """Show instructions for starting Odoo"""
        instance_key = config["odoo"]["instance_key"]
        odoo_url = config["odoo"]["url"]

        print("\n📋 To start your Odoo instance:")
        print(
            f"   1. Run: /Users/markshaw/Desktop/git/odoo/manage-odoo.sh start-{instance_key}"
        )
        print(f"   2. Wait for startup, then open: {odoo_url}")
        print(f"   3. Create database: {config['odoo']['database']}")
        print(f"   4. Setup user: {config['odoo']['username']}")
        print("   5. Restart Claude/Cursor to reload MCP servers")

    def show_project_summary(self, config: Dict):
        """Show project setup summary"""
        print(f"\n📊 Project: {config['project_name']}")
        print("-" * 40)
        print(f"📋 Monday Board: {config['monday']['board_name']}")
        print(f"   ID: {config['monday']['board_id']}")
        if config["monday"].get("group_name"):
            print(f"👥 Working Group: {config['monday']['group_name']}")
            print(f"   ID: {config['monday']['group_id']}")
        else:
            print("👥 Working Group: All groups (no filter)")
        print(f"🐙 GitHub Repo: {config['github']['repo_full_name']}")
        print(f"🔧 Odoo Instance: {config['odoo']['instance_name']}")
        print(f"   URL: {config['odoo']['url']}")
        print(f"   Database: {config['odoo']['database']}")
        print(f"   Username: {config['odoo']['username']}")
        print(
            f"🐘 PostgreSQL: {config['postgresql'].get('connection_string', 'Not configured')}"
        )
        print()
        print("🔄 Next steps:")
        print("1. Restart Cursor/Claude Desktop to apply MCP changes")
        print("2. Verify all MCP servers show green status:")
        print("   ✅ itms-workflow (Monday.com integration)")
        print("   ✅ postgresql (Database queries)")
        print("   ✅ odoo (Odoo integration)")
        print("   ✅ context7 (Documentation search)")
        print("3. If Odoo MCP servers show red, ensure Odoo is running:")
        print(
            f"   ▶️  Start: /Users/markshaw/Desktop/git/odoo/manage-odoo.sh start-{config['odoo']['instance_key']}"
        )
        print(f"   🌐 Access: {config['odoo']['url']}")
        print(f"   🗄️  Create database: {config['odoo']['database']}")
        print("4. Start working on your project tasks!")

        # Show nickname and workspace info if available
        if hasattr(self, "_created_nickname"):
            print(f"\n🎯 Project nickname: {self._created_nickname}")
            print(
                f"   Switch to this project anytime with: ./itms project {self._created_nickname}"
            )

        if hasattr(self, "_workspace_file"):
            print(f"💼 Cursor workspace: {self._workspace_file}")
            print(f"   Open with: cursor '{self._workspace_file}'")

        print("\n📁 Configuration files updated:")
        print(f"   📋 .env file: {self.setup_dir / '.env'}")
        print("   🔧 Odoo configs: ./odoo_config.json & ~/.odoo_config.json")
        print(f"   ⚙️  Project context: {self.setup_dir / 'project_config.json'}")

    # Helper methods
    def get_monday_boards(self) -> List[Dict]:
        """Fetch Monday.com boards"""
        query = """
        query {
            boards(limit: 50) {
                id
                name
                description
                items_count
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
                boards = data["data"]["boards"]
                # Filter out Subitems boards as they're not selectable project boards
                filtered_boards = [
                    board
                    for board in boards
                    if not board["name"].startswith("Subitems of")
                ]
                return filtered_boards
        except:
            pass

        return []

    def get_monday_groups(self, board_id: str) -> List[Dict]:
        """Fetch Monday.com groups for a specific board"""
        query = f"""
        query {{
            boards(ids: [{board_id}]) {{
                groups {{
                    id
                    title
                    color
                    archived
                }}
            }}
        }}
        """

        try:
            response = self.session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers={"Authorization": self.monday_token},
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" not in data and data["data"]["boards"]:
                    groups = data["data"]["boards"][0]["groups"]
                    # Return only non-archived groups
                    return [g for g in groups if not g.get("archived", False)]
        except:
            pass

        return []

    def get_github_repos(self) -> List[Dict]:
        """Fetch GitHub repositories"""
        try:
            repos = []

            # User repos
            response = self.session.get(
                "https://api.github.com/user/repos",
                headers={"Authorization": f"token {self.github_token}"},
                params={"per_page": 30, "sort": "updated"},
            )
            if response.status_code == 200:
                repos.extend(response.json())

            # Org repos
            github_org = os.getenv("GITHUB_ORG", "itmsgroup-au")
            if github_org:
                response = self.session.get(
                    f"https://api.github.com/orgs/{github_org}/repos",
                    headers={"Authorization": f"token {self.github_token}"},
                    params={"per_page": 30, "sort": "updated"},
                )
                if response.status_code == 200:
                    repos.extend(response.json())

            return repos
        except:
            return []

    def is_odoo_running(self, pid_file: str) -> bool:
        """Check if Odoo instance is running"""
        try:
            if os.path.exists(pid_file):
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)  # Test if process exists
                return True
        except:
            pass
        return False

    def start_odoo_instance(self, instance_key: str):
        """Start Odoo instance using manage-odoo.sh"""
        try:
            manage_script = "/Users/markshaw/Desktop/git/odoo/manage-odoo.sh"
            if os.path.exists(manage_script):
                subprocess.run([manage_script, f"start-{instance_key}"])
                print(f"✅ Starting {instance_key}...")
        except Exception as e:
            print(f"❌ Failed to start Odoo: {e}")

    def database_exists(self, db_name: str) -> bool:
        """Check if database exists"""
        try:
            conn = psycopg2.connect(
                host="localhost", port=5432, user="postgres", database="postgres"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except:
            return False

    def create_database(self, db_name: str, owner: str = "odoo") -> bool:
        """Create database"""
        try:
            conn = psycopg2.connect(
                host="localhost", port=5432, user="postgres", database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'CREATE DATABASE "{db_name}" OWNER "{owner}"')
            conn.close()
            return True
        except Exception as e:
            print(f"Database creation error: {e}")
            return False

    def postgresql_user_exists(self, username: str) -> bool:
        """Check if PostgreSQL user exists"""
        try:
            conn = psycopg2.connect(
                host="localhost", port=5432, user="postgres", database="postgres"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (username,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except:
            return False

    def create_postgresql_user(self, username: str, password: str = None) -> bool:
        """Create PostgreSQL user"""
        try:
            conn = psycopg2.connect(
                host="localhost", port=5432, user="postgres", database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()

            if password:
                cursor.execute(
                    f"CREATE USER \"{username}\" WITH PASSWORD '{password}' CREATEDB"
                )
            else:
                cursor.execute(f'CREATE USER "{username}" CREATEDB')

            conn.close()
            return True
        except Exception as e:
            print(f"User creation error: {e}")
            return False

    def update_env_file(self, config: Dict):
        """Update .env file with project configuration"""
        env_file = self.setup_dir / ".env"
        if not env_file.exists():
            return

        content = env_file.read_text()
        lines = content.split("\n")

        updates = {
            "MONDAY_BOARD_ID": config["monday"]["board_id"],
            "MONDAY_GROUP_ID": config["monday"]["group_id"] or "",
            "MONDAY_GROUP_NAME": config["monday"]["group_name"] or "",
            "GITHUB_REPO": config["github"]["repo_full_name"],
            "GITHUB_ORG": config["github"]["repo_owner"],
            "ODOO_URL": config["odoo"]["url"],
            "ODOO_DB": config["odoo"]["database"],
            "ODOO_USERNAME": config["odoo"]["username"],
            "ODOO_PASSWORD": config["odoo"]["password"],
            "POSTGRES_CONNECTION_STRING": f"postgresql://localhost:5432/{config['odoo']['database']}",
        }

        for key, value in updates.items():
            found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
                    found = True
                    break

            if not found:
                lines.append(f"{key}={value}")

        env_file.write_text("\n".join(lines))

    def create_project_nickname(self, config: Dict):
        """Create a project nickname for easy switching"""
        print("Creating project nickname for easy project switching...")

        # Generate suggested nickname from project name
        project_name = config["project_name"]
        suggested_nickname = (
            project_name.lower().replace("-", "").replace("_", "").replace(" ", "")
        )

        print(f"Suggested nickname: {suggested_nickname}")
        nickname = (
            input(f"Enter project nickname [{suggested_nickname}]: ").strip()
            or suggested_nickname
        )

        # Import project nickname manager
        sys.path.insert(0, str(self.setup_dir.parent / "src"))
        from project_nicknames import ProjectNicknameManager

        nickname_manager = ProjectNicknameManager()

        # Create nickname configuration
        nickname_config = {
            "monday_board_id": config["monday"]["board_id"],
            "monday_board_name": config["monday"]["board_name"],
            "monday_group_id": config["monday"].get("group_id", ""),
            "monday_group_name": config["monday"].get("group_name", ""),
            "github_repo": config["github"]["repo_name"],
            "github_owner": config["github"]["repo_owner"],
            "odoo_database": config["odoo"]["database"],
            "odoo_url": config["odoo"]["url"],
            "description": f"{config['project_name']} - {config['monday']['board_name']}",
        }

        if nickname_manager.add_project_nickname(nickname, nickname_config):
            print(f"✅ Project nickname '{nickname}' created successfully!")
            print(
                f"   You can now switch to this project with: ./itms project {nickname}"
            )

            # Store for summary
            self._created_nickname = nickname

            # Switch to this project immediately
            if nickname_manager.switch_to_project(nickname):
                print(f"✅ Switched to project '{nickname}'")
        else:
            print("❌ Failed to create project nickname")

    def create_cursor_workspace(self, config: Dict):
        """Create Cursor workspace for the project"""
        print("Creating Cursor workspace for the project...")

        # Import contextual dev environment
        sys.path.insert(0, str(self.setup_dir.parent / "src"))
        from contextual_dev_environment import ContextualDevEnvironment

        try:
            env = ContextualDevEnvironment()

            # Get project workspace (this will create it if it doesn't exist)
            workspace_file = env.get_project_workspace()

            print(f"✅ Cursor workspace created: {workspace_file}")
            print(f"   Open with: cursor '{workspace_file}'")

            # Store for summary
            self._workspace_file = workspace_file

            # Ask if user wants to open the workspace immediately
            open_now = input("Open Cursor workspace now? [y/N]: ").strip().lower()
            if open_now in ["y", "yes"]:
                try:
                    subprocess.run(["cursor", workspace_file], check=True)
                    print("✅ Cursor workspace opened")
                except subprocess.CalledProcessError:
                    print("❌ Failed to open Cursor workspace. Please open manually.")
                except FileNotFoundError:
                    print(
                        "❌ Cursor command not found. Please open workspace manually."
                    )
        except Exception as e:
            print(f"❌ Failed to create Cursor workspace: {e}")


def main():
    """Main entry point"""
    try:
        wizard = ProjectSetupWizard()
        wizard.run_wizard()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
