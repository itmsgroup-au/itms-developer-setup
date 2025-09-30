#!/usr/bin/env python3
"""
Smart Code Review Integration - AI-powered code review for ITMS
Integrates with Monday.com for task updates and follows Odoo patterns
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()


class SmartCodeReviewer:
    """AI-powered code review with ITMS and Odoo patterns"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent.parent
        self.config = self.load_config()
        self.session = requests.Session()

        # Load Odoo patterns and security rules
        self.odoo_patterns = self.load_odoo_patterns()
        self.security_rules = self.load_security_rules()
        self.performance_rules = self.load_performance_rules()

        # Active task context
        self.active_task_file = self.setup_dir / ".active_task.json"
        self.active_task = self.load_active_task()

    def load_config(self) -> dict:
        """Load configuration from config.yaml"""
        config_file = self.setup_dir / "config" / "config.yaml"
        with open(config_file, "r") as f:
            content = f.read()

        # Handle environment variable expansion
        import re

        def replace_env_vars(match):
            var_expr = match.group(1)
            if ":-" in var_expr:
                var_name, default_value = var_expr.split(":-", 1)
                default_value = default_value.strip("'\"")
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, match.group(0))

        content = re.sub(r"\$\{([^}]+)\}", replace_env_vars, content)
        return yaml.safe_load(content)

    def load_active_task(self) -> Optional[Dict]:
        """Load currently active task from file"""
        if self.active_task_file.exists():
            try:
                with open(self.active_task_file, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def load_odoo_patterns(self) -> Dict:
        """Load Odoo development patterns and best practices"""
        return {
            "model_patterns": {
                "naming": r"^[a-z]+(\.[a-z]+)*$",
                "required_fields": ["_name"],
                "optional_fields": ["_description", "_order", "_rec_name"],
                "forbidden_patterns": [
                    r"\.sudo\(\)\.write\(",  # Dangerous sudo usage
                    r"\.env\.cr\.execute\(",  # Direct SQL execution
                    r'\.env\.ref\([\'"][^\'"]+"[\'"].*\.sudo\(\)',  # Sudo with refs
                ],
            },
            "view_patterns": {
                "arch_validation": True,
                "xpath_safety": True,
                "required_attrs": ["id", "model"],
                "forbidden_xpath": [
                    '//field[@name="id"]',  # Don't show ID field
                    '//field[@name="create_uid"]',  # Avoid exposing system fields
                ],
            },
            "security_patterns": {
                "access_rights": r"ir\.model\.access\.csv",
                "record_rules": r"ir\.rule",
                "required_groups": ["base.group_user"],
            },
        }

    def load_security_rules(self) -> List[Dict]:
        """Load security validation rules"""
        return [
            {
                "name": "No hardcoded passwords",
                "pattern": r'password\s*=\s*[\'"][^\'"]+[\'"]',
                "severity": "critical",
                "message": "Hardcoded passwords detected. Use environment variables.",
            },
            {
                "name": "No SQL injection risks",
                "pattern": r'\.execute\([\'"][^\'"]*.format\(',
                "severity": "high",
                "message": "Potential SQL injection. Use parameterized queries.",
            },
            {
                "name": "No dangerous sudo usage",
                "pattern": r"\.sudo\(\)\.(?:create|write|unlink)\(",
                "severity": "high",
                "message": "Dangerous sudo usage. Verify security implications.",
            },
            {
                "name": "No API keys in code",
                "pattern": r'(?:api_key|secret_key|access_token)\s*=\s*[\'"][^\'"]+[\'"]',
                "severity": "critical",
                "message": "API keys detected in code. Use environment variables.",
            },
            {
                "name": "No debug code in production",
                "pattern": r"(?:pdb\.set_trace\(|debugger;|console\.log\()",
                "severity": "medium",
                "message": "Debug code found. Remove before production.",
            },
            {
                "name": "Suspicious debug prints",
                "pattern": r'print\([\'"](?:DEBUG|TEST|FIXME|TODO|XXX)',
                "severity": "low",
                "message": "Debug print statement found. Consider using logging.",
            },
        ]

    def load_performance_rules(self) -> List[Dict]:
        """Load performance validation rules"""
        return [
            {
                "name": "Avoid N+1 queries in loops",
                "pattern": r"for\s+.*\s+in\s+.*:\s*\n\s*.*\.search\(",
                "severity": "medium",
                "message": "Potential N+1 query. Consider using search_read or batch operations.",
            },
            {
                "name": "Use proper field selection",
                "pattern": r'\.search\([^)]*\)(?!\[[\'"][^\'"]+[\'"]\])',
                "severity": "low",
                "message": "Consider specifying fields to improve performance.",
            },
            {
                "name": "Avoid large recordsets",
                "pattern": r"\.search\(\[\]\)",
                "severity": "medium",
                "message": "Searching all records. Consider pagination or filters.",
            },
            {
                "name": "Use computed fields efficiently",
                "pattern": r"@api\.depends\([^)]*\)\s*\n.*for.*in.*:",
                "severity": "low",
                "message": "Consider batch processing for computed fields.",
            },
        ]

    def get_changed_files(self, commit_range: str = None) -> List[Path]:
        """Get list of changed files in current branch"""
        if commit_range:
            cmd = ["git", "diff", "--name-only", commit_range]
        else:
            cmd = ["git", "diff", "--name-only", "HEAD~1..HEAD"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.setup_dir
            )
            if result.returncode == 0:
                files = [
                    Path(f.strip()) for f in result.stdout.split("\n") if f.strip()
                ]
                # Filter by extension and exclude certain patterns
                filtered_files = []
                for f in files:
                    if f.suffix in [".py", ".xml", ".js", ".css"]:
                        # Skip certain files that shouldn't be analyzed strictly
                        if not any(
                            pattern in str(f)
                            for pattern in [
                                "archive/",
                                "__pycache__/",
                                ".git/",
                                "node_modules/",
                                "itms_workflow.py",
                                "itms_setup.py",  # Skip CLI tools
                            ]
                        ):
                            filtered_files.append(f)
                return filtered_files
            return []
        except:
            return []

    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze Python file for Odoo patterns and issues"""
        issues = []

        if not file_path.exists():
            return {"file": str(file_path), "issues": issues}

        content = file_path.read_text()

        # Determine if this is an Odoo-specific file
        is_odoo_file = any(
            keyword in content
            for keyword in [
                "models.Model",
                "models.TransientModel",
                "from odoo",
                "import odoo",
                "api.depends",
                "fields.",
                "_inherit",
                "_name",
            ]
        )

        # Check security rules (always apply)
        for rule in self.security_rules:
            import re

            matches = re.finditer(
                rule["pattern"], content, re.MULTILINE | re.IGNORECASE
            )
            for match in matches:
                line_number = content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": "security",
                        "severity": rule["severity"],
                        "line": line_number,
                        "message": rule["message"],
                        "rule": rule["name"],
                        "code": match.group(),
                    }
                )

        # Check performance rules only for Odoo files
        if is_odoo_file:
            for rule in self.performance_rules:
                import re

                matches = re.finditer(
                    rule["pattern"], content, re.MULTILINE | re.IGNORECASE
                )
                for match in matches:
                    line_number = content[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "type": "performance",
                            "severity": rule["severity"],
                            "line": line_number,
                            "message": rule["message"],
                            "rule": rule["name"],
                            "code": match.group(),
                        }
                    )

            # Check Odoo model patterns
            if "models.Model" in content or "models.TransientModel" in content:
                issues.extend(self.check_odoo_model_patterns(content, file_path))

        return {"file": str(file_path), "issues": issues}

    def check_odoo_model_patterns(self, content: str, file_path: Path) -> List[Dict]:
        """Check Odoo-specific model patterns"""
        issues = []

        # Check for required _name field
        if "class " in content and "models.Model" in content:
            import re

            # Find all model classes
            class_pattern = (
                r"class\s+(\w+)\([^)]*models\.(?:Model|TransientModel)[^)]*\):"
            )
            classes = re.finditer(class_pattern, content, re.MULTILINE)

            for class_match in classes:
                class_start = class_match.end()
                # Find the end of the class (next class or end of file)
                next_class = re.search(r"\nclass\s+", content[class_start:])
                class_end = (
                    class_start + next_class.start() if next_class else len(content)
                )

                class_content = content[class_start:class_end]

                # Check for _name field
                if "_name" not in class_content:
                    line_number = content[: class_match.start()].count("\n") + 1
                    issues.append(
                        {
                            "type": "odoo_pattern",
                            "severity": "high",
                            "line": line_number,
                            "message": "Odoo model missing required _name field",
                            "rule": "odoo_model_name_required",
                            "code": class_match.group(),
                        }
                    )

                # Check for dangerous patterns
                for pattern in self.odoo_patterns["model_patterns"][
                    "forbidden_patterns"
                ]:
                    matches = re.finditer(pattern, class_content, re.MULTILINE)
                    for match in matches:
                        line_number = (
                            content[: class_start + match.start()].count("\n") + 1
                        )
                        issues.append(
                            {
                                "type": "odoo_pattern",
                                "severity": "high",
                                "line": line_number,
                                "message": f"Dangerous Odoo pattern detected: {match.group()}",
                                "rule": "odoo_dangerous_pattern",
                                "code": match.group(),
                            }
                        )

        return issues

    def analyze_xml_file(self, file_path: Path) -> Dict:
        """Analyze XML file for Odoo view patterns"""
        issues = []

        if not file_path.exists():
            return {"file": str(file_path), "issues": issues}

        content = file_path.read_text()

        # Check for dangerous XPath patterns
        for xpath in self.odoo_patterns["view_patterns"]["forbidden_xpath"]:
            if xpath in content:
                import re

                matches = re.finditer(re.escape(xpath), content, re.MULTILINE)
                for match in matches:
                    line_number = content[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "type": "odoo_view",
                            "severity": "medium",
                            "line": line_number,
                            "message": f"Potentially problematic XPath: {xpath}",
                            "rule": "odoo_xpath_safety",
                            "code": xpath,
                        }
                    )

        # Check for missing required attributes in record tags
        import re

        record_pattern = r"<record[^>]*>"
        records = re.finditer(record_pattern, content, re.MULTILINE)

        for record_match in records:
            record_tag = record_match.group()
            if "id=" not in record_tag:
                line_number = content[: record_match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": "odoo_view",
                        "severity": "high",
                        "line": line_number,
                        "message": "Record missing required id attribute",
                        "rule": "odoo_record_id_required",
                        "code": record_tag,
                    }
                )

        return {"file": str(file_path), "issues": issues}

    def run_comprehensive_review(self, target_files: List[Path] = None) -> Dict:
        """Run comprehensive code review on changed files"""
        if target_files is None:
            target_files = self.get_changed_files()

        if not target_files:
            # If no changed files, get all Python/XML files in current directory
            target_files = list(Path(".").glob("**/*.py")) + list(
                Path(".").glob("**/*.xml")
            )
            # Filter out non-Odoo files
            target_files = [
                f
                for f in target_files
                if not any(
                    pattern in str(f)
                    for pattern in [
                        "archive/",
                        "__pycache__/",
                        ".git/",
                        "node_modules/",
                        "itms_workflow.py",
                        "itms_setup.py",
                        "setup_git_hooks.py",
                        "code_review_integration.py",
                        "contextual_dev_environment.py",
                    ]
                )
                and not str(f).startswith(".")
            ]

        review_results = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": len(target_files),
            "files": [],
            "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        }

        print(f"🔍 Analyzing {len(target_files)} files...")

        for file_path in target_files:
            if file_path.suffix == ".py":
                result = self.analyze_python_file(file_path)
            elif file_path.suffix == ".xml":
                result = self.analyze_xml_file(file_path)
            else:
                continue

            review_results["files"].append(result)

            # Update summary counts
            for issue in result["issues"]:
                severity = issue["severity"]
                if severity in review_results["summary"]:
                    review_results["summary"][severity] += 1

        return review_results

    def generate_review_report(self, review_results: Dict) -> str:
        """Generate human-readable review report"""
        report = []
        report.append("# 🔍 Smart Code Review Report")
        report.append(f"**Generated:** {review_results['timestamp']}")
        report.append(f"**Files Analyzed:** {review_results['files_analyzed']}")
        report.append("")

        # Summary
        summary = review_results["summary"]
        total_issues = sum(summary.values())

        if total_issues == 0:
            report.append("## ✅ No Issues Found")
            report.append("All files pass the code review checks!")
            return "\n".join(report)

        report.append("## 📊 Summary")
        report.append(f"- 🔴 Critical: {summary['critical']}")
        report.append(f"- 🟠 High: {summary['high']}")
        report.append(f"- 🟡 Medium: {summary['medium']}")
        report.append(f"- 🔵 Low: {summary['low']}")
        report.append(f"- **Total Issues:** {total_issues}")
        report.append("")

        # Detailed findings
        report.append("## 🔍 Detailed Findings")

        for file_result in review_results["files"]:
            if not file_result["issues"]:
                continue

            report.append(f"### 📄 {file_result['file']}")

            # Group issues by severity
            issues_by_severity = {}
            for issue in file_result["issues"]:
                severity = issue["severity"]
                if severity not in issues_by_severity:
                    issues_by_severity[severity] = []
                issues_by_severity[severity].append(issue)

            for severity in ["critical", "high", "medium", "low"]:
                if severity in issues_by_severity:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🔵",
                    }
                    report.append(
                        f"**{severity_emoji[severity]} {severity.title()} Issues:**"
                    )

                    for issue in issues_by_severity[severity]:
                        report.append(f"- Line {issue['line']}: {issue['message']}")
                        if issue.get("code"):
                            report.append("  ```")
                            report.append(f"  {issue['code']}")
                            report.append("  ```")
                    report.append("")

        # Recommendations
        report.append("## 💡 Recommendations")

        if summary["critical"] > 0:
            report.append("- **Critical issues must be fixed** before deployment")
        if summary["high"] > 0:
            report.append("- **High priority issues** should be addressed promptly")
        if summary["medium"] > 0:
            report.append(
                "- **Medium issues** should be reviewed and planned for fixes"
            )
        if summary["low"] > 0:
            report.append(
                "- **Low priority issues** can be addressed in future iterations"
            )

        report.append("")
        report.append("---")
        report.append("*Generated by ITMS Smart Code Review Integration*")

        return "\n".join(report)

    def update_monday_task(self, review_results: Dict, report: str):
        """Update Monday.com task with review results"""
        if not self.active_task:
            print("ℹ️  No active task - skipping Monday.com update")
            return

        summary = review_results["summary"]
        total_issues = sum(summary.values())

        # Create update message
        if total_issues == 0:
            update_text = f"✅ Code review completed - No issues found in {review_results['files_analyzed']} files"
        else:
            update_text = "🔍 Code review completed:\n"
            update_text += f"📊 Issues found: {total_issues} total\n"
            update_text += f"- 🔴 Critical: {summary['critical']}\n"
            update_text += f"- 🟠 High: {summary['high']}\n"
            update_text += f"- 🟡 Medium: {summary['medium']}\n"
            update_text += f"- 🔵 Low: {summary['low']}\n"

            if summary["critical"] > 0:
                update_text += "⚠️ Critical issues require immediate attention"

        # Post to Monday.com
        self.post_monday_update(self.active_task["id"], update_text)

    def post_monday_update(self, item_id: str, update_text: str):
        """Post an update to Monday.com item"""
        mutation = """
        mutation {
            create_update(
                item_id: %s,
                body: "%s"
            ) {
                id
                body
            }
        }
        """ % (
            item_id,
            update_text.replace('"', '\\"').replace("\n", "\\n"),
        )

        try:
            monday_token = self.config["apis"]["monday"]["token"]
            response = self.session.post(
                "https://api.monday.com/v2",
                json={"query": mutation},
                headers={"Authorization": monday_token},
            )

            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print(f"⚠️  Monday.com update warning: {result['errors']}")
                else:
                    print("✅ Monday.com task updated with review results")
            else:
                print(f"❌ Failed to post to Monday.com: {response.status_code}")

        except Exception as e:
            print(f"❌ Monday.com update failed: {e}")

    def save_review_report(self, report: str, results: Dict) -> Path:
        """Save review report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.setup_dir / f"code_review_{timestamp}.md"

        report_file.write_text(report)

        # Also save JSON results
        json_file = self.setup_dir / f"code_review_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)

        return report_file


def main():
    """Main entry point for code review"""
    import argparse

    parser = argparse.ArgumentParser(description="Smart Code Review Integration")
    parser.add_argument("--files", nargs="*", help="Specific files to review")
    parser.add_argument(
        "--commit-range", help="Git commit range to review (e.g., HEAD~3..HEAD)"
    )
    parser.add_argument(
        "--save-report", action="store_true", help="Save report to file"
    )
    parser.add_argument(
        "--update-monday", action="store_true", help="Update Monday.com task"
    )
    parser.add_argument(
        "--include-setup-files",
        action="store_true",
        help="Include workflow/setup files in analysis",
    )
    parser.add_argument(
        "--odoo-only",
        action="store_true",
        help="Only analyze files that appear to be Odoo modules",
    )

    args = parser.parse_args()

    reviewer = SmartCodeReviewer()

    # Determine target files
    target_files = None
    if args.files:
        target_files = [Path(f) for f in args.files]
    elif args.commit_range:
        target_files = reviewer.get_changed_files(args.commit_range)
    else:
        # Get changed files or all files if none changed
        target_files = reviewer.get_changed_files()
        if not target_files:
            target_files = list(Path(".").glob("**/*.py")) + list(
                Path(".").glob("**/*.xml")
            )

            # Apply filtering based on arguments
            if not args.include_setup_files:
                target_files = [
                    f
                    for f in target_files
                    if not any(
                        pattern in str(f)
                        for pattern in [
                            "archive/",
                            "__pycache__/",
                            ".git/",
                            "node_modules/",
                            "itms_workflow.py",
                            "itms_setup.py",
                            "setup_git_hooks.py",
                            "code_review_integration.py",
                            "contextual_dev_environment.py",
                            "project_context.py",
                            "itms_mcp_server.py",
                        ]
                    )
                    and not str(f).startswith(".")
                ]

            # Filter to Odoo-only if requested
            if args.odoo_only:
                odoo_files = []
                for f in target_files:
                    if f.suffix == ".py":
                        try:
                            content = f.read_text()
                            if any(
                                keyword in content
                                for keyword in [
                                    "models.Model",
                                    "models.TransientModel",
                                    "from odoo",
                                    "import odoo",
                                    "api.depends",
                                    "fields.",
                                    "_inherit",
                                    "_name",
                                ]
                            ):
                                odoo_files.append(f)
                        except:
                            pass
                    elif f.suffix == ".xml" and any(
                        pattern in str(f)
                        for pattern in ["views/", "data/", "security/"]
                    ):
                        odoo_files.append(f)
                target_files = odoo_files

    # Run review
    print("🚀 Starting Smart Code Review...")
    results = reviewer.run_comprehensive_review(target_files)

    # Generate report
    report = reviewer.generate_review_report(results)
    print(report)

    # Save report if requested
    if args.save_report:
        report_file = reviewer.save_review_report(report, results)
        print(f"\n📄 Report saved: {report_file}")

    # Update Monday.com if requested
    if args.update_monday:
        reviewer.update_monday_task(results, report)

    # Exit with appropriate code
    total_issues = sum(results["summary"].values())
    critical_issues = results["summary"]["critical"]

    if critical_issues > 0:
        print("\n❌ Critical issues found - review failed")
        sys.exit(1)
    elif total_issues > 0:
        print(f"\n⚠️  {total_issues} issues found - review completed with warnings")
        sys.exit(0)
    else:
        print("\n✅ No issues found - review passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
