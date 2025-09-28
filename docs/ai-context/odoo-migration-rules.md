# Odoo Migration Rules Memory Context

## Critical v17→v18 Changes

### 1. View Structure Updates
- **Change**: `<tree>` tags → `<list>` tags
- **Pattern**: Replace all `<tree>` elements in XML views
- **Example**: `<tree string="Records">` → `<list string="Records">`

### 2. XPath Expression Fixes
- **Issue**: XPath selectors targeting `<tree>` elements fail
- **Fix**: Update XPath to target `<list>` elements
- **Pattern**: `//tree[@string='name']` → `//list[@string='name']`

### 3. Action View Modes
- **Change**: Update action definitions for new view structure
- **Check**: Ensure `view_mode` parameters reference correct view types
- **Validate**: All actions with tree views work correctly

### 4. Attrs Deprecation
- **Issue**: `attrs` attribute deprecated in favor of direct attributes
- **Pattern**: Move `attrs` logic to individual field attributes
- **Example**: `attrs="{'invisible': [('state', '!=', 'draft')]}"` → `invisible="state != 'draft'"`

## Critical v18→v19 Changes

### 1. ORM Method Updates
- **Area**: Model method signatures and return types
- **Action**: Check for deprecated ORM methods
- **Validate**: All custom model methods use current API

### 2. Python 3.10+ Compliance
- **Requirement**: Code must run on Python 3.10+
- **Check**: Remove deprecated Python features
- **Validate**: Type hints and modern syntax usage

### 3. Asset Bundle Conflicts
- **Issue**: Asset definitions may conflict between modules
- **Fix**: Use `asset_conflict_fix` module patterns
- **Pattern**: Proper asset inheritance and bundle management

### 4. Security Permission Updates
- **Area**: Access rights and record rules
- **Check**: Ensure all security definitions are valid
- **Validate**: Test access controls after upgrade

## General Migration Patterns

### 1. Manifest File Updates
```python
{
    'name': 'Module Name',
    'version': '19.0.1.0.0',  # Always update version
    'depends': ['base'],       # Check dependency versions
    'installable': True,       # Ensure still installable
    'auto_install': False,     # Review auto-install logic
}
```

### 2. JavaScript/OWL Updates
- **Framework**: Migrate to OWL framework components
- **Pattern**: Update client-side code for new architecture
- **Test**: Verify all interactive elements work

### 3. Template Structure
- **Views**: Ensure template inheritance works correctly
- **QWeb**: Update QWeb templates for new structure
- **Assets**: Verify asset loading and dependencies

## Validation Checklist

### Pre-Migration
- [ ] Backup current state
- [ ] Document current version
- [ ] List all custom modifications
- [ ] Plan rollback strategy

### During Migration
- [ ] Update manifest versions
- [ ] Fix view structures (tree→list)
- [ ] Update XPath expressions
- [ ] Test module installation
- [ ] Validate basic functionality

### Post-Migration
- [ ] Run full test suite
- [ ] Verify UI functionality
- [ ] Check data integrity
- [ ] Performance validation
- [ ] Security audit

## Common Pitfalls

### 1. Incomplete XPath Updates
- **Problem**: Missing XPath expressions still targeting `<tree>`
- **Solution**: Systematic search and replace across all files
- **Tool**: Use `grep -r "tree\[" module_directory/`

### 2. Asset Loading Issues
- **Problem**: JavaScript/CSS assets not loading correctly
- **Solution**: Review asset bundle definitions
- **Check**: Browser console for loading errors

### 3. Security Access Issues
- **Problem**: Access rights not working after upgrade
- **Solution**: Review and update security definitions
- **Test**: Login as different user types

## Module-Specific Considerations

### ITMS Modules
- **Pattern**: Follow established ITMS naming conventions
- **Testing**: Extra attention to complex business logic
- **Integration**: Ensure inter-module compatibility

### Custom Fields
- **Migration**: Custom field definitions may need updates
- **Validation**: Ensure all custom fields still function
- **Data**: Check for data loss or corruption

### Reports
- **Templates**: Report templates may need structure updates
- **Data**: Verify report data accuracy
- **Performance**: Check report generation speed