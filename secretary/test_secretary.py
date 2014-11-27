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

import os
import pwd
import grp

from nose.tools import raises

import secretary


def test_getSystemLoad_listWithThreeEntries():
    avg = secretary.get_system_load()
    assert(len(avg) is 3)


def test_getPollingDelayIt_delayIsRaising():
    delay_it = secretary.get_polling_delay_it()
    delay_a = delay_it.next()
    delay_b = delay_it.next()
    assert(delay_a < delay_b)


def test_getPollingDelayIt_delayMaxIsMAX_POLLING_INTERVAL():
    delay_it = secretary.get_polling_delay_it()
    delay_prev = 0
    delay = delay_it.next()
    while delay_prev < delay:
        delay_prev = delay
        delay = delay_it.next()

    assert(delay is secretary.MAX_POLLING_INTERVAL)


def test_do_drop_privileges_setCurrentUserReturnsTrue():
    uname = pwd.getpwuid(os.getuid()).pw_name
    gname = grp.getgrgid(os.getgid()).gr_name
    ret = secretary.do_drop_privileges(user_name=uname, group_name=gname)
    assert(ret is True)


def test_do_drop_privileges_setUserWithoutPermissionReturnsFalse():
    ret = secretary.do_drop_privileges(user_name='root', group_name='root')
    assert(ret is False)


def test_do_drop_privileges_setUnknownUserReturnsFalse():
    ret = secretary.do_drop_privileges(user_name='foo', group_name='foo')
    assert(ret is False)