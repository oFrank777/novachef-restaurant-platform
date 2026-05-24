import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  const fetchCart = useCallback(async () => {
    if (!isAuthenticated) {
      setItems([]);
      return;
    }
    setLoading(true);
    try {
      const res = await api.get('/cart/');
      setItems(res.data || []);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const addToCart = async (menuItemId, quantity = 1) => {
    const res = await api.post('/cart/', { menu_item_id: menuItemId, quantity });
    await fetchCart();
    return res.data;
  };

  const updateQuantity = async (cartItemId, quantity) => {
    if (quantity <= 0) {
      return removeItem(cartItemId);
    }
    const res = await api.put(`/cart/${cartItemId}`, { quantity });
    await fetchCart();
    return res.data;
  };

  const removeItem = async (cartItemId) => {
    await api.del(`/cart/${cartItemId}`);
    await fetchCart();
  };

  const clearCart = async () => {
    await api.del('/cart/');
    setItems([]);
  };

  const cartTotal = items.reduce((sum, item) => {
    const price = item.menu_item?.price || item.price || 0;
    return sum + price * (item.quantity || 0);
  }, 0);

  const cartCount = items.reduce((sum, item) => sum + (item.quantity || 0), 0);

  return (
    <CartContext.Provider
      value={{
        items,
        loading,
        fetchCart,
        addToCart,
        updateQuantity,
        removeItem,
        clearCart,
        cartTotal,
        cartCount,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}

export default CartContext;
