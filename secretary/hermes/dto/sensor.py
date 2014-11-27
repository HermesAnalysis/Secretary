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


class Sensor(object):
    """DTO that represents the sensor of the hermes system. Contains the url
    of the download location of the sensor file.

    Attributes:
        id                -- the id of the sensor on the hermes server
        name              -- the name of the sensor
        description       -- a description of the sensor
        md5               -- the md5 hash of the sensor file
        file_url          -- the download url of the sensor file
        original_filename -- the original name of the sensor file
    """

    def __init__(self, hermes_id, name, sensor_type, description, md5,
                 file_url, original_filename):
        self.id = hermes_id
        self.name = name
        self.type = sensor_type,
        self.description = description
        self.md5 = md5
        self.file_url = file_url
        self.original_filename = original_filename