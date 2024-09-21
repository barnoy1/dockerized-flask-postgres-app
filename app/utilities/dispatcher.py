
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

from app.utilities.decorators import Singleton
logger = logging.getLogger('app_logger')

class TaskStatus:
    COMPLETE = "complete"
    CANCELED = "canceled"
    ERROR = "error"
import threading
import os
import signal
import logging
class StoppableThread(threading.Thread):
    def __init__(self, task_id, target, callback, command=None, capture_std=False, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self._target = target
        self._callback = callback
        self.task_id = task_id
        self.command = command
        self.process = None
        self.capture_std = capture_std
        
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
            result = self._target()
            if isinstance(result, subprocess.Popen):
                self.process = result
            else:
                # If the target doesn't return a process, we'll consider it complete
                self._callback(TaskStatus.COMPLETE)
                return

            if self.command is None:
                self.command = Command(conf_file=None, id='', script_path='', exec='')
            
            while self.process.poll() is None:
                if self.stopped():
                    self.stop()
                    break
                
                # Read output and error streams
                if self.capture_std:
                    output = self.process.stdout.readline()
                    if output:
                        logger.info(f"[Task {self.task_id}][{self.command.id}] {output.strip()}")
                    
                    error = self.process.stderr.readline()
                    if error:
                        logger.error(f"[Task {self.task_id}][{self.command.id}] {error.strip()}")
                    
                time.sleep(0.1)
            
            # Read any remaining output
            if self.capture_std and self.process:
                output, error = self.process.communicate()
                if output:
                    logger.info(f"[Task {self.task_id}][{self.command.id}] {output.strip()}")
                if error:
                    logger.error(f"[Task {self.task_id}][{self.command.id}] {error.strip()}")
            
            if self.process:
                exit_code = self.process.returncode
                
                if self.stopped():
                    logger.info(f"[Task {self.task_id}][{self.command.id}] status - {TaskStatus.CANCELED}")
                    self._callback(TaskStatus.CANCELED)
                elif exit_code == 0:
                    logger.info(f"[Task {self.task_id}][{self.command.id}] status - {TaskStatus.COMPLETE}")
                    self._callback(TaskStatus.COMPLETE)
                else:
                    logger.error(f"[Task {self.task_id}][{self.command.id}] status - {TaskStatus.ERROR}")
                    self._callback(TaskStatus.ERROR, f"Exit code: {exit_code}")
            else:
                # If there's no process, consider it complete
                self._callback(TaskStatus.COMPLETE)
        except Exception as e:
            logger.error(f"Thread encountered an error for [Task {self.task_id}]: {e}")
            self._callback(TaskStatus.ERROR, str(e))
            
class Command:
    def __init__(self, conf_file, id, script_path, exec='python3'):
        self.exec = exec
        self.conf_file = conf_file
        self.id = id
        self.script_path = script_path
        if conf_file:
            self.config = self.load_config()

    def load_config(self):
        """Loads YAML configuration file and extracts parameters for the command."""
        with open(self.conf_file, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def build(self):
        """Constructs the full command by injecting parameters from the YAML file."""
        command = [self.exec] + [self.script_path]  # Start with the script path

        # Iterate over configuration parameters and inject them into the command
        for key, value in self.config.items():
            command.append(f"--{key}")
            command.append(str(value))

        return command

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

        wrapped_callback = self._on_task_end(callback, task_id)
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

    def _on_task_end(self, callback, task_id):
        def wrapper(status, message=None):
            callback(task_id, status, message)
            if task_id in self.threads:
                del self.threads[task_id]
        return wrapper

    def get_live_tasks(self):
        return list(self.threads.keys())

# Example callback function
def task_callback(task_id, status, message=None):
    if status == TaskStatus.COMPLETE:
        logger.info(f"Task {task_id} completed successfully.")
    elif status == TaskStatus.CANCELED:
        logger.info(f"Task {task_id} was canceled.")
    elif status == TaskStatus.ERROR:
        logger.error(f"Task {task_id} encountered an error: {message}")