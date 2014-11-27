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

"""Constants for key and method names of the hermes api."""

#: the API entry point
CONTROLLER = "publishing/"

## the server methods, mapping to specific urls

#: the name of the brewCoffee url-path
METHOD_BREW_COFFEE = "brewCoffee"
#: the name of the messageDummy url-path
METHOD_SEND_MESSAGE_DUMMY = "messageDummy"
#: the name of the pollJobs url-path
METHOD_POLL_JOBS = "pollJobs"
#: the name of the registerNode url-path
METHOD_REGISTER_NODE = "registerNode"
#: the name of the getHypervisors url-path
METHOD_GET_HYPERVISORS = "getHypervisors"
#: the name of the notifyStartJob url-path
METHOD_NOTIFY_START_JOB = "notifyStartJob"
#: the name of the notifyFinishJob url-path
METHOD_NOTIFY_FINISH_JOB = "notifyFinishJob"
#: the name of the notifyFailJob url-path
METHOD_NOTIFY_FAIL_JOB = "notifyFailJob"
#: the name of the notifyNodeAvgLoad url-path
METHOD_NOTIFY_NODE_LOAD = "notifyNodeAvgLoad"
#: the name of the login url-path
METHOD_LOGIN = "j_spring_security_check"
#: the name of the updateNodeState url-path
METHOD_UPDATE_NODE_STATE = "updateNodeState"


##  request post parameter keys

#: message post param for messageDummy method
PARAM_SEND_MESSAGE_DUMMY_MSG = "msg"

#: name post param for registerNode method
PARAM_REGISTER_NODE_NAME = "name"
#: networkAddress post param for registerNode method
PARAM_REGISTER_NODE_NETWORK = "networkAddress"
#: metadata post param for registerNode method
PARAM_REGISTER_NODE_META = "metadata"
#: hypervisorIds post param for registerNode method
PARAM_REGISTER_NODE_HYPERVISOR = "hypervisorIds"

#: nodeId post param for pollJobs method
PARAM_POLL_JOBS_NODE = "nodeId"

#: nodeId post param for notify method
PARAM_NOTIFY_NODE = "nodeId"
#: publishedJobId post param for notify method
PARAM_NOTIFY_JOB = "publishedJobId"
#: errorLog post param for notify method
PARAM_NOTIFY_ERROR = "errorLog"
#: loadAvg1 post param for notify method
PARAM_NOTIFY_LOAD_1 = "loadAvg1"
#: loadAvg5 post param for notify method
PARAM_NOTIFY_LOAD_5 = "loadAvg5"
#: loadAvg15 post param for notify method
PARAM_NOTIFY_LOAD_15 = "loadAvg15"

#: nodeId post param for updateState method
PARAM_UPDATE_STATE_NODE = "nodeId"
#: state post param for updateState method
PARAM_UPDATE_STATE_STATE = "state"


## response keys for the json response

#: response key for hypervisor list field
KEY_HYPERVISOR = "hypervisors"
#: response key for hypervisor id field
KEY_HYPERVISOR_ID = "id"
#: response key for hypervisor name field
KEY_HYPERVISOR_NAME = "name"

#: response key for node object field
KEY_NODE = "node"
#: response key for node id field
KEY_NODE_ID = "id"
#: response key for node name field
KEY_NODE_NAME = "name"
#: response key for node networkAddress field
KEY_NODE_NETWORK = "networkAddress"
#: response key for node metadata field
KEY_NODE_META = "metadata"
#: response key for node currentState field
KEY_NODE_STATE = "currentState"

#: response key for publishedJobs list field
KEY_PUBLISHED_JOBS = "publishedJobs"

#: response key for job object field
KEY_JOB = "job"
#: response key for job id field
KEY_JOB_ID = "id"

## status codes

#: status code for ok response
STATUS_CODE_OK = 1
#: status code for error response
STATUS_CODE_ERROR = 100
