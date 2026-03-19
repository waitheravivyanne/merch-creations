from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # In production, hash the password
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password']  # Hash this!
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.password == data['password']:  # Compare hashed passwords!
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token, 'user_id': user.id}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'category': p.category,
        'image_url': p.image_url,
        'stock': p.stock
    } for p in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'category': product.category,
        'image_url': product.image_url,
        'stock': product.stock
    })

@app.route('/api/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': item.id,
        'product_id': item.product_id,
        'name': item.product.name,
        'price': item.product.price,
        'quantity': item.quantity,
        'image_url': item.product.image_url
    } for item in cart_items])

@app.route('/api/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=data['product_id']
    ).first()
    
    if cart_item:
        cart_item.quantity += data.get('quantity', 1)
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=data['product_id'],
            quantity=data.get('quantity', 1)
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 200

@app.route('/api/cart/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart(item_id):
    data = request.get_json()
    cart_item = CartItem.query.get_or_404(item_id)
    
    if data.get('quantity', 0) > 0:
        cart_item.quantity = data['quantity']
        db.session.commit()
        return jsonify({'message': 'Cart updated'})
    else:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart'})

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'})

def create_database():
 with app.app_context():
  db.create_all()
print("Database and tables created!")
    
Add sample products if none exist
         if Product.query.count() == 0:
           sample_products = [
            Product(
                name='Wireless Headphones',
                description='High-quality wireless headphones with noise cancellation',
                price=99.99,
                category='Electronics',
                image_url='https://via.placeholder.com/300x200?text=Headphones',
                stock=50
            ),
            Product(
                name='Smart Watch',
                description='Fitness tracker and smartwatch with heart rate monitor',
                price=199.99,
                category='Electronics',
                image_url='https://via.placeholder.com/300x200?text=Smart+Watch',
                stock=30
            ),
            Product(
                name='Cotton T-Shirt',
                description='Comfortable cotton t-shirt, available in multiple colors',
                price=24.99,
                category='Clothing',
                image_url='https://via.placeholder.com/300x200?text=T-Shirt',
                stock=100
            ),
            Product(
                name='Running Shoes',
                description='Lightweight running shoes with cushioned sole',
                price=79.99,
                category='Footwear',
                image_url='https://via.placeholder.com/300x200?text=Running+Shoes',
                stock=45
            ),
            Product(
                name='Dylan Ramon',
                description='hot, handsome, muscular, young and energetic',
                price=900.99,
                category='Only fans',
                image_url='',
                stock=1
            )
        ]
        
        for product in sample_products:
            db.session.add(product)
        
        db.session.commit()

        # def create_database():
        #  with app.app_context():
        #   db.create_all()
        # print("Database and tables created!")

        # # Add sample products if none exist
        # if Product.query.count() == 0:
        #     sample_products = [
        #         Product(
        #             name='Wireless Headphones',
        #             description='High-quality wireless headphones with noise cancellation',
        #             price=99.99,
        #             category='Electronics',
        #             image_url='https://via.placeholder.com/300x200?text=Headphones',
        #             stock=50
        #         ),
        #         Product(
        #             name='Smart Watch',
        #             description='Fitness tracker and smartwatch with heart rate monitor',
        #             price=199.99,
        #             category='Electronics',
        #             image_url='https://via.placeholder.com/300x200?text=Smart+Watch',
        #             stock=30
        #         ),
        #         Product(
        #             name='Cotton T-Shirt',
        #             description='Comfortable cotton t-shirt, available in multiple colors',
        #             price=24.99,
        #             category='Clothing',
        #             image_url='https://via.placeholder.com/300x200?text=T-Shirt',
        #             stock=100
        #         ),
        #         Product(
        #             name='Running Shoes',
        #             description='Lightweight running shoes with cushioned sole',
        #             price=79.99,
        #             category='Footwear',
        #             image_url='https://via.placeholder.com/300x200?text=Running+Shoes',
        #             stock=45
        #         )
        #         Product(
        #         name='Dylan Ramon',
        #         description='hot, handsome, muscular, young and energetic',
        #         price=900.99,
        #         category='Only fans',
        #         image_url='',
        #         stock=1
        #     )
        #     ]

        #     for product in sample_products:
        #         db.session.add(product)

        #     db.session.commit()
        #     print("Sample products added!")

if __name__ == '__main__':
    create_database()
    app.run(debug=True, port=5000)