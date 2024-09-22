

import datetime
from venv import logger
from app.consts import TaskStatus
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Time
from flask_login import UserMixin
from sqlalchemy.schema import Sequence

db = SQLAlchemy()

class Status(object):
    PENDING = 'pending'
    IN_PROGRESS = 'in progress'
    CANCELED = 'canceled'
    FAILED = 'failed'
    COMPLETED = 'completed'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

   
class TaskRequest(db.Model):
    __tablename__ = 'task_request_api'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), index=True)
    cmd = db.Column(db.String(100), index=True)
    status = db.Column(db.String(100), default=Status.PENDING, nullable=False)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)
    duration = db.Column(Time, default=None, nullable=True)
    
    def __init__(self, task_id, command):
        self.id = task_id
        self.usr_email = command.name
        self.cmd = command.build()
    
    def clear_open_job_request():
        # remove pending or in progress for now
        query = TaskRequest.query
        query = query.filter(db.or_(
                TaskRequest.status.like(f'in progress'),
                TaskRequest.status.like(f'pending'),
            ))
        if query.count() > 0:
            db_data = [TaskRequest.to_dict() for TaskRequest in query]
            for d in db_data:
                job = TaskRequest.query.get(int(d['id']))
                db.session.delete(job)
                db.session.commit()
                
    def to_dict(self):
        
        try:
            # calculate elapsed time if job is still running depends on job status
            if self.status == Status.PENDING:
                elapsed_time_or_duration = '00:00:00'
            elif self.status == Status.IN_PROGRESS:
                from ..api import calc_elapsed_time
                elapsed_time_or_duration =  calc_elapsed_time(self.created_date)
            elif self.status == Status.CANCELED and self.duration is None: 
                elapsed_time_or_duration = '-'
            else:
                elapsed_time_or_duration = self.duration.strftime("%H:%M:%S")
                
            return {
                'id': f'{self.id}',
                'process_name': self.project,
                'status': self.status,
                'created_date': self.created_date,
                'duration': elapsed_time_or_duration
            }
        except Exception as e:
            logger.error(f'error while processing job id {self.id}:\n{e}')
            