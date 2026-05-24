import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { eventEmitter } from '../utils/eventEmitter';
import {
  ArrowRight, Eye, X, XCircle
} from 'lucide-react';
import {
  STATUS_FLOW, STATUS_LABELS, STATUS_COLORS, getNextStatuses, isPickupOrder
} from '../constants/orderStatus';

export default function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [detailOrder, setDetailOrder] = useState(null);
  const [updatingOrderId, setUpdatingOrderId] = useState(null);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const res = await api.get('/orders/');
      setOrders(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, []);

  const handleStatusChange = async (orderId, newStatus) => {
    if (updatingOrderId) return;
    setUpdatingOrderId(orderId);
    try {
      await api.patch(`/orders/${orderId}/status`, { status: newStatus });
      eventEmitter.emit('globalError', `Pedido #${orderId} actualizado a: ${STATUS_LABELS[newStatus] || newStatus}`);
      fetchOrders();
      if (detailOrder?.id === orderId) setDetailOrder(prev => ({ ...prev, status: newStatus }));
    } catch (err) {
      eventEmitter.emit('globalError', err.message || 'No se pudo actualizar el pedido');
    } finally {
      setUpdatingOrderId(null);
    }
  };

  const filtered = filter === 'ALL' ? orders : orders.filter(o => o.status === filter);
  const isStaff = user?.role === 'admin' || user?.role === 'cajero';
  const isDelivery = user?.role === 'delivery';

  const filterTabs = [
    { key: 'ALL', label: 'Todos' },
    { key: 'PENDIENTE', label: 'Pendientes' },
    { key: 'PREPARANDO', label: 'Preparando' },
    { key: 'LISTO', label: 'Listos' },
    { key: 'ENVIADO', label: 'En Camino' },
    { key: 'ENTREGADO', label: 'Entregados' },
    { key: 'CANCELADO', label: 'Cancelados' },
  ];

  const pageSubtitle = isStaff
    ? 'Gestiona la cocina, mostrador y cancelaciones del negocio.'
    : isDelivery
      ? 'Consulta pedidos a domicilio y coordina con la pantalla de Entregas.'
      : 'Revisa el estado de tus pedidos.';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%' }}>
      <div>
        <h1 className="text-h2" style={{ marginBottom: '4px' }}>Pedidos</h1>
        <p className="text-muted" style={{ fontSize: '0.95rem' }}>{pageSubtitle}</p>
      </div>

      <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', padding: '4px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-full)', width: 'fit-content', maxWidth: '100%' }}>
        {filterTabs.map(t => (
          <button key={t.key} onClick={() => setFilter(t.key)}
            style={{
              padding: '7px 18px', borderRadius: 'var(--radius-full)', border: 'none', cursor: 'pointer',
              fontWeight: 600, fontSize: '0.82rem', whiteSpace: 'nowrap',
              background: filter === t.key ? 'var(--bg-primary)' : 'transparent',
              color: filter === t.key ? 'var(--text-primary)' : 'var(--text-muted)',
              boxShadow: filter === t.key ? 'var(--shadow-sm)' : 'none'
            }}>{t.label}</button>
        ))}
      </div>

      <div className="card glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '700px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-light)', background: 'var(--bg-secondary)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Pedido</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estado</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tipo</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Dirección</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Fecha</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>Cargando pedidos...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan="7" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>No hay pedidos en esta categoría.</td></tr>
              ) : (
                filtered.map(order => {
                  const nextStatuses = getNextStatuses(order, user?.role);
                  return (
                    <tr key={order.id} style={{ borderBottom: '1px solid var(--border-light)', transition: 'background 0.15s' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-secondary)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                      <td style={{ padding: '14px 16px', fontWeight: 700, fontSize: '0.9rem' }}>
                        ORD-{order.id.toString().padStart(4, '0')}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          display: 'inline-block', padding: '4px 12px', borderRadius: '20px', fontSize: '0.76rem', fontWeight: 600,
                          background: `${STATUS_COLORS[order.status] || '#888'}18`, color: STATUS_COLORS[order.status] || '#888'
                        }}>{STATUS_LABELS[order.status] || order.status}</span>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                        {isPickupOrder(order) ? 'Mostrador' : 'Domicilio'}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {order.delivery_address || 'Recogida en local'}
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 700, fontSize: '0.95rem' }}>${order.total_amount?.toFixed(2)}</td>
                      <td style={{ padding: '14px 16px', textAlign: 'right', fontSize: '0.82rem', color: 'var(--text-muted)' }}>{new Date(order.created_at).toLocaleDateString('es-ES')}</td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                          <button onClick={() => setDetailOrder(order)} title="Ver detalle"
                            style={{ width: 32, height: 32, borderRadius: '8px', background: 'var(--bg-tertiary)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                            <Eye size={16} />
                          </button>
                          {nextStatuses.filter(s => s !== 'CANCELADO').map(ns => (
                            <button key={ns} onClick={() => handleStatusChange(order.id, ns)} disabled={updatingOrderId === order.id} title={STATUS_LABELS[ns]}
                              style={{ height: 32, padding: '0 12px', borderRadius: '8px', background: `${STATUS_COLORS[ns]}18`, border: 'none', cursor: 'pointer', fontSize: '0.76rem', fontWeight: 600, color: STATUS_COLORS[ns], display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <ArrowRight size={14} /> {STATUS_LABELS[ns]}
                            </button>
                          ))}
                          {nextStatuses.includes('CANCELADO') && (
                            <button onClick={() => handleStatusChange(order.id, 'CANCELADO')} disabled={updatingOrderId === order.id} title="Cancelar"
                              style={{ width: 32, height: 32, borderRadius: '8px', background: 'rgba(239,68,68,0.1)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ef4444' }}>
                              <XCircle size={16} />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      <AnimatePresence>
        {detailOrder && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, backdropFilter: 'blur(4px)' }}
            onClick={() => setDetailOrder(null)}>
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              className="card glass-panel" style={{ width: '500px', maxWidth: '90%', maxHeight: '80vh', overflow: 'auto', padding: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontWeight: 700, fontSize: '1.2rem' }}>Pedido ORD-{detailOrder.id.toString().padStart(4, '0')}</h2>
                <button onClick={() => setDetailOrder(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={22} /></button>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', gap: '4px', marginBottom: '8px' }}>
                  {STATUS_FLOW.map((s, i) => {
                    const idx = STATUS_FLOW.indexOf(detailOrder.status);
                    return (
                      <div key={s} style={{ flex: 1, height: 4, borderRadius: 2, background: i <= idx ? STATUS_COLORS[s] : 'var(--border-light)' }} />
                    );
                  })}
                </div>
                <div style={{ textAlign: 'center', fontSize: '0.85rem', fontWeight: 600, color: STATUS_COLORS[detailOrder.status] }}>
                  {STATUS_LABELS[detailOrder.status] || detailOrder.status}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Total</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 800 }}>${detailOrder.total_amount?.toFixed(2)}</div>
                </div>
                <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Tipo</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{isPickupOrder(detailOrder) ? 'Recojo en local' : 'Entrega a domicilio'}</div>
                </div>
              </div>

              {detailOrder.delivery_address && (
                <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginBottom: '16px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Dirección</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{detailOrder.delivery_address}</div>
                </div>
              )}

              {detailOrder.items && detailOrder.items.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '10px', textTransform: 'uppercase' }}>Productos</div>
                  {detailOrder.items.map(item => (
                    <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-light)', fontSize: '0.9rem' }}>
                      <span>x{item.quantity} Producto #{item.menu_item_id}</span>
                      <span style={{ fontWeight: 600 }}>${(item.unit_price * item.quantity).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
