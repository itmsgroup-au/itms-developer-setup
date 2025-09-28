# Odoo Testing Standards Memory Context

## 4-Level Testing Hierarchy

### Level 1: Installation Testing (100% Automated)
**Purpose**: Verify module installs without errors
**Automation**: Fully automated
**Target Time**: 5 minutes per module

```python
def test_module_installation(module_name, database):
    """Test if module installs without errors"""
    cmd = ['odoo-bin', '-d', database, '-i', module_name, '--stop-after-init']
    result = subprocess.run(cmd, capture_output=True, timeout=300)
    return result.returncode == 0
```

**Critical Checks**:
- [ ] Module installs without Python errors
- [ ] No XML syntax errors
- [ ] All dependencies available
- [ ] Database tables created correctly
- [ ] No manifest file issues

### Level 2: Basic Functionality Testing (85% Automated)
**Purpose**: Verify core module features work
**Automation**: 85% automated, 15% manual verification
**Target Time**: 15 minutes per module

```python
def test_module_functionality(module_name, database):
    """Test basic module functionality"""
    tests = [
        test_models_accessible(),
        test_views_loadable(), 
        test_menus_functional(),
        test_actions_executable(),
        test_workflows_intact()
    ]
    return all(tests)
```

**Test Areas**:
- [ ] Model CRUD operations
- [ ] View rendering (list, form, kanban)
- [ ] Menu items accessible
- [ ] Actions execute without error
- [ ] Basic business logic functions

### Level 3: Integration Testing (60% Automated)
**Purpose**: Verify module integrations with Odoo core
**Automation**: 60% automated, 40% requires human validation
**Target Time**: 30 minutes per module

**Test Areas**:
- [ ] Data flow between modules
- [ ] Computed fields work correctly
- [ ] Security permissions enforced
- [ ] Report generation functions
- [ ] Email/notification systems
- [ ] API endpoint responses

**Key Integration Points**:
- Core Odoo modules (sale, purchase, inventory, accounting)
- Other ITMS modules
- Third-party integrations
- Custom workflows

### Level 4: UI/UX Testing (30% Automated)
**Purpose**: Verify user interface and experience
**Automation**: 30% automated with Selenium, 70% manual
**Target Time**: 45 minutes per module

```python
def test_ui_accessibility(module_name, database):
    """Test UI elements are accessible and functional"""
    driver = setup_selenium_driver()
    # Basic UI testing with Selenium
    # Form loads, buttons work, wizards complete
    pass
```

**Test Areas**:
- [ ] Forms load correctly
- [ ] Buttons and links functional
- [ ] Wizards complete successfully
- [ ] Search and filter operations
- [ ] Mobile responsiveness
- [ ] Accessibility compliance

## Quality Tool Integration

### Black Formatter
**Standard**: 100% compliance for all delivered code
**Command**: `black --check --diff module_path/`
**Auto-fix**: `black module_path/`

```python
def check_black_compliance(module_path):
    """Check if code is Black compliant"""
    result = subprocess.run(['black', '--check', str(module_path)], 
                          capture_output=True)
    return result.returncode == 0
```

### Pylint Analysis
**Standard**: Minimum score 8.5/10
**Command**: `pylint module_path/ --rcfile=.pylintrc`
**Focus**: Code quality, potential bugs, style issues

```python
def run_pylint_analysis(module_path):
    """Run Pylint analysis and return score"""
    result = subprocess.run(['pylint', str(module_path)], 
                          capture_output=True, text=True)
    # Parse score from output
    return score
```

### Bandit Security Scanning
**Standard**: 0 high/critical security issues
**Command**: `bandit -r module_path/ -f json`
**Focus**: Security vulnerabilities, unsafe practices

```python
def run_bandit_scan(module_path):
    """Run security scan with Bandit"""
    result = subprocess.run(['bandit', '-r', str(module_path), '-f', 'json'], 
                          capture_output=True, text=True)
    issues = json.loads(result.stdout)
    return issues
```

### Custom Odoo Rules
**Focus**: Odoo-specific best practices
**Areas**: Model definitions, view structure, security rules

## Performance Testing

### Database Query Analysis
- Monitor SQL query count and complexity
- Identify N+1 query problems
- Validate index usage

### Memory Usage Monitoring
- Track memory consumption during operations
- Identify memory leaks
- Validate garbage collection

### Load Testing Scenarios
```python
def test_concurrent_users(module_name, user_count=10):
    """Test module performance under load"""
    # Simulate concurrent user operations
    # Measure response times
    # Check for deadlocks or errors
    pass
```

## Test Data Management

### Test Database Setup
- Clean database for each test run
- Consistent demo data loading
- Isolated test environments

### Data Integrity Validation
- Check data consistency after operations
- Validate referential integrity
- Ensure no data corruption

## Continuous Integration

### Pre-commit Hooks
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/pylint
    rev: v2.13.0
    hooks:
      - id: pylint
```

### Automated Test Pipeline
1. **Code Quality**: Black, Pylint, Bandit
2. **Unit Tests**: Module installation and basic functionality
3. **Integration Tests**: Cross-module compatibility
4. **Performance Tests**: Load and stress testing

## Success Criteria

### Module Readiness Thresholds
- **Installation**: 100% success rate
- **Functionality**: 95% automated tests pass
- **Integration**: 90% tests pass with manual validation
- **Quality Score**: 75+ points overall
- **Security**: 0 high/critical issues

### Deployment Criteria
- All 4 test levels pass minimum thresholds
- Quality score above 75 points
- Security scan clean
- Performance within acceptable limits
- Manual UAT sign-off completed

## Test Documentation

### Test Results Format
```markdown
## Module: itms_accounting
### Installation Test: ✅ PASS
### Functionality Test: ✅ PASS (47/50 tests)
### Integration Test: ⚠️ WARNING (8/10 tests, manual validation needed)
### UI Test: ✅ PASS (manual testing completed)
### Quality Score: 82/100
### Security: ✅ CLEAN
```

### Issue Tracking
- Document all failed tests
- Priority classification (Critical, High, Medium, Low)
- Assignment and resolution tracking
- Retest verification