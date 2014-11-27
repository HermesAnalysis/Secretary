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

from ConfigParser import SafeConfigParser
import logging
import logging.config
import os
import pwd
import grp
import shutil
import time
import multiprocessing
import thread
import signal
import traceback

from requests.exceptions import HTTPError, ConnectionError
import sys
from hermes.dto.job import Job

from monitor.launcher import CuckooCoreWrapper, CuckooApiWrapper, MonitorThread
from cuckoo.cuckoo_instance import CuckooInstance
from hermes.connector import Connector
from error import HermesError, CuckooError, Error
from cuckoo.rest_api_client import RestApiClient
from cuckoo.request import Request
from hermes.error import ApiError
from hermes.error import RequestError
from monitor.monitoring import Observer


__VERSION__ = "0.2"

logging.config.fileConfig('logging.conf')
log = logging.getLogger("secretary")

MAX_POLLING_INTERVAL = 60
MIN_POLLING_INTERVAL = 10

CUCKOO_LOG_FILE_NAME = "analysis.log"
CUCKOO_REPORT_FILE_NAME = "report.html"


def get_system_load():
    """Return system load respecting the number of CPUs in the
    system. A load higher 1.00 means excessive load.
    Returns (1min, 5min, 15min) average.
    """
    num_cpu = multiprocessing.cpu_count()
    load = [(x / num_cpu) for x in os.getloadavg()]
    return load


def get_polling_delay_it():
    """Returns an iterator, which runs between MIN_POLLING_INTERVAL and
    MAX_POLLING_INTERVAL.
    """
    wt = MIN_POLLING_INTERVAL
    while wt < MAX_POLLING_INTERVAL:
        yield wt
        wt *= 2
    wt = MAX_POLLING_INTERVAL
    while True:
        yield wt


