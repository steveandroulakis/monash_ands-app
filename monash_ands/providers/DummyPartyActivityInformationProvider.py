import logging
from django.conf import settings
import urllib2
from tardis.apps.monash_ands.PartyActivityInformationProvider \
    import PartyActivityInformationProvider
from xml.dom.minidom import parseString

logger = logging.getLogger(__name__)

class DummyPartyActivityInformationProvider(PartyActivityInformationProvider):

    name = u'Dummy EIF038 Web Services'

    def get_unique_party_id(self, username):
        """
        return the user dictionary in the format of::

        """

        return str(username[:3]) + str(45)

    def get_party_rifcs(self, unique_party_id):
        """
        return the user dictionary in the format of::


        """
        party_xml = '<registryObject group="Monash University">'\
                    '<key>dummyxml</key></registryObject>'

        return party_xml

    def get_display_name_for_party(self, unique_party_id):
        """
        return the user dictionary in the format of::


        """

        return "Professor Foo Bar"

    def get_activity_summary_dict(self, username):

        activities = []

        activity = {}
        activity2 = {}

        activity['projectId'] = "activity-1"

        activity['projectTitle'] = "Control of proteases in infectious,"\
        "degenerative and cardiovascular disease"

        activity['grantorCode'] = "1263"

        activity['projectDateApplied'] = "1/1/1970"

        activities.append(activity)

        activity2['projectId'] = "activity-2"

        activity2['projectTitle'] = "Genetic and Bioinformatic analysis of"\
        " complex human diseases"

        activity2['grantorCode'] = "2724"

        activity2['projectDateApplied'] = "2/1/1970"

        activities.append(activity2)

        return activities


    def get_activity_rifcs(self, activity_id):
        """
        return the user dictionary in the format of::


        """
        activity_xml = '<registryObject group="Monash University">'\
                    '<key>dummyxml</key></registryObject>'

        return activity_xml