import sys
from urllib2 import HTTPError
import urllib2
import logging
from django.conf import settings
from django.template.loader import render_to_string

"""
DOI Service

Mints DOIs using ANDS' Cite My Data service.
POSTs DataCite XML to a web services endpoint.

.. moduleauthor:: Steve Androulakis <steve.androulakis@monash.edu>

"""

logger = logging.getLogger(__name__)

class DOIService():

    def __init__(self, experiment):
        """
        :param experiment: The experiment model object
        :type experiment: :class:`tardis.tardis_portal.models.Experiment`
        """

        logger.debug("initialize ...")
        self.experiment = experiment

        # get settings specific to Monash ANDS app
        self.mas_settings = sys.modules['%s.%s.settings' %
                    (settings.TARDIS_APP_ROOT, 'monash_ands')]

    def mint(self, hdlURL):
        """
        POSTs DataCite XML to the DOI minting URL specified in settings
        :param hldURL: The URL the DOI will resolve to
        :type hdlURL: string
        :return: The DOI string
        :rtype: string
        """
        doi_request_xml = self.__render_datacite_xml()
        mint_url = self.mas_settings.DOI_MINTURL + "?app_id=" + \
            self.mas_settings.DOI_APP_ID + \
            "&url=" + hdlURL

        try:
            doi = self.__request(doi_request_xml, mint_url)
        except HTTPError, e:
            raise e

        # Successfully minted 10.5072/03/4EA4F0D91D383
        return self.mas_settings.DOI_ACCESS_URL + doi.split()[2]

    def __request(self, doi_request_xml, mint_url):
        """
        Private method to POST data to endpoint
        """
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
            }

        xml_POST = "xml=" + doi_request_xml

        req = urllib2.Request(mint_url, xml_POST, headers)

        response = urllib2.urlopen(req)

        logger.debug('Handle response ' + str(response))

        data = response.read()

        return data

    def __render_datacite_xml(self):
        """
        Private method that passes a context dictionary to a datacite
        template and renders it as a string
        """
        from django.template import Context

        c = Context(dict({
            'experiment': self.experiment,
            'authors': self.experiment.author_experiment_set.all(),
            }))

        doi_request_xml = render_to_string(
            self.mas_settings.DOI_DATACITE_TEMPLATE_PATH,
            context_instance=c)

        return doi_request_xml
