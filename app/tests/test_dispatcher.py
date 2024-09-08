import pytest
import time
from app.utilities.dispatcher import Dispatcher


# Mock callback function to capture task results
def mock_callback(task_id, status, message=None):
    print(f"Task {task_id} - Status: {status}, Message: {message}")

@pytest.fixture
def dispatcher():
    """Fixture to provide a Dispatcher instance."""
    return Dispatcher()

def test_run_single_task(dispatcher):
    # Mock command that mimics a short task
    command = ["python3", "-c", "import time; print('Task running'); time.sleep(2); print('Task complete')"]
    
    task_id = dispatcher.run_task(command, mock_callback)
    
    assert task_id in dispatcher.get_live_tasks()
    
    time.sleep(8)  # Wait for task to complete
    
    assert task_id not in dispatcher.get_live_tasks()
    
def test_run_multiple_tasks(dispatcher):
    # Mock commands to simulate output and delays
    command1 = ["python3", "-c", "import time; [print(f'Output 1, line {i}') or time.sleep(1) for i in range(5)]"]
    command2 = ["python3", "-c", "import time; [print(f'Output 2, line {i}') or time.sleep(1) for i in range(7)]"]

    task_id_1 = dispatcher.run_task(command1, mock_callback)
    task_id_2 = dispatcher.run_task(command2, mock_callback)

    live_tasks = dispatcher.get_live_tasks()

    assert task_id_1 in live_tasks
    assert task_id_2 in live_tasks

    time.sleep(8)  # Wait for tasks to complete (ensure task 2 has enough time to finish)

    live_tasks_after = dispatcher.get_live_tasks()

    assert task_id_1 not in live_tasks_after
    assert task_id_2 not in live_tasks_after

def test_stop_task(dispatcher):
    # Mock command that mimics a long-running task
    command = ["python3", "-c", "import time; [print(f'Running') or time.sleep(1) for _ in range(10)]"]

    task_id = dispatcher.run_task(command, mock_callback)

    time.sleep(3)  # Allow the task to run for 3 seconds
    dispatcher.stop_task(task_id)

    assert task_id not in dispatcher.get_live_tasks()
