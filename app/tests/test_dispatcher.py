import logging
import pytest
import tempfile
import os
import time
import yaml
from app.utilities.dispatcher import Command, Dispatcher, TaskStatus, StoppableThread

@pytest.fixture
def temp_config_file():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml', delete=False) as temp_file:
        config = {
            'arg1': 'value1',
            'arg2': 'value2'
        }
        yaml.dump(config, temp_file)
    yield temp_file.name
    os.unlink(temp_file.name)


@pytest.fixture
def mock_script():
    script_content = """
#!/usr/bin/env python3
import sys
import time

def main():
    print(f"Mock script started with arguments: {sys.argv[1:]}")
    try:
        for i in range(10):
            print(f"Processing step {i+1}")
            sys.stdout.flush()  # Ensure output is immediately visible
            time.sleep(0.1)  # Reduced sleep time for faster tests
    except KeyboardInterrupt:
        print("Mock script interrupted")
        sys.exit(1)
    print("Mock script completed successfully")

if __name__ == "__main__":
    main()
    """
    
    # Create the temporary script file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
        temp_file.write(script_content)
        script_path = temp_file.name

    # Set executable permissions on the mock script
    os.chmod(script_path, 0o777)  # Add execute permissions

    yield script_path

    # Clean up the temporary file after the test
    os.unlink(script_path)


@pytest.fixture
def dispatcher():
    return Dispatcher.instance()


def test_run_task(dispatcher, temp_config_file, mock_script):
    command = Command(temp_config_file, 'test_run_task_cmd', mock_script)
    callback = lambda task_id, status, message=None: None
    task_id = dispatcher.run_task(command, callback)

    # Wait for the task to complete using join
    thread = dispatcher.threads[task_id]
    thread.join()  # Wait for the task thread to complete

    assert task_id not in dispatcher.threads
    

def test_stop_task(dispatcher, temp_config_file, mock_script):
    command = Command(temp_config_file, 'test_stop_task_cmd', mock_script)
    callback = lambda task_id, status, message=None: None

    task_id = dispatcher.run_task(command, callback)
    time.sleep(0.2)  # Let the task run for a bit
    dispatcher.stop_task(task_id)

    # Wait for the task to be stopped
    start_time = time.time()
    while task_id in dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert task_id not in dispatcher.threads

def test_run_multiple_tasks(dispatcher, temp_config_file, mock_script):
    python_cmd = Command(temp_config_file, 'test_run_multiple_tasks_cmd', mock_script)
    callback = lambda task_id, status, message=None: None

    task_id_a = dispatcher.run_task(python_cmd, callback)
    task_id_b = dispatcher.run_task(python_cmd, callback)

    
    assert len(dispatcher.get_live_tasks()) == 2

    # Wait for tasks to be stopped
    time.sleep(0.8)
    dispatcher.stop_task(task_id_a)
    
    # Wait for the task to complete using join
    if len(dispatcher.threads) > 0:
        thread = dispatcher.threads[task_id_b]
        thread.join()  # Wait for the task thread to complete

    assert len(dispatcher.get_live_tasks()) == 0

def test_stop_all_tasks(dispatcher, temp_config_file, mock_script):
    python_cmd1 = Command(temp_config_file, 'test_stop_all_tasks_cmd1', mock_script)
    python_cmd2 = Command(temp_config_file, 'test_stop_all_tasks_cmd2', mock_script)
    callback = lambda task_id, status, message=None: None

    dispatcher.run_task(python_cmd1, callback)
    dispatcher.run_task(python_cmd2, callback)

    time.sleep(0.2)  # Let the tasks start

    dispatcher.stop_all_tasks()

    # Wait for tasks to be stopped
    start_time = time.time()
    while dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert len(dispatcher.threads) == 0
