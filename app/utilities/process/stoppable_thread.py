
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

from app.consts import TaskStatus
from app.utilities.process.command import Command

from app.utilities.decorators import Singleton
logger = logging.getLogger('app_logger')

class StoppableThread(threading.Thread):
    def __init__(self, task_id, target, callback, command=None, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self._target = target
        self._callback = callback
        self.task_id = task_id
        self.command = command
        self.process = None
        
    def stop(self):
        self._stop_event.set()
        if self.process:
            try:
                if sys.platform != "win32":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
            except ProcessLookupError:
                pass  # Process already terminated

    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        try:
            process = self._target()
            if isinstance(process, subprocess.Popen):
                self.process = process
            else:
                # If the target doesn't return a process, we'll consider it complete
                self._callback(TaskStatus.COMPLETED)
                return

            
            while self.process.poll() is None:
                if self.stopped():
                    self.stop()
                    break
                
                time.sleep(0.1)
            
            if self.process:
                exit_code = self.process.returncode
                
                if self.stopped():
                    logger.info(f"[Task {self.task_id}][{self.command.id}] status - {TaskStatus.CANCELED}")
                    self._callback(TaskStatus.CANCELED)
                elif exit_code == 0:
                    logger.info(f"[Task {self.task_id}][{self.command.id}] status - {TaskStatus.COMPLETED}")
                    self._callback(TaskStatus.COMPLETED)
                else:
                    logger.error(f"[Task {self.task_id}][{self.command.id}] status - {TaskStatus.ERROR}")
                    self._callback(TaskStatus.ERROR, f"Exit code: {exit_code}")
            else:
                # If there's no process, consider it complete
                self._callback(TaskStatus.COMPLETED)
        except Exception as e:
            logger.error(f"Thread encountered an error for [Task {self.task_id}]: {e}")
            self._callback(TaskStatus.ERROR, str(e))
         