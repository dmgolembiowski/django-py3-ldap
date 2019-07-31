from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from django_py3_ldap import ldap


class Command(BaseCommand):

    help = ("Creates local user models for all users found "
            "in the remote LDAP authentication server.")

    @transaction.atomic()
    def handle(self, *args, **kwargs):
        verbosity = int(kwargs.get("verbosity", 1))
        with ldap.connection() as connection:
            if connection is None:
                raise CommandError("Could not connect to LDAP server")
            for user in connection.iter_users():
                if verbosity >= 1:
                    self.stdout.write("Synced {user}".format(
                        user=user,
                    ))
