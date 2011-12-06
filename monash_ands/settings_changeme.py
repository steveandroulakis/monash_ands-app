# -*- coding: utf-8 -*-
#
# Copyright (c) 2010, Monash e-Research Centre
#   (Monash University, Australia)
# Copyright (c) 2010, VeRSI Consortium
#   (Victorian eResearch Strategic Initiative, Australia)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    *  Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    *  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    *  Neither the name of the VeRSI, the VeRSI Consortium members, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

NAME = "ANDS Register"

# Only this protocol is allowed to
ALLOWED_PROTOCOL = "ldap"

#handle.net settings
# if this is false then the other settings don't matter and handles won't be minted
# NOTE: for handles to work, site domain needs to be configured in django /admin
HANDLE_ENABLE = False
AUTHTYPE = "SSLHost"
AUTHDOMAIN = "monash.edu.au"
IDENTIFIER = "Monash MeRC"
APPID = "x" # assigned by ANDS
MINTURL = "https://test.ands.org.au:8443/pids/mint?type=URL&value="
SSL = True
HANDLEURL = "http://hdl.handle.net"
PARTY_ACTIVITY_INFORMATION_PROVIDER = "tardis.apps.monash_ands.providers.DummyPartyActivityInformationProvider.DummyPartyActivityInformationProvider"

# DOI Settings
DOI_ENABLE = True
DOI_APP_ID = "someone will probably think it's is a bad idea to display this in a changeme"
DOI_MINTURL = "https://services.ands.org.au/home/dois/doi_mint.php"
DOI_ACCESS_URL = "http://dx.doi.org/"
DOI_DATACITE_TEMPLATE_PATH = "monash_ands/doi_request.xml"
