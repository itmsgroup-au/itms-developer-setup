#!/usr/bin/env python3
"""
ITMS Project Setup Wizard
Complete project initialization: Monday board + GitHub repo + Odoo + Database + PostgreSQL
"""

import json
import os
import sys
import subprocess
import psycopg2
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class ProjectSetupWizard:
    """Complete project setup wizard for ITMS development"""
    
    def __init__(self):
        self.setup_dir = Path(__file__).parent
        self.session = requests.Session()
        
        # API tokens
        self.monday_token = os.getenv('MONDAY_API_TOKEN')
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Odoo configurations from manage-odoo.sh
        self.odoo_instances = {
            'enterprise18': {
                'name': 'Odoo 18 Enterprise',
                'url': 'http://localhost:8018/odoo',
                'config': '/Users/markshaw/Desktop/git/odoo/config/odoo18-enterprise.conf',
                'pid': '/Users/markshaw/Desktop/git/odoo/odoo18-enterprise.pid'
            },
            'community18': {
                'name': 'Odoo 18 Community', 
                'url': 'http://localhost:8019/odoo',
                'config': '/Users/markshaw/Desktop/git/odoo/config/odoo18-community.conf',
                'pid': '/Users/markshaw/Desktop/git/odoo/odoo18-community.pid'
            },
            'enterprise19': {
                'name': 'Odoo 19 Enterprise',
                'url': 'http://localhost:8021/odoo', 
                'config': '/Users/markshaw/Desktop/git/odoo/config/odoo19-enterprise.conf',
                'pid': '/Users/markshaw/Desktop/git/odoo/odoo19-enterprise.pid'
            },
            'community19': {
                'name': 'Odoo 19 Community',
                'url': 'http://localhost:8022/odoo',
                'config': '/Users/markshaw/Desktop/git/odoo/config/odoo19-community.conf', 
                'pid': '/Users/markshaw/Desktop/git/odoo/odoo19-community.pid'
            }
        }
        
        # PostgreSQL connection
        self.pg_path = "/Applications/Postgres.app/Contents/Versions/17/bin"
        os.environ['PATH'] = f"{self.pg_path}:{os.environ['PATH']}"
        
        # Set up API headers
        self.session.headers.update({
            'User-Agent': 'ITMS-Setup-Wizard/1.0',
            'Accept': 'application/json'
        })
    
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
        
        if input("Continue? (y/n) [y]: ").strip().lower() == 'n':
            print("❌ Setup cancelled")
            return
        
        # Step 1: Monday Board
        print("\n" + "="*50)
        print("📋 STEP 1: Monday.com Board Selection")
        print("="*50)
        board = self.select_monday_board()
        if not board:
            print("❌ Setup cancelled - no board selected")
            return
        
        # Step 2: GitHub Repo
        print("\n" + "="*50) 
        print("🐙 STEP 2: GitHub Repository Selection")
        print("="*50)
        repo = self.select_github_repo()
        if not repo:
            print("❌ Setup cancelled - no repo selected")
            return
        
        # Step 3: Odoo Instance
        print("\n" + "="*50)
        print("🔧 STEP 3: Odoo Instance Configuration")
        print("="*50)
        odoo_config = self.select_odoo_instance()
        if not odoo_config:
            print("❌ Setup cancelled - no Odoo instance selected")
            return
        
        # Step 4: Database Setup
        print("\n" + "="*50)
        print("🗄️  STEP 4: Database Configuration")
        print("="*50)
        db_config = self.setup_database(odoo_config)
        if not db_config:
            print("❌ Setup cancelled - database setup failed")
            return
        
        # Step 5: PostgreSQL Access
        print("\n" + "="*50)
        print("🐘 STEP 5: PostgreSQL Access Verification")
        print("="*50)
        pg_config = self.verify_postgresql_access()
        
        # Step 6: Save Configuration
        print("\n" + "="*50)
        print("💾 STEP 6: Saving Project Configuration")
        print("="*50)
        project_config = self.save_project_config(board, repo, odoo_config, db_config, pg_config)
        
        # Step 7: Update MCP Servers
        print("\n" + "="*50)
        print("🔗 STEP 7: Updating MCP Server Configurations")
        print("="*50)
        self.update_mcp_configurations(project_config)
        
        # Step 8: Update Odoo MCP config files  
        print("\n" + "="*50)
        print("📝 STEP 8: Updating Odoo MCP Configuration Files")
        print("="*50)
        self.update_odoo_config_files(project_config)
        
        # Step 9: Verify Odoo connectivity
        print("\n" + "="*50)
        print("🔍 STEP 9: Verifying Odoo Connection")
        print("="*50)
        self.verify_odoo_connection(project_config)
        
        print("\n" + "="*50)
        print("✅ PROJECT SETUP COMPLETE!")
        print("="*50)
        self.show_project_summary(project_config)
    
    def select_monday_board(self) -> Optional[Dict]:
        """Select Monday.com board"""
        boards = self.get_monday_boards()
        if not boards:
            return None
        
        print("\nAvailable Monday.com boards:")
        for i, board in enumerate(boards, 1):
            print(f"{i:2d}. {board['name']} (ID: {board['id']}, Items: {board.get('items_count', 0)})")
        
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
            status = "🟢 Running" if self.is_odoo_running(config['pid']) else "🔴 Stopped"
            print(f"{i}. {config['name']} ({config['url']}) {status}")
        
        try:
            choice = input(f"\nSelect Odoo instance (1-{len(instances)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(instances):
                key, config = instances[int(choice) - 1]
                
                # Check if running, offer to start
                if not self.is_odoo_running(config['pid']):
                    start = input(f"Start {config['name']}? (y/n) [y]: ").strip().lower()
                    if start != 'n':
                        self.start_odoo_instance(key)
                
                print(f"✅ Selected: {config['name']}")
                return {'key': key, **config}
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
            if use_existing == 'n':
                return None
        else:
            # Create database
            create = input(f"Create database '{db_name}'? (y/n) [y]: ").strip().lower()
            if create != 'n':
                if self.create_database(db_name, db_user):
                    print(f"✅ Database '{db_name}' created")
                else:
                    print(f"❌ Failed to create database '{db_name}'")
                    return None
        
        return {
            'name': db_name,
            'user': db_user,
            'password': db_password,
            'host': 'localhost',
            'port': 5432
        }
    
    def verify_postgresql_access(self) -> Dict:
        """Verify PostgreSQL access and configuration"""
        print("\n🐘 Verifying PostgreSQL access...")
        
        try:
            # Test connection
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                database='postgres'
            )
            conn.close()
            print("✅ PostgreSQL connection successful")
            
            # Check if odoo user exists
            odoo_user_exists = self.postgresql_user_exists('odoo')
            if not odoo_user_exists:
                create_user = input("Create 'odoo' PostgreSQL user? (y/n) [y]: ").strip().lower()
                if create_user != 'n':
                    if self.create_postgresql_user('odoo'):
                        print("✅ PostgreSQL user 'odoo' created")
                    else:
                        print("❌ Failed to create PostgreSQL user 'odoo'")
            else:
                print("✅ PostgreSQL user 'odoo' exists")
            
            return {
                'host': 'localhost',
                'port': 5432,
                'path': self.pg_path,
                'connection_string': 'postgresql://localhost:5432/postgres'
            }
            
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return {}
    
    def save_project_config(self, board: Dict, repo: Dict, odoo_config: Dict, db_config: Dict, pg_config: Dict) -> Dict:
        """Save complete project configuration"""
        config = {
            'project_name': repo['name'],
            'created_at': datetime.now().isoformat(),
            'monday': {
                'board_id': str(board['id']),
                'board_name': board['name']
            },
            'github': {
                'repo_full_name': repo['full_name'],
                'repo_owner': repo['owner']['login'],
                'repo_name': repo['name']
            },
            'odoo': {
                'instance_key': odoo_config['key'],
                'instance_name': odoo_config['name'],
                'url': odoo_config['url'],
                'database': db_config['name'],
                'username': db_config['user'],
                'password': db_config['password']
            },
            'postgresql': pg_config
        }
        
        # Save to project context
        context_file = self.setup_dir / '.project_context.json'
        with open(context_file, 'w') as f:
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
                'board_id': config['monday']['board_id'],
                'board_name': config['monday']['board_name'],
                'repo_full_name': config['github']['repo_full_name'],
                'repo_owner': config['github']['repo_owner'],
                'repo_name': config['github']['repo_name'],
                'updated_at': config['created_at']
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
                "url": config['odoo']['url'],
                "db": config['odoo']['database'],
                "username": config['odoo']['username'],
                "password": config['odoo']['password'],
                "version": "18.0"
            }
            
            # Save to current directory
            config_file = self.setup_dir / 'odoo_config.json'
            with open(config_file, 'w') as f:
                json.dump(odoo_config, f, indent=2)
            print(f"✅ Created {config_file}")
            
            # Also save to home directory as fallback
            home_config = Path.home() / '.odoo_config.json'
            with open(home_config, 'w') as f:
                json.dump(odoo_config, f, indent=2)
            print(f"✅ Created {home_config}")
            
            print("✅ Odoo MCP configuration files updated")
            
        except Exception as e:
            print(f"❌ Failed to update Odoo config files: {e}")
    
    def verify_odoo_connection(self, config: Dict):
        """Verify Odoo connection and provide setup guidance"""
        try:
            odoo_url = config['odoo']['url']
            db_name = config['odoo']['database']
            username = config['odoo']['username']
            
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
                        input=""  # Provide empty input to avoid hanging
                    )
                    
                    if "Authentication error" in result.stderr:
                        print("⚠️  MCP-Odoo config created but authentication failed")
                        print(f"   This is normal if database '{db_name}' doesn't exist yet or user '{username}' needs setup")
                        print("   📝 Next steps:")
                        print(f"   1. Start Odoo: Open {odoo_url} in browser")
                        print(f"   2. Create database '{db_name}' or verify user '{username}' exists")
                        print("   3. Restart Claude/Cursor to reload MCP servers")
                    elif "Error starting server" not in result.stderr:
                        print("✅ MCP-Odoo configuration working!")
                    else:
                        print("⚠️  MCP-Odoo configuration may need adjustment")
                        
                else:
                    print(f"⚠️  Odoo server responded with status {response.status_code}")
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
        instance_key = config['odoo']['instance_key']
        odoo_url = config['odoo']['url']
        
        print("\n📋 To start your Odoo instance:")
        print(f"   1. Run: /Users/markshaw/Desktop/git/odoo/manage-odoo.sh start-{instance_key}")
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
        print(f"🐙 GitHub Repo: {config['github']['repo_full_name']}")
        print(f"🔧 Odoo Instance: {config['odoo']['instance_name']}")
        print(f"   URL: {config['odoo']['url']}")
        print(f"   Database: {config['odoo']['database']}")
        print(f"   Username: {config['odoo']['username']}")
        print(f"🐘 PostgreSQL: {config['postgresql'].get('connection_string', 'Not configured')}")
        print()
        print("🔄 Next steps:")
        print("1. Restart Cursor/Claude Desktop to apply MCP changes")
        print("2. Verify all MCP servers show green status:")
        print("   ✅ itms-workflow (Monday.com integration)")
        print("   ✅ postgresql (Database queries)")
        print("   ✅ odoo & odoo-browse (Odoo integration)")
        print("   ✅ context7 (Documentation search)")
        print("3. If Odoo MCP servers show red, ensure Odoo is running:")
        print(f"   ▶️  Start: /Users/markshaw/Desktop/git/odoo/manage-odoo.sh start-{config['odoo']['instance_key']}")
        print(f"   🌐 Access: {config['odoo']['url']}")
        print(f"   🗄️  Create database: {config['odoo']['database']}")
        print("4. Start working on your project tasks!")
        print(f"\n📁 Configuration files updated:")
        print(f"   📋 .env file: {self.setup_dir / '.env'}")
        print(f"   🔧 Odoo configs: ./odoo_config.json & ~/.odoo_config.json")
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
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['data']['boards']
        except:
            pass
        
        return []
    
    def get_github_repos(self) -> List[Dict]:
        """Fetch GitHub repositories"""
        try:
            repos = []
            
            # User repos
            response = self.session.get(
                'https://api.github.com/user/repos',
                headers={'Authorization': f'token {self.github_token}'},
                params={'per_page': 30, 'sort': 'updated'}
            )
            if response.status_code == 200:
                repos.extend(response.json())
            
            # Org repos
            github_org = os.getenv('GITHUB_ORG', 'itmsgroup-au')
            if github_org:
                response = self.session.get(
                    f'https://api.github.com/orgs/{github_org}/repos',
                    headers={'Authorization': f'token {self.github_token}'},
                    params={'per_page': 30, 'sort': 'updated'}
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
                with open(pid_file, 'r') as f:
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
                subprocess.run([manage_script, f'start-{instance_key}'])
                print(f"✅ Starting {instance_key}...")
        except Exception as e:
            print(f"❌ Failed to start Odoo: {e}")
    
    def database_exists(self, db_name: str) -> bool:
        """Check if database exists"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                database='postgres'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except:
            return False
    
    def create_database(self, db_name: str, owner: str = 'odoo') -> bool:
        """Create database"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                database='postgres'
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
                host='localhost',
                port=5432,
                user='postgres',
                database='postgres'
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
                host='localhost',
                port=5432,
                user='postgres',
                database='postgres'
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            if password:
                cursor.execute(f"CREATE USER \"{username}\" WITH PASSWORD '{password}' CREATEDB")
            else:
                cursor.execute(f"CREATE USER \"{username}\" CREATEDB")
            
            conn.close()
            return True
        except Exception as e:
            print(f"User creation error: {e}")
            return False
    
    def update_env_file(self, config: Dict):
        """Update .env file with project configuration"""
        env_file = self.setup_dir / '.env'
        if not env_file.exists():
            return
        
        content = env_file.read_text()
        lines = content.split('\n')
        
        updates = {
            'MONDAY_BOARD_ID': config['monday']['board_id'],
            'GITHUB_REPO': config['github']['repo_full_name'],
            'GITHUB_ORG': config['github']['repo_owner'],
            'ODOO_URL': config['odoo']['url'],
            'ODOO_DB': config['odoo']['database'],
            'ODOO_USERNAME': config['odoo']['username'],
            'ODOO_PASSWORD': config['odoo']['password'],
            'POSTGRES_CONNECTION_STRING': f"postgresql://localhost:5432/{config['odoo']['database']}"
        }
        
        for key, value in updates.items():
            found = False
            for i, line in enumerate(lines):
                if line.startswith(f'{key}='):
                    lines[i] = f'{key}={value}'
                    found = True
                    break
            
            if not found:
                lines.append(f'{key}={value}')
        
        env_file.write_text('\n'.join(lines))

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