class Secretary(Observer):
    """A manager class for a cuckoo node, used to poll jobs from the hermes
    system and submit them to the node.
    Uses the cuckoo REST-API for submitting jobs.

    Attributes:
        name -- the name of the node on which secretary is running
        network_address -- the ip address of the node
        metadata -- some descriptive metadata about the node
        download_dir -- the directory that is used to download files
                        from hermes
        cuckoo_instances -- dictionary with configured cuckoo instances. The
                            keys are the used hypervisors.
        jobs -- a list of all active jobs
        hermes -- the interface to the hermes server
        id -- the id of the node on which secretary is running
    """

    ERROR_MSG_NO_HYPERVISOR = "no corresponding hypervisor found"
    CONFIG_FILE = "secretary.conf"
    SYSTEM_FILE = "system.conf"

    def __init__(self):
        log.info("load node config...")

        self.is_interrupted = False

        config_parser = SafeConfigParser()
        config_parser.read(self.CONFIG_FILE)

        self.name = config_parser.get("node", "name")
        self.network_address = config_parser.get("node", "network_address")
        self.metadata = config_parser.get("node", "metadata")
        self.download_dir = config_parser.get("node", "download_dir")
        self.hermes = Connector(config_parser.get("hermes", "hermes_url"))
        self.username = config_parser.get("hermes", "username")
        self.password = config_parser.get("hermes", "password")

        cuckoo_instances = config_parser.get("node", "cuckoo_instances")\
            .split(",")

        self._mt = MonitorThread()
        self._mt.start()
        self._mt.attach(self)

        self.cuckoo_instances = dict()
        for instance in cuckoo_instances:
            hypervisor = config_parser.get(instance, "hypervisor")
            ip = config_parser.get(instance, "rest_api_ip")
            port = config_parser.get(instance, "rest_api_port")
            cuckoo_base_dir = config_parser.get(instance, "cuckoo_base_dir")
            sensor_dir = cuckoo_base_dir + config_parser.get(instance, "sensor_dir")
            self.storage_dir = cuckoo_base_dir + config_parser.get(instance, "storage_dir")
            self.binaries_dir = cuckoo_base_dir + config_parser.get(instance, "binaries_dir")
            db_dir = cuckoo_base_dir + config_parser.get(instance, "db_dir")
            cuckoo_config = CuckooInstance(hypervisor, ip, port, sensor_dir,
                                           self.storage_dir)
            self.cuckoo_instances[hypervisor] = cuckoo_config

            # cleanup old files
            self.cleanup_cuckoo(db_dir, self.storage_dir)

            # launch cuckoo and api processes
            cuckoo_py = cuckoo_base_dir + config_parser.get(instance, "cuckoo_py")
            api_py = cuckoo_base_dir + config_parser.get(instance, "api_py")
            self.init_subprocesses(cuckoo_py, api_py)

        self.jobs = []
        self.failed_job_ids = []

        self.login()

        config_parser.read(self.SYSTEM_FILE)
        if config_parser.has_option("system", "node_id"):
            self.id = config_parser.get("system", "node_id")
        else:
            # this means node is not registered
            log.info("no node id found, registering node on hermes")
            self.register_node()

    def update(self):
        log.error("update from observable")

    def init_subprocesses(self, cuckoo_path, api_path):
        self._mt.attach_process(CuckooCoreWrapper(target=cuckoo_path, name="CuckooCore", respawn=True))
        time.sleep(5)  # Wait for cuckoo core to become ready
        self._mt.attach_process(CuckooApiWrapper(target=api_path, name="CuckooApi", respawn=True))

    def login(self):
        try:
            self.hermes.login(self.username, self.password)
        except ApiError, e:
            raise HermesError(str(e))
        except RequestError, e:
            raise HermesError(str(e))

    def register_node(self):
        """Register the node on which Secretary is running in the hermes
        system and saves the id to the config file.
        """
        try:
            self.update_hypervisor_id()

            hypervisor_id_string = ""
            for cuckoo in self.cuckoo_instances.values():
                hypervisor_id_string = hypervisor_id_string + str(cuckoo.hypervisor_id) + ","

            hypervisor_id_string = hypervisor_id_string[:-1]

            node = self.hermes.register_node(self.name,
                                             self.network_address,
                                             self.metadata,
                                             hypervisor_id_string)
        except ApiError, e:
            # log.error(e.msg)
            raise HermesError(str(e))
        except RequestError, e:
            # log.error(e.msg)
            raise HermesError(str(e))
        except ConnectionError, e:
            raise HermesError(str(e))

        self.id = node.id
        config_parser = SafeConfigParser()
        config_parser.add_section("system")
        config_parser.set("system", "node_id", str(self.id))
        output_file = open(self.SYSTEM_FILE, 'w')
        config_parser.write(output_file)

    def update_hypervisor_id(self):
        """Get all available hypervisors from the hermes system and searches
        for the corresponding hypervisor which is running on the current node.
        Stores the id of the found hypervisor for future usage.
        """
        hypervisors = self.hermes.get_hypervisors()

        hypervisor_found = False
        for hypervisor in hypervisors:
            if hypervisor.name in self.cuckoo_instances:
                self.cuckoo_instances[
                    hypervisor.name].hypervisor_id = hypervisor.id
                hypervisor_found = True

        if not hypervisor_found:
            raise HermesError(self.ERROR_MSG_NO_HYPERVISOR)

    def poll_jobs(self):
        """Poll available jobs from the hermes system."""
        try:
            polling_result = self.hermes.poll_jobs(self.id)
            self.jobs = polling_result['jobs']
            self.failed_job_ids = polling_result['failed']
        except ApiError, e:
            # log.error(e.msg)
            raise HermesError(str(e))
        except RequestError, e:
            # log.error(e.msg)
            raise HermesError(str(e))
        except ConnectionError, e:
            raise HermesError(str(e))

    def download_vm(self, job):
        """Download the vm for the given job.

        Keyword arguments:
            job -- the vm for this job is downloaded
        """
        request = Request(job.virtual_machine.file_url)

        download_dir = self.download_dir + "vm/" \
            + str(job.virtual_machine.id) + "/"

        request.get_file(download_dir, job.virtual_machine.original_filename)

        return download_dir + job.virtual_machine.original_filename

    def download_sample(self, job):
        """Download the sample for the given job.

        Keyword arguments:
            job -- the job for which this sample is downloaded
        """
        request = Request(job.sample.file_url)

        download_dir = self.download_dir + "sample/" \
            + str(job.sample.id) + "/"

        # for now we try to download until we succeed, death or glory!
        success = False
        delay_iterator = get_polling_delay_it()
        while not success:
            try:
                request.get_file(download_dir, job.sample.original_filename)
                success = True
            except HTTPError, e:
                log.error("Error in download_sample: " + str(e))
                time.sleep(delay_iterator.next())

        return download_dir + job.sample.original_filename

    def download_sensor(self, job):
        """Download the sensor for the given job, if a sensor is available.
        Return the path to the sensor file.
        If no sensor is available return None.

        Keyword arguments:
            job -- the job for which this sensor is downloaded
        """
        if job.sensor:
            request = Request(job.sensor.file_url)

            download_dir = self.download_dir + "sensor/" \
                + str(job.sensor.id) + "/"

            # try to download until successful
            success = False
            delay_iterator = get_polling_delay_it()
            while not success:
                try:
                    request.get_file(download_dir, job.sensor.original_filename)
                    success = True
                except HTTPError, e:
                    log.error("Error in download_sample: " + str(e))
                    time.sleep(delay_iterator.next())

            return download_dir + job.sensor.original_filename

        else:
            return None

    def poll_jobs_loop(self):
        """Poll jobs in the given interval until jobs are received.

        Keyword arguments:
            interval -- interval between pollings in ms.
        """
        try:
            self.poll_jobs()
            log.info("polled " + str(len(self.jobs)) + " jobs")
        except HermesError, e:
            log.error("error in poll_jobs_loop: " + e.msg)

        delay_iterator = get_polling_delay_it()
        while len(self.jobs) == 0 and len(self.failed_job_ids) == 0 and not self.is_interrupted:
            time.sleep(delay_iterator.next())

            try:
                self.poll_jobs()
                delay_iterator = get_polling_delay_it()  # reset iterator
                log.info("polled " + str(len(self.jobs)) + " jobs")
            except HermesError, e:
                log.error("error in poll_jobs_loop: " + e.msg)

    def submit_jobs(self):
        """Submit all available jobs."""
        for job in self.jobs:
            sample_location = self.download_sample(job)
            sensor_location = self.download_sensor(job)
            self.submit_job(sample_location, sensor_location, job)

    def fail_jobs(self):
        """Fail all failed jobs."""
        for job_id in self.failed_job_ids:
            self.abort_job("error while deserializing job", job_id)

    def abort_job(self, error_msg, job):
        """Abort the given job and send the error_msg to hermes.

        Keyword arguments:
            error_msg -- the error message send to hermes
            job -- the job which is aborted
        """

        if isinstance(job, Job):
            job.state = job.STATE_FAILURE
            job_id = job.id
            try:
                cuckoo_log = self.get_analysis_file(job)
            except IOError, e:
                # log file might not be written yet
                cuckoo_log = "log file could not be read"
        else:
            job_id = job
            cuckoo_log = "not submitted to cuckoo"

        notify_successful = False
        notify_delay_it = get_polling_delay_it()
        while not notify_successful:
            try:
                self.hermes.notify_fail_job(self.id, job_id, error_msg,
                                            cuckoo_log)
                notify_successful = True
            except ApiError, e:
                log.error(e.msg)
                time.sleep(notify_delay_it.next())
            except RequestError, e:
                log.error(e.msg)
                time.sleep(notify_delay_it.next())

    def retry_loop_notify_start_job(self, job):
        """Notify hermes about starting the job.
        If an exception occurs, the action is repeated with an increasing
        delay until successful.

        Keyword arguments:
            job -- the job which was started
        """
        submit_successful = False
        submit_delay_it = get_polling_delay_it()
        while not submit_successful:
            time.sleep(submit_delay_it.next())
            try:
                self.hermes.notify_start_job(self.id, job.id)
                submit_successful = True
            except ApiError, e:
                log.error(e.msg)
            except RequestError, e:
                log.error(e.msg)

    def submit_job(self, sample_path, sensor_path, job):
        """Submit a job to cuckoo and notify hermes.

        Keyword arguments:
            sample_path -- the path to the sample file
            sensor_path -- the path to the sensor file
            job -- the job which is submitted to cuckoo
        """

        # dummy default values
        enforce_timeout = False
        custom_options = ""

        cuckoo_for_job = self.cuckoo_instances[
            job.virtual_machine.hypervisor]

        if sensor_path:
            # copy sensor to cuckoo sensor folder
            self.copy_sensor_file_to_cuckoo(sensor_path, cuckoo_for_job.sensor_dir)
            path, sensor_filename = os.path.split(sensor_path)
        else:
            sensor_filename = None

        client = RestApiClient(cuckoo_for_job.ip,
                               cuckoo_for_job.port)

        try:
            response = client.create_file_task(
                job.id,
                sample_path,
                sensor_filename,
                job.timeout,
                job.priority,
                job.memory_dump,
                job.simulated_time,
                enforce_timeout,
                custom_options
            )
            job.cuckoo_id = response['task_id']

            try:
                self.hermes.notify_start_job(self.id, job.id)
            except ApiError, e:
                # log.error(e.msg)
                raise HermesError(str(e))
            except RequestError, e:
                # log.error(e.msg)
                raise HermesError(str(e))
            except ConnectionError, e:
                raise HermesError(str(e))

        except CuckooError, e:
            error_msg = str(e)
            log.error("CuckooError while submitting the job: " + error_msg)
            self.abort_job(error_msg, job)

        except HermesError, e:
            log.error("HermesError while submitting the job: " + e.msg)

            # retry loop
            self.retry_loop_notify_start_job(job)

    def retry_loop_notify_finish(self, job):
        """Notify hermes about finishing the job.
        If an exception occurs, the action is repeated with an increasing
        delay until successful.

        Keyword arguments:
            job -- the job which was started
        """
        cuckoo_log = self.get_analysis_file(job)
        report_html = self.get_report_file(job)
        notify_successful = False
        notify_delay_it = get_polling_delay_it()
        while not notify_successful:
            try:
                self.hermes.notify_finish_job(self.id, job.id, cuckoo_log,
                                              report_html)
                notify_successful = True
            except ApiError, e:
                log.error(e.msg)
                time.sleep(notify_delay_it.next())
            except RequestError, e:
                log.error(e.msg)
                time.sleep(notify_delay_it.next())

    def get_cuckoo_result(self, job):
        """Get the current state of the given job and update the
        state according to the result.

        Keyword arguments:
            job -- the job which is used to obtain the result
        """

        cuckoo_for_job = self.cuckoo_instances[job.virtual_machine.hypervisor]

        client = RestApiClient(cuckoo_for_job.ip,
                               cuckoo_for_job.port)
        try:
            response = client.view_task(job.id)
            status = response['task']['status']
            log.info("job " + str(job.id) + " status " + status)

            if job.state != status:
                # state has changed, update job and notify hermes
                if status == "pending":
                    job.state = job.STATE_PENDING
                elif status == "running":
                    job.state = job.STATE_PROCESSING
                    # self.hermes.notify_start_job(self.id, job.id)
                elif status == "reported":

                    # check for errors
                    errors = response['task']['errors']
                    print errors
                    if len(errors) > 0:
                        job.state = job.STATE_FAILURE
                        self.abort_job(str(errors), job)
                    else:
                        job.state = job.STATE_SUCCESS
                        self.retry_loop_notify_finish(job)

        except CuckooError, e:
            error_msg = str(e)
            log.error("CuckooError while getting cuckoo result: " + error_msg)
            self.abort_job(error_msg, job)

    def poll_cuckoo_results(self):
        """Poll the state of all jobs."""
        for job in self.jobs:
            self.get_cuckoo_result(job)

    def poll_cuckoo_results_loop(self, interval):
        """Poll jobs in a loop in the given interval.

        Keyword arguments:
            interval -- interval between pollings in ms.
        """
        self.poll_cuckoo_results()

        while not self.is_jobs_finished() and not self.is_interrupted:
            time.sleep(interval)
            self.poll_cuckoo_results()

    def is_jobs_finished(self):
        """Check if all jobs are finished."""
        finished = True

        for job in self.jobs:
            if job.state != job.STATE_FAILURE and job.state \
                    != job.STATE_SUCCESS:
                # one unfinished job means jobs in general are not finished
                finished = False
                break

        return finished

    def get_analysis_file(self, job):
        """Get the analysis file for the cuckoo task of the given job

        Keyword arguments:
            job -- the job for which to get the file
        """
        cuckoo_for_job = self.cuckoo_instances[job.virtual_machine.hypervisor]
        analysis_file = open(cuckoo_for_job.storage_dir + "/" + str(job.cuckoo_id)
                             + "/" + CUCKOO_LOG_FILE_NAME)

        return analysis_file

    def get_report_file(self, job):
        """Get the generated html report file for the cuckoo task of the given
        job.

        Keyword arguments:
            job -- the job for which to get the file
        """
        cuckoo_for_job = self.cuckoo_instances[job.virtual_machine.hypervisor]
        report_file = open(cuckoo_for_job.storage_dir + "/" + str(job.cuckoo_id)
                             + "/reports/" + CUCKOO_REPORT_FILE_NAME)

        return report_file

    def clean_directory(self, target_dir):
        """Deletes everything inside the given directory."""
        for currentFile in os.listdir(target_dir):
            file_path = os.path.join(target_dir, currentFile)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            else:
                shutil.rmtree(file_path)

    def copy_sensor_file_to_cuckoo(self, sensor_path, target_dir):
        """Copy the sensor file at the given path to the cuckoo sensor
        directory.

        Keyword arguments:
            interval -- interval between pollings in ms.
        """

        # clean the directory first
        self.clean_directory(target_dir)

        shutil.copy(sensor_path, target_dir)

    def notify_load(self):
        load = get_system_load()
        log.info("load: " + str(load))

        try:
            self.hermes.notify_node_load(self.id, load)
        except ApiError, e:
            # log.error(e.msg)
            raise HermesError(str(e))
        except RequestError, e:
            # log.error(e.msg)
            raise HermesError(str(e))
        except ConnectionError, e:
            raise HermesError(str(e))

    def notify_load_loop(self):
        polling_delay = get_polling_delay_it()
        while True:
            time.sleep(polling_delay.next())

            try:
                self.notify_load()
                polling_delay = get_polling_delay_it()
            except HermesError, e:
                log.error("error in notify_load_loop: " + e.msg)

    def update_node_state_online(self):
        self.hermes.update_node_state(self.id, self.hermes.NODE_STATE_ONLINE)

    def update_node_state_offline(self):
        self.hermes.update_node_state(self.id, self.hermes.NODE_STATE_OFFLINE)

    def update_node_state_failure(self):
        self.hermes.update_node_state(self.id, self.hermes.NODE_STATE_FAILURE)

    def cleanup_cuckoo(self, db_dir, analyses_dir):
        """Deletes cuckoo files and folders that are left from prior
        startups."""
        self.clean_directory(db_dir)
        self.clean_directory(analyses_dir)

    def stop(self):
        log.info("stopping secretary")
        self.is_interrupted = True

    def clean_temp_files(self):
        self.clean_directory(self.download_dir)
        self.clean_directory(self.binaries_dir)

    def run(self):
        """Run secretary forever!"""

        while not self.is_interrupted:
            self.clean_temp_files()
            self.poll_jobs_loop()
            self.fail_jobs()
            self.submit_jobs()
            self.poll_cuckoo_results_loop(10)

        self._mt.abort()


