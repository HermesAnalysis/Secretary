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


class Sample(object):
    """DTO for malware sample file. Contains the url of the download location
    of the sample file.

    Attributes:
        id                -- the id of the sample on the hermes server
        name              -- the name of the sample
        file_content_type -- the content type of the sample file
        description       -- a description of the malware sample file
        md5               -- the md5 hash of the file
        sha1              -- the sha1 hash of the file
        sha256            -- the sha256 hash of the file
        sha512            -- the sha512 hash of the file
        file_url          -- the download url of the file
        original_filename -- the original name of the sample file
    """

    def __init__(self, hermes_id, name, file_content_type, description, md5,
                 sha1, sha256, sha512, file_url, original_filename):
        self.id = hermes_id
        self.name = name
        self.file_content_type = file_content_type
        self.description = description
        self.md5 = md5
        self.sha1 = sha1
        self.sha256 = sha256
        self.sha512 = sha512
        self.file_url = file_url
        self.original_filename = original_filename