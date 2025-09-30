#!/usr/bin/env python3
"""
Git Hooks Setup for ITMS Smart Code Review
Creates pre-commit and commit-msg hooks with code review integration
"""

import os
import stat
import sys
from pathlib import Path
from typing import Dict


class GitHooksSetup:
    """Setup and manage Git hooks for code review integration"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent.parent
        self.git_root = self.find_git_root()
        self.hooks_dir = self.git_root / ".git" / "hooks" if self.git_root else None

    def find_git_root(self) -> Path:
        """Find the Git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        # If not found in cwd, check setup directory
        current = self.setup_dir
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        raise RuntimeError("Not in a Git repository")

    def create_pre_commit_hook(self) -> Path:
        """Create comprehensive pre-commit hook"""
        hook_content = f'''#!/usr/bin/env python3
"""
ITMS Pre-commit Hook - Smart Code Review Integration
Runs security, performance, and Odoo convention checks
"""

import sys
import subprocess
import os
from pathlib import Path

# Add setup directory to path for imports
sys.path.insert(0, str(Path("{self.setup_dir}").resolve()))

def run_code_review():
    """Run smart code review on staged files"""
    try:
        # Get staged files
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Failed to get staged files")
            return False

        staged_files = [f.strip() for f in result.stdout.split('\\n') if f.strip()]
        python_xml_files = [f for f in staged_files if f.endswith(('.py', '.xml'))]

        if not python_xml_files:
            print("ℹ️  No Python/XML files staged - skipping code review")
            return True

        print(f"🔍 Running code review on {{len(python_xml_files)}} staged files...")

        # Run the code reviewer
        review_cmd = [
            sys.executable,
            str(Path("{self.setup_dir}") / "src" / "code_review_integration.py"),
            "--files"
        ] + python_xml_files

        result = subprocess.run(review_cmd, cwd="{self.git_root}")

        if result.returncode == 0:
            print("✅ Code review passed")
            return True
        elif result.returncode == 1:
            print("❌ Critical issues found - commit blocked")
            print("Fix critical issues before committing")
            return False
        else:
            print("⚠️  Code review completed with warnings")

            # Ask user if they want to proceed
            response = input("Proceed with commit despite warnings? (y/N): ")
            return response.lower() == 'y'

    except Exception as e:
        print(f"❌ Code review failed: {{e}}")
        return False

def run_formatters():
    """Run Black and Ruff formatters"""
    try:
        print("🎨 Running Black formatter...")
        result = subprocess.run(['black', '--check', '--diff', '.'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Black formatting issues found:")
            print(result.stdout)
            print("Run 'black .' to fix formatting")
            return False

        print("🔍 Running Ruff linter...")
        result = subprocess.run(['ruff', 'check', '.'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Ruff linting issues found:")
            print(result.stdout)
            print("Run 'ruff check --fix .' to fix issues")
            return False

        print("✅ Formatting and linting passed")
        return True

    except FileNotFoundError as e:
        print(f"⚠️  Formatter not found: {{e}}")
        print("Install with: pip install black ruff")
        return True  # Don't block commit if tools aren't installed
    except Exception as e:
        print(f"❌ Formatting check failed: {{e}}")
        return False

def main():
    """Main pre-commit hook logic"""
    print("🚀 ITMS Pre-commit Hook")
    print("=" * 40)

    # Run formatters first
    if not run_formatters():
        print("\\n❌ Pre-commit hook failed - formatting issues")
        sys.exit(1)

    # Run code review
    if not run_code_review():
        print("\\n❌ Pre-commit hook failed - code review issues")
        sys.exit(1)

    print("\\n✅ Pre-commit hook passed - ready to commit")
    sys.exit(0)

if __name__ == "__main__":
    main()
'''

        hook_file = self.hooks_dir / "pre-commit"
        hook_file.write_text(hook_content)

        # Make executable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        return hook_file

    def create_commit_msg_hook(self) -> Path:
        """Create commit message hook for Monday.com integration"""
        hook_content = f'''#!/usr/bin/env python3
"""
ITMS Commit Message Hook - Monday.com Integration
Validates commit messages and updates Monday.com tasks
"""

import sys
import re
import json
import subprocess
from pathlib import Path

# Add setup directory to path for imports
sys.path.insert(0, str(Path("{self.setup_dir}").resolve()))

def load_active_task():
    """Load active task from workflow"""
    task_file = Path("{self.setup_dir}") / '.active_task.json'
    if task_file.exists():
        try:
            with open(task_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate commit message format"""
    lines = message.strip().split('\\n')
    if not lines:
        return False, "Empty commit message"

    subject = lines[0]

    # Check conventional commit format
    conventional_pattern = r'^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\\(.+\\))?: .+$'

    if not re.match(conventional_pattern, subject):
        return False, "Commit message should follow conventional format: type(scope): description"

    # Check length
    if len(subject) > 72:
        return False, "Subject line should be 72 characters or less"

    # Check for proper capitalization and punctuation
    description = subject.split(':', 1)[1].strip()
    if not description[0].islower():
        return False, "Description should start with lowercase letter"

    if description.endswith('.'):
        return False, "Description should not end with period"

    return True, "Valid commit message"

def enhance_commit_message(message: str, active_task: dict) -> str:
    """Enhance commit message with task information"""
    lines = message.strip().split('\\n')
    subject = lines[0]
    body = lines[1:] if len(lines) > 1 else []

    # Add empty line if body exists
    if body and body[0] != '':
        body.insert(0, '')

    # Add task reference
    body.extend([
        '',
        f'Related to Monday.com task: {{active_task["name"]}}',
        f'Task ID: {{active_task["id"]}}',
        '',
        '🤖 Generated with Claude Code',
        'Co-Authored-By: Claude <noreply@anthropic.com>'
    ])

    return '\\n'.join([subject] + body)

def update_monday_task(active_task: dict, commit_hash: str, commit_message: str):
    """Update Monday.com task with commit information"""
    try:
        from src.code_review_integration import SmartCodeReviewer

        reviewer = SmartCodeReviewer()

        # Get short commit hash
        short_hash = commit_hash[:7] if commit_hash else "pending"

        # Create update text
        commit_subject = commit_message.split('\\n')[0]
        update_text = f"💻 Code committed: {{commit_subject}}\\n"
        update_text += f"🔗 Commit: {{short_hash}}"

        # Post to Monday.com
        reviewer.post_monday_update(active_task['id'], update_text)

    except Exception as e:
        print(f"⚠️  Failed to update Monday.com: {{e}}")

def main():
    """Main commit message hook logic"""
    if len(sys.argv) != 2:
        print("Usage: commit-msg <commit-msg-file>")
        sys.exit(1)

    commit_msg_file = Path(sys.argv[1])

    # Read commit message
    message = commit_msg_file.read_text()

    # Validate message
    is_valid, error = validate_commit_message(message)
    if not is_valid:
        print(f"❌ Invalid commit message: {{error}}")
        print("\\nExpected format: type(scope): description")
        print("Examples:")
        print("  feat(auth): add user login functionality")
        print("  fix(ui): resolve button alignment issue")
        print("  docs(readme): update installation instructions")
        sys.exit(1)

    # Load active task
    active_task = load_active_task()

    if active_task:
        print(f"🎯 Active task: {{active_task['name']}}")

        # Enhance commit message with task info
        enhanced_message = enhance_commit_message(message, active_task)
        commit_msg_file.write_text(enhanced_message)

        # Schedule Monday.com update (will run in post-commit)
        task_update_file = Path("{self.setup_dir}") / '.pending_task_update.json'
        with open(task_update_file, 'w') as f:
            json.dump({{
                'task': active_task,
                'message': message
            }}, f)

    print("✅ Commit message validated")

if __name__ == "__main__":
    main()
'''

        hook_file = self.hooks_dir / "commit-msg"
        hook_file.write_text(hook_content)

        # Make executable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        return hook_file

    def create_post_commit_hook(self) -> Path:
        """Create post-commit hook for Monday.com updates"""
        hook_content = f'''#!/usr/bin/env python3
"""
ITMS Post-commit Hook - Complete Monday.com Integration
Updates Monday.com tasks after successful commit
"""

import sys
import json
import subprocess
from pathlib import Path

# Add setup directory to path for imports
sys.path.insert(0, str(Path("{self.setup_dir}").resolve()))

def main():
    """Main post-commit hook logic"""
    # Check for pending task update
    task_update_file = Path("{self.setup_dir}") / '.pending_task_update.json'

    if not task_update_file.exists():
        return

    try:
        # Load pending update
        with open(task_update_file, 'r') as f:
            update_data = json.load(f)

        # Get commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                              capture_output=True, text=True)
        commit_hash = result.stdout.strip() if result.returncode == 0 else "unknown"

        # Update Monday.com task
        from src.code_review_integration import SmartCodeReviewer

        reviewer = SmartCodeReviewer()
        active_task = update_data['task']
        commit_message = update_data['message']

        # Create update text
        commit_subject = commit_message.split('\\n')[0]
        short_hash = commit_hash[:7]

        update_text = f"💻 Code committed: {{commit_subject}}\\n"
        update_text += f"🔗 Commit: {{short_hash}}"

        # Post to Monday.com
        reviewer.post_monday_update(active_task['id'], update_text)

        # Clean up
        task_update_file.unlink()

        print(f"✅ Monday.com task updated: {{active_task['name']}}")

    except Exception as e:
        print(f"⚠️  Failed to update Monday.com in post-commit: {{e}}")
        # Clean up on error
        if task_update_file.exists():
            task_update_file.unlink()

if __name__ == "__main__":
    main()
'''

        hook_file = self.hooks_dir / "post-commit"
        hook_file.write_text(hook_content)

        # Make executable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        return hook_file

    def install_hooks(self) -> Dict[str, Path]:
        """Install all Git hooks"""
        if not self.hooks_dir:
            raise RuntimeError("Git hooks directory not found")

        self.hooks_dir.mkdir(exist_ok=True)

        hooks = {}

        print("🪝 Installing Git hooks...")

        # Install pre-commit hook
        try:
            hooks["pre-commit"] = self.create_pre_commit_hook()
            print(f"✅ Installed: {hooks['pre-commit']}")
        except Exception as e:
            print(f"❌ Failed to install pre-commit hook: {e}")

        # Install commit-msg hook
        try:
            hooks["commit-msg"] = self.create_commit_msg_hook()
            print(f"✅ Installed: {hooks['commit-msg']}")
        except Exception as e:
            print(f"❌ Failed to install commit-msg hook: {e}")

        # Install post-commit hook
        try:
            hooks["post-commit"] = self.create_post_commit_hook()
            print(f"✅ Installed: {hooks['post-commit']}")
        except Exception as e:
            print(f"❌ Failed to install post-commit hook: {e}")

        return hooks

    def uninstall_hooks(self):
        """Remove ITMS Git hooks"""
        hooks_to_remove = ["pre-commit", "commit-msg", "post-commit"]

        for hook_name in hooks_to_remove:
            hook_file = self.hooks_dir / hook_name
            if hook_file.exists():
                # Check if it's our hook
                content = hook_file.read_text()
                if "ITMS" in content:
                    hook_file.unlink()
                    print(f"🗑️  Removed: {hook_file}")
                else:
                    print(f"⚠️  Skipped: {hook_file} (not ITMS hook)")

    def status(self):
        """Show status of Git hooks"""
        print("📊 Git Hooks Status")
        print("=" * 40)

        if not self.hooks_dir or not self.hooks_dir.exists():
            print("❌ No Git hooks directory found")
            return

        hooks_to_check = ["pre-commit", "commit-msg", "post-commit"]

        for hook_name in hooks_to_check:
            hook_file = self.hooks_dir / hook_name

            if hook_file.exists():
                content = hook_file.read_text()
                if "ITMS" in content:
                    status_icon = "✅"
                    status_text = "Installed (ITMS)"
                else:
                    status_icon = "⚠️ "
                    status_text = "Exists (Not ITMS)"

                # Check if executable
                if not os.access(hook_file, os.X_OK):
                    status_icon = "❌"
                    status_text += " - Not executable"
            else:
                status_icon = "❌"
                status_text = "Not installed"

            print(f"{status_icon} {hook_name}: {status_text}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ITMS Git Hooks Setup")
    parser.add_argument(
        "action", choices=["install", "uninstall", "status"], help="Action to perform"
    )

    args = parser.parse_args()

    try:
        setup = GitHooksSetup()

        if args.action == "install":
            hooks = setup.install_hooks()
            print(f"\\n🎉 Installed {len(hooks)} Git hooks")
            print("\\nHooks will now:")
            print("- ✅ Run code review on pre-commit")
            print("- 📝 Validate commit messages")
            print("- 📋 Update Monday.com tasks automatically")

        elif args.action == "uninstall":
            setup.uninstall_hooks()
            print("\\n🗑️  ITMS Git hooks removed")

        elif args.action == "status":
            setup.status()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
