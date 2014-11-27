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
from requests import HTTPError
from requests.exceptions import ConnectionError
from error import CuckooError

from request import Request


log = logging.getLogger("restApiClient")


class RestApiClient(object):
    """Client for the REST-API of the cuckoo server. Implements all needed
    methods for submitting jobs.
    """

    METHOD_CREATE_FILE_TASK = "/tasks/create/file"
    METHOD_VIEW_TASK = "/tasks/view_custom/"

    CLOCK_FORMAT = "%m-%d-%Y %H:%M:%S"

    def __init__(self, host, port):
        self.server_url = "http://" + host + ":" + port
        pass

    def create_file_task(self, task_id, sample_path, sensor_filename, timeout,
                         priority, memory, clock, enforce_timeout,
                         custom_options):
        """Submit the given file to the cuckoo api in order to create a
        new task for it.

        Keyword arguments:
            task_id -- the manually specified id for the task
            sample_path -- the path to the sample file
            sensor_filename -- the name of the sensor file
            timeout -- timeout for the task
            priority -- priority to assign to the task (1-3)
            memory -- enable the creation of a full memory dump of the
                      analysis machine
            clock -- sets the vm clock for this task to the given value
            enforce_timeout -- enable to enforce the execution for the full
                               timeout value
            custom_options --  custom option parameters that will be appended
                               to the option parameter of the cuckoo api

        """
        api_url = self.server_url + self.METHOD_CREATE_FILE_TASK

        if sensor_filename:
            options_params = "sensor=" + sensor_filename
        else:
            options_params = ""

        if custom_options:
            options_params = options_params + ", " + custom_options

        post_params = {
            'custom': task_id,
            'options': options_params,
            'timeout': timeout,
            'priority': priority,
            'memory': memory,
            'clock': clock,
            'enforce_timeout': enforce_timeout
        }

        files = {'file': open(sample_path, 'rb')}
        request = Request(api_url)

        log.info("Request to " + api_url + " with params " + str(post_params))
        try:
            response = request.post(post_params, files)
        except HTTPError, e:
            log.error("Error in create_file_task: " + str(e))
            raise CuckooError(str(e))
        except ConnectionError, e:
            log.error("Error in view_task: " + str(e))
            raise CuckooError(str(e))

        log.info("Response: " + str(response))

        return response

    def view_task(self, task_id):
        """Get the details of the task with the given id."""
        api_url = self.server_url + self.METHOD_VIEW_TASK + str(task_id)

        request = Request(api_url)

        log.info("Request to " + api_url)
        try:
            response = request.get()
        except HTTPError, e:
            log.error("Error in view_task: " + str(e))
            raise CuckooError(str(e))
        except ConnectionError, e:
            log.error("Error in view_task: " + str(e))
            raise CuckooError(str(e))

        log.info("Response: " + str(response))

        return response