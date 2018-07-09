Introduction
============

Django_ OpenID Provider application acts as OpenID provider (in lame terms
Server) for your `django.contrib.auth` accounts.

If you have your own Django_ powered website you might want to use your admin
account to authenticate on other sites like stackoverflow_ or even in other
django websites you manage (with django_openid_auth for example).

Reasons to do that:

- forget about dozens of passwords on different sites,
- manage and revoke OpenID authorization for sites you log on,
- http://openidexplained.com/

.. _Django: http://www.djangoproject.com/
.. _stackoverflow: http://stackoverflow.com/


Features
--------

- Automatic redirect to login page for unauthorized users.
- Semi-automated creation of OpenID identifiers (leave OpenID field empty).
- Decision page for adding trust_root to one's OpenID trusted sites.


New releases and bug reporting
------------------------------

Code and issue tracker is hosted on `bitbucket.org/romke/django_openid_provider/`_

.. _`bitbucket.org/romke/django_openid_provider/`: http://bitbucket.org/romke/django_openid_provider/

