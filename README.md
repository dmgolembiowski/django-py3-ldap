django-py3-ldap
===============

**django-py3-ldap** provides Django LDAP user authentication backend for Python 3.  
This project is heavily inspired by [django-python3-ldap](https://github.com/etianen/django-python3-ldap).

Purpose
-------

The original library `django-python3-ldap` did not provide
features which were needed for particular use cases.  
These new features required heavy redesign of the authentication logic
established in `django-python3-ldap` library.  
Changing it directly in `django-python3-ldap` could break authentication in existing Django apps.

Aim of this project is **not** to replace `django-python3-ldap` library.  
It was written to resolve specific use cases.  
Stick to the original unless you find yourself in similar situation as described below. 


Installation
------------
1. Install using `pipenv install -e git+https://github.com/sonicblind/django-py3-ldap.git#egg=django-py3-ldap`.
2. Add `'django_py3_ldap'` to your `INSTALLED_APPS` setting.
3. Set (or add) your `AUTHENTICATION_BACKENDS` setting to `("django_py3_ldap.auth.LDAPBackend",)`
4. Configure the settings for your LDAP server (see Available settings, below).


##### New functionality

- DN Format:  
  - Some LDAP servers might require DN in format `CN=Name Lastname,OU=people,DC=example,DC=com`.
For such LDAP configuration `django-python3-ldap` fails to authenticate user if 
username is provided instead of full name.
  - With `django-py3-ldap`, it does not matter what DN format the LDAP server is using. 
The application ensures that correctly formatted DN is used for authentication. To achieve this, 
the application first binds with the admin account, then searches the LDAP database
for a user with provided username and retrieves user's DN. This DN (whatever the format is)
is then used to re-bind to authenticate the user.  


- Admin account required:
  - Because of the above point, a predefined account with admin privileges is required.
Config attributes `LDAP_ADMIN_DN` and `LDAP_ADMIN_PASSWORD` must be defined.  
  


##### Not supported features
Some of the original functionality is not available, this includes:
- management commands (`ldap_sync_users`, `ldap_promote`)
- Microsoft Active Directory support
- installation using pip
- not tested with Python 2


How it works
------------

When a user attempts to authenticate, a connection is made to the LDAP
server, and the application attempts to bind using predefined credentials,
which have enough LDAP privileges to perform search queries across the LDAP database.

If the admin bind attempt is successful, application attempts to search the user
and learn user details, specifically then the user DN.

If the search is successful (the user exists in LDAP), application attempts
to re-bind with learned DN and password provided by user.

If the rebind is successful (user is authenticated), the user details are saved
in a local Django `User` model.  
The local model is only created once,
and the details will be kept updated with the LDAP record details on every login.


Available settings
------------------
These settings are similar to the original.  
Change their default values and add them to your `settings.py` file.

```python
# The URL of the LDAP server.
LDAP_URL = "ldap://localhost:389"

# Initiate TLS on connection.
LDAP_USE_TLS = False

# LDAP account with admin privileges, allowed to search LDAP DB
LDAP_ADMIN_DN = None
LDAP_ADMIN_PASSWORD = None

# LDAP timeouts in seconds
LDAP_CONNECT_TIMEOUT = None
LDAP_RECEIVE_TIMEOUT = None

# User model fields mapped to the LDAP attributes that represent them.
LDAP_USER_FIELDS = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# A tuple of Django model fields used to uniquely identify a user.
LDAP_USER_LOOKUP_FIELDS = ('username',)

# The LDAP search base for looking up users.
LDAP_USER_SEARCH_BASE = "ou=people,dc=example,dc=com"

# The LDAP class that represents a user.
LDAP_USER_OBJECT_CLASS = "person"

# Path to a callable which returns final search filter.
LDAP_FORMAT_SEARCH_FILTERS = "django_py3_ldap.utils.format_search_filters"

# Use this callable to customize how LDAP data is saved to the User model.
LDAP_CLEAN_USER_DATA = "django_py3_ldap.utils.clean_user_data"

# Use this callable to update user relations.
LDAP_SYNC_USER_RELATIONS = "django_py3_ldap.utils.sync_user_relations"
```


More information
----------------

Follow the original documentation on project site [django-python3-ldap](http://github.com/etianen/django-python3-ldap).
