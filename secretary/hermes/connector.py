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
from requests.exceptions import HTTPError, ConnectionError, RequestException

from hermes import api_params as api
from hermes.dto.dto_factory import DtoFactory, DtoFactoryError
from hermes.dto.hypervisor import Hypervisor
from hermes.dto.node import Node
from hermes.error import ApiError, RequestError, AuthenticationError
from hermes.request import Request

log = logging.getLogger("hermesConnector")


class Connector:
    """The Connector class provides access to the hermes API.

    Attributes:
        url -- the url of the hermes server
    """

    ERROR_MSG_UNKNOWN_STATUS = "unknown status code"

    NODE_STATE_ONLINE = "online"
    NODE_STATE_OFFLINE = "offline"
    NODE_STATE_FAILURE = "failure"

    def __init__(self, url):
        self.url = url + api.CONTROLLER
        self.base_url = url
        self.request = Request(self.url)
        self.username = None
        self.password = None

    def brew_coffee(self):
        """Try to brew some coffee with hermes."""
        return self._post_request(api.METHOD_BREW_COFFEE)

    def send_dummy_message(self, msg):
        """Send a dummy message to the hermes server and receive it as a
        response.

        Keyword arguments:
            msg -- the message which is send to the server
        """
        return self._post_request(api.METHOD_SEND_MESSAGE_DUMMY,
                                  {api.PARAM_SEND_MESSAGE_DUMMY_MSG: msg})

    def get_hypervisors(self):
        """Get a list of all available hypervisors from the hermes server."""
        json_response = self._post_request(api.METHOD_GET_HYPERVISORS)
        hypervisors_json = json_response[api.KEY_HYPERVISOR]

        hypervisors = []
        for json in hypervisors_json:
            hypervisor_id = json[api.KEY_HYPERVISOR_ID]
            name = json[api.KEY_HYPERVISOR_NAME]
            hypervisors.append(Hypervisor(hypervisor_id, name))

        return hypervisors

    def register_node(self, name, networkAddress, metadata, hypervisorIds):
        """Register a node on the hermes server and return the registered node.

        Keyword arguments:
            name           -- the name of the node
            networkAddress -- the ip address of the node inside the LAN
            metadata       -- some descriptive metadata
            hypervisorIds  -- the ids of the running hypervisors as a comma seperated list
        """
        post_dict = {
            api.PARAM_REGISTER_NODE_NAME: name,
            api.PARAM_REGISTER_NODE_NETWORK: networkAddress,
            api.PARAM_REGISTER_NODE_META: metadata,
            api.PARAM_REGISTER_NODE_HYPERVISOR: hypervisorIds
        }
        json_response = self._post_request(api.METHOD_REGISTER_NODE, post_dict)
        json_node = json_response[api.KEY_NODE]
        node = Node(
            json_node[api.KEY_NODE_ID],
            json_node[api.KEY_NODE_NAME],
            json_node[api.KEY_NODE_NETWORK],
            json_node[api.KEY_NODE_META],
            json_node[api.KEY_NODE_STATE]
        )
        return node

    def poll_jobs(self, node_id):
        """Poll the maximum number of jobs that are available for the node
        with the given id.

        Returns a dict of a list of published job and a list of failed job ids.

        Keyword arguments:
            node_id -- the id of the node that polls jobs
        """
        json_response = self._post_request(api.METHOD_POLL_JOBS,
                                           {api.PARAM_POLL_JOBS_NODE: node_id})
        json_published_jobs = json_response[api.KEY_PUBLISHED_JOBS]

        factory = DtoFactory()
        published_jobs = []
        failed_job_ids = []
        for json in json_published_jobs:

            try:
                deserialized_job = factory.create_job_from_json(json)
                published_jobs.append(deserialized_job)
            except DtoFactoryError, e:
                # deserialization fail
                failed_job_ids.append(e.id)

        return {'jobs': published_jobs, 'failed': failed_job_ids}

    def notify_node_load(self, node_id, load):
        """Notify the server about the current load average stats.

         Keyword arguments:
            node_id -- the id of the node that sends the stats
            load    -- list of load averages
        """

        json_response = self._post_request(api.METHOD_NOTIFY_NODE_LOAD,
                                           {api.PARAM_NOTIFY_NODE: node_id,
                                            api.PARAM_NOTIFY_LOAD_1: load[0],
                                            api.PARAM_NOTIFY_LOAD_5: load[1],
                                            api.PARAM_NOTIFY_LOAD_15: load[2]})

    def notify_start_job(self, node_id, job_id):
        """Notify the server that the job was started.

        Keyword arguments:
            node_id -- the id of the node that starts the job
            job_id  -- the id of the job which is started
        """
        json_response = self._post_request(api.METHOD_NOTIFY_START_JOB,
                                           {api.PARAM_NOTIFY_NODE: node_id,
                                            api.PARAM_NOTIFY_JOB: job_id})

        job_json = json_response[api.KEY_JOB]

        return job_json[api.KEY_JOB_ID]

    def notify_finish_job(self, node_id, job_id, cuckoo_log, report_html):
        """Notify the server that the job is finished.

        Keyword arguments:
            node_id -- the id of the node that finished the job
            job_id  -- the id of the job which is finished
            cuckoo_log -- the cuckoo analysis log file
            report_html -- the generated html report
        """

        files = {'logFile': cuckoo_log, 'reportFile': report_html}

        json_response = self._post_request(api.METHOD_NOTIFY_FINISH_JOB,
                                           {api.PARAM_NOTIFY_NODE: node_id,
                                            api.PARAM_NOTIFY_JOB: job_id},
                                           files)

        job_json = json_response[api.KEY_JOB]

        return job_json[api.KEY_JOB_ID]

    def notify_fail_job(self, node_id, job_id, error_log, cuckoo_log):
        """Notify the server that the job has failed.

        Keyword arguments:
            node_id -- the id of the node that failed the job
            job_id  -- the id of the job which failed
            cuckoo_log -- the cuckoo analysis log file
        """
        files = {'logFile': cuckoo_log}

        json_response = self._post_request(api.METHOD_NOTIFY_FAIL_JOB,
                                           {api.PARAM_NOTIFY_NODE: node_id,
                                            api.PARAM_NOTIFY_JOB: job_id,
                                            api.PARAM_NOTIFY_ERROR: error_log},
                                           files)

        job_json = json_response[api.KEY_JOB]

        return job_json[api.KEY_JOB_ID]

    def update_node_state(self, node_id, node_state):
        """Notify the server about the current state of the node

        Keyword arguments:
            node_id -- the id of the node which notifies about a new state
            node_state -- the new state
        """
        self._post_request(api.METHOD_UPDATE_NODE_STATE,
                           {api.PARAM_UPDATE_STATE_NODE: node_id,
                            api.PARAM_UPDATE_STATE_STATE: node_state})

    def login(self, username, password):
        """Login to hermes with the given credentials.

        Keyword arguments:
            username -- the username
            password -- blank password
        """
        success = False
        self.username = username
        self.password = password

        try:
            success = self.request.ajax_login(self.base_url + api.METHOD_LOGIN, username, password)
        except HTTPError, e:
            log.error("Error in _post_request " + str(e))
            raise RequestError("", str(e))
        except ConnectionError, e:
            log.error("Error in _post_request " + str(e))
            raise RequestError("", str(e))

        if not success:
            raise ApiError(0, "login failed")

    def _relogin(self):
        """Reauthenticate with already stored credentials.
        If no credentials are stored, raise an AuthenticationError.
        """
        if self.username and self.password:
            self.login(self.username, self.password)
        else:
            raise AuthenticationError("username and/or password not set")

    def _post_request(self, url, post_params=None, files=None):
        """Send a post request to the given url with the given params and
        return the response.
        Raise an ApiError if the response contains a error code.

        Keyword arguments:
            url        -- the url for the request
            postParams -- a dict containing post parameter data, defaults to
                          an empty dict (optional)
            files      -- files for multipart-form request upload
        """

        if post_params is None:
            post_params = {}

        url = self.url + url

        try:
            response = self.request.multipart_post(url, post_params, files)
        except HTTPError, e:
            log.error("Error in _post_request " + str(e))
            raise RequestError("", str(e))
        except ConnectionError, e:
            log.error("Error in _post_request " + str(e))
            raise RequestError("", str(e))
        except RequestException, e:
            log.error("Error in _post_request " + str(e))
            raise RequestError("", str(e))
        except AuthenticationError, e:
            log.error("Error in _post_request " + str(e))
            # login and retry request
            self._relogin()
            response = self.request.multipart_post(url, post_params, files)

        # check api status
        status = int(response['code'])
        if status == api.STATUS_CODE_OK:
            pass
        elif status == api.STATUS_CODE_ERROR:
            error_msg = response['error']
            raise ApiError(status, error_msg)
        else:
            raise ApiError(status, self.ERROR_MSG_UNKNOWN_STATUS)

        return response
