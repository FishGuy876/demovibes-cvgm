from django.contrib import admin
from forum.models import Forum, Thread, Post, Subscription

class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', '_parents_repr')
    ordering = ['parent', 'title']

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['author','thread']

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'thread']

class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'forum', 'sticky', 'closed']
    search_fields = ['title']

admin.site.register(Forum, ForumAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
