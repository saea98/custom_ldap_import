import ldap
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class LDAPUserImport:
    def __init__(self, env, ldap_config):
        self.env = env
        self.ldap_config = ldap_config
        self.ldap_conn = None

    def connect_ldap(self):
        try:
            ldap_uri = self.ldap_config.ldap_server
            if not ldap_uri.startswith('ldap://'):
                ldap_uri = f'ldap://{ldap_uri}'
            if ':' not in ldap_uri:
                ldap_uri = f'{ldap_uri}:389'

            ldap_base = self.ldap_config.ldap_base
            ldap_binddn = self.ldap_config.ldap_binddn
            ldap_password = self.ldap_config.ldap_password

            _logger.info(f"Attempting to connect to LDAP server: {ldap_uri}")
            _logger.info(f"Using base: {ldap_base}")
            _logger.info(f"Using binddn: {ldap_binddn}")

            self.ldap_conn = ldap.initialize(ldap_uri)
            self.ldap_conn.simple_bind_s(ldap_binddn, ldap_password)
            _logger.info("Successfully connected to LDAP server")
            return True
        except Exception as e:
            _logger.error(f"LDAP Connection Error: {str(e)}")
            return False

    def get_ldap_users(self):
        if not self.connect_ldap():
            return []

        try:
            search_filter = "(objectClass=person)"
            attributes = ['uid', 'cn', 'mail']
            
            results = self.ldap_conn.search_s(
                self.ldap_config.ldap_base,
                ldap.SCOPE_SUBTREE,
                search_filter,
                attributes
            )
            
            users = []
            for dn, attrs in results:
                if attrs:
                    user_data = {
                        'login': attrs.get('uid', [b''])[0].decode('utf-8'),
                        'name': attrs.get('cn', [b''])[0].decode('utf-8'),
                        'email': attrs.get('mail', [b''])[0].decode('utf-8') if 'mail' in attrs else '',
                    }
                    users.append(user_data)
            return users
        except Exception as e:
            _logger.error(f"Error searching LDAP: {str(e)}")
            return []
        finally:
            if self.ldap_conn:
                self.ldap_conn.unbind_s()

    def import_users(self):
        users = self.get_ldap_users()
        created_count = 0
        skipped_count = 0

        for user_data in users:
            try:
                existing_user = self.env['res.users'].search([
                    ('login', '=', user_data['login'])
                ], limit=1)

                if not existing_user:
                    self.env['res.users'].create({
                        'login': user_data['login'],
                        'name': user_data['name'],
                        'email': user_data['email'],
                        'password': 'changeme',
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                        'ldap_user': True,
                        'active': True,
                    })
                    created_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                _logger.error(f"Error creating user {user_data['login']}: {str(e)}")

        return {
            'created': created_count,
            'skipped': skipped_count,
            'total': len(users)
        }