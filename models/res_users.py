from odoo import models, fields, api
from .ldap_import import LDAPUserImport
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    ldap_user = fields.Boolean(string='LDAP User', default=False)

    def import_ldap_users_action(self):
        ldap_config = self.env['res.company.ldap'].search([], limit=1)
        if not ldap_config:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'No LDAP configuration found',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        try:
            _logger.info("Starting LDAP import process")
            importer = LDAPUserImport(self.env, ldap_config)
            result = importer.import_users()
            
            message = f"""
            LDAP import completed:
            - Created: {result['created']} users
            - Skipped: {result['skipped']} users
            - Total processed: {result['total']} users
            """
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Imported Users',
                'res_model': 'res.users',
                'view_mode': 'tree,form',
                'domain': [('ldap_user', '=', True)],
                'context': {'create': False},
                'target': 'current',
                'views': [(False, 'tree'), (False, 'form')],
                'help': message,
            }

        except Exception as e:
            _logger.error(f"Error during LDAP import: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Error during LDAP import: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }