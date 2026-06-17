import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = useCart();
  const { token } = useAuth();

  useEffect(() => {
    // Move fetchProduct inside useEffect
    const fetchProduct = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/products/${id}`);
        setProduct(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching product:', error);
        setLoading(false);
      }
    };
    
    fetchProduct();
  }, [id]); // Only id is needed as dependency

  const handleAddToCart = () => {
    if (!token) {
      navigate('/login');
      return;
    }
    addToCart(product.id, quantity);
    alert('Product added to cart!');
  };

  const handleQuantityChange = (change) => {
    const newQuantity = quantity + change;
    if (newQuantity >= 1 && newQuantity <= (product?.stock || 1)) {
      setQuantity(newQuantity);
    }
  };

  if (loading) return <div className="loading">Loading product...</div>;
  if (!product) return <div className="error">Product not found</div>;

  return (
    <div className="product-detail-container">
      <button onClick={() => navigate('/products')} className="btn btn-secondary">
        ← Back to Products
      </button>
      
      <div className="product-detail">
        <div className="product-image">
          <img src={product.image_url} alt={product.name} />
        </div>
        
        <div className="product-info">
          <h1>{product.name}</h1>
          <p className="product-category">Category: {product.category}</p>
          <p className="product-price">${product.price.toFixed(2)}</p>
          <p className="product-description">{product.description}</p>
          <p className="product-stock">Availability: {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}</p>
          
          {product.stock > 0 && (
            <div className="purchase-section">
              <div className="quantity-control">
                <button onClick={() => handleQuantityChange(-1)} className="quantity-btn">-</button>
                <span className="quantity">{quantity}</span>
                <button onClick={() => handleQuantityChange(1)} className="quantity-btn">+</button>
              </div>
              
              <button onClick={handleAddToCart} className="btn btn-primary btn-large">
                Add to Cart
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;