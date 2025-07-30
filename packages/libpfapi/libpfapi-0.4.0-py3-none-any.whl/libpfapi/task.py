import logging
import time

P_OK = 'SUCCESS'
P_FAIL = 'FAILURE'
P_ERROR = 'ERROR'
P_WARNING = 'WARNING'
P_RUNNING = 'RUNNING'
P_QUEUED = 'QUEUED'
P_UNKNOWN = 'UNKNOWN'
POLL_TIME = 5


class Task:
    """
        A task instance follows the status of a given pathfinder server task

        A task only holds information on current status alongside a small plain
        text message on which step is running right now.
    """
    def __init__(self, tid, api):
        """
            Create a Task reference.

            :param tid: Server task ID
            :param api: `libpfapi.api.API` instance to know where to connect.
        """
        self.msg = None
        self.task_id = tid
        self._api = api
        self._last_updated = None
        self.status = None
        self._raw = None

    def get_message(self):
        """
            Retrieve current message on the task

            ..note:
                This is updated every 5 seconds.  So calling it multiple times
                in a row will simply return a cached value
        """
        return self.msg

    def get_status(self):
        """
            Retrieve current status of the task.

            ..note:
                This is updated every 5 seconds.  So calling it multiple times
                in a row will simply return a cached value
        """
        # if first time, or sufficient polling time passed, get new status
        ctime = time.time()
        if self._last_updated is None or ctime - self._last_updated > POLL_TIME:
            self._raw = self._api.get_progress(self.task_id)

        self.status = self._raw.get('state', P_UNKNOWN)
        self.msg = self._raw.get('details', P_UNKNOWN)
        return self.status

    def cancel(self):
        """
            Call Pathfinder API to stop the current task
        """
        self._api.cancel_task(self.task_id)

    def wait_till_finished(self, cancel_callback=None):
        """
            Block the running thread in a loop until the task has finished in
            the server

            param: cancel_callback: function to be called to check cancellation
                                    state. Should return a Boolean.
        """
        while True:
            if cancel_callback and cancel_callback():
                self.cancel()
                break
            self.get_status()
            if self.status not in [P_OK, P_FAIL, P_ERROR, P_WARNING]:
                logging.info('Task state %s, waiting %ss --> %s', self.status, POLL_TIME, self.msg)
                time.sleep(POLL_TIME)
            else:
                logging.info('Task finished with state: %s', self.status)
                break

    @property
    def success(self):
        return self.status in [P_OK, P_WARNING]

    @property
    def has_warning(self):
        return self.status == P_WARNING

    @property
    def failure(self):
        return self.status not in [P_RUNNING, P_QUEUED, P_OK, P_WARNING]

    @property
    def running(self):
        return self.status in [P_RUNNING, P_QUEUED]
