import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import {
  DollarSign, ShoppingBag, Activity, Package,
  ArrowUpRight, Clock, AlertTriangle, Truck, CheckCircle
} from 'lucide-react';

import { STATUS_LABELS, STATUS_COLORS, isPickupOrder } from '../constants/orderStatus';

export default function DashboardPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([]);
  const [orders, setOrders] = useState([]);
  const [lowStock, setLowStock] = useState([]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const role = user?.role;

        if (role === 'admin' || role === 'cajero') {
          const [salesRes, ordersRes, invRes] = await Promise.all([
            role === 'admin'
              ? api.get('/reports/sales').catch(() => ({ data: { total_revenue: 0, total_orders: 0 } }))
              : Promise.resolve({ data: null }),
            api.get('/orders/'),
            role === 'admin'
              ? api.get('/inventory/').catch(() => ({ data: [] }))
              : Promise.resolve({ data: [] }),
          ]);
          const allOrders = ordersRes.data || [];
          const inv = invRes.data || [];
          const revenue = salesRes.data?.total_revenue
            ?? allOrders.filter(o => o.status === 'ENTREGADO').reduce((s, o) => s + (o.total_amount || 0), 0);
          const totalOrders = salesRes.data?.total_orders ?? allOrders.length;
          const active = allOrders.filter(o => !['ENTREGADO', 'CANCELADO'].includes(o.status)).length;
          const lowItems = inv.filter(i => i.stock <= i.min_stock);

          const pendingKitchen = allOrders.filter(o => ['PENDIENTE', 'PREPARANDO'].includes(o.status)).length;
          setStats(role === 'cajero' ? [
            { label: 'Cola de Cocina', value: pendingKitchen.toString(), icon: Clock, color: '#f59e0b' },
            { label: 'Pedidos Activos', value: active.toString(), icon: ShoppingBag, color: '#8b5cf6' },
            { label: 'Listos / Enviados', value: allOrders.filter(o => ['LISTO', 'RECOGIDO', 'ENVIADO'].includes(o.status)).length.toString(), icon: Truck, color: '#3b82f6' },
            { label: 'Ingresos (entregados)', value: `$${revenue.toFixed(2)}`, icon: DollarSign, color: '#10b981' },
          ] : [
            { label: 'Ingresos Totales', value: `$${revenue.toFixed(2)}`, icon: DollarSign, color: '#10b981' },
            { label: 'Pedidos Activos', value: active.toString(), icon: ShoppingBag, color: '#f59e0b' },
            { label: 'Total Pedidos', value: totalOrders.toString(), icon: Activity, color: '#3b82f6' },
            { label: 'Alertas Stock', value: lowItems.length.toString(), icon: AlertTriangle, color: lowItems.length > 0 ? '#ef4444' : '#10b981' },
          ]);
          setOrders(allOrders.slice(0, 8));
          setLowStock(lowItems.slice(0, 5));

        } else if (role === 'delivery') {
          const ordersRes = await api.get('/orders/');
          const all = (ordersRes.data || []).filter(o => !isPickupOrder(o));
          const ready = all.filter(o => o.status === 'LISTO');
          const inRoute = all.filter(o => ['RECOGIDO', 'ENVIADO'].includes(o.status));
          const delivered = all.filter(o => o.status === 'ENTREGADO');

          setStats([
            { label: 'Listos para recoger', value: ready.length.toString(), icon: Package, color: '#06b6d4' },
            { label: 'En ruta', value: inRoute.length.toString(), icon: Truck, color: '#f59e0b' },
            { label: 'Completadas hoy', value: delivered.length.toString(), icon: CheckCircle, color: '#10b981' },
          ]);
          setOrders([...ready, ...inRoute].slice(0, 8));

        } else {
          const ordersRes = await api.get('/orders/');
          const my = ordersRes.data || [];
          const totalSpent = my.reduce((s, o) => s + (o.total_amount || 0), 0);
          const active = my.filter(o => !['ENTREGADO', 'CANCELADO'].includes(o.status)).length;

          setStats([
            { label: 'Pedidos Activos', value: active.toString(), icon: ShoppingBag, color: '#f59e0b' },
            { label: 'Total Pedidos', value: my.length.toString(), icon: Package, color: '#3b82f6' },
            { label: 'Total Gastado', value: `$${totalSpent.toFixed(2)}`, icon: DollarSign, color: '#10b981' },
          ]);
          setOrders(my.slice(0, 8));
        }
      } catch (err) {
        console.error('Error cargando dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', color: 'var(--text-muted)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: 40, height: 40, border: '3px solid var(--border-light)', borderTopColor: 'var(--accent-blue)', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }} />
          <p>Cargando panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
      <div>
        <h1 className="text-h2" style={{ marginBottom: '4px' }}>
          Hola, {user?.first_name || user?.username || 'Usuario'}
        </h1>
        <p className="text-muted" style={{ fontSize: '1rem' }}>Aquí tienes el resumen de tu actividad.</p>
      </div>

      {}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', width: '100%' }}>
        {stats.map((stat, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
            className="card glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div style={{ width: 44, height: 44, borderRadius: 12, background: `${stat.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: stat.color }}>
                <stat.icon size={22} />
              </div>
              <ArrowUpRight size={16} style={{ color: 'var(--text-muted)' }} />
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500, marginBottom: '4px' }}>{stat.label}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>{stat.value}</div>
          </motion.div>
        ))}
      </div>

      {}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        className="card glass-panel" style={{ padding: '24px', width: '100%' }}>
        <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)' }}>Pedidos Recientes</h3>
        {orders.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>No hay pedidos registrados aún.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Pedido</th>
                  <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estado</th>
                  <th style={{ padding: '10px 12px', textAlign: 'right', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total</th>
                  <th style={{ padding: '10px 12px', textAlign: 'right', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <td style={{ padding: '12px', fontWeight: 600, fontSize: '0.9rem' }}>ORD-{order.id.toString().padStart(4, '0')}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        display: 'inline-block', padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 600,
                        background: `${STATUS_COLORS[order.status] || '#888'}18`,
                        color: STATUS_COLORS[order.status] || '#888'
                      }}>
                        {STATUS_LABELS[order.status] || order.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', fontWeight: 600, fontSize: '0.95rem' }}>${order.total_amount?.toFixed(2)}</td>
                    <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{new Date(order.created_at).toLocaleDateString('es-ES')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>

      {}
      {lowStock.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="card glass-panel" style={{ padding: '24px', border: '1px solid rgba(239,68,68,0.2)' }}>
          <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '16px', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} /> Alertas de Inventario Bajo
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {lowStock.map(item => (
              <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', background: 'rgba(239,68,68,0.05)', borderRadius: '8px' }}>
                <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>{item.menu_item?.name || `Producto #${item.menu_item_id}`}</span>
                <span style={{ fontSize: '0.85rem', color: '#ef4444', fontWeight: 600 }}>Stock: {item.stock} / Mín: {item.min_stock}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
