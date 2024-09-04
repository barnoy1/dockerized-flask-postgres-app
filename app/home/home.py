
"""General page routes."""
from flask import Blueprint, redirect, url_for
from flask import current_app as app
from flask import render_template
from flask_login import login_required, current_user
# from ..api import fetch_data, fetch_dropbox_project_list

# Blueprint Configuration
home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates", static_folder="static"
)


@home_bp.route("/", methods=["GET", "POST"])
def home():
    """Homepage."""
    curr_user_name = 'Guest' if current_user.is_anonymous else current_user.name
    # project_name_list = fetch_dropbox_project_list()
    return render_template(
        "index.jinja2",
        title="Application Name",
        subtitle="scan images for cancer data",
        template="home-template",
        curr_user_name=curr_user_name,
        project_name_list=['project_name_1', 'project_name_2']
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
