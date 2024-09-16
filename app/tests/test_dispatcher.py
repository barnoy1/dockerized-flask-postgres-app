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
            'command_a': {
                'arg1': 'value1',
                'arg2': 'value2'
            },
            'command_b': {
                'arg3': 'value3',
                'arg4': 'value4'
            }
        }
        yaml.dump(config, temp_file)
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def mock_script():
    script_content = """
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
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
        temp_file.write(script_content)
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def dispatcher():
    return Dispatcher()

def test_command_load_config(temp_config_file):
    command = Command(temp_config_file, 'command_a', 'mock_script.py')
    assert command.config == {'arg1': 'value1', 'arg2': 'value2'}

def test_command_build_command(temp_config_file, mock_script):
    command = Command(temp_config_file, 'command_a', mock_script)
    expected = [mock_script, '--arg1', 'value1', '--arg2', 'value2']
    assert command.build_command() == expected

@pytest.mark.parametrize("process_key, expected", [
    ('command_a', ['--arg1', 'value1', '--arg2', 'value2']),
    ('command_b', ['--arg3', 'value3', '--arg4', 'value4'])
])
def test_multiple_commands(temp_config_file, mock_script, process_key, expected):
    command = Command(temp_config_file, process_key, mock_script)
    assert command.build_command() == [mock_script] + expected

def test_run_task(dispatcher, temp_config_file, mock_script):
    command = Command(temp_config_file, 'command_a', mock_script)
    callback = lambda task_id, status, message=None: None

    task_id = dispatcher.run_task(command, callback)

    # Wait for the task to complete
    start_time = time.time()
    while task_id in dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert task_id not in dispatcher.threads

def test_stop_task(dispatcher, temp_config_file, mock_script):
    command = Command(temp_config_file, 'command_a', mock_script)
    callback = lambda task_id, status, message=None: None

    task_id = dispatcher.run_task(command, callback)
    time.sleep(0.2)  # Let the task run for a bit
    dispatcher.stop_task(task_id)

    # Wait for the task to be stopped
    start_time = time.time()
    while task_id in dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert task_id not in dispatcher.threads

def test_get_live_tasks(dispatcher, temp_config_file, mock_script):
    command_a = Command(temp_config_file, 'command_a', mock_script)
    command_b = Command(temp_config_file, 'command_b', mock_script)
    callback = lambda task_id, status, message=None: None

    task_id_a = dispatcher.run_task(command_a, callback)
    task_id_b = dispatcher.run_task(command_b, callback)

    time.sleep(0.2)  # Let the tasks start

    live_tasks = dispatcher.get_live_tasks()
    assert set(live_tasks) == {task_id_a, task_id_b}

    dispatcher.stop_all_tasks()

def test_stoppable_thread():
    def target():
        time.sleep(0.2)

    callback = lambda status, message=None: None

    thread = StoppableThread('test_task', target, callback)
    thread.start()
    thread.join()

    assert not thread.is_alive()

def test_stoppable_thread_stop():
    def target():
        time.sleep(0.5)

    callback = lambda status, message=None: None

    thread = StoppableThread('test_task', target, callback)
    thread.start()
    time.sleep(0.1)
    thread.stop()
    thread.join()

    assert not thread.is_alive()

def test_run_multiple_tasks(dispatcher, temp_config_file, mock_script):
    command_a = Command(temp_config_file, 'command_a', mock_script)
    command_b = Command(temp_config_file, 'command_b', mock_script)
    callback = lambda task_id, status, message=None: None

    task_id_a = dispatcher.run_task(command_a, callback)
    task_id_b = dispatcher.run_task(command_b, callback)

    time.sleep(0.2)  # Let the tasks start

    assert len(dispatcher.get_live_tasks()) == 2

    dispatcher.stop_all_tasks()

    # Wait for tasks to be stopped
    start_time = time.time()
    while dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert len(dispatcher.threads) == 0

def test_stop_all_tasks(dispatcher, temp_config_file, mock_script):
    command_a = Command(temp_config_file, 'command_a', mock_script)
    command_b = Command(temp_config_file, 'command_b', mock_script)
    callback = lambda task_id, status, message=None: None

    dispatcher.run_task(command_a, callback)
    dispatcher.run_task(command_b, callback)

    time.sleep(0.2)  # Let the tasks start

    dispatcher.stop_all_tasks()

    # Wait for tasks to be stopped
    start_time = time.time()
    while dispatcher.threads and time.time() - start_time < 5:
        time.sleep(0.1)

    assert len(dispatcher.threads) == 0