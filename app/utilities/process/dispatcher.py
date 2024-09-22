
import subprocess
import threading
import sys
import time
import uuid
import yaml
import logging
import os
import signal
import io

import threading
import os
import signal
import logging

from app.utilities.decorators import Singleton
logger = logging.getLogger('app_logger')
from app.utilities.process.stoppable_thread import StoppableThread

@Singleton
class Dispatcher:
    def __init__(self):
        self.threads = {}

    def run_task(self, command_obj, callback):
        task_id = str(uuid.uuid4())[:8]
        command = command_obj.build()

        def task():
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                preexec_fn=os.setsid if sys.platform != "win32" else None
            )

            return process

        wrapped_callback = self._on_task_end(callback, task_id, command)
        thread = StoppableThread(task_id=task_id, command=command_obj, target=task, callback=wrapped_callback)
        self.threads[task_id] = thread
        thread.start()
        return task_id

    def stop_task(self, task_id):
        if task_id in self.threads and self.threads[task_id].is_alive():
            self.threads[task_id].stop()
            self.threads[task_id].join(timeout=5)  # Wait for the thread to finish
            if task_id in self.threads:
                del self.threads[task_id]

    def stop_all_tasks(self):
        for task_id in list(self.threads.keys()):
            self.stop_task(task_id)

    def _on_task_end(self, callback, task_id, command):
        def wrapper(status, message=None):
            callback(task_id, command, status, message)
            if task_id in self.threads:
                del self.threads[task_id]
        return wrapper

    def get_live_tasks(self):
        return list(self.threads.keys())
