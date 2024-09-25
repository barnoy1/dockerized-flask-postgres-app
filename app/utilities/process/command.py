     
     
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

from app.utilities.conf.slconfig import SLConfig
from app.utilities.decorators import Singleton
from app import logger

class Command:
    def __init__(self, conf_file, entry_point, command_name=None, exec='python3'):
        self.exec = exec
        self.conf_file = conf_file
        self.name = command_name
        self.entry_point = entry_point
        if conf_file:
            self.cfg = SLConfig.fromfile(conf_file)  # Load YAML configuration using SLConfig

    def _parse_section_kvp_to_command_str(self, kvp):
        cmd_segment = []
        for key, value in kvp.items():
            if isinstance(value, list):
                # If the parameter is a list, join the values with a space
                cmd_segment.append(f"--{key}")
                cmd_segment.extend(map(str, value))  # Add each list element as a separate argument
            else:
                # Otherwise, treat it as a single value
                cmd_segment.append(f"--{key}")
                cmd_segment.append(str(value))
        return cmd_segment
    
    def _parse_section_list_to_command_str(self, flags):
        cmd_segment = []
        return [f'{--f}' for f in flags] 
        
    def build(self):
        """Constructs the full command by injecting parameters from the YAML file."""
        command = [self.exec, self.entry_point]  # Start with the script path

        # Access the 'globals' section from self.cfg
        globals_config = self.cfg.get('globals', {})
        paths = globals_config.get('paths', {})
        sub_commands = globals_config.get('sub_commands', {})

        
        # Handle paths in the same way, considering list 
        command += self._parse_section_kvp_to_command_str(paths)
        
        
        # Find the matching subcommand from the 'sub_commands' section using the 'name'
        if self.name in sub_commands:
            sub_command_parser = sub_commands[self.name]

            command += [self.name]
            
            # Extract the specific configurations for the command
            configurations = sub_command_parser.get('configurations', {})
            command += self._parse_section_kvp_to_command_str(configurations)
            
            # Extract parameters for the subcommand
            parameters = sub_command_parser.get('parameters', {})
            command += self._parse_section_kvp_to_command_str(parameters)
            
            # Extract flags for the subcommand
            flags = sub_command_parser.get('flags', {})
            command +=  [f'--{flag}' for flag in flags] 
            
        return command
