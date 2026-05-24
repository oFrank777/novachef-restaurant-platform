import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { ShoppingCart, Trash2, CreditCard, ArrowRight, Package, MapPin } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { api } from '../api/client';
import { eventEmitter } from '../utils/eventEmitter';
import { createIdempotencyKey } from '../utils/idempotency';

export default function CartPage() {
  const { items, cartTotal, updateQuantity, removeItem, clearCart } = useCart();
  const [isProcessing, setIsProcessing] = useState(false);
  const [address, setAddress] = useState('');
  const navigate = useNavigate();

  const handleProcessOrder = async () => {
    if (items.length === 0 || isProcessing) return;
    setIsProcessing(true);
    try {
      const addr = (address || 'Recogida en local').trim().slice(0, 200);
      await api.post(
        '/orders/',
        { delivery_address: addr || 'Recogida en local' },
        { headers: { 'Idempotency-Key': createIdempotencyKey('order') } }
      );
      await clearCart();
      eventEmitter.emit('globalError', 'Pedido enviado correctamente');
      navigate('/orders');
    } catch {
      setIsProcessing(false);
    }
  };

  const tax = cartTotal * 0.085;
  const serviceFee = items.length > 0 ? 3.00 : 0;
  const finalTotal = cartTotal + tax + serviceFee;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h1 className="text-h2" style={{ marginBottom: '4px' }}>Carrito de Compras</h1>
        <p className="text-muted" style={{ fontSize: '0.95rem' }}>Revisa tu pedido antes de enviarlo a cocina.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        {}
        <div className="card glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ fontWeight: 700, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShoppingCart size={20} style={{ color: 'var(--text-muted)' }} /> Pedido Actual
            </h3>
            {items.length > 0 && (
              <button onClick={clearCart} style={{ padding: '6px 12px', borderRadius: '8px', background: 'var(--bg-tertiary)', border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                Vaciar
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <AnimatePresence>
              {items.length === 0 ? (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Tu carrito está vacío. Añade platillos desde el menú.
                </motion.div>
              ) : (
                items.map((item, i) => (
                  <motion.div key={item.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} transition={{ delay: i * 0.04 }}
                    style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '12px 14px', background: 'var(--bg-secondary)', borderRadius: '10px', border: '1px solid var(--border-light)' }}>
                    <div style={{ width: 48, height: 48, borderRadius: 10, background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem', flexShrink: 0 }}>
                      <Package size={20} style={{ color: 'var(--text-muted)' }} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.menu_item?.name || 'Producto'}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{item.menu_item?.category || 'General'}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-primary)', borderRadius: '20px', padding: '2px', border: '1px solid var(--border-light)' }}>
                        <button onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          style={{ width: 26, height: 26, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: 'none', cursor: 'pointer', fontSize: '0.9rem' }}>-</button>
                        <span style={{ width: 28, textAlign: 'center', fontWeight: 700, fontSize: '0.85rem' }}>{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          style={{ width: 26, height: 26, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--text-primary)', color: 'var(--bg-primary)', border: 'none', cursor: 'pointer', fontSize: '0.9rem' }}>+</button>
                      </div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem', width: '70px', textAlign: 'right' }}>
                        ${((item.menu_item?.price || 0) * item.quantity).toFixed(2)}
                      </div>
                      <button onClick={() => removeItem(item.id)} style={{ padding: '6px', background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>

            <Link to="/menu" style={{ textDecoration: 'none' }}>
              <button style={{ width: '100%', padding: '16px', borderRadius: '10px', border: '1px dashed var(--border-light)', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 500, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <Package size={16} /> Añadir más productos del menú
              </button>
            </Link>
          </div>
        </div>

        {}
        <div className="card glass-panel" style={{ padding: '24px', height: 'fit-content' }}>
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '20px' }}>Resumen del Pedido</h3>

          {}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <MapPin size={14} /> Dirección de Entrega
            </label>
            <input type="text" className="input" value={address} onChange={e => setAddress(e.target.value)}
              placeholder="Ej: Av. Principal 123, Lima" style={{ padding: '10px 14px', fontSize: '0.9rem' }} />
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Dejar vacío para recogida en local</div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid var(--border-light)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <span>Subtotal</span>
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>${cartTotal.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <span>Impuesto (8.5%)</span>
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>${tax.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <span>Tarifa de Servicio</span>
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>${serviceFee.toFixed(2)}</span>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <span style={{ fontWeight: 700, fontSize: '1rem' }}>Total</span>
            <span style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-blue)' }}>${finalTotal.toFixed(2)}</span>
          </div>

          <button disabled={items.length === 0 || isProcessing} onClick={handleProcessOrder}
            className="btn btn-gradient"
            style={{ width: '100%', padding: '14px', fontSize: '1rem', marginBottom: '10px', opacity: items.length === 0 ? 0.5 : 1, cursor: items.length === 0 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <CreditCard size={18} /> {isProcessing ? 'Procesando...' : 'Confirmar Pedido'}
          </button>
        </div>
      </div>
    </div>
  );
}
