
"""General page routes."""
from flask import Blueprint, redirect, url_for, send_from_directory
from flask import current_app as app
from flask import render_template
from flask_login import login_required, current_user
# from ..api import fetch_data, fetch_dropbox_project_list


# Blueprint Configuration
job_bp = Blueprint(
    "job_bp",
    __name__,
    template_folder="templates",  # Points to "home/templates"
    static_folder="../static"     # Points to the root-level "static" folder
)

@job_bp.route('/js/<path:filename>')
def custom_js(filename):
    """Serve JavaScript files from the home/templates directory."""
    return send_from_directory('pages/home/templates', filename)


@job_bp.route("/job/<int:id>/cancel/",  methods=['GET', 'POST'])
def cancel_job(task_id):
    """cancel job."""
    from ...utilities.dispatcher import Dispatcher
    dispatcher = Dispatcher.instance()
    dispatcher.stop_task(task_id)
    return redirect(url_for('home_bp.home'))


@job_bp.route("/job/<int:id>/console", methods=['GET'])
def get_log_content(id):
    """log content."""
    from ..api import fetch_log_content
    file_content = fetch_log_content(id)
    conv = Ansi2HTMLConverter(dark_bg=False, scheme="solarized", markup_lines=True)
    headers = conv.produce_headers()
    content = conv.convert(file_content, full=False)
    content = '<pre class="ansi2html-content">{}</pre>'.format(content)
    
    # if job is not completed load page with refersh cycle
    job = JobRequest.query.get(int(id))
    if job.status == Status.IN_PROGRESS: 
        content += '<script type="text/javascript"> window.setTimeout( function() { window.location.reload(); console.log("refresh"); }, 1000 * 60); </script>'
    file_content = headers + content
    return file_content