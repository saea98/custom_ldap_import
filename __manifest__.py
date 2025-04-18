{
    'name': 'LDAP User Import',
    'version': '1.0',
    'category': 'Authentication',
    'summary': 'Import users from LDAP',
    'description': """
        Import users from LDAP server to Odoo
    """,
    'author': 'Salvador Jiménez Sánchez',
    'website': 'saea98.com',
    'depends': ['auth_ldap', 'base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}