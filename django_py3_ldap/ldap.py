import ldap3
import logging
from ldap3.core.exceptions import LDAPException
from contextlib import contextmanager
from django_py3_ldap.conf import settings
from django_py3_ldap.utils import import_func, format_search_filter
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


class Connection(object):
    """
    Opened connection to an LDAP server.
    """
    def __init__(self, connection):
        self._connection = connection

    def search_user(self, **kwargs):
        """
        Search the user in LDAP.
        Return DN and other attributes if found, otherwise return None.
        """
        # Search the LDAP database
        try:
            self._connection.search(
                search_base=settings.LDAP_USER_SEARCH_BASE,
                search_filter=format_search_filter(kwargs),
                search_scope=ldap3.SUBTREE,
                attributes=ldap3.ALL_ATTRIBUTES,
                get_operational_attributes=True,
                size_limit=1,
            )
            return self._connection.response[0]['attributes']
        except KeyError:
            logger.warning(f"LDAP user lookup failed: no such user")
            return None
        except LDAPException as ex:
            logger.warning(f"LDAP user lookup failed: {ex}")
            return None

    def get_user(self, user_ldap_data=None, password=None):
        """
        Try to rebind with user provided credentials.
        Return Django User object when successful, otherwise None.
        """
        # Rebind with DN learned during user lookup in search_user()
        try:
            self._connection.rebind(
                user=user_ldap_data['distinguishedName'][0],
                password=password,
            )
            logger.info(f'LDAP user rebind successful')
            return self._get_or_create_user(user_ldap_data)
        except KeyError as ke:
            logger.warning(f"LDAP rebind failed: {ke}")
            return None
        except LDAPException as ex:
            logger.warning(f"LDAP rebind failed: {ex}")
            return None

    def iter_users(self):
        """
        Returns an iterator of Django users that correspond to
        users in the LDAP database.
        """
        try:
            paged_entries = self._connection.extend.standard.paged_search(
                search_base=settings.LDAP_USER_SEARCH_BASE,
                search_filter=format_search_filter({}),
                search_scope=ldap3.SUBTREE,
                attributes=ldap3.ALL_ATTRIBUTES,
                get_operational_attributes=True,
                paged_size=30,
            )
            return filter(None, (
                self._get_or_create_user(entry["attributes"])
                for entry
                in paged_entries
                if entry["type"] == "searchResEntry"
            ))
        except KeyError as ke:
            logger.warning(f"LDAP iter_users failed: {ke}")
        except LDAPException as ex:
            logger.warning(f"LDAP paged search failed: {ex}")

    def _get_or_create_user(self, attributes):
        """
        Returns a Django user for the given LDAP user data.
        If the user does not exist, then it will be created.
        """
        if attributes is None:
            logger.warning("LDAP user attributes empty")
            return None

        User = get_user_model()

        # Create the user data
        user_fields = {
            field_name: (
                attributes[attribute_name][0]
                if isinstance(attributes[attribute_name], (list, tuple)) else
                attributes[attribute_name]
            )
            for field_name, attribute_name
            in settings.LDAP_USER_FIELDS.items()
            if attribute_name in attributes
        }
        user_fields = import_func(settings.LDAP_CLEAN_USER_DATA)(user_fields)
        # user_fields: {'username':'value', 'first_name':'value', ...}

        # Create the user lookup
        user_lookup = {
            field_name: user_fields.pop(field_name, "")
            for field_name
            in settings.LDAP_USER_LOOKUP_FIELDS
        }
        # user_lookup: {'username':'value'}
        # user_fields: {'first_name':'value', ...}

        # Update or create the user
        user, created = User.objects.update_or_create(
            defaults=user_fields,
            **user_lookup
        )

        # If the user was created, set them an unusable password
        if created:
            logger.info(f"LDAP user created in Django DB: {user_lookup}")
            user.set_unusable_password()
            user.save()

        # Update relations
        import_func(settings.LDAP_SYNC_USER_RELATIONS)(user, attributes)

        return user


@contextmanager
def connection():
    """
    Creates and yields admin-priviledged connection to the LDAP server.
    """
    # Configure the connection.
    if settings.LDAP_USE_TLS:
        auto_bind = ldap3.AUTO_BIND_TLS_BEFORE_BIND
    else:
        auto_bind = ldap3.AUTO_BIND_NO_TLS

    # Connect with Admin account to LDAP.
    try:
        c = ldap3.Connection(
            ldap3.Server(
                settings.LDAP_URL,
                allowed_referral_hosts=[("*", True)],
                get_info=ldap3.NONE,
                connect_timeout=settings.LDAP_CONNECT_TIMEOUT,
            ),
            user=settings.LDAP_ADMIN_DN,
            password=settings.LDAP_ADMIN_PASSWORD,
            auto_bind=auto_bind,
            raise_exceptions=True,
            receive_timeout=settings.LDAP_RECEIVE_TIMEOUT,
        )
    except LDAPException as ex:
        logger.warning(f"LDAP admin bind failed: {ex}")
        yield None
        return

    # Connect and bind successful, yield the connection.
    logger.info("LDAP admin bind successful")
    try:
        yield Connection(c)
    finally:
        c.unbind()


def authenticate(*args, **kwargs):
    """
    Authenticates with the LDAP server, and returns
    the corresponding Django user instance.
    """
    # Check validity of login data.
    password = kwargs.pop("password")
    if not password or \
            frozenset(kwargs) != frozenset(settings.LDAP_USER_LOOKUP_FIELDS):
        return None

    # Connect to LDAP Server with admin-priviledged account
    with connection() as c:
        # Admin bind failed
        if c is None:
            return None

        # Admin bind successful, search user
        user_ldap_data = c.search_user(**kwargs)
        if user_ldap_data:
            logger.info("LDAP user lookup successful")
        else:
            return None

        # User exists, rebind with user credentials.
        # Return User object or None based on rebind result.
        return c.get_user(
            user_ldap_data=user_ldap_data,
            password=password,
        )
