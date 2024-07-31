from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Define the Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)

# Create the database tables
with app.app_context():
    db.create_all()

# Root route
@app.route('/')
def home():
    return "Welcome to the Flask API!"

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Create a new item
@app.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    new_item = Item(name=data['name'], description=data.get('description'))
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item created successfully'}), 201

# Get all items
@app.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    items = Item.query.all()
    output = [{'id': item.id, 'name': item.name, 'description': item.description} for item in items]
    return jsonify(output), 200

# Get a single item by ID
@app.route('/items/<int:id>', methods=['GET'])
@jwt_required()
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify({'id': item.id, 'name': item.name, 'description': item.description}), 200

# Update an item by ID
@app.route('/items/<int:id>', methods=['PUT'])
@jwt_required()
def update_item(id):
    data = request.get_json()
    item = Item.query.get_or_404(id)
    item.name = data['name']
    item.description = data.get('description')
    db.session.commit()
    return jsonify({'message': 'Item updated successfully'}), 200

# Delete an item by ID
@app.route('/items/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
