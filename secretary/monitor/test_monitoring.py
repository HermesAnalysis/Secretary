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

from nose.tools import raises

import monitoring


class MyObserver(monitoring.Observer):
    def __init__(self):
        self.updated = False

    def update(self):
        print("hit update")
        self.updated = True


@raises(ValueError)
def test_attach_doubleAttachObserver_raiseValueError():
    o = MyObserver()
    obs = monitoring.Observable()

    obs.attach(o)
    obs.attach(o)  # should raise ValueError


@raises(ValueError)
def test_attach_attachNoneValue_raisesValueError():
    obs = monitoring.Observable()
    obs.attach(None)


def test_detach_detachNoneValue_isIgnored():
    obs = monitoring.Observable()
    obs.detach(None)


def test_detach_detachNotAttachedObservable_isIgnored():
    o1 = MyObserver()
    o2 = MyObserver()
    obs = monitoring.Observable()

    obs.attach(o1)
    obs.detach(o2)


def test_update_checkObservableNotificationUpdatesObserver_checkTestValueIsTrue():
    o = MyObserver()
    obs = monitoring.Observable()
    obs.attach(o)
    obs.notify()
    print("Notification update is: " + str(o.updated))
    assert(o.updated is True)
