"""
Views which allow users to create and activate accounts.

"""


from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.core.mail import EmailMessage

from registration.forms import RegistrationForm, RegistrationFormNoFreeEmail
from registration.models import RegistrationProfile
from django.contrib.sites.models import Site

from webview.models import OnelinerMuted
import j2shim
import datetime

class RegistrationFormNoFreeEmailFromSetting(RegistrationFormNoFreeEmail):
    bad_domains = getattr(settings, "BAD_EMAIL_DOMAINS", [])

def activate(request, activation_key,
             template_name='registration/activate.html',
             extra_context=None):
    """
    Activate a ``User``'s account from an activation key, if their key
    is valid and hasn't expired.
    
    By default, use the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    **Required arguments**
    
    ``activation_key``
       The activation key to validate and use for activating the
       ``User``.
    
    **Optional arguments**
       
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.
    
    ``template_name``
        A custom template to use.
    
    **Context:**
    
    ``account``
        The ``User`` object corresponding to the account, if the
        activation was successful. ``False`` if the activation was not
        successful.
    
    ``expiration_days``
        The number of days for which activation keys stay valid after
        registration.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key) # Returns User if successful, otherwise a bool
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
        
    if(type(account).__name__=='bool'):
        # This returned something other than a user profile. In future, if this
        # Returns FALSE, we know there was a problem. For now, just bail out.
        return render_to_response(template_name,
                              { 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=context)
        
    # Inform admin on new user registration?
    email_admin = getattr(settings, 'ADMIN_NOTIFY_ON_NEW_USER', 0) # Disabled by default
    email_user = getattr(settings, 'USER_SEND_CONF_OK', 0) # Disabled by default
    
    if email_admin > 0:
        try:
            mail_to = settings.DEFAULT_FROM_EMAIL
            mail_tpl = loader.get_template('registration/t/new_registrant.txt')
            site = Site.objects.get_current()
            
            c = Context({
                'site' : site,
                'username': account.username,
                'email': account.email,
                'userid': account.id,
                })
            email = EmailMessage(
                    subject='[' + site.name + '] New User Registration Activated!',
                    body=mail_tpl.render(c),
                    from_email=mail_to, # Will always be the same address
                    to=[mail_to])
            email.send(fail_silently=True)
        except:
            # Failed to process the email request for some reason
            pass
        
    if email_user > 0:
        try:
            mail_to = account.email
            mail_tpl = loader.get_template('registration/t/welcome.txt')
            site = Site.objects.get_current()
            
            c = Context({
                'site' : site,
                'username': account.username,
                })
            email = EmailMessage(
                    subject='[' + site.name + '] Your Account Is Now Active!',
                    body=mail_tpl.render(c),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[mail_to])
            email.send(fail_silently=True)
        except:
            # Failed to process the email request for some reason
            pass
        
    return render_to_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=context)


def register(request, success_url=None,
             form_class=RegistrationFormNoFreeEmailFromSetting, profile_callback=None,
             template_name='registration/registration_form.html',
             extra_context=None):
    """
    Allow a new user to register an account.
    
    Following successful registration, issue a redirect; by default,
    this will be whatever URL corresponds to the named URL pattern
    ``registration_complete``, which will be
    ``/accounts/register/complete/`` if using the included URLConf. To
    change this, point that named pattern at another URL, or pass your
    preferred URL as the keyword argument ``success_url``.
    
    By default, ``registration.forms.RegistrationForm`` will be used
    as the registration form; to change this, pass a different form
    class as the ``form_class`` keyword argument. The form class you
    specify must have a method ``save`` which will create and return
    the new ``User``, and that method must accept the keyword argument
    ``profile_callback`` (see below).
    
    To enable creation of a site-specific user profile object for the
    new user, pass a function which will create the profile object as
    the keyword argument ``profile_callback``. See
    ``RegistrationManager.create_inactive_user`` in the file
    ``models.py`` for details on how to write this function.
    
    By default, use the template
    ``registration/registration_form.html``; to change this, pass the
    name of a template as the keyword argument ``template_name``.
    
    **Required arguments**
    
    None.
    
    **Optional arguments**
    
    ``form_class``
        The form class to use for registration.
    
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.
    
    ``profile_callback``
        A function which will be used to create a site-specific
        profile instance for the new ``User``.
    
    ``success_url``
        The URL to redirect to on successful registration.
    
    ``template_name``
        A custom template to use.
    
    **Context:**
    
    ``form``
        The registration form.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    if request.method == 'POST':
        userip = request.META["REMOTE_ADDR"]
        r = OnelinerMuted.objects.filter(ip_ban=userip, muted_to__gt=datetime.datetime.now())
        if r:
            d = {
                "reason": r[0].reason,
                "time": r[0].muted_to,
            }
            return j2shim.r2r('webview/muted.html', {'muted' : d}, request)

        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)
