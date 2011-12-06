'''
Created on 20/01/2010

@author: Simon
'''
#import sys
from urllib2 import HTTPError, URLError
import urllib2
import logging

logger = logging.getLogger(__name__)

class HandleService:

    def _init_(self):
        logger.debug("initialize ...")

    def mint(self, authType, identifier, authDomain, appId,mintURL, hdlURL):
        #construct an user authentication info
        body = "<request name=\"addValue\">\n\
             <properties>\n\
             <property name=\"authType\" value=\"" + authType + "\"/>\n\
             <property name=\"identifier\" value=\"" + identifier + "\"/>\n\
             <property name=\"authDomain\" value=\"" + authDomain + "\"/>\n\
             <property name=\"appId\" value=\"" + appId + "\"/>\n\
             </properties>\n\
             </request>"

        #Parameters for Handle Service
        #params = [('type',"URL"), ('value', hdlURL)]

        #Handle Server Connection URL
        #postString = mintURL + "?" + urllib.urlencode(params)
        postString = mintURL + hdlURL

        #send the request to handle service
        return self.request(postString, body)

    def request(self, postString, body):

	logger.debug('Requesting handle')
        logger.debug(postString)
        logger.debug(body)

        #connect to Handle Service
        req = urllib2.Request(postString, body)
        #open the connection
        
        response = None   

        #try:
        response = urllib2.urlopen(req)
        #except HTTPError, e:
        #    logger.error('The handle server could not fulfill the request.')
        #    logger.debug('Exception: ', e.code)
        #except URLError, e:
        #    logger.error('Failed to reach the handle server.')
        #    logger.debug('Reason: ', e.reason)
        
        logger.debug('Handle response ' + str(response))

        data = response.read()
            #read the response
            #result = ''
            #while 1:
            #    data = response.read(1024)
            #    if not len(data):
            #        break
            #        result = result + repr(data)
            #        sys.stdout.write(data)
        return data
