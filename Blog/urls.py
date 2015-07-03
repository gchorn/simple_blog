from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$','blogs.views.homepage'),
    url(r'^older/(?P<end>\d+)-(?P<next_set>\d+)/$','blogs.views.older'),
    url(r'^about/$','blogs.views.about'),
    url(r'^archives/(?P<arcyear>\d{4})/(?P<arcmonth>\d{1,2})/$','blogs.views.archive'),
    url(r'^categories/(?P<category>\w+|\w+-\w+|\w+(?:\s\w+)+)/$','blogs.views.category'),
    url(r'^tags/(?P<tag>\w+|\w+-\w+|\w+(?:\s\w+)+)/$','blogs.views.tags'),
    url(r'^searchresults/$','blogs.views.search'),
    url(r'^posts/(?P<post_id>\d+)[a-z,-]+/$','blogs.views.postdetail'),
    url(r'^comments/',include('django.contrib.comments.urls')),
    url(r'^thankyou/(?P<post_id>\d+)/$','blogs.views.posted'),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',          
        {'document_root':settings.MEDIA_ROOT}),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
                       
)
