import React, { createContext, useState, useContext, useEffect, useCallback } from 'react'; // Add useCallback
import axios from 'axios';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  const API_URL = 'http://localhost:5000/api';

  // Wrap fetchCart in useCallback
  const fetchCart = useCallback(async () => {
    if (!token) return; // Add early return if no token
    
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/cart`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCartItems(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  }, [token, API_URL]); // Add dependencies

  useEffect(() => {
    if (token) {
      fetchCart();
    } else {
      setCartItems([]);
    }
  }, [token, fetchCart]); // Add fetchCart to dependencies

  const addToCart = useCallback(async (productId, quantity = 1) => {
    try {
      await axios.post(`${API_URL}/cart/add`, 
        { product_id: productId, quantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchCart();
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  }, [token, API_URL, fetchCart]);

  const updateCartItem = useCallback(async (itemId, quantity) => {
    try {
      await axios.put(`${API_URL}/cart/update/${itemId}`,
        { quantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchCart();
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  }, [token, API_URL, fetchCart]);

  const removeFromCart = useCallback(async (itemId) => {
    try {
      await axios.delete(`${API_URL}/cart/remove/${itemId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchCart();
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  }, [token, API_URL, fetchCart]);

  const getCartTotal = useCallback(() => {
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  }, [cartItems]);

  return (
    <CartContext.Provider value={{
      cartItems,
      loading,
      addToCart,
      updateCartItem,
      removeFromCart,
      getCartTotal,
      fetchCart
    }}>
      {children}
    </CartContext.Provider>
  );
};