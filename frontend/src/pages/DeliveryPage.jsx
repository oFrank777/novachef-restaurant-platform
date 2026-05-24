import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { eventEmitter } from '../utils/eventEmitter';
import {
  MapPin, Clock, CheckCircle, ArrowRight
} from 'lucide-react';
import {
  STATUS_FLOW, STATUS_LABELS, STATUS_COLORS, getNextStatuses, isPickupOrder
} from '../constants/orderStatus';

function getETA(status) {
  const map = { PREPARANDO: '~20 min', LISTO: '~5 min', RECOGIDO: '~15 min', ENVIADO: '~10 min' };
  return map[status] || '';
}

export default function DeliveryPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [tab, setTab] = useState('active');
  const [updatingOrderId, setUpdatingOrderId] = useState(null);

  const deliveryByOrderId = useMemo(() => {
    const map = {};
    deliveries.forEach(d => { map[d.order_id] = d; });
    return map;
  }, [deliveries]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [ordersRes, delRes] = await Promise.all([
        api.get('/orders/'),
        api.get('/delivery/').catch(() => ({ data: [] })),
      ]);
      setOrders((ordersRes.data || []).filter(o => !isPickupOrder(o)));
      setDeliveries(delRes.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const canManageOrder = (order) => {
    if (user?.role === 'admin') return true;
    if (user?.role !== 'delivery') return false;
    const del = deliveryByOrderId[order.id];
    if (order.status === 'LISTO') {
      return !del?.driver_id || del.driver_id === user.id;
    }
    if (['RECOGIDO', 'ENVIADO'].includes(order.status)) {
      return del?.driver_id === user.id;
    }
    return false;
  };

  const handleStatusChange = async (orderId, newStatus) => {
    if (updatingOrderId) return;
    setUpdatingOrderId(orderId);
    try {
      const del = deliveryByOrderId[orderId];
      if (newStatus === 'RECOGIDO' && del && !del.driver_id && user?.role === 'delivery') {
        await api.patch(`/delivery/${del.id}/status`, { driver_id: user.id });
      }
      await api.patch(`/orders/${orderId}/status`, { status: newStatus });
      eventEmitter.emit('globalError', `Pedido #${orderId}: ${STATUS_LABELS[newStatus]}`);
      await fetchData();
      if (selectedOrder?.id === orderId) {
        setSelectedOrder(prev => ({ ...prev, status: newStatus }));
      }
    } catch (err) {
      eventEmitter.emit('globalError', err.message || 'No se pudo actualizar la entrega');
    } finally {
      setUpdatingOrderId(null);
    }
  };

  const waitingKitchen = orders.filter(o => ['PENDIENTE', 'PREPARANDO'].includes(o.status));
  const readyForPickup = orders.filter(o => o.status === 'LISTO');
  const activeOrders = orders.filter(o => ['LISTO', 'RECOGIDO', 'ENVIADO'].includes(o.status));
  const completedOrders = orders.filter(o => o.status === 'ENTREGADO');
  const displayOrders = tab === 'active' ? activeOrders : completedOrders;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      <div>
        <h1 className="text-h2" style={{ marginBottom: '4px' }}>
          {user?.role === 'delivery' ? 'Mis Entregas' : 'Gestión de Entregas'}
        </h1>
        <p className="text-muted" style={{ fontSize: '0.95rem' }}>
          Flujo: cocina prepara → pedido <strong>LISTO</strong> → repartidor recoge → en camino → entregado.
        </p>
      </div>

      {(user?.role === 'delivery' || user?.role === 'admin') && waitingKitchen.length > 0 && (
        <div className="card glass-panel" style={{ padding: '16px 20px', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ fontWeight: 700, marginBottom: '8px' }}>En cocina ({waitingKitchen.length})</div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0 }}>
            El cajero debe marcar estos pedidos como <strong>En preparación</strong> y luego <strong>Listo</strong> antes de que puedas recogerlos.
          </p>
        </div>
      )}

      {readyForPickup.length > 0 && (
        <div className="card glass-panel" style={{ padding: '16px 20px', borderLeft: '4px solid #06b6d4' }}>
          <div style={{ fontWeight: 700, marginBottom: '8px' }}>Listos para recoger ({readyForPickup.length})</div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0 }}>
            Selecciona un pedido y pulsa <strong>Recogido</strong> para asignártelo y salir a entregar.
          </p>
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-full)', padding: '4px', width: 'fit-content' }}>
        {[{ key: 'active', label: `Activas (${activeOrders.length})` }, { key: 'completed', label: `Completadas (${completedOrders.length})` }].map(t => (
          <button key={t.key} onClick={() => { setTab(t.key); setSelectedOrder(null); }}
            style={{
              padding: '8px 20px', borderRadius: 'var(--radius-full)', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '0.88rem',
              background: tab === t.key ? 'var(--bg-primary)' : 'transparent',
              color: tab === t.key ? 'var(--text-primary)' : 'var(--text-muted)',
              boxShadow: tab === t.key ? 'var(--shadow-sm)' : 'none'
            }}>{t.label}</button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selectedOrder ? '1fr 1fr' : '1fr', gap: '20px', flex: 1, minHeight: 0 }}>
        <div className="card glass-panel" style={{ padding: '0', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-light)', fontWeight: 700, fontSize: '0.95rem' }}>
            {tab === 'active' ? 'Entregas Activas' : 'Entregas Completadas'}
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
            {loading ? (
              <p style={{ padding: '20px', color: 'var(--text-muted)', textAlign: 'center' }}>Cargando entregas...</p>
            ) : displayOrders.length === 0 ? (
              <p style={{ padding: '20px', color: 'var(--text-muted)', textAlign: 'center' }}>
                {tab === 'active' ? 'No hay entregas activas. Espera pedidos LISTOS desde cocina.' : 'No hay entregas completadas.'}
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {displayOrders.map(order => {
                  const del = deliveryByOrderId[order.id];
                  const assignedToMe = del?.driver_id === user?.id;
                  const unassigned = order.status === 'LISTO' && !del?.driver_id;
                  return (
                    <motion.div key={order.id} whileHover={{ scale: 1.01 }}
                      onClick={() => setSelectedOrder(order)}
                      style={{
                        padding: '14px 16px', borderRadius: 'var(--radius-md)', cursor: 'pointer',
                        border: `1px solid ${selectedOrder?.id === order.id ? 'var(--accent-blue)' : 'var(--border-light)'}`,
                        background: selectedOrder?.id === order.id ? 'var(--bg-tertiary)' : 'var(--bg-secondary)',
                      }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>ORD-{order.id.toString().padStart(4, '0')}</span>
                        <span style={{
                          padding: '3px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600,
                          background: `${STATUS_COLORS[order.status]}18`, color: STATUS_COLORS[order.status]
                        }}>{STATUS_LABELS[order.status]}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                        <MapPin size={14} /> {order.delivery_address}
                      </div>
                      {del && (
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                          Envío: ${del.delivery_cost?.toFixed(2)} · {del.distance_km} km
                          {unassigned && ' · Sin repartidor'}
                          {assignedToMe && ' · Asignado a ti'}
                        </div>
                      )}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        <Clock size={13} /> {new Date(order.created_at).toLocaleString('es-ES')}
                        {getETA(order.status) && <span style={{ marginLeft: 'auto', color: 'var(--accent-blue)', fontWeight: 600 }}>ETA: {getETA(order.status)}</span>}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <AnimatePresence>
          {selectedOrder && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
              className="card glass-panel" style={{ padding: '0', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 700, fontSize: '1rem' }}>Detalle ORD-{selectedOrder.id.toString().padStart(4, '0')}</span>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-blue)' }}>${selectedOrder.total_amount?.toFixed(2)}</span>
              </div>
              <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem', marginBottom: '16px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Seguimiento</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0px', paddingLeft: '12px' }}>
                    {STATUS_FLOW.map((status, i) => {
                      const currentIdx = STATUS_FLOW.indexOf(selectedOrder.status);
                      const isCompleted = i <= currentIdx;
                      const isCurrent = i === currentIdx;
                      const color = isCompleted ? STATUS_COLORS[status] : 'var(--border-light)';
                      return (
                        <div key={status} style={{ display: 'flex', gap: '14px' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '24px' }}>
                            <div style={{
                              width: isCurrent ? 22 : 16, height: isCurrent ? 22 : 16, borderRadius: '50%',
                              background: isCompleted ? color : 'var(--bg-tertiary)',
                              border: `2px solid ${color}`,
                              display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2
                            }}>
                              {isCompleted && <CheckCircle size={isCurrent ? 14 : 10} color="white" />}
                            </div>
                            {i < STATUS_FLOW.length - 1 && (
                              <div style={{ width: 2, height: 28, background: i < currentIdx ? STATUS_COLORS[STATUS_FLOW[i + 1]] : 'var(--border-light)' }} />
                            )}
                          </div>
                          <div style={{ paddingBottom: i < STATUS_FLOW.length - 1 ? '12px' : '0' }}>
                            <div style={{ fontWeight: isCurrent ? 700 : 500, fontSize: '0.88rem', color: isCompleted ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                              {STATUS_LABELS[status]}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div style={{ padding: '14px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <MapPin size={18} style={{ color: 'var(--accent-blue)', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Dirección</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{selectedOrder.delivery_address}</div>
                  </div>
                </div>

                {getNextStatuses(selectedOrder, user?.role).map(nextStatus => (
                  canManageOrder(selectedOrder) && (
                    <button key={nextStatus}
                      onClick={() => handleStatusChange(selectedOrder.id, nextStatus)}
                      disabled={updatingOrderId === selectedOrder.id}
                      className="btn btn-gradient"
                      style={{ width: '100%', padding: '14px', fontSize: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '8px' }}>
                      <ArrowRight size={20} />
                      {nextStatus === 'RECOGIDO' && 'Marcar como recogido'}
                      {nextStatus === 'ENVIADO' && 'Salir a entregar (en camino)'}
                      {nextStatus === 'ENTREGADO' && 'Confirmar entrega al cliente'}
                      {!['RECOGIDO', 'ENVIADO', 'ENTREGADO'].includes(nextStatus) && `Avanzar a ${STATUS_LABELS[nextStatus]}`}
                    </button>
                  )
                ))}

                {!canManageOrder(selectedOrder) && selectedOrder.status === 'LISTO' && user?.role === 'delivery' && (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                    Este pedido ya está asignado a otro repartidor.
                  </p>
                )}

                {selectedOrder.status === 'ENTREGADO' && (
                  <div style={{ padding: '14px', background: 'rgba(16,185,129,0.1)', borderRadius: '10px', textAlign: 'center', color: '#10b981', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <CheckCircle size={20} /> Entrega completada
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
