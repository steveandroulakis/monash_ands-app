import logging

logger = logging.getLogger(__name__)

class PartyActivityInformationProvider:

    def get_unique_party_id(self, username):
        """
        return the user dictionary in the format of::

        """
        raise NotImplemented()

    def get_party_rifcs(self, unique_party_id):
        """
        return the user dictionary in the format of::
        

        """
        
        raise NotImplemented()

    def get_display_name_for_party(self, unique_party_id):
        """
        return the user dictionary in the format of::


        """
        raise NotImplemented()

    def get_activity_summary_dict(self, username):
        """
        return the user dictionary in the format of::


        """
        raise NotImplemented()

    def get_activity_rifcs(self, activity_id):
        """
        return the user dictionary in the format of::


        """
        raise NotImplemented()
