import logging
import os
from flask import Flask, request, jsonify
from app.database.models import db, User

from flask_assets import Environment
from flask_cors import CORS
from flask_login import LoginManager


if os.getenv('FLASK_ENV') == 'development':
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    
app = Flask(__name__,  static_folder="../static")
app.config.from_object('app.config.Config')

CORS(app)

assets = Environment()
assets.init_app(app)

logger = logging.getLogger('my_logger')

with app.app_context():
    
    from .pages.home import route as home_route
    
    # instantiate database
    from .database.models import db, User
    db.init_app(app)
    db.create_all()

    # Register Blueprints
    app.register_blueprint(home_route.home_bp)
    
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
        
        
@app.route('/test', methods=['GET'])
def get_result():
    import logging
    logger.info("This is an info message logged to both console and file.")
    return jsonify({'result': 'ok'})


# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        os.abort(400, description="Invalid input")
    
    name = data['name']
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Read a specific user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user is None:
        os.abort(404, description="User not found")
    return jsonify(user.to_dict())

# Update a user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if user is None:
        os.abort(404, description="User not found")
    if 'name' in data:
        user.name = data['name']
    db.session.commit()
    return jsonify(user.to_dict())

# Delete a user by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        os.abort(404, description="User not found")
    db.session.delete(user)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
