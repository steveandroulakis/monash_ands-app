import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
from tardis.apps.monash_ands.PartyActivityInformationProvider \
    import PartyActivityInformationProvider
# from xml.dom.minidom import parseString
from suds.client import Client
import suds

logger = logging.getLogger(__name__)

class EIF038PartyActivityInformationProvider(PartyActivityInformationProvider):

    name = u'EIF038 Web Services'
    _client = None
    _namespace = 'rif'
    _uri = 'http://ands.org.au/standards/rif-cs/registryObjects'

    def __init__(self):

        # Basic info
#        url = "http://mobs-qa.its.monash.edu.au:7778/"\
#             "esb/wsil/AI/ResearchMaster/AIRMANDSService_RS?wsdl"

        #url = "http://mobs-dev.its.monash.edu.au:7778/esb/wsil"\
        #    "/AI/ResearchMaster/AIRMANDSService_RS?wsdl"

        url = "http://mobs.its.monash.edu.au:7778/orabpel/"\
              "ResearchMaster/AIRMANDSService/AIRMANDSService?wsdl"

        self._client = Client(url)

    def get_unique_party_id(self, username):
        """
        return the user dictionary in the format of::

        """
        response = self._client.service.getNlaId(username)

        return response.pnlaidOut.nlaId

    def get_party_rifcs(self, unique_party_id):
        """
        return the user dictionary in the format of::


        """
        self._client.service.getPartyregistryobject(unique_party_id)
        xmldata = self._client.last_received()
        #print xmldata

        regObj = xmldata.childAtPath('Envelope/Body/registryObjects')
        regObj.applyns((self._namespace, self._uri))
        regObj.walk(visitor)
        return regObj.str()

    def get_display_name_for_party(self, unique_party_id):
        """
        return the user dictionary in the format of::


        """
        self._client.service.getPartyregistryobject(unique_party_id)
        xmldata = self._client.last_received()
        #print xmldata

        regObj = xmldata.childAtPath('Envelope/Body/registryObjects/registryObject')

        from lxml import etree
        import StringIO
        
        rif_tree = etree.parse(StringIO.StringIO(regObj))
        title = rif_tree.xpath('//name/namePart[@type="title"]/text()')[0]
        given = rif_tree.xpath('//name/namePart[@type="given"]/text()')[0]
        family = rif_tree.xpath('//name/namePart[@type="family"]/text()')[0]
        
        return title + " " + given + " " + family

    def get_activity_summary_dict(self, username):
        """
        return the user dictionary in the format of::


        """
        try:
            projects = self._client.service.getProjects(username)
            return projects.pprojectsOut
        except suds.WebFault:
            return {}

    def get_activity_rifcs(self, activity_id):
        """
        return the user dictionary in the format of::


        """
        self._client.service.getActivityregistryobject(activity_id)
        xmldata = self._client.last_received()
        #print xmldata

        regObj = xmldata.childAtPath('Envelope/Body/registryObjects')
        regObj.applyns((self._namespace, self._uri))
        regObj.walk(visitor)
        return regObj.str()

def visitor(obj):
    obj.setPrefix('rif')
