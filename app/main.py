import os
from flask import Flask, request, jsonify
from app.models import db, User

if os.getenv('FLASK_ENV') == 'development':
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    
app = Flask(__name__)
app.config.from_object('app.config.Config')

db.init_app(app)

with app.app_context():
        # Create tables if they don't exist
        db.create_all()

@app.route('/test', methods=['GET'])
def get_result():
    return jsonify({'result': 'ok'})


# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description="Invalid input")
    
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
        abort(404, description="User not found")
    return jsonify(user.to_dict())

# Update a user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if user is None:
        abort(404, description="User not found")
    if 'name' in data:
        user.name = data['name']
    db.session.commit()
    return jsonify(user.to_dict())

# Delete a user by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        abort(404, description="User not found")
    db.session.delete(user)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
