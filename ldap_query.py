import ldap
from django.conf import settings

class LDAPUserQuery():
    def __init__(self):


        base = settings.LDAP_BASE
        self._user_base = '' + base
        self._user_login_attr = "mail"

        user_attr_map = {"uid": "uid", "mail": "email"}
        self._retrieveAttributes = user_attr_map.keys() + \
                             [self._user_login_attr]

    @staticmethod
    def get_user_attr(user, attr_key):
        return user[1][attr_key][0]

    def get_users(self, email_substring):

        search_string = "*" + email_substring + "*@monash*"
        userRDN = self._user_login_attr + '=' + search_string

        l = ldap.initialize(settings.LDAP_URL)
        ldap_result = l.search_s(self._user_base, ldap.SCOPE_SUBTREE,
                                  userRDN, self._retrieveAttributes)

        return ldap_result

    def get_authcate_exact(self, email):

        search_string = email
        userRDN = self._user_login_attr + '=' + search_string

        l = ldap.initialize(settings.LDAP_URL)
        ldap_result = l.search_s(self._user_base, ldap.SCOPE_SUBTREE,
                                  userRDN, self._retrieveAttributes)

        return ldap_result