def do_drop_privileges(user_name='cuckoo', group_name='cuckoo'):
    """
    Drop privileges of the current process.

    Keyword arguments:
        user_name -- name of the user the process should run with (default is 'cuckoo')
        group_name -- name of the group the process should run with (default is 'cuckoo')

    Return values:
        False -- if any operation fails
        True -- if group and user is successfully set
    """
    try:
        user = pwd.getpwnam(user_name)
        group = grp.getgrnam(group_name)

        # set the user and group of current process
        os.setuid(user.pw_uid)
        os.setgid(group.gr_gid)
        # check if current process's group and user is set correctly
        if (os.getuid() != user.pw_uid) and (os.getgid() != group.gr_gid):
            return False
        else:
            return True

    except KeyError as e:
        log.error(e)
        return False
    except OSError as e:
        log.error(e)
        return False


def main():
    log.info("starting secretary \(^-^)/")

    # if not do_drop_privileges():
    #     log.error("Terminating process...")
    #     sys.exit(1)

    try:
        secretary = Secretary()

        # start notify loop in separate thread
        thread.start_new_thread(secretary.notify_load_loop, ())

        def sigint_handler(signum, frame):
            secretary.stop()

        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)

        secretary.update_node_state_online()
        secretary.run()
        secretary.update_node_state_offline()

    except BaseException, e:
        log.error(str(traceback.format_exc()))
        secretary.update_node_state_failure()
        secretary._mt.abort()
        sys.exit(e)

if __name__ == "__main__":
    main()
