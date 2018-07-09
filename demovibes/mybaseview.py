from baseview import BaseView as BV
import j2shim

class MyBaseView(BV):
    def render_template(self, template, context, request):
        return j2shim.r2r(template, context, request, mimetype=self.content_type)

    def deny_permission(self):
        return j2shim.r2r('base/error.html', { 'error' : "Sorry, you're not allowed to see this" }, request=self.request)
