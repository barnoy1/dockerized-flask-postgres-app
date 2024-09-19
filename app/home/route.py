
"""General page routes."""
from flask import Blueprint, redirect, url_for, send_from_directory
from flask import current_app as app
from flask import render_template
from flask_login import login_required, current_user
# from ..api import fetch_data, fetch_dropbox_project_list

# Blueprint Configuration
home_bp = Blueprint(
    "home_bp",
    __name__,
    template_folder="templates",  # Points to "home/templates"
    static_folder="../static"     # Points to the root-level "static" folder
)

@home_bp.route('/js/<path:filename>')
def custom_js(filename):
    """Serve JavaScript files from the home/templates directory."""
    return send_from_directory('home/templates', filename)


@home_bp.route("/", methods=["GET", "POST"])
def home():
    """Homepage."""
    curr_user_name = 'Guest' if current_user.is_anonymous else current_user.name
    return render_template(
        "index.jinja2",
        title="Application Name",
        user_name=curr_user_name
    )


@home_bp.route("/api/job/log/<string:id>", methods=["GET", "POST"])
def job_log(id):
    """Homepage."""
    return redirect(url_for('auth_bp.login'))
    

@home_bp.route("/web/data", methods=["GET"])
def get_data():
    """Dashboard."""
    job_data = fetch_data()
    return job_data
