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


class Observer(object):

    def __init__(self):
        pass

    def update(self):
        raise NotImplementedError("You should implement this!")


class Observable(object):

    _observers = []

    def __init__(self):
        pass

    def attach(self, observer):
        if not observer:
            raise ValueError

        if not observer in self._observers:
            self._observers.append(observer)
        else:
            raise ValueError

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError as e:
            print("Unable to detach observer! Reason: %s" % (e.message))

    def notify(self, modifier=None):
        for observer in self._observers:
            if observer != modifier:
                observer.update()
