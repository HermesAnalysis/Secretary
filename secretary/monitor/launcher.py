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

import imp
import os
import sys
import time
import threading
import multiprocessing
import logging

from monitor.monitoring import Observable

loggerName = "launcher"


class SubprocessWrapper(multiprocessing.Process):

    _respawn = False
    _target = None

    def __init__(self, group=None, target=None, name=None, respawn=False, *args, **kwargs):
        multiprocessing.Process.__init__(self, group, target, name, args, kwargs)
        self._target = target
        self._respawn = respawn
        self.name = name

    def respawn(self):
        return self._respawn

    def run(self):
        self._run_method()

    def _run_method(self):
        NotImplementedError("You should implement this method!")

    def status(self):
        return self.is_alive()


class CuckooCoreWrapper(SubprocessWrapper):

    _kwargs = {}

    def __init__(self, group=None, target=None, name=None, respawn=False, *args, **kwargs):
        SubprocessWrapper.__init__(self, group, target, name, respawn, args, kwargs)
        self._log = logging.getLogger(loggerName)
        self._kwargs = kwargs

    def _run_method(self):

        cuckoo_dir = os.path.dirname(self._target)

        # add cuckoo dir to system path and change directory to launch cuckoo
        # from its own directory
        sys.path.append(cuckoo_dir)
        os.chdir(cuckoo_dir)

        cuckoo = imp.load_source('cuckoo', self._target)
        cuckoo.main()


class CuckooApiWrapper(SubprocessWrapper):

    _kwargs = {}

    def __init__(self, group=None, target=None, name=None, respawn=False, *args, **kwargs):
        SubprocessWrapper.__init__(self, group, target, name, respawn, args, kwargs)
        self._log = logging.getLogger(loggerName)
        self._kwargs = kwargs

    def _run_method(self):

        os.chdir(os.path.dirname(self._target))
        cuckoo = imp.load_source('api', self._target)
        cuckoo.main()

        # os.path.join(os.path.abspath(self._target))
        # ## target specific implementation
        # module_name = os.path.basename(self._target)
        # module_name = modulename[:-3]
        # __import__(module_name)
        # loaded_module = sys.modules[module_name]
        # loaded_module.run(host=self._kwargs[host], port=self._kwargs[port])


class MonitorThread(threading.Thread, Observable):

    _monitored_subprocs = []
    _running = True

    def __init__(self):
        threading.Thread.__init__(self)
        self._log = logging.getLogger(loggerName)

    def stop(self):
        self._running = False

    def attach_process(self, subprocesswrapper=None):
        if issubclass(subprocesswrapper.__class__, SubprocessWrapper):
            if not subprocesswrapper in self._monitored_subprocs:
                subprocesswrapper.start()
                self._monitored_subprocs.append(subprocesswrapper)
            else:
                raise ValueError("Already attached")

    def detach_process(self, subprocesswrapper=None):
        try:
            self._monitored_subprocs.remove(subprocesswrapper)
        except ValueError:
            raise ValueError("")

    def _handle_fail(self, proc):
        self.notify()
        if proc.respawn():
            self._log.error("respawning process %s" % proc.name)
            # TODO: refactoring for generalisation
            self.detach_process(proc)
            if isinstance(proc, CuckooCoreWrapper):
                self.attach_process(CuckooCoreWrapper(target=proc._target, name=proc.name, respawn=True))
            elif isinstance(proc, CuckooApiWrapper):
                self.attach_process(CuckooApiWrapper(target=proc._target, name=proc.name, respawn=True))

        else:
            raise RuntimeError("Process %s terminated - not re-spawned" % (proc.name))

    def _monitor_loop(self):
        for proc in self._monitored_subprocs:
            if not proc.is_alive():
                self._log.critical("Process %s failed" % (proc.name))
                self._handle_fail(proc)

    def run(self):
        try:
            while self._running:
                self._monitor_loop()
                time.sleep(5)
        except RuntimeError as e:
            self._log.critical(e.message)
            self._log.critical("Shutting down sub-processes...")
            # self.notify()

        for proc in self._monitored_subprocs:
            self._log.info("terminating process %s" % proc.name)
            proc.terminate()
            proc.join()

    def abort(self):
        self._running = False

    def status(self):
        ret = {}
        for proc in self._monitored_subprocs:
            ret[proc.name] = proc.status

        return ret