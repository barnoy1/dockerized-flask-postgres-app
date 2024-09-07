import subprocess
import threading
import logging
import sys
import time
import uuid

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
            if not self.stopped():
                self._target()
        except Exception as e:
            logging.error(f"Thread encountered an error for task {self.task_id}: {e}")
            self._callback(self.task_id, TaskStatus.ERROR, str(e))

# Dispatcher class that handles running multiple tasks in stoppable threads
class Dispatcher:
    def __init__(self):
        self.threads = {}  # Dictionary to track live tasks

    def run_task(self, command, callback):
        """Starts a new task in a stoppable thread."""
        task_id = str(uuid.uuid4())  # Generate a unique ID for each task

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
                    # Check if the thread is stopped
                    if self.threads[task_id].stopped():
                        process.terminate()
                        callback(task_id, TaskStatus.CANCELED)
                        return

                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        logging.info(f"[Task {task_id}] {output.strip()}")
                        sys.stdout.flush()

                    error = process.stderr.readline()
                    if error:
                        logging.error(f"[Task {task_id}] {error.strip()}")
                        sys.stderr.flush()

            finally:
                process.stdout.close()
                process.stderr.close()

            exit_code = process.wait()
            if exit_code == 0:
                callback(task_id, TaskStatus.COMPLETE)
            else:
                callback(task_id, TaskStatus.ERROR, f"Exit code: {exit_code}")

        # Create a stoppable thread with the task and start it
        thread = StoppableThread(task_id=task_id, target=task, callback=self._on_task_end(callback, task_id))
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
        logging.info(f"Task {task_id} completed successfully.")
    elif status == TaskStatus.CANCELED:
        logging.info(f"Task {task_id} was canceled.")
    elif status == TaskStatus.ERROR:
        logging.error(f"Task {task_id} encountered an error: {message}")

# Example usage with multiple mock commands
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)

    # Create dispatcher
    dispatcher = Dispatcher()

    # Mock commands to simulate output and delays
    command1 = ["python3", "-c", "import time; [print(f'Output 1, line {i}') or time.sleep(1) for i in range(5)]"]
    command2 = ["python3", "-c", "import time; [print(f'Output 2, line {i}') or time.sleep(1) for i in range(7)]"]

    # Start two tasks
    task_id_1 = dispatcher.run_task(command1, task_callback)
    task_id_2 = dispatcher.run_task(command2, task_callback)

    # List live tasks
    logging.info(f"Live tasks: {dispatcher.get_live_tasks()}")

    # Stop the first task after 3 seconds (for demonstration purposes)
    time.sleep(3)
    dispatcher.stop_task(task_id_1)

    # List live tasks after stopping task 1
    logging.info(f"Live tasks after stopping task 1: {dispatcher.get_live_tasks()}")

    # Let the second task complete
    time.sleep(10)

    # List live tasks after all tasks complete
    logging.info(f"Live tasks after all tasks: {dispatcher.get_live_tasks()}")
