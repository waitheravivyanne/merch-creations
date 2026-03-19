import React from 'react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
// import './Cart.css';

const Cart = () => {
  const { cartItems, loading, updateCartItem, removeFromCart, getCartTotal } = useCart();
  const { token } = useAuth();
  const navigate = useNavigate();

  if (!token) {
    navigate('/login');
    return null;
  }

  if (loading) return <div className="loading">Loading cart...</div>;

  if (cartItems.length === 0) {
    return (
      <div className="empty-cart">
        <h2>Your cart is empty</h2>
        <button onClick={() => navigate('/products')} className="btn btn-primary">
          Continue Shopping
        </button>
      </div>
    );
  }

  const handleCheckout = () => {
    alert('Checkout functionality coming soon!');
  };

  return (
    <div className="cart-container">
      <h1>Shopping Cart</h1>
      
      <div className="cart-content">
        <div className="cart-items">
          {cartItems.map(item => (
            <div key={item.id} className="cart-item">
              <img src={item.image_url} alt={item.name} />
              
              <div className="item-details">
                <h3>{item.name}</h3>
                <p className="item-price">${item.price.toFixed(2)}</p>
                
                <div className="item-actions">
                  <div className="quantity-control">
                    <button 
                      onClick={() => updateCartItem(item.id, item.quantity - 1)}
                      className="quantity-btn"
                    >-</button>
                    <span className="quantity">{item.quantity}</span>
                    <button 
                      onClick={() => updateCartItem(item.id, item.quantity + 1)}
                      className="quantity-btn"
                    >+</button>
                  </div>
                  
                  <button 
                    onClick={() => removeFromCart(item.id)}
                    className="btn btn-danger"
                  >
                    Remove
                  </button>
                </div>
              </div>
              
              <div className="item-total">
                ${(item.price * item.quantity).toFixed(2)}
              </div>
            </div>
          ))}
        </div>
        
        <div className="cart-summary">
          <h2>Order Summary</h2>
          <div className="summary-item">
            <span>Subtotal:</span>
            <span>${getCartTotal().toFixed(2)}</span>
          </div>
          <div className="summary-item">
            <span>Shipping:</span>
            <span>Free</span>
          </div>
          <div className="summary-item total">
            <span>Total:</span>
            <span>${getCartTotal().toFixed(2)}</span>
          </div>
          
          <button onClick={handleCheckout} className="btn btn-primary btn-large">
            Proceed to Checkout
          </button>
        </div>
      </div>
    </div>
  );
};

export default Cart;