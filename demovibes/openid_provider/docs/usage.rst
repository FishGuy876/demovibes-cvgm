=====
Usage 
=====

After instalation and database sync login to your django admin site.
You'll notice new application and it's model ``OpenIDs``.

Click `add` and at least select ``User`` from select box.
If you want that user to have human-friendly openid identifier enter it into ``Openid`` field.
Hit `Save` and your first OpenID is ready.

Your OpenID Claimed Identifier URL will be::

    <your host>/<your openid base url>/<contents of Openid field>/


When you will use it to login on the web, Relaying Party [#]_ will redirect you to your site.
If you aren't logged in on your site you'll first have to log in, then you'll be asked if you
want to add Relaying Party to your "Trusted Roots" [#]_. Add it and next time you'll log in it'll be
automatic - you won't even notice your site appearance if you'll be still logged in.

Customization
-------------

You can grant your users way to customize their OpenID by preparing form or you can automate it's creation.

After creating user you can::

    from django.contrib.auth.models import User
    user = User.objects.get(pk=...)
    # create openid for that user:
    user.openid_set.create(openid=user.username)

Revoking Relaying Party authorization
-------------------------------------

At any time you can revoke any Relaying Party authorization to use your OpenID by removing it from
"Trusted Roots" list associated with your OpenID::

    # note that there can be few openids associated with each user
    openid = OpenID.objects.filter(user=request.user, default=True)[0]

    # remove all relaying parties with google.com in URL
    openid.trustedroot_set.filter(trust_root__contains='google.com').delete()

.. rubric:: Footnotes

.. [#] that's fancy name for site where you want to login via OpenID.
.. [#] list of sites authorized to use your OpenID as login information.
