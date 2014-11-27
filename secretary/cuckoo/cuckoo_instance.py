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


class CuckooInstance(object):
    """
    Represents a cuckoo instance and the data needed to communicate with
    it.
    """

    def __init__(self, hypervisor, ip, port, sensor_dir, storage_dir):
        self.hypervisor = hypervisor
        self.ip = ip
        self.port = port
        self.sensor_dir = sensor_dir
        self.storage_dir = storage_dir
        self.hypervisor_id = None