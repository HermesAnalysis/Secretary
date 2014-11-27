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


class Job(object):
    """DTO that represents a job configuration. This class is a combination of
    the Job and the PublishedJob classes of the hermes system.

    Attributes:
        id              -- the id of the published job on the hermes server
        name            -- the name of the job
        sensor          -- the sensor that is used for this job
        sample          -- the sample that is analysed in this job
        virtual_machine -- the virtual machine that is used to run this job
        simulated_time  -- the time which must be simulated when running
                           this job
        timeout         -- the time period after which the job is considered to
                           have timed out (in seconds)
        priority        -- the priority of this job, the higher the value, the
                           higher the priority
        memory_dump     -- true if the node must send a memory dump after
                           processing the job
    """

    # the different states of the job as provided by cuckoo
    STATE_PUBLISHED = "published"
    STATE_PENDING = "pending"
    STATE_PROCESSING = "running"
    STATE_SUCCESS = "success"
    STATE_FAILURE = "failure"

    def __init__(self, hermes_id, name, sensor, sample, virtual_machine, simulated_time, timeout, priority, memory_dump):
        self.id = hermes_id
        self.name = name
        self.sensor = sensor
        self.sample = sample
        self.virtual_machine = virtual_machine
        self.simulated_time = simulated_time
        self.timeout = timeout
        self.priority = priority
        self.memory_dump = memory_dump
        self.state = self.STATE_PUBLISHED
        self.cuckoo_id = None
