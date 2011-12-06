from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'tardis.apps.monash_ands.views',
    (r'^(?P<experiment_id>\d+)/$', 'index'),
    (r'^ajax/ldap_list/$', 'retrieve_ldap_user_list'),
    )
