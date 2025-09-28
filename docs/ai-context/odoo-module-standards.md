# Odoo Module Standards Memory Context

## Module Structure Standards

### Directory Structure
```
module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── *.py
├── views/
│   ├── *.xml
│   └── templates.xml
├── data/
│   ├── *.xml
│   └── *.csv
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── static/
│   ├── src/
│   └── description/
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── README.rst
└── HISTORY.rst
```

### Manifest File Standards
```python
{
    'name': 'Module Name',
    'version': '19.0.1.0.0',  # Semantic versioning
    'summary': 'Brief module description',
    'description': """
        Detailed module description
        Multiple lines allowed
    """,
    'author': 'ITMS Group',
    'website': 'https://itmsgroup.com.au',
    'category': 'Appropriate Category',
    'depends': ['base'],  # Minimal dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/model_views.xml',
        'data/data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'module_name/static/src/js/*.js',
            'module_name/static/src/css/*.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
```

## Code Quality Standards

### Python Code Standards
- **Formatting**: Black compliance (100%)
- **Linting**: Pylint score 8.5+ out of 10
- **Security**: Bandit scan with 0 high/critical issues
- **Type Hints**: Use type hints for complex functions
- **Docstrings**: All public methods documented

### Model Definitions
```python
class CustomModel(models.Model):
    _name = 'custom.model'
    _description = 'Custom Model Description'
    _order = 'name'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Name',
        required=True,
        help='Model instance name'
    )
    
    @api.depends('field1', 'field2')
    def _compute_total(self):
        """Compute total value from field1 and field2."""
        for record in self:
            record.total = record.field1 + record.field2
```

### View Definitions
```xml
<odoo>
    <data>
        <!-- List View -->
        <record id="custom_model_view_list" model="ir.ui.view">
            <field name="name">custom.model.view.list</field>
            <field name="model">custom.model</field>
            <field name="arch" type="xml">
                <list string="Custom Models">
                    <field name="name"/>
                    <field name="date"/>
                    <field name="state"/>
                </list>
            </field>
        </record>
        
        <!-- Form View -->
        <record id="custom_model_view_form" model="ir.ui.view">
            <field name="name">custom.model.view.form</field>
            <field name="model">custom.model</field>
            <field name="arch" type="xml">
                <form string="Custom Model">
                    <sheet>
                        <group>
                            <field name="name"/>
                            <field name="date"/>
                        </group>
                    </sheet>
                </form>
            </field>
        </record>
    </data>
</odoo>
```

## Security Standards

### Access Rights (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_model,base.group_user,1,0,0,0
access_custom_model_manager,custom.model.manager,model_custom_model,base.group_system,1,1,1,1
```

### Record Rules
```xml
<record id="custom_model_rule_user" model="ir.rule">
    <field name="name">Custom Model: User Access</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Testing Standards

### Unit Test Structure
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomModel(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Model = self.env['custom.model']
        
    def test_create_custom_model(self):
        """Test custom model creation."""
        record = self.Model.create({
            'name': 'Test Record',
        })
        self.assertTrue(record.id)
        self.assertEqual(record.name, 'Test Record')
        
    def test_validation_rules(self):
        """Test model validation rules."""
        with self.assertRaises(ValidationError):
            self.Model.create({
                'name': '',  # Should fail validation
            })
```

### Test Coverage Requirements
- **Critical Modules**: 70%+ test coverage
- **Standard Modules**: 50%+ test coverage
- **All Models**: Basic CRUD tests
- **Business Logic**: Complete scenario testing

## Documentation Standards

### README.rst Format
```rst
Module Name
===========

Brief description of the module purpose and functionality.

Features
--------

* Feature 1
* Feature 2
* Feature 3

Installation
------------

1. Install dependencies
2. Update module list
3. Install module

Configuration
-------------

1. Go to Settings > Module Settings
2. Configure options
3. Save configuration

Usage
-----

Detailed usage instructions with examples.

Known Issues
------------

* Issue 1 description and workaround
* Issue 2 description and workaround

Credits
-------

* Author Name <email@domain.com>
* Company Name
```

### HISTORY.rst Format (OCA Standard)
```rst
History
=======

19.0.1.0.0 (2025-09-27)
========================

Features
--------
* Initial release for Odoo 19.0
* Feature description

Improvements
------------
* Improvement description

Bug Fixes
---------
* Fix description

Technical
---------
* Technical change description

Upgrade Notes
-------------
* Important upgrade information
```

## Performance Standards

### Database Efficiency
- Use appropriate indexes on frequently queried fields
- Avoid N+1 query problems
- Use `@api.depends` correctly for computed fields
- Implement proper caching where beneficial

### Memory Management
- Avoid memory leaks in long-running processes
- Use generators for large data processing
- Properly handle file operations and connections

### Frontend Performance
- Minimize JavaScript bundle size
- Use lazy loading for heavy components
- Optimize CSS for fast rendering
- Implement proper caching strategies

## Module Complexity Scoring

### Code Complexity (40 points)
- **Lines of Code** (10 pts): <500 (10), 500-1000 (7), 1000-2000 (5), >2000 (2)
- **Cyclomatic Complexity** (10 pts): Simple methods, minimal nesting
- **Inheritance Depth** (10 pts): Minimal inheritance chains
- **Method Count** (10 pts): Focused, single-responsibility methods

### Odoo Integration Complexity (35 points)
- **Custom Fields** (10 pts): Minimal field additions to core models
- **View Customizations** (10 pts): Clean view inheritance
- **Workflow Complexity** (10 pts): Simple, linear workflows
- **External Integrations** (5 pts): Minimal external dependencies

### Upgrade Risk Factors (25 points)
- **Deprecated API Usage** (10 pts): Use current APIs only
- **Custom XPath** (5 pts): Minimal complex XPath expressions
- **Database Schema** (5 pts): Avoid direct database modifications
- **Dependencies** (5 pts): Minimal third-party dependencies

## Quality Assurance Checklist

### Pre-Development
- [ ] Requirements clearly defined
- [ ] Module structure planned
- [ ] Dependencies identified
- [ ] Security requirements understood

### During Development
- [ ] Code follows standards
- [ ] Tests written for new functionality
- [ ] Documentation updated
- [ ] Security considerations addressed

### Pre-Deployment
- [ ] All tests pass
- [ ] Code quality standards met
- [ ] Security scan clean
- [ ] Performance tested
- [ ] Documentation complete

### Post-Deployment
- [ ] Functionality verified in production
- [ ] Performance monitoring active
- [ ] User feedback collected
- [ ] Issues tracked and resolved