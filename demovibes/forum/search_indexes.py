from haystack.indexes import *
from haystack import site
import forum.models as M

class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    render = CharField(indexed=False, use_template=True)

    def get_queryset(self):
        return M.Post.objects.filter(thread__forum__is_private=False)

    def get_updated_field(self):
        return "edited"

site.register(M.Post, PostIndex)
