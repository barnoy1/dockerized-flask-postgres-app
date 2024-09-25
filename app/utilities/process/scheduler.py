
import datetime
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
from app.utilities.decorators import Singleton
from app import logger
from app.utilities.process.dispatcher import Dispatcher
from app.database.models import db, TaskRequest
        
@Singleton
class Scheduler(Dispatcher):
    def __init__(self):
        pass
    
    def invoke_process_task(self, command, callback):
        
        # wrap input callback with db operations
        wrapped_callback = self._on_task_end_db(callback, task_id, command)
        task_id = super().run_task(command, wrapped_callback)
        
        # Insert new TaskRequest record in the database using the new task_id
        from app.database.models import db, TaskRequest
        new_task_request = TaskRequest(task_id=task_id, command=command)

        try:
            db.session.add(new_task_request)
            db.session.commit()
            logger.info(f"New task_request {new_task_request.task_id} inserted into the database")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inserting new task_request into database: {e}")
           

    def stop_task(self, task_id):
        super().stop_task(task_id)
        # delete from db
        task_request = self._get_task_request_by_task_id(task_id)
        if task_request:
                self._update_task_request_status(task_request, TaskStatus.CANCELED) 

    def _on_task_end_db(self, callback, task_id, command, task_request):
        def wrapper(status, message=None):
            # Call the callback provided
            callback(task_id, command, status, message)
            # Update task_request status to COMPLETED and commit it to the database
            self._update_task_request_status(task_request, status)
            # Optionally set duration if needed
            task_request.duration = datetime.utcnow() - task_request.created_date
            from app.database.models import db
            db.session.commit()


        return wrapper
    def _update_task_request_status(self, task_request, status):
        
        """Helper function to update task_request status in the database"""
        try:
            task_request.status = status
            db.session.commit()
            logger.info(f"Job {task_request.task_id} updated to status: {status}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating task_request {task_request.task_id} to status {status}: {e}")

    def _get_task_request_by_task_id(self, task_id):
        """Helper function to retrieve a TaskRequest object by task_id"""
        task_request = TaskRequest.query.filter_by(task_id=task_id).first()
        return task_request

    def _clear_open_task_request_request(self):
        """Clear task_requests with status 'pending' or 'in progress'"""
        query = TaskRequest.query.filter(
            db.or_(
                TaskRequest.status.like(f'in progress'),
                TaskRequest.status.like(f'pending')
            )
        )
        if query.count() > 0:
            db_data = [task_request.to_dict() for task_request in query]
            for d in db_data:
                task_request = TaskRequest.query.get(int(d['id']))
                db.session.delete(task_request)
                db.session.commit()
            logger.info(f"Cleared {len(db_data)} open task_request requests.")