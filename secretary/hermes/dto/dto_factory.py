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

import datetime
import logging
from hermes.dto.job import Job
from hermes.dto.sample import Sample
from hermes.dto.sensor import Sensor
from hermes.dto.virtual_machine import VirtualMachine

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"  # hermes format
CLOCK_FORMAT = "%m-%d-%Y %H:%M:%S"  # cuckoo format
TIMEOUT_FORMAT = "%H:%M:%S"  # hermes timeout format

log = logging.getLogger("dtoFactory")


class DtoFactory(object):
    """Factory class which provides static methods to create hermes.dto
    objects.
    """

    def create_job_from_json(self, json):
        """Create a job object from the given decoded json dict.
        Raises DtoFactoryError if an error occurred during deserialization.
        """

        job_json = json['job']

        job_id = json['id']  # use the id of the published job
        name = job_json['name']
        priority = job_json['priority']
        memory_dump = job_json['memoryDump']

        try:
            simulated_time = datetime.datetime.strptime(job_json['simulatedTime'],
                                                        DATE_TIME_FORMAT)
            simulated_time = simulated_time.strftime(CLOCK_FORMAT)  # to string

            timeout_date = datetime.datetime.strptime(job_json['timeout'],
                                                  TIMEOUT_FORMAT)
        except ValueError, e:
            log.error("error while parsing the time format: " + str(e.message))
            raise DtoFactoryError(str(e.message), job_id)

        timeout_delta = datetime.timedelta(hours=timeout_date.hour,
                                           minutes=timeout_date.minute,
                                           seconds=timeout_date.second)

        timeout = str(timeout_delta.total_seconds())  # to string

        if job_json['sensor']:
            sensor = self.create_sensor_from_json(job_json['sensor'])
        else:
            sensor = None

        sample = self.create_sample_from_json(job_json['sample'])
        virtual_machine = self.create_virtual_machine_from_json(
            job_json['virtualMachine'])

        job = Job(job_id, name, sensor, sample, virtual_machine, simulated_time, timeout, priority, memory_dump)

        return job

    def create_sensor_from_json(self, json):
        """Create a sensor object from the given decoded json dict."""

        sensor_id = json['id']
        name = json['name']
        sensor_type = json['type']
        description = json['description']
        md5 = json['md5']
        file_url = json['fileUrl']
        original_filename = json['originalFilename']

        sensor = Sensor(sensor_id, name, sensor_type, description, md5,
                        file_url, original_filename)
        return sensor

    def create_sample_from_json(self, json):
        """Create a sample object from the given decoded json dict."""

        sample_id = json['id']
        name = json['name']
        file_content_type = json['fileContentType']
        description = json['description']
        md5 = json['md5']
        sha1 = json['sha1']
        sha256 = json['sha256']
        sha512 = json['sha512']
        file_url = json['fileUrl']
        original_filename = json['originalFilename']

        sample = Sample(sample_id, name, file_content_type, description, md5,
                        sha1, sha256, sha512, file_url, original_filename)
        return sample

    def create_virtual_machine_from_json(self, json):
        """Create a virtual machine object from the given decoded json dict."""

        vm_id = json['id']
        name = json['name']
        description = json['description']
        hypervisor = json['hypervisor']['name']
        operating_system = json['os']['name']
        file_url = json['fileUrl']
        original_filename = json['originalFilename']

        vm = VirtualMachine(vm_id, name, description, hypervisor,
                            operating_system, file_url, original_filename)
        return vm


class DtoFactoryError(Exception):

    def __init__(self, msg, id):
        self.msg = msg
        self.id = id