from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # App URLS
    url(r'^$', RedirectView.as_view(url='home/'), name='reverse'),  # redirected to home
    url(r'^home/', include('base.urls', namespace="base")),  # note the lack of a terminal dollar sign.
    url(r'^meetings/', include('meetings.urls', namespace="meetings")),  # note the lack of a terminal dollar sign.

    # Admin URLS
    url(r'^admin/', include(admin.site.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),  # Rich text widget
    url(r'^captcha/', include('captcha.urls')),  # captcha form challenge

    # Django Fiber URLS
    (r'^api/v2/', include('fiber.rest_api.urls')),
    (r'^admin/fiber/', include('fiber.admin_urls')),   # Does this need to be placed above the admin entry?
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',), }),
    (r'', 'fiber.views.page'),  # This catches everything not matched above!


)

"""
The following code insures users uploaded media are served with the development
server. It will NOT work when settings.DEBUG = False.
Details available from the Django 1.6 documentation:
https://docs.djangoproject.com/en/1.6/howto/static-files/

IMPORTANT: One key difference between the paleocore implementation and the documentation
is that the MEDIA_URL settings are added to the beginning of the url patterns. If appened
to the end as shown in the documentation the fiber.view.page entry catches and returns 404.
"""
urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
