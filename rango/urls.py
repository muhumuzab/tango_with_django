from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from rango.views import index,about,category,add_category,add_page,register,user_login,restricted,user_logout,search,profile,searchh,track_url,like_category,suggest_category,get_cat,user_lookup

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^about/', about),
    url(r'^add_category/$', add_category),
    url(r'^register/$', register),
    url(r'^login/$', user_login),
    url(r'^category/(?P<category_name_url>\w+)/add_page/$', add_page),
    url(r'^category/(?P<category_name_url>\w+)/$', category),
    url(r'^restricted/$', restricted),
    url(r'^user_logout/$', user_logout),
    url(r'^search/$', search),
    url(r'^searchh/$', searchh),
    url(r'^profile/$', profile),
    url(r'^goto/$',track_url),
    url(r'^like_category/$', like_category),
    url(r'^suggest_category/$',suggest_category),
    #url(r'^CategoryAutocomplete/$',CategoryAutocomplete.as_view())
    url(r'^get_cat/$',get_cat),
    url(r'^lookup/$',user_lookup)




   
                       
    
    
    
)
