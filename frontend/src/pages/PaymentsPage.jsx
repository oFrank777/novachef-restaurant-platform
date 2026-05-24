import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CreditCard, DollarSign, ArrowUpRight, ArrowDownRight, Download, FileText } from 'lucide-react';
import { api } from '../api/client';
import { eventEmitter } from '../utils/eventEmitter';

function exportCSV(orders) {
  const header = 'Pedido,Estado,Total,Fecha\n';
  const rows = orders.map(o => `ORD-${o.id.toString().padStart(4,'0')},${o.status},${o.total_amount.toFixed(2)},${new Date(o.created_at).toLocaleDateString('es-ES')}`).join('\n');
  const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `pagos_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function PaymentsPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true);
        const res = await api.get('/orders/');
        const successful = (res.data || []).filter(o => o.status !== 'CANCELADO').sort((a, b) => b.id - a.id);
        setOrders(successful);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const totalRevenue = orders.reduce((acc, o) => acc + o.total_amount, 0);
  const processingFees = totalRevenue * 0.029;
  const netVolume = totalRevenue - processingFees;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 className="text-h2" style={{ marginBottom: '4px' }}>Transacciones</h1>
          <p className="text-muted" style={{ fontSize: '0.95rem' }}>Historial de pagos y facturación del negocio.</p>
        </div>
        <button className="btn btn-secondary" onClick={() => { exportCSV(orders); eventEmitter.emit('globalError', 'Archivo CSV exportado correctamente'); }}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Download size={16} /> Exportar CSV
        </button>
      </div>

      {}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="card glass-panel" style={{ padding: '24px' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>Volumen Neto</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>${netVolume.toFixed(2)}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontWeight: 600, fontSize: '0.85rem' }}>
            <ArrowUpRight size={16} /> Tiempo Real
          </div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card glass-panel" style={{ padding: '24px' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>Tarifas de Procesamiento (2.9%)</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>${processingFees.toFixed(2)}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#ef4444', fontWeight: 600, fontSize: '0.85rem' }}>
            <ArrowDownRight size={16} /> Comisión
          </div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card glass-panel" style={{ padding: '24px' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>Transacciones Exitosas</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>{orders.length}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontWeight: 600, fontSize: '0.85rem' }}>
            <ArrowUpRight size={16} /> Tiempo Real
          </div>
        </motion.div>
      </div>

      {}
      <div className="card glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-light)', fontWeight: 700 }}>Pagos Recientes</div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-light)', background: 'var(--bg-secondary)' }}>
                <th style={{ padding: '10px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Transacción</th>
                <th style={{ padding: '10px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estado</th>
                <th style={{ padding: '10px 16px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Monto</th>
                <th style={{ padding: '10px 16px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>Cargando transacciones...</td></tr>
              ) : orders.length === 0 ? (
                <tr><td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>No hay transacciones registradas.</td></tr>
              ) : (
                orders.slice(0, 20).map(order => (
                  <tr key={order.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <CreditCard size={16} />
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Pago ORD-{order.id.toString().padStart(4, '0')}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ padding: '3px 10px', borderRadius: '20px', fontSize: '0.76rem', fontWeight: 600, background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>Exitoso</span>
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 700, color: '#10b981', fontSize: '0.95rem' }}>+${order.total_amount.toFixed(2)}</td>
                    <td style={{ padding: '14px 16px', textAlign: 'right', fontSize: '0.82rem', color: 'var(--text-muted)' }}>{new Date(order.created_at).toLocaleString('es-ES')}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
