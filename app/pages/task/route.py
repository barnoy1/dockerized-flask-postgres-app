
"""General page routes."""
from app.database.models import TaskRequest

from flask import Blueprint, redirect, url_for, send_from_directory
from flask import current_app as app
from flask import render_template
from flask_login import login_required, current_user
# from ..api import fetch_data, fetch_dropbox_project_list
from app.consts import TaskStatus
    
# Blueprint Configuration
task_bp = Blueprint(
    "task_bp",
    __name__,
    template_folder="templates",  # Points to "task/templates"
    static_folder="../static"     # Points to the root-level "static" folder
)


@task_bp.route('/js/<path:filename>')
def custom_js(filename):
    """Serve JavaScript files from the task/templates directory."""
    return send_from_directory('pages/task/templates', filename)



@task_bp.route("/task/invoke/<string:process>", methods=['GET', 'POST'])
def invoke_task(process):
    from app.config import Config
    proc_data = [proc_data for proc_data in Config.PROCESS_MAPPING 
                         if proc_data.name == process]
    # do nothing
    if len(proc_data) == 0: return redirect(url_for('home_bp.home'))
    proc_data = proc_data[0]
    
    from utilities.process.command import Command
    command = Command(conf_file=proc_data.config_file,
                      entry_point=proc_data.entry_point,
                      name=proc_data.name)
    
    from app.utilities.process.scheduler import Scheduler
    scheduler = Scheduler.instance()
    scheduler.invoke_process_task(command)
    return redirect(url_for('home_bp.home'))

@task_bp.route("/task/cancel/<string:id>",  methods=['GET', 'POST'])
def cancel_job(task_id):
    """cancel job."""
    from app.utilities.process.scheduler import Scheduler
    dispatcher = Scheduler.instance()
    dispatcher.stop_task(task_id)
    return redirect(url_for('home_bp.home'))


@task_bp.route("/task/console/<string:id>", methods=['GET'])
def get_log_content(id):
    """log content."""
    from ..api import fetch_log_content
    file_content = fetch_log_content(id)
    conv = Ansi2HTMLConverter(dark_bg=False, scheme="solarized", markup_lines=True)
    headers = conv.produce_headers()
    content = conv.convert(file_content, full=False)
    content = '<pre class="ansi2html-content">{}</pre>'.format(content)
    
    # if job is not completed load page with refersh cycle
    job = TaskRequest.query.get(int(id))
    if job.status == TaskStatus.IN_PROGRESS: 
        content += '<script type="text/javascript"> window.setTimeout( function() { window.location.reload(); console.log("refresh"); }, 1000 * 60); </script>'
    file_content = headers + content
    return file_content