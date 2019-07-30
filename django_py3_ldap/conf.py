from django.conf import settings


class LazySetting(object):
    """
    A proxy to names Django setting.
    """
    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return getattr(obj._settings, self.name, self.default)


class LazySettings(object):
    """
    A proxy to LDAP-specific Django settings.
    """
    def __init__(self, settings):
        self._settings = settings

    LDAP_URL = LazySetting(
        name="LDAP_URL",
        default="ldap://localhost:389",
    )

    LDAP_USE_TLS = LazySetting(
        name="LDAP_USE_TLS",
        default=False,
    )

    LDAP_ADMIN_DN = LazySetting(
        name="LDAP_ADMIN_DN",
        default=None,
    )

    LDAP_ADMIN_PASSWORD = LazySetting(
        name="LDAP_ADMIN_PASSWORD",
        default=None,
    )

    LDAP_CONNECT_TIMEOUT = LazySetting(
        name="LDAP_CONNECT_TIMEOUT",
        default=None
    )

    LDAP_RECEIVE_TIMEOUT = LazySetting(
        name="LDAP_RECEIVE_TIMEOUT",
        default=None
    )

    LDAP_USER_SEARCH_BASE = LazySetting(
        name="LDAP_USER_SEARCH_BASE",
        default="ou=people,dc=example,dc=com",
    )

    LDAP_USER_OBJECT_CLASS = LazySetting(
        name="LDAP_USER_OBJECT_CLASS",
        default="inetOrgPerson",
    )

    LDAP_USER_FIELDS = LazySetting(
        name="LDAP_USER_FIELDS",
        default={
            "username": "sAMAccountName",
            "first_name": "givenName",
            "last_name": "sn",
            "email": "mail",
        },
    )

    LDAP_USER_LOOKUP_FIELDS = LazySetting(
        name="LDAP_USER_LOOKUP_FIELDS",
        default=(
            "username",
        ),
    )

    LDAP_FORMAT_SEARCH_FILTERS = LazySetting(
        name="LDAP_FORMAT_SEARCH_FILTERS",
        default="django_py3_ldap.utils.format_search_filters",
    )

    LDAP_CLEAN_USER_DATA = LazySetting(
        name="LDAP_CLEAN_USER_DATA",
        default="django_py3_ldap.utils.clean_user_data",
    )

    LDAP_SYNC_USER_RELATIONS = LazySetting(
        name="LDAP_SYNC_USER_RELATIONS",
        default="django_py3_ldap.utils.sync_user_relations",
    )


settings = LazySettings(settings)
