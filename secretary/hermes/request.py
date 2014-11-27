# coding=utf-8
#
# Copyright (c) 2013,  Institute for Internet Security - if(is)
#
# This file is part of Secretary.
#
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl 5
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

import logging
from simplejson import JSONDecodeError
import requests
from hermes.error import AuthenticationError

log = logging.getLogger("hermesConnector")


class Request(object):
    """Helper class for HTTP-requests.
    TODO: merge with request class from cuckoo package.

    Attributes:
        url -- the url for the request
    """

    MSG_HTTP_ERROR = 'The server could not fulfill the request. Error code: '
    MSG_URL_ERROR = 'We failed to reach a server. Reason: '

    def __init__(self, url):
        self.session = requests.Session()

    def multipart_post(self, url, post_params, files=None):
        """Send a HTTP-POST-request and return the response as a decoded
        json dict. Raise an error if a bad status code is received.

        Keyword arguments:
            post_params -- a dict containing the post data.
        """
        response = self.session.post(url, post_params, files=files, verify=False)

        # raise error if we got a bad status code
        response.raise_for_status()

        try:
            json = response.json()
        except JSONDecodeError, e:
            log.error("Error in multipart_post " + str(e))
            # In context of hermes this means we are not logged in, so the login form is returned in the response
            # as normal html. This is a longshot, but normally this should be the only reason for the JSONDecodeError...
            raise AuthenticationError(e)

        return json

    def ajax_login(self, url, username, password):
        """Login hack for SpringSecurity, simulating an ajax request.
        After a successful login the session keeps logged in until timed out.

        Keyword arguments:
            url      -- login url
            username -- the login name
            password -- plain password

        Return:
            True if login was successful. False else.
        """
        header = {'X-Requested-With': "XMLHttpRequest"}  # simulates ajax request
        payload = {'j_username': username, 'j_password': password}

        response = self.session.post(url, payload, headers=header, verify=False)

        json = response.json()

        success = False
        if 'success' in json:
            success = json['success']

        return success