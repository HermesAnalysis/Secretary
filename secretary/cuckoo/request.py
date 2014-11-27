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

import os
import requests


class Request(object):
    """Helper class for HTTP-requests.

    Attributes:
        url -- the url for the request
    """

    MSG_HTTP_ERROR = 'The server could not fulfill the request. Error code: '
    MSG_URL_ERROR = 'We failed to reach a server. Reason: '

    WRITE_BUFFER = 1024

    def __init__(self, url):
        self.url = url

    def get(self):
        """Send a HTTP-GET-request and return the response as a decoded
        json dict.
        """

        request = requests.get(self.url)

        # raise error if we got a bad status code
        request.raise_for_status()

        return request.json()

    def post(self, post_params, files=None):
        """Send a HTTP-POST-request and return the response as a decoded
        json dict. Raise an error if a bad status code is received.

        Keyword arguments:
            post_params -- a dict containing the post data.
        """

        response = requests.post(self.url, post_params, files=files)

        # raise error if we got a bad status code
        response.raise_for_status()

        return response.json()

    def get_file(self, download_dir, filename):
        """Download the content and save it to the given path of the file
        system.
        """
        request = requests.get(self.url, verify=False)

        # raise error if we got a bad status code
        request.raise_for_status()

        # save content to file

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        file_path = download_dir + filename

        with open(file_path, 'wb') as f:
            for chunk in request.iter_content(self.WRITE_BUFFER):
                f.write(chunk)