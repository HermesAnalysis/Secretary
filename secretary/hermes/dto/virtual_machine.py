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


class VirtualMachine(object):
    """DTO representing the virtual machine image file on the server.

    Attributes:
        id                -- the id of the virtual machine on the hermes server
        name              -- the name of the virtual machine
        description       -- a description of the virtual machine
        hypervisor        -- the hypervisor used for the virtual machine
        operating_system  -- the name of the operating system used by the
                             virtual machine
        file_url          -- the download url of the virtual machine image file
        original_filename -- the original name of the image file
    """

    def __init__(self, hermes_id, name, description, hypervisor,
                 operating_system, file_url, original_filename):
        self.id = hermes_id
        self.name = name
        self.description = description
        self.hypervisor = hypervisor
        self.operating_system = operating_system
        self.file_url = file_url
        self.original_filename = original_filename
