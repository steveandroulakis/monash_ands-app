# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseServerError
#from django.template import Context

from tardis.tardis_portal.shortcuts import render_response_index
from MonashANDSService import MonashANDSService
from tardis.tardis_portal.models import Experiment, UserAuthentication
from tardis.apps.monash_ands.ldap_query import \
    LDAPUserQuery
from django.contrib.auth.decorators import login_required
from tardis.tardis_portal.creativecommonshandler import CreativeCommonsHandler
from tardis.tardis_portal.auth import decorators as authz
from django.conf import settings


def index(request, experiment_id):
    url = 'monash_ands/form.html'

#    try:
    e = Experiment.objects.get(id=experiment_id)

    import sys
    allowed_protocol = sys.modules['%s.%s.settings' %
                (settings.TARDIS_APP_ROOT, 'monash_ands')].ALLOWED_PROTOCOL

    if not request.user.is_authenticated():
        # todo: de-duplicate
        from django.template import Context
        c = Context()
        c['disallowed_protocol'] = True

        return HttpResponse(render_response_index(request, url, c))

    ua = UserAuthentication.objects.get(username=request.user.username)
    if not ua.authenticationMethod == allowed_protocol:
        from django.template import Context
        c = Context()
        c['is_owner'] = authz.has_experiment_ownership(request,
            experiment_id)
        c['disallowed_protocol'] = True

        return HttpResponse(render_response_index(request, url, c))

    if not request.POST:
        monashandsService = MonashANDSService(experiment_id)
        c = monashandsService.get_context(request)
        if request.user.is_authenticated():
            c['is_owner'] = authz.has_experiment_ownership(request,
                experiment_id)

        c['experiment'] = e

        cch = CreativeCommonsHandler(experiment_id=experiment_id, create=False)
        c['has_cc_license'] = cch.has_cc_license()

        return HttpResponse(render_response_index(request, url, c))
    else:
        monashandsService = MonashANDSService(experiment_id)
        c = monashandsService.register(request)
        if request.user.is_authenticated():
            c['is_owner'] = authz.has_experiment_ownership(request,
                experiment_id)

        c['experiment'] = e

        return HttpResponse(render_response_index(request, url, c))
#    except Exception, e:
#        # todo: check with web services for adequate responses..
#        message = '<b>An error occured:</b> ' + str(e)
#        return HttpResponse(content=message)

@login_required()
def retrieve_ldap_user_list(request):

    if 'q' in request.GET:
        if len(request.GET['q']) < 3:
            return HttpResponse('')
        else:
            query_input = request.GET['q']
            l = LDAPUserQuery()

            userlist = '\n'.join([LDAPUserQuery.get_user_attr(u, 'mail') for u in \
                l.get_users(query_input)])

        return HttpResponse(userlist)
    else:
        return HttpResponse('')
