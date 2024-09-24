import pytest
import tempfile
import os
import time
import yaml
from app.consts import TaskStatus
from app.utilities.process.command import Command 
from app.utilities.process.dispatcher import Dispatcher
import logging

logger = logging.getLogger('app_logger')

# Mock YAML config based on your provided structure
@pytest.fixture(scope='module')
def temp_config_file():
    config = {
        'globals': {
            'paths': {
                'path1': 'path/to/dir1',
                'path2': ['path/to/dir2', 'path/to/dir3']
            },
            'sub_commands': {
                'command_a': {
                    'configurations': {
                        'cmd_resouce_path': '/path/to/cmd_a/resource'
                    },
                    'parameters': {
                        'num_of_threads': 3,
                        'transparency': 0.4,
                        'options': ['a', 'b']
                    },
                    'flags': ['save_images', 'use_aug']
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml', delete=False) as temp_file:
        yaml.dump(config, temp_file)
        config_file_path = temp_file.name
    
    yield config_file_path
    os.unlink(config_file_path)


# Mock Python script that uses arguments from the configuration file
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
        entry_point = temp_file.name

    # Set executable permissions on the mock script
    os.chmod(entry_point, 0o777)  # Add execute permissions

    yield entry_point

    # Clean up the temporary file after the test
    os.unlink(entry_point)


@pytest.fixture
def dispatcher():
    return Dispatcher.instance()

# Example callback function
def task_test_callback(task_id, command, status, message=None):
    if status == TaskStatus.COMPLETED:
        logger.info(f"Task {task_id} completed custom mock postprocessing callback.")
    elif status == TaskStatus.CANCELED:
        logger.info(f"Task {task_id} canceled custom mock postprocessing callback")
    elif status == TaskStatus.ERROR:
        logger.error(f"Task {task_id} error custom mock postprocessing callback.\ninput error message: {message}")


# Tests
def test_run_task(dispatcher, temp_config_file, mock_script):
    
    command = Command(conf_file=temp_config_file, 
                      command_name='command_a', 
                      entry_point=mock_script, 
                      exec='python3')
    
    callback = task_test_callback
    task_id = dispatcher.run_task(command, callback)

    # Wait for the task to complete using join
    thread = dispatcher.threads[task_id]
    thread.join()  # Wait for the task thread to complete

    assert task_id not in dispatcher.threads
    

def test_stop_task(dispatcher, temp_config_file, mock_script):
    command = Command(temp_config_file, 'command_a', mock_script)
    callback = task_test_callback

    task_id = dispatcher.run_task(command, callback)
    time.sleep(0.2)  # Let the task run for a bit
    dispatcher.stop_task(task_id)

    # Wait for the task to be stopped
    start_time = time.time()
    while task_id in dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert task_id not in dispatcher.threads


def test_run_multiple_tasks(dispatcher, temp_config_file, mock_script):
    python_cmd = Command(temp_config_file, 'command_a', mock_script)
    callback = task_test_callback

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
    python_cmd1 = Command(temp_config_file, 'command_a', mock_script)
    python_cmd2 = Command(temp_config_file, 'command_a', mock_script)
    callback = task_test_callback

    dispatcher.run_task(python_cmd1, callback)
    dispatcher.run_task(python_cmd2, callback)

    time.sleep(0.2)  # Let the tasks start

    dispatcher.stop_all_tasks()

    # Wait for tasks to be stopped
    start_time = time.time()
    while dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert len(dispatcher.threads) == 0
