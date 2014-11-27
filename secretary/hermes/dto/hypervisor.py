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


class Hypervisor(object):
    """
    DTO that represents a hypervisor that can be used to run images of
    virtual machines.

    Attributes:
        id   -- the id on the hermes server
        name -- the name of the hypervisor
    """

    def __init__(self, hermes_id, name):
        self.id = hermes_id
        self.name = name

    def __repr__(self):
        return "id: %d, name: %s"%(self.id, self.name)