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


class Node(object):
    """A DTO representing a physical machine, running a cuckoo node."""

    def __init__(self, hermes_id, name, network_address, metadata, state):
        self.id = hermes_id
        self.name = name
        self.network_address = network_address
        self.metadata = metadata
        self.state = state

    def __repr__(self):
        return "id: %d, name: %s"%(self.id, self.name)