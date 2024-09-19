
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