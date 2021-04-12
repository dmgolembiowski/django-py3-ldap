from setuptools import find_packages, setup

from django_py3_ldap import __version__


version_str = ".".join(str(n) for n in __version__)

setup(
    name='django_py3_ldap',
    version=version_str,
    license='BSD License',
    description='Django LDAP user authentication backend for Python 3.',
    author='Martin Vlasko',
    author_email='mail@martinvlasko.com',
    url='https://github.com/dmgolembiowski/django-py3-ldap',
    packages=find_packages(),
    install_requires=[
        "django>=2.2",
        "ldap3>=2.5",
        "pyasn1>=0.4.5",
    ],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
