from django.core.files.storage import get_storage_class
from django.utils.translation import gettext_lazy as _
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from cmsplugin_contact_plus.admin import ExtraFieldInline
from cmsplugin_contact_plus.models import ContactPlus
from cmsplugin_contact_plus.forms import ContactFormPlus


import time


class CMSContactPlusPlugin(CMSPluginBase):
    """
    """
    model = ContactPlus
    inlines = [ExtraFieldInline, ]
    name = _('Contact Form')
    render_template = "cmsplugin_contact_plus/contact.html"
    change_form_template = 'cmsplugin_contact_plus/change_form.html'
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']

        if instance and instance.template:
            self.render_template = instance.template

        if request.method == "POST" and "contact_plus_form_" + str(instance.id) in request.POST.keys():
            form = ContactFormPlus(contactFormInstance=instance,
                    request=request,
                    data=request.POST,
                    files=request.FILES)
            if form.is_valid():
                ts = str(int(time.time()))

                for fl in request.FILES:
                    storage = get_storage_class()()
                    for f in request.FILES.getlist(fl):
                        storage.save(ts + '-' + f.name, f)

                form.send(instance.recipient_email, request, ts, instance, form.is_multipart)
                context.update({
                    'contact': instance,
                })
                return context
            else:
                context.update({
                    'contact': instance,
                    'form': form,
                })

        else:
            form = ContactFormPlus(contactFormInstance=instance, request=request)
            context.update({
                    'contact': instance,
                    'form': form,
            })
        return context


plugin_pool.register_plugin(CMSContactPlusPlugin)
