"""
All forum logic is kept here - displaying lists of forums, threads
and posts, adding new threads, and adding replies.
"""
from django.utils.html import escape
from forum.models import Forum,Thread,Post,Subscription
from forum.forms import ThreadForm, ReplyForm, EditForm
from datetime import datetime
from webview import models as wm
from webview.views import check_muted
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden
from django.template import Context, loader
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.defaultfilters import striptags, wordwrap
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, InvalidPage
import j2shim

NOTIFY_POST = getattr(settings, "NOTIFY_NEW_FORUM_POST", False)
NOTIFY_THREAD = getattr(settings, "NOTIFY_NEW_FORUM_THREAD", False)
TRUNCATED_THREAD_SIZE = getattr(settings, "TRUNCATED_THREAD_STRING_SIZE", 256)
NUM_LAST_FORUM_POSTS = getattr(settings, "NUM_DISPLAY_LAST_FORUM_POSTS", 5)

def forum_email_notification(post):
    try:
        mail_subject = settings.FORUM_MAIL_PREFIX
    except AttributeError:
        me = Site.objects.get_current()
        mail_subject = "[%s Forums]" % me.name
    try:
        mail_from = settings.FORUM_MAIL_FROM
    except AttributeError:
        mail_from = settings.DEFAULT_FROM_EMAIL
    mail_tpl = loader.get_template('forum/notify.txt')
    c = Context({
        'body': wordwrap(striptags(post.body), 72),
        'site' : Site.objects.get_current(),
        'thread': post.thread,
        'author' : post.author,
        'subject' : post.thread.title,
        })
    email = EmailMessage(
            subject=mail_subject+' '+striptags(post.thread.title),
            body=mail_tpl.render(c),
            from_email=mail_from,
            to=[mail_from],
            bcc=[s.author.email for s in post.thread.subscription_set.all()])
    email.send(fail_silently=True)

def edit(request, post_id):
    P = get_object_or_404(Post, id=post_id)
    t = P.thread
    if request.user != P.author:
        return HttpResponseRedirect(t.get_absolute_url())
    if request.method == 'POST':
        edit_form = EditForm(request.POST, instance=P)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(t.get_absolute_url())
    else:
        edit_form = EditForm(instance=P)
    return j2shim.r2r('forum/post_edit.html',{'edit_form' : edit_form, 'thread': t, 'forum': t.forum}, request)

def forum(request, slug):
    """
    Displays a list of threads within a forum.
    Threads are sorted by their sticky flag, followed by their
    most recent post.
    """
    f = get_object_or_404(Forum, slug=slug)

    # If the user is not authorized to view the thread, then redirect
    if f.is_private and request.user.is_staff != True:
         return HttpResponseRedirect('/forum')

    # Process new thread form if data was sent
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseServerError()
        thread_form = ThreadForm(request.POST)
        
        r = check_muted(request)
        if r: return r

        if thread_form.is_valid():
            new_thread = thread_form.save(commit = False)
            new_thread.forum = f
            new_thread.save()
            if NOTIFY_THREAD and not f.is_private:
                wm.send_notification("%s created a new thread \"<a href='%s'>%s</a>\" in forum \"%s\"" % (
                    escape(request.user.username),
                    new_thread.get_absolute_url(),
                    escape(new_thread.title),
                    escape(new_thread.forum.title),
                ), None, 1)
            Post.objects.create(thread=new_thread, author=request.user,
                body=thread_form.cleaned_data['body'],
                time=datetime.now())
            if (thread_form.cleaned_data['subscribe'] == True):
                Subscription.objects.create(author=request.user,
                    thread=new_thread)
            return HttpResponseRedirect(new_thread.get_absolute_url())
    else:
        thread_form = ThreadForm()

    # Pagination
    t = f.thread_set.all()
    paginator = Paginator(t, settings.FORUM_PAGINATE)
    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1
    try:
        threads = paginator.page(page)
    except (EmptyPage, InvalidPage):
        threads = paginator.page(paginator.num_pages)

    return j2shim.r2r('forum/thread_list.html',
        {
            'forum': f,
            'threads': threads.object_list,
            'page_range': paginator.page_range,
            'page': page,
            'thread_form': thread_form
        }, request)

def forum_list(request):
    """
    Modified to show Forum lists, but also the most recent posts from any
    Forums. Secret forums are hidden from public view.
    """
    forums = Forum.objects.filter(parent__isnull=True)
    
    # Add a filter is the user isn't staff (users normally can't see 'Secret' forums)
    if request.user.is_staff:
        posts = Post.objects.all().order_by('-time')[:NUM_LAST_FORUM_POSTS]
    else:
        posts = Post.objects.filter(thread__forum__is_private=False).order_by('-time')[:NUM_LAST_FORUM_POSTS]

    return j2shim.r2r('forum/forum_list.html',
        {
            'object_list': forums,
            'posts': posts,
            'preview_size': TRUNCATED_THREAD_SIZE,
        }, request)

def thread(request, thread):
    """
    Increments the viewed count on a thread then displays the
    posts for that thread, in chronological order.
    """
    t = get_object_or_404(Thread, pk=thread)
    p = t.post_set.all().order_by('time')
    if request.user.is_authenticated():
        s = t.subscription_set.filter(author=request.user)
    else:
        s = False

    # If the user is not authorized to view, we redirect them
    if t.forum.is_private and request.user.is_staff != True:
         return HttpResponseRedirect('/forum')

    # Process reply form if it was sent
    if (request.method == 'POST'):
        if not request.user.is_authenticated() or t.closed:
            return HttpResponseServerError()
            
        r = check_muted(request)
        if r: return r

        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            new_post = reply_form.save(commit = False)
            new_post.author = request.user
            new_post.thread = t
            new_post.time=datetime.now()
            new_post.save()
            # Change subscription
            if reply_form.cleaned_data['subscribe']:
                Subscription.objects.get_or_create(thread=t,
                    author=request.user)
            else:
                Subscription.objects.filter(thread=t, author=request.user).delete()
            # Send email
            forum_email_notification(new_post)
            if NOTIFY_POST and not t.forum.is_private:
                wm.send_notification("%s posted a reply to \"<a href='%s#post%s'>%s</a>\" in forum \"%s\"" % (
                    escape(request.user.username),
                    new_post.thread.get_absolute_url(),
                    new_post.id,
                    escape(new_post.thread.title),
                    escape(new_post.thread.forum.title),
                ), None, 1)
            return HttpResponseRedirect(new_post.get_absolute_url())
    else:
        reply_form = ReplyForm(initial={'subscribe': s})

    # Pagination
    paginator = Paginator(p, settings.FORUM_PAGINATE)
    try:
        page = int(request.GET.get('page', paginator.num_pages))
    except:
        page = paginator.num_pages

    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)

    t.views += 1
    t.save()
    #{'object_list' : artistic.object_list, 'page_range' : paginator.page_range, 'page' : page, 'letter' : letter, 'al': alphalist}, \
    return j2shim.r2r('forum/thread.html',
            {
            'forum': t.forum,
            'thread': t,
            'posts': posts.object_list,
            'page_range': paginator.page_range,
            'page': page,
            'reply_form': reply_form
        }, request)

def updatesubs(request):
    """
    Allow users to update their subscriptions all in one shot.
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden(_('Sorry, you need to login.'))

    subs = Subscription.objects.filter(author=request.user)

    if request.POST:
        # remove the subscriptions that haven't been checked.
        post_keys = [k for k in request.POST.keys()]
        for s in subs:
            if not str(s.thread.id) in post_keys:
                s.delete()
        return HttpResponseRedirect(reverse('forum_subscriptions'))

    return j2shim.r2r('forum/updatesubs.html',
        {
            'subs': subs,
        }, request)

