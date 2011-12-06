'''
Monash ANDS Publish Provider (Research Master Interaction)

.. moduleauthor:: Steve Androulakis <steve.androulakis@monash.edu>
'''
from django.conf import settings
from django.template import Context
from tardis.tardis_portal.models import Experiment, ExperimentParameter, \
    ExperimentParameterSet
import urllib2
import datetime
from tardis.apps.monash_ands.partyactivityinformationservice \
    import PartyActivityInformationService
from tardis.tardis_portal.xmlwriter \
    import XMLWriter
from tardis.tardis_portal.ParameterSetManager import ParameterSetManager
import os
from tardis.apps.monash_ands.ldap_query import \
    LDAPUserQuery
import suds
from django.contrib.sites.models import Site
from tardis.tardis_portal.creativecommonshandler import CreativeCommonsHandler
# import the logging library
import logging

# Get an instance of a logger
from tardis.apps.monash_ands.DOIService import DOIService

logger = logging.getLogger(__name__)


class MonashANDSService():

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    name = u'Monash ANDS Publish'

    def register(self, request):
        """
        Use the EIF038 web services to gather and store party/activity
        ids for the linkages required by ANDS Research Data Australia.

        :param request: a HTTP Request instance
        :type request: :class:`django.http.HttpRequest`

        """
        username = request.user.username
        pais = PartyActivityInformationService()
        pai = pais.get_pai()

        monash_id_list = []

        experiment = Experiment.objects.get(id=self.experiment_id)

        self.clear_existing_parameters(request)

        if not('ldap_existing_party' in request.POST or\
            'ldap_party' in request.POST):
            return {'status': False,
            'message': 'Error: Must have at least' +
            ' one Monash party nominated'}

        if 'ldap_existing_party' in request.POST:
            for email in request.POST.getlist('ldap_existing_party'):
                relation_name = 'exists-' + email + '-relation'
                if relation_name in request.POST:
                    monash_id_list.append(\
                        {'party_param': email,
                        'relation_param': request.POST[relation_name]})

                # write new party info for existing party
                if settings.OAI_DOCS_PATH:
                    party_rif_cs = pai.get_party_rifcs(email)

                    XMLWriter.write_xml_to_file(
                        '',
                        'party',
                        email.replace('MON:',''),
                        party_rif_cs
                        )

        message = ""
        if 'ldap_party' in request.POST:
            fail = False

            for email in request.POST.getlist('ldap_party'):
                if str(email):

                    monash_id = ""
                    try:

                        l = LDAPUserQuery()

                        authcate = []
                        authcate.append([LDAPUserQuery.get_user_attr(u, 'uid')\
                            for u in \
                            l.get_authcate_exact(email)])

                        monash_id = pai.get_unique_party_id(authcate[0][0])
                        relation_name = 'new-' + email + '-relation'
                        if relation_name in request.POST:
                            monash_id_list.append(\
                                {'party_param': monash_id,
                                'relation_param': request.POST[relation_name]})

                    except urllib2.URLError:
                        fail = True
                        logger.error("Can't contact research" +
                            " master web service")

                        message = message + \
                        'Error: Cannot contact Activity' + \
                        ' / Party Service. Please try again later.' \
                        + "<br/>"
                    except IndexError:
                        logger.error("Can't contact ldap for " +
                            email)
                        fail = True
                        error = "Can't get authcate for email address: " + email\
                        + "<br/>"

                        message = message + "<br/>" + error
                    except KeyError:
                        logger.error("Couldn't find authcate for " +
                            email)
                        fail = True
                        error = "Can't get authcate for email address: " + email\
                        + "<br/>"

                        message = message + "<br/>" + error

            if fail:
                return {'status': False,
                'message': message}

        for monash_id in monash_id_list:

            self.save_party_parameter(experiment,
                monash_id['party_param'], monash_id['relation_param'])

            if settings.OAI_DOCS_PATH:
                party_rif_cs = pai.get_party_rifcs(monash_id['party_param'])

                XMLWriter.write_xml_to_file(
                    '',
                    'party',
                    monash_id['party_param'].replace('MON:',''),
                    party_rif_cs
                    )

        for activity_id in request.POST.getlist('activity'):

            if activity_id in self.get_existing_activity_keys():
                pass
            else:
                self.save_activity_parameter(experiment, activity_id)

                if settings.OAI_DOCS_PATH:
                    activity_rif_cs = pai.get_activity_rifcs(activity_id)

                    XMLWriter.write_xml_to_file(
                        '',
                        'activity',
                        activity_id.replace('MON:',''),
                        activity_rif_cs
                        )

        cch = CreativeCommonsHandler(experiment_id=experiment.id, create=False)

        license_name = ""
        if cch.has_cc_license():
            psm = cch.get_or_create_cc_parameterset()

            license_name = ""
            try:
                license_name = psm.get_param('license_name', True)
            except ExperimentParameter.DoesNotExist:
                pass

        c = Context(dict({
                    'now': datetime.datetime.now(),
                    'experiment': experiment,
                    'party_keys': monash_id_list,
                    'activity_keys': request.POST.getlist('activity'),
                    'site_domain': Site.objects.get_current().domain,
                    'license_name': license_name,
                    }))

        custom_description = None
        if 'custom_description' in request.POST:
            custom_description = request.POST['custom_description']

            if custom_description:
                schema = 'http://localhost/pilot/collection/1.0/'

                psm = \
                    self.get_or_create_parameterset(schema)

                psm.set_param("custom_description", custom_description,
                    "Custom Description For ANDS Research Data Australia")

        c['custom_description'] = custom_description

        selected_profile = self.get_profile()
        if not selected_profile:
            selected_profile = "default.xml"

        profile_template = "monash_ands/profiles/" + selected_profile

        import sys
        mas_settings = sys.modules['%s.%s.settings' %
                    (settings.TARDIS_APP_ROOT, 'monash_ands')]

        if mas_settings.DOI_ENABLE:
            if 'mint_doi' in request.POST:
                doisrv = DOIService(experiment)
                try:
                    site_url = Site.objects.get_current().domain
                    exp_url = experiment.get_absolute_url()
                    print site_url + exp_url
                    doi = doisrv.mint(site_url + exp_url)
                    self.save_doi(doi)
                except urllib2.HTTPError, e:
                    logger.error("doi minting failed")
                    logger.debug(e.read())

        if mas_settings.HANDLE_ENABLE:
            if not experiment.handle:
                try:
                    from HandleService import HandleService

                    hdlsrv = HandleService()

                    response = hdlsrv.mint(
                        mas_settings.AUTHTYPE, mas_settings.IDENTIFIER,
                        mas_settings.AUTHDOMAIN, mas_settings.APPID,
                        mas_settings.MINTURL, \
                            Site.objects.get_current().domain +\
                            "/experiment/view/" + str(experiment.id))
                    from xml.dom import minidom
                    xmldoc = minidom.parseString(response)

                    handle = xmldoc.firstChild.childNodes[1].attributes["handle"].value

                    if handle:
                        experiment.handle = handle
                        experiment.save()

                except KeyError:
                    logger.error(response)
                    logger.error("Persistent handle minting failed")

        if settings.OAI_DOCS_PATH:
            XMLWriter.write_template_to_file(
                '',
                'collection',
                experiment.id,
                profile_template,
                c,
                )

        if request.POST['profile']:

            profile = request.POST['profile']
            self.save_rif_cs_profile(experiment, profile)

        else:
            return {'status': True,
            'message': 'No profiles exist to choose from'}

        schema = "http://localhost/pilot/registration_record/1.0/"

        psm = ParameterSetManager(schema=schema,
                parentObject=experiment)

        now = datetime.datetime.now().strftime("%d %B %Y %I:%M%p")
        psm.set_param("registration_date", now,
            "Registration Date")
        psm.set_param("registered_by", request.user.username,
            "Registered By")

        return {'status': True, 'message': 'Successfully registered experiment.'}

    def get_context(self, request):
        """
        Use the logged in username to get a list of activity summaries from
        Research Master and display them on screen for selection.

        :param request: a HTTP Request instance
        :type request: :class:`django.http.HttpRequest`

        """
        username = request.user.username
        usermail = request.user.email
        pais = PartyActivityInformationService()
        pai = pais.get_pai()
        # already has entries

        import sys
        mas_settings = sys.modules['%s.%s.settings' %
                    (settings.TARDIS_APP_ROOT, 'monash_ands')]

        schema = 'http://localhost/pilot/collection/1.0/'

        psm = \
            self.get_or_create_parameterset(schema)

        custom_description = ""

        try:
            custom_description = psm.get_param("custom_description",
                True)
        except ExperimentParameter.DoesNotExist:
            pass

        monash_id = ""
        try:
            monash_id = pai.get_unique_party_id(username)
        except urllib2.URLError:
            logger.error("Can't contact research master web service")
            return {'message':
            'Error: Failed to contact Research Master web service ' +
            'to retrieve Party / Activity information. Please contact ' +
            'a system administrator.'}
        except suds.WebFault:
            logger.error("Can't get valid authcate " + username)
            return {'message':
            'Can\'t get a valid authcate name for ' + username}

        activity_summaries = {}
        try:
            activity_summaries = pai.get_activity_summary_dict(monash_id)
        except urllib2.URLError:
            logger.error("Can't contact research master web service")
            return {'message':
            'Error: Failed to contact Research Master web service ' +
            'to retrieve Party / Activity information. Please contact ' +
            'a system administrator.'}

        rif_cs_profiles = self.get_rif_cs_profile_list()

        selected_profile = "default.xml"

        if self.get_profile():
            selected_profile = self.get_profile()

        registered = False
        if self.has_registration_record():
            registered = True

        doi_enabled = False
        if mas_settings.DOI_ENABLE:
            doi_enabled = True

        return {"activity_summaries":
                    activity_summaries,
                "current_activities":
                    self.get_existing_activity_keys(),
                "current_parties_ldap":
                    self.get_existing_ldap_party_info(),
                "custom_description":
                    custom_description,
                "rif_cs_profiles":
                    rif_cs_profiles,
                "selected_profile":
                    selected_profile,
                "registered":
                    registered,
                "usermail":
                    usermail,
                "has_doi":
                    self.has_doi(),
                "doi_enabled": doi_enabled,
                }

    def save_party_parameter(self, experiment, party_param, relation_param):
        """
        Save Research Master's returned Party ID as an experiment parameter
        """
        namespace = "http://localhost/pilot/party/1.0/"

        parameter_name = 'party_id'
        parameter_fullname = 'Party ID'

        relation_name = 'relationToCollection'
        relation_fullname = 'Relation to Collection'

        psm = \
            self.get_or_create_unique_parameterset(namespace,\
                parameter_name, party_param)

        eid = psm.set_param(parameter_name, party_param, parameter_fullname)
        psm.set_param(relation_name, relation_param, relation_fullname)

        return eid

    def save_activity_parameter(self, experiment, activity_id):
        """
        Save Research Master's returned Activity ID as an experiment parameter
        """
        namespace = "http://localhost/pilot/activity/1.0/"
        schema = None

        psm = \
            self.get_or_create_parameterset(namespace)

        eid = psm.new_param("activity_id", activity_id, "Activity ID")

        return eid

    def clear_existing_parameters(self, request):
        """
        Clear existing party/activity keys
        """
        for e_param in self.get_existing_ldap_party_keys():
            if  not e_param.string_value in\
                request.POST.getlist('ldap_existing_party'):

                e_param.delete()

        namespace = "http://localhost/pilot/activity/1.0/"

        psm = \
            self.get_or_create_parameterset(namespace)

        psm.delete_params('activity_id')

    def get_existing_ldap_party_info(self):
        pais = PartyActivityInformationService()
        pai = pais.get_pai()

        eps = ExperimentParameter.objects.filter(name__name='party_id',
        parameterset__schema__namespace='http://localhost/pilot/party/1.0/',
        parameterset__experiment__id=self.experiment_id)

        party_info = []

        for ep in eps:
            psm = ParameterSetManager(parameterset=ep.parameterset)
            display_name = pai.get_display_name_for_party(ep.string_value)
            info = {}
            info['party_id'] = ep.string_value
            info['party_fullname'] = display_name
            info['relation'] = psm.get_param('relationToCollection', True)

            party_info.append(info)

        return party_info

    def get_existing_ldap_party_keys(self):

        eps = ExperimentParameter.objects.filter(name__name='party_id',
        parameterset__schema__namespace='http://localhost/pilot/party/1.0/',
        parameterset__experiment__id=self.experiment_id)

        party_keys = []
        for ep in eps:
            party_keys.append(ep)

        return party_keys

    def get_existing_activity_keys(self):
        eps = ExperimentParameter.objects.filter(name__name='activity_id',
        parameterset__schema__namespace='http://localhost/pilot/activity/1.0/',
        parameterset__experiment__id=self.experiment_id)

        return eps

    def get_rif_cs_profile_list(self):
        """
        Return a list of the possible RIF-CS profiles that can
        be applied. Scans the profile directory.

        :rtype: list of strings
        """

        # TODO this is not a scalable or pluggable way of listing
        #  or defining RIF-CS profiles. The current method REQUIRES
        #  branching of the templates directory. instead of using the
        #  built in template resolution tools.
        TARDIS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        profile_dir = os.path.join(TARDIS_ROOT,
                      "templates/monash_ands/profiles/")

        profile_list = list()

        try:
            for f in os.listdir(profile_dir):
                if not os.path.isfile(profile_dir + f) or \
                       f.startswith('.') or not f.endswith('.xml'):
                    continue
                profile_list.append(f)
        except OSError:
            logger.error("Can't find profile directory " +
            "or no profiles available")

        return profile_list

    def save_rif_cs_profile(self, experiment, profile):
        """
        Save selected profile choice as experiment parameter
        """
        namespace = "http://monash.edu.au/rif-cs/profile/"

        psm = self.get_or_create_parameterset(namespace)
        psm.delete_params("profile")
        psm.set_param("profile", profile,
            "ANDS RIFCS Profile")

    def save_doi(self, doi):
        """
        Save selected profile choice as experiment parameter
        """
        namespace = "http://localhost/pilot/doi/1.0"

        psm = self.get_or_create_parameterset(namespace)
        psm.delete_params("doi")
        psm.set_param("doi", doi,
            "Digital Object Identifier")

    def get_profile(self):
        """
        Retrieve existing rif-cs profile for experiment, if any
        """
        namespace = 'http://monash.edu.au/rif-cs/profile/'

        psm = self.get_or_create_parameterset(namespace)

        try:
            return psm.get_param('profile', value=True)
        except ExperimentParameter.DoesNotExist:
            return None

    def has_registration_record(self):
        """
        Retrieve existing rif-cs profile for experiment, if any
        """
        namespace = 'http://localhost/pilot/registration_record/1.0/'

        parametersets = ExperimentParameterSet.objects.filter(
            schema__namespace=namespace,
            experiment__id=self.experiment_id)

        if len(parametersets):
            return True
        else:
            return False

    def has_doi(self):
        """
        Retrieve existing rif-cs profile for experiment, if any
        """
        namespace = "http://localhost/pilot/doi/1.0"

        parametersets = ExperimentParameterSet.objects.filter(
            schema__namespace=namespace,
            experiment__id=self.experiment_id)

        if len(parametersets):
            return True
        else:
            return False

    def get_or_create_parameterset(self, schema):
        parameterset = ExperimentParameterSet.objects.filter(
        schema__namespace=schema,
        experiment__id=self.experiment_id)

        experiment = Experiment.objects.get(id=self.experiment_id)

        psm = None
        if not len(parameterset):
            psm = ParameterSetManager(schema=schema,
                    parentObject=experiment)
        else:
            psm = ParameterSetManager(parameterset=parameterset[0])

        return psm

    def get_or_create_unique_parameterset(self, schema, parametername, value):
        parameterset = ExperimentParameterSet.objects.filter(
        schema__namespace=schema,
        experiment__id=self.experiment_id)

        experiment = Experiment.objects.get(id=self.experiment_id)

        psm = None

        if not len(parameterset):
            psm = ParameterSetManager(schema=schema,
                    parentObject=experiment)
            return psm
        else:
            for ps in parameterset:
                psm = ParameterSetManager(parameterset=ps)
                try:
                    ps_value = psm.get_param("party_id",
                        True)
                    if value == ps_value:
                        return psm
                except ExperimentParameter.DoesNotExist:
                    pass # keep going

        psm = ParameterSetManager(schema=schema,
                parentObject=experiment)

        return psm
