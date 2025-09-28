# Git Commit Best Practices Guide

This guide outlines best practices for writing better Git commit messages, including adopting conventional commits, enforcing standards with hooks, automating with tools, and integrating with CI workflows.

## Prerequisites

Before setting up, ensure you have:
- Python 3.8+ installed
- Node.js and npm installed (for commitlint)
- Git initialized in your project
- (Optional) A GitHub repository for CI automation

## Team Setup Instructions

Follow these steps to set up the commit standards across your team:

1. **Install Dependencies:**
   ```
   # Install commitlint globally
   npm install -g @commitlint/cli @commitlint/config-conventional

   # Install Python tools
   pip install commitizen black pylint towncrier
   ```

2. **Configure Commitlint:**
   - Create `.commitlintrc.json` in project root:
     ```json
     {
       "extends": ["@commitlint/config-conventional"]
     }
     ```

3. **Set Up Pre-commit Hook:**
   - Create `.git/hooks/prepare-commit-msg`:
     ```bash
     #!/bin/sh
     exec < /dev/null
     commitlint --edit $1
     ```
   - Make executable: `chmod +x .git/hooks/prepare-commit-msg`

4. **Initialize Commitizen:**
   - Create `pyproject.toml` with:
     ```toml
     [tool.commitizen]
     name = "cz_conventional_commits"
     tag_format = "v$version"
     changelog_file = "HISTORY.rst"

     [tool.towncrier]
     filename = "HISTORY.rst"
     directory = "newsfragments"
     title_format = "## {version} ({project_date})"
     underlines = "-"

     [[tool.towncrier.type]]
     directory = "feature"
     name = "Features"
     showcontent = true

     [[tool.towncrier.type]]
     directory = "bugfix"
     name = "Bug Fixes"
     showcontent = true

     [[tool.towncrier.type]]
     directory = "doc"
     name = "Documentation"
     showcontent = true

     [[tool.towncrier.type]]
     directory = "misc"
     name = "Miscellaneous"
     showcontent = true
     ```
   - Or run `cz init` (if interactive terminal available)

5. **Set Up CI Workflow:**
   - Create `.github/workflows/ci.yml` with the provided YAML

6. **Verify Setup:**
   - Test commit: `cz commit` (should prompt for conventional commit)
   - Check formatting: `black --check .`
   - Lint code: `pylint **/*.py`
   - Check changelog: `towncrier check`

## Adopt Conventional Commits for Structure

Use standardized prefixes to categorize commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code formatting (no behavior change)
- `refactor:` - Code changes without behavior change
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Format:** `<type>[optional scope]: <description>`

Examples:
- `feat(auth): add user login validation`
- `fix(api): resolve timeout on data fetch`
- `docs(readme): update installation instructions`

**Guidelines:**
- Keep the description under 50 characters
- Use imperative mood (e.g., "add validation" not "added validation")
- Add a body for detailed explanations if needed
- Use footer to reference issues (e.g., "Closes #42")

## Enforce with Git Hooks

Use commitlint to validate commit messages before they are created.

1. Install commitlint globally:
   ```
   npm install -g @commitlint/cli @commitlint/config-conventional
   ```

2. Create `.commitlintrc.json` in your project root:
   ```json
   {
     "extends": ["@commitlint/config-conventional"]
   }
   ```

3. Add a pre-commit hook:
   - Edit `.git/hooks/prepare-commit-msg` (create if it doesn't exist)
   - Add the following content:
     ```bash
     #!/bin/sh
     exec < /dev/null
     commitlint --edit $1
     ```
   - Make it executable:
     ```
     chmod +x .git/hooks/prepare-commit-msg
     ```

This will validate commit messages and reject non-compliant ones.

## Automate with Commitizen (for Interactive Commits)

Commitizen provides an interactive prompt for generating compliant commit messages.

1. Install Commitizen (Python-friendly):
   ```
   pip install commitizen
   ```

2. Initialize in your project:
   ```
   cz init
   ```

3. Use for commits:
   ```
   cz commit
   ```

This will prompt for type, scope, description, and generate a properly formatted message.

**Integration with towncrier:**
Commitizen automatically creates changelog fragments in `newsfragments/` based on commit types (e.g., `feat` creates in `feature/` directory).

## Automate Code Quality and Commit Standards with GitHub Actions

To enforce consistent code formatting, linting, and commit message standards, automate checks in GitHub Actions. This runs on every push and pull request, preventing bad code or non-compliant commits from merging.

Create or update `.github/workflows/ci.yml` with the following workflow:

```yaml
name: Python CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Required for commitlint to check commit history
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: pip install black pylint towncrier
    - name: Format with Black
      run: black --check .
    - name: Lint with Pylint
      run: pylint **/*.py
    - name: Check Changelog Fragments (if releasing)
      run: towncrier check
    - name: Install commitlint
      run: npm install -g @commitlint/cli @commitlint/config-conventional
    - name: Lint commit messages
      uses: wagoid/commitlint-github-action@v5
      with:
        configFile: .commitlintrc.json
```

This workflow:
- Formats code with Black (fails if not formatted)
- Lints Python code with Pylint
- Checks changelog fragments with towncrier
- Validates commit messages against conventional commit standards

Ensure your `.commitlintrc.json` is configured as shown in the "Enforce with Git Hooks" section.

For towncrier integration, ensure changelog fragments are generated based on commit types (e.g., `feat` commits create fragments in `newsfragments/feature/`).

## Using Towncrier for Changelog

Towncrier generates a `HISTORY.rst` file from changelog fragments created by commits.

### Creating Changelog Fragments

- Use `cz commit` to create commits, which automatically generates fragments.
- Or manually create files in `newsfragments/{type}/` directories (e.g., `newsfragments/feature/123.feature.rst` for a feature).

Fragment files contain the changelog entry text.

### Generating the Changelog

1. Before release: `towncrier build --version 1.0.0 --yes` (replace with actual version)
2. This creates `HISTORY.rst` with all fragments, grouped by type.
3. Commit the updated `HISTORY.rst` and remove processed fragments.

### Checking Fragments

- `towncrier check` validates that fragments exist for unreleased changes.
- Run this in CI to ensure releases have changelog entries.