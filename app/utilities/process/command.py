     
     
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


class Command:
    def __init__(self, conf_file, name, entry_point, exec='python3'):
        self.exec = exec
        self.conf_file = conf_file
        self.name = name
        self.entry_point = entry_point
        if conf_file:
            self.config = self.load_config()

    def load_config(self):
        """Loads YAML configuration file and extracts parameters for the command."""
        with open(self.conf_file, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def build(self):
        """Constructs the full command by injecting parameters from the YAML file."""
        command = [self.exec] + [self.entry_point]  # Start with the script path

        # Iterate over configuration parameters and inject them into the command
        for key, value in self.config.items():
            command.append(f"--{key}")
            command.append(str(value))

        return command
