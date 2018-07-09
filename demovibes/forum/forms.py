from django.forms import ModelForm, CharField, BooleanField, Textarea
from models import Post, Thread

class ThreadForm(ModelForm):
    class Meta:
        model = Thread
        fields = ['title']
    title = CharField(required = True, label = 'Subject')
    body = CharField(required = True, label = 'Message',
        widget = Textarea(attrs = {'rows': '12', 'cols': '80',
            'class': 'input'}))
    subscribe = BooleanField(required = False,
        label='Receive updates via email')


class ReplyForm(ModelForm):
    class Meta:
        model = Post
        fields = ['body']
    body = CharField(required = True, label = 'Your Message',
        widget = Textarea(attrs = {'rows': '12', 'cols': '80',
            'class': 'input'}))
    subscribe = BooleanField(required = False,
        label='Receive updates via email')

class EditForm(ModelForm):
    class Meta:
        model = Post
        fields = ['body']
    body = CharField(required = True, label = 'Your Message',
    widget = Textarea(attrs = {'rows': '20', 'cols': '60',
        'class': 'input'}))

