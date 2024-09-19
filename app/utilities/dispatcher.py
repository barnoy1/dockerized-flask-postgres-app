import subprocess
import threading

import sys
import time
import uuid
import yaml

import logging
logger = logging.getLogger('app_logger')

# Define constants for task status
class TaskStatus:
    COMPLETE = "complete"
    CANCELED = "canceled"
    ERROR = "error"

# Define the StoppableThread class
class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, task_id, target, callback, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self._target = target
        self._callback = callback
        self.task_id = task_id

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    
    def run(self):
        try:
            while not self.stopped():
                self._target()
                break  # Run the target function once and then break the loop
        except Exception as e:
            logger.error(f"Thread encountered an error for task {self.task_id}: {e}")
            self._callback(TaskStatus.ERROR, str(e))
        finally:
            # Call the callback based on whether the task was stopped or completed
            if self.stopped():
                self._callback(TaskStatus.CANCELED)
            else:
                self._callback(TaskStatus.COMPLETE)

# Define the Command class
class Command:
    def __init__(self, conf_file, id, script_path, exec='python3'):
        self.exec = exec
        self.conf_file = conf_file
        self.id = id
        self.script_path = script_path
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

# Dispatcher class that handles running multiple tasks in stoppable threads
class Dispatcher:
    def __init__(self):
        self.threads = {}  # Dictionary to track live tasks

    def run_task(self, command_obj, callback):
        """Starts a new task in a stoppable thread."""
        task_id = str(uuid.uuid4())[:8]  # Generate a unique ID for each task
        command = command_obj.build()  # Get the constructed command from the Command object

        def task():
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            try:
                while True:
                    if self.threads[task_id].stopped():
                        process.terminate()
                        callback(task_id, TaskStatus.CANCELED)
                        return

                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        logger.info(f"[Task {task_id}][{command_obj.id}] {output.strip()}")
                        sys.stdout.flush()

                    error = process.stderr.readline()
                    if error:
                        logger.error(f"[Task {task_id}] {error.strip()}")
                        sys.stderr.flush()

            finally:
                process.stdout.close()
                process.stderr.close()

            exit_code = process.wait()
            if exit_code == 0:
                callback(task_id, TaskStatus.COMPLETE)
            else:
                callback(task_id, TaskStatus.ERROR, f"Exit code: {exit_code}")


        # Wrapped callback to remove task after completion
        wrapped_callback = self._on_task_end(callback, task_id)
        thread = StoppableThread(task_id=task_id, target=task, callback=wrapped_callback)
        self.threads[task_id] = thread
        thread.start()
        return task_id

    def stop_task(self, task_id):
        """Stops a task based on its task ID."""
        if task_id in self.threads and self.threads[task_id].is_alive():
            self.threads[task_id].stop()

    def stop_all_tasks(self):
        """Stops all running tasks."""
        for task_id in list(self.threads.keys()):
            self.stop_task(task_id)

    def _on_task_end(self, callback, task_id):
        """Callback wrapper to remove tasks from the threads dictionary when finished."""
        def wrapper(status, message=None):
            callback(task_id, status, message)
            # Remove task from live tasks once it has completed or stopped
            if task_id in self.threads:
                del self.threads[task_id]

        return wrapper

    def get_live_tasks(self):
        """Returns a list of currently running task IDs."""
        return list(self.threads.keys())

# Example callback function
def task_callback(task_id, status, message=None):
    if status == TaskStatus.COMPLETE:
        logger.info(f"Task {task_id} completed successfully.")
    elif status == TaskStatus.CANCELED:
        logger.info(f"Task {task_id} was canceled.")
    elif status == TaskStatus.ERROR:
        logger.error(f"Task {task_id} encountered an error: {message}")

# Example usage
if __name__ == "__main__":
    logger.basicConfig(level=logger.INFO, format='%(message)s', stream=sys.stdout)

    # Create dispatcher
    dispatcher = Dispatcher()

    # Create Command object
    command_a = Command(
        conf_file="conf.yaml",
        identifier="command_a",
        script_path="/path/to/process_a.py"
    )

    # Start a task
    task_id = dispatcher.run_task(command_a, task_callback)

    # List live tasks
    logger.info(f"Live tasks: {dispatcher.get_live_tasks()}")

    # Stop the task after 3 seconds (for demonstration purposes)
    time.sleep(3)
    dispatcher.stop_task(task_id)

    # List live tasks after stopping task
    logger.info(f"Live tasks after stopping task: {dispatcher.get_live_tasks()}")

    # Wait to ensure any remaining tasks complete
    time.sleep(10)

    # List live tasks after all tasks complete
    logger.info(f"Live tasks after all tasks: {dispatcher.get_live_tasks()}")
