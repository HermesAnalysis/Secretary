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


class Error(Exception):
    """Base class for exceptions in this package."""
    pass


class HermesError(Error):
    """Exception raised for problems with the hermes system.

    Attributes:
        msg   -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


class CuckooError(Error):
    """Exception raised for problems with cuckoo.

    Attributes:
        msg   -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)