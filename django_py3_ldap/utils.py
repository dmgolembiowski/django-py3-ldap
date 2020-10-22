import re
import binascii
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
try:
    from django.utils import six
except:
    import six

from django_py3_ldap.conf import settings


def import_func(func):
    if callable(func):
        return func
    elif isinstance(func, six.string_types):
        return import_string(func)
    raise AttributeError("Expected a function {0!r}".format(func))


def clean_ldap_name(name):
    """
    Transforms given name into a form that won't interfere with LDAP queries.
    """
    return re.sub(
        r'[^a-zA-Z0-9 _\-.@:*]',
        lambda c: "\\" + force_text(
            binascii.hexlify(c.group(0).encode("latin-1", errors="ignore"))
        ).upper(),
        force_text(name),
    )


def convert_model_fields_to_ldap_fields(model_fields):
    """
    Converts a set of model fields into a set of corresponding LDAP fields.
    """
    return {
        settings.LDAP_AUTH_USER_FIELDS[field_name]: field_value
        for field_name, field_value
        in model_fields.items()
    }


def format_search_filters(ldap_fields):
    return [
        "({attribute_name}={field_value})".format(
            attribute_name=clean_ldap_name(field_name),
            field_value=clean_ldap_name(field_value),
        )
        for field_name, field_value
        in ldap_fields.items()
    ]


def format_search_filter(model_fields):
    """
    Creates an LDAP search filter for the given set of model fields.
    There are examples of the content of dictionaries in comments.
    """
    # model_fields: {'username': 'login_value'}

    ldap_fields = convert_model_fields_to_ldap_fields(model_fields)
    # ldap_fields: {'sAMAccountName': 'provided_value'}

    ldap_fields["objectClass"] = settings.LDAP_AUTH_USER_OBJECT_CLASS
    # ldap_fields: {'sAMAccountName': 'login_value', 'objectClass': 'person'}

    # LDAP_AUTH_FORMAT_SEARCH_FILTERS is by default format_search_filters()
    search_filters = import_func(
        settings.LDAP_AUTH_FORMAT_SEARCH_FILTERS)(ldap_fields)
    # search_filters: [(sAMAccountName=provided_value), (objectClass=person)]

    # return: (&(sAMAccountName=provided_value)(objectClass=person))
    return "(&{})".format("".join(search_filters))


def clean_user_data(model_fields):
    """
    Transforms the user data loaded from
    LDAP into a form suitable for creating a user.
    """
    return model_fields


def sync_user_relations(user, ldap_attributes):
    # do nothing by default
    pass